"""
Image extractor for the knowledge graph-based business consulting system.
Extracts text, objects, and insights from image files using vision models.
"""
import re
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
    Process image using the vision model with enhanced business document analysis
    
    Args:
        img_base64: Base64 encoded image
        file_path: Original file path (for reference)
        
    Returns:
        dict: Vision model results with structured business insights
    """
    logger.info("Processing image with vision model")
    
    # Get model configuration
    model_config = config.MODELS['vision']
    
    # Determine likely document type from file extension for better prompting
    file_ext = os.path.splitext(file_path)[1].lower()
    is_likely_chart = file_ext in ['.png', '.jpg', '.jpeg'] and 'chart' in file_path.lower()
    
    # Create enhanced prompt for the vision model based on likely content
    if is_likely_chart:
        prompt = _create_chart_analysis_prompt()
    else:
        prompt = _create_general_document_prompt()
    
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
                
                # Post-process the results
                vision_data = _post_process_vision_results(vision_data, file_path)
                
                return vision_data
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse JSON from vision model response: {e}")
                # Try to fix common JSON parsing issues
                fixed_json = _fix_json_response(content)
                if fixed_json:
                    logger.info("Successfully fixed and parsed JSON response")
                    return _post_process_vision_results(fixed_json, file_path)
        
        # Fallback to text extraction if JSON parsing fails
        logger.warning("Using fallback text extraction from vision model response")
        text_content = _extract_text_from_non_json_response(content)
        return _create_fallback_vision_results(text_content)
        
    except Exception as e:
        logger.error(f"Vision model processing failed: {e}")
        return _create_fallback_vision_results("")

def _create_chart_analysis_prompt():
    """
    Create a specialized prompt for chart and graph analysis
    
    Returns:
        str: Prompt text
    """
    return """
    Analyze this business chart or graph image and extract detailed information in a structured format.
    
    Please identify:
    1. Chart type (line, bar, pie, scatter, etc.)
    2. Title and subtitle if present
    3. X and Y axis labels and units
    4. Legend items
    5. All visible data series names and values
    6. Key trends, patterns, or outliers
    7. All text visible in the image
    
    For financial or business charts, please also identify:
    1. Time period covered
    2. Financial metrics shown (revenue, profit, growth, etc.)
    3. Performance indicators (positive/negative trends, significant changes)
    4. Any annotations, callouts or important notes
    5. Companies or entities mentioned
    
    Format your response as JSON with these fields:
    {
      "document_type": "chart type (line, bar, pie, etc.)",
      "title": "chart title",
      "text": "all visible text in the image",
      "description": "brief factual description of what the chart shows",
      "time_period": "time range covered by the data",
      "metrics": ["list of metrics shown"],
      "entities": ["companies or organizations mentioned"],
      "axis_info": {
        "x_axis": {"label": "x-axis label", "units": "units if specified"},
        "y_axis": {"label": "y-axis label", "units": "units if specified"}
      },
      "data_series": [
        {"name": "series name", "values": [values if clearly visible]},
        ...
      ],
      "key_insights": ["list of 3-5 key insights from the chart"],
      "limitations": ["any limitations in your analysis"]
    }
    
    Return ONLY valid JSON with no explanations or text outside the JSON structure.
    """

def _create_general_document_prompt():
    """
    Create a general prompt for business document analysis
    
    Returns:
        str: Prompt text
    """
    return """
    Analyze this business document image and extract structured information.
    
    Please identify:
    1. Document type (presentation slide, report page, form, screenshot, diagram, etc.)
    2. All visible text in the image
    3. Main topics or subject matter
    4. Key business entities mentioned (companies, people, products, etc.)
    5. Any metrics, numbers, dates, or KPIs visible
    6. The overall purpose or context of this document
    
    If the image contains tables:
    1. Table headers
    2. Key data shown in the table
    3. What the table represents
    
    If the image contains diagrams or flowcharts:
    1. What the diagram represents
    2. Key components and their relationships
    3. Main processes or workflows shown
    
    Format your response as JSON with these fields:
    {
      "document_type": "type of document",
      "text": "all visible text in the image",
      "description": "brief factual description of the document",
      "main_topics": ["list of main topics"],
      "entities": {
        "companies": ["company names"],
        "people": ["person names"],
        "products": ["product names"],
        "other": ["other important entities"]
      },
      "metrics": [{"name": "metric name", "value": "metric value", "unit": "unit if any"}],
      "tables": [
        {"headers": ["header1", "header2", ...], "description": "what this table shows"}
      ],
      "diagrams": [
        {"type": "diagram type", "components": ["key elements"], "description": "what this diagram shows"}
      ],
      "key_insights": ["list of 3-5 key business insights from this document"],
      "limitations": ["any limitations in your analysis"]
    }
    
    Return ONLY valid JSON with no explanations or text outside the JSON structure.
    """

def _post_process_vision_results(vision_data, file_path):
    """
    Post-process and enhance the vision model results
    
    Args:
        vision_data: Raw vision results
        file_path: Original file path
        
    Returns:
        dict: Enhanced vision results
    """
    # Ensure all expected fields exist
    if "type" not in vision_data and "document_type" in vision_data:
        vision_data["type"] = vision_data["document_type"]
    
    # Create a standard set of fields
    standard_fields = [
        "type", "text", "description", "insights", "objects", "charts"
    ]
    
    for field in standard_fields:
        if field not in vision_data:
            if field == "insights" and "key_insights" in vision_data:
                vision_data["insights"] = vision_data["key_insights"]
            else:
                vision_data[field] = [] if field in ["insights", "objects", "charts"] else ""
    
    # Handle chart-specific data
    if "chart" in vision_data.get("type", "").lower() or any("chart" in str(insight).lower() for insight in vision_data.get("insights", [])):
        if "charts" not in vision_data or not vision_data["charts"]:
            # Create chart data structure if it doesn't exist
            chart_data = {
                "type": vision_data.get("type", "unknown chart"),
                "title": vision_data.get("title", ""),
                "metrics": vision_data.get("metrics", []),
                "time_period": vision_data.get("time_period", ""),
                "data_series": vision_data.get("data_series", []),
                "axis_info": vision_data.get("axis_info", {})
            }
            vision_data["charts"] = [chart_data]
    
    # Add confidence score
    if "confidence" not in vision_data:
        # Estimate confidence based on amount of content extracted
        text_length = len(vision_data.get("text", ""))
        insights_count = len(vision_data.get("insights", []))
        
        # More text and insights usually means better extraction
        if text_length > 200 and insights_count >= 3:
            confidence = 0.9
        elif text_length > 100 and insights_count >= 1:
            confidence = 0.7
        else:
            confidence = 0.5
            
        vision_data["confidence"] = confidence
    
    # Add metadata about the processing
    vision_data["processing_metadata"] = {
        "model": config.MODELS['vision']['name'],
        "timestamp": datetime.now().isoformat(),
        "source_file": os.path.basename(file_path)
    }
    
    return vision_data

def _fix_json_response(content):
    """
    Attempt to fix common JSON errors in model responses
    
    Args:
        content: Model response text
        
    Returns:
        dict: Fixed JSON object or None if fixing failed
    """
    # Find the JSON part
    json_start = content.find('{')
    json_end = content.rfind('}') + 1
    
    if json_start >= 0 and json_end > json_start:
        json_str = content[json_start:json_end]
        
        # Try common fixes
        try:
            # Fix 1: Try to parse as is
            return json.loads(json_str)
        except json.JSONDecodeError:
            pass
        
        try:
            # Fix 2: Fix unescaped quotes in strings
            fixed_str = re.sub(r'(?<!")("[\w\s]+)(?!")(?=:)', r'\1"', json_str)
            fixed_str = re.sub(r'(?<=:)(?<!")([\w\s]+")(?!")', r'"\1', fixed_str)
            return json.loads(fixed_str)
        except (json.JSONDecodeError, re.error):
            pass
        
        try:
            # Fix 3: Fix missing quotes around keys
            fixed_str = re.sub(r'([{,])\s*(\w+)\s*:', r'\1"\2":', json_str)
            return json.loads(fixed_str)
        except (json.JSONDecodeError, re.error):
            pass
        
        try:
            # Fix 4: Replace single quotes with double quotes
            fixed_str = json_str.replace("'", '"')
            return json.loads(fixed_str)
        except json.JSONDecodeError:
            pass
            
    # All fixes failed
    return None

def _extract_text_from_non_json_response(content):
    """
    Extract useful text from a non-JSON response
    
    Args:
        content: Model response text
        
    Returns:
        str: Extracted text content
    """
    # Remove code blocks and any JSON-like structures
    cleaned_text = re.sub(r'```.*?```', '', content, flags=re.DOTALL)
    cleaned_text = re.sub(r'{.*?}', '', cleaned_text, flags=re.DOTALL)
    
    # Extract lines that might be text content from the image
    text_lines = []
    for line in cleaned_text.split('\n'):
        line = line.strip()
        # Skip lines that look like instructions or explanation
        if line and not line.startswith(('I ', 'The ', 'This ', 'Here')):
            text_lines.append(line)
    
    return ' '.join(text_lines)

def _create_fallback_vision_results(text_content):
    """
    Create fallback vision results when model processing fails
    
    Args:
        text_content: Any text content extracted
        
    Returns:
        dict: Basic vision results with the extracted text
    """
    return {
        "type": "unknown",
        "text": text_content or "No text extracted",
        "description": "Automated image analysis provided limited results",
        "insights": ["Manual review recommended", "Limited text extraction performed"],
        "objects": [],
        "charts": [],
        "confidence": 0.3,
        "processing_metadata": {
            "model": config.MODELS['vision']['name'],
            "timestamp": datetime.now().isoformat(),
            "status": "fallback_processing"
        }
    }

# For testing
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python image_extractor.py <image_file_path>")
        sys.exit(1)
        
    image_path = sys.argv[1]
    extract(image_path)