"""
Image extractor for the knowledge graph-based business consulting system.
Extracts text, objects, and insights from image files using vision models.
"""

import os
import logging
import json
import requests
import base64
from datetime import datetime
from PIL import Image
import io
import config
from extractors.extractor_utils import (
    ensure_output_dir, generate_output_filename, save_extraction_result,
    create_extraction_result_template, detect_entities, COMMON_ENTITY_PATTERNS
)

# Set up logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def extract(file_path, output_dir=None):
    """
    Extract content from an image file
    
    Args:
        file_path (str): Path to the image file
        output_dir (str, optional): Directory to save parsed data
        
    Returns:
        dict: Extracted content with metadata
    """
    logger.info(f"Extracting content from image: {file_path}")
    
    # Validate file exists
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Check file extension
    file_ext = os.path.splitext(file_path)[1].lower()[1:]  # Remove the dot
    if file_ext not in config.VISION_SETTINGS['supported_formats']:
        raise ValueError(f"Unsupported image format: {file_ext}")
    
    # Ensure output directory exists
    output_dir = ensure_output_dir(output_dir)
    
    # Generate output filename
    name_without_ext, output_filename = generate_output_filename(file_path)
    output_path = os.path.join(output_dir, output_filename)
    
    # Create extraction result template
    result = create_extraction_result_template(file_path, "image_extractor")
    
    try:
        # Open and process the image
        with Image.open(file_path) as img:
            # Get image metadata
            width, height = img.size
            img_format = img.format
            img_mode = img.mode
            
            # Store basic image metadata
            result["document_metadata"] = {
                "width": width,
                "height": height,
                "format": img_format,
                "color_mode": img_mode,
                "file_size_bytes": os.path.getsize(file_path)
            }
            
            # Resize image if needed
            max_size = config.VISION_SETTINGS['max_image_size']
            if width > max_size or height > max_size:
                if width > height:
                    new_width = max_size
                    new_height = int(height * (max_size / width))
                else:
                    new_height = max_size
                    new_width = int(width * (max_size / height))
                
                img = img.resize((new_width, new_height))
                logger.info(f"Resized image from {width}x{height} to {new_width}x{new_height}")
            
            # Convert image to base64 for vision model
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format=img_format)
            img_base64 = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')
            
            # Extract insights using vision model
            vision_results = _process_with_vision_model(img_base64, file_path)
            
            # Extract entities from the text content
            if vision_results.get("text"):
                entities = detect_entities(vision_results["text"], COMMON_ENTITY_PATTERNS)
                result["content"]["entities"] = entities
            
            # Add vision results to the output
            result["content"]["text"] = vision_results.get("text", "")
            result["content"]["objects"] = vision_results.get("objects", [])
            result["content"]["charts"] = vision_results.get("charts", [])
            result["content"]["insights"] = vision_results.get("insights", [])
            
            # Add image info
            result["content"]["images"] = [{
                "image_id": "main_image",
                "width": width,
                "height": height,
                "format": img_format,
                "description": vision_results.get("description", "")
            }]
        
        # Save extraction result
        save_extraction_result(result, output_path)
        
        logger.info(f"Extraction completed successfully. Output saved to: {output_path}")
        return result
    
    except Exception as e:
        logger.error(f"Image extraction failed: {e}")
        raise

def _process_with_vision_model(img_base64, file_path):
    """
    Process image using the vision model
    
    Args:
        img_base64: Base64 encoded image
        file_path: Original file path (for reference)
        
    Returns:
        dict: Vision model results
    """
    logger.info("Processing image with vision model")
    
    # Get model configuration
    model_config = config.MODELS['vision']
    
    # Create prompt for the vision model
    prompt = f"""
    Analyze this business document image and extract the following:
    1. All visible text in the image
    2. Type of document (chart, diagram, screenshot, etc.)
    3. Main topics or subject matter
    4. Any key metrics, numbers, or KPIs visible
    5. Entities mentioned (companies, people, products)
    
    If the image contains a chart or graph:
    1. Describe the type of chart
    2. Summarize the main trend or insight
    3. List the key data points (if visible)
    
    Format your response as JSON with these fields:
    - type: document type
    - text: all visible text
    - description: brief description of the image
    - insights: list of key insights
    - objects: list of objects detected
    - charts: details about any charts (if present)
    
    Only return the JSON and nothing else.
    """
    
    # Call the vision model API (Ollama)
    try:
        response = requests.post(
            model_config['endpoint'],
            json={
                "model": model_config['name'],
                "messages": [
                    {"role": "user", "content": prompt},
                ],
                "stream": False,
                "images": [img_base64],
                **model_config['parameters']
            }
        )
        
        result = response.json()
        content = result.get('message', {}).get('content', '')
        
        # Extract JSON from the response
        start_idx = content.find('{')
        end_idx = content.rfind('}') + 1
        
        if start_idx >= 0 and end_idx > start_idx:
            json_str = content[start_idx:end_idx]
            try:
                vision_data = json.loads(json_str)
                logger.info("Successfully parsed vision model response")
                return vision_data
            except json.JSONDecodeError:
                logger.warning("Failed to parse JSON from vision model response")
        
        # Fallback to basic extraction if JSON parsing fails
        return _create_fallback_vision_results(content)
        
    except Exception as e:
        logger.error(f"Vision model processing failed: {e}")
        return _create_fallback_vision_results("")

def _create_fallback_vision_results(text_content):
    """
    Create fallback vision results when model processing fails
    
    Args:
        text_content: Any text content extracted
        
    Returns:
        dict: Basic vision results
    """
    return {
        "type": "unknown",
        "text": text_content or "No text extracted",
        "description": "Image analysis failed",
        "insights": ["Automated analysis failed, manual review recommended"],
        "objects": [],
        "charts": []
    }

# For testing
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python image_extractor.py <image_file_path>")
        sys.exit(1)
        
    image_path = sys.argv[1]
    extract(image_path)