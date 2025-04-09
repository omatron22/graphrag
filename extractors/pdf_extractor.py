"""
PDF document extractor for the knowledge graph-based business consulting system.
Extracts text, tables, and structured information from PDF documents.
"""

import os
import logging
import json
from datetime import datetime
import pymupdf  # Using the new pymupdf name

# Set up logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def extract(file_path, output_dir=None):
    """
    Extract content from a PDF document
    
    Args:
        file_path (str): Path to the PDF file
        output_dir (str, optional): Directory to save parsed data
        
    Returns:
        dict: Extracted content with metadata
    """
    logger.info(f"Extracting content from PDF: {file_path}")
    
    # Validate file exists and is a PDF
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
        
    if not file_path.lower().endswith('.pdf'):
        raise ValueError(f"File is not a PDF: {file_path}")
    
    # If no output directory specified, use default
    if output_dir is None:
        output_dir = os.path.join("data", "parsed")
        os.makedirs(output_dir, exist_ok=True)
    
    # Extract timestamp and filename for output
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_filename = os.path.basename(file_path)
    output_filename = f"{os.path.splitext(base_filename)[0]}_{timestamp}.json"
    output_path = os.path.join(output_dir, output_filename)
    
    # Initialize extraction results
    result = {
        "metadata": {
            "source_file": file_path,
            "extraction_date": datetime.now().isoformat(),
            "parser": "pymupdf",
        },
        "document_metadata": {},
        "content": {
            "pages": [],
            "tables": [],
            "images": [],
            "entities": [],
        }
    }
    
    try:
        # Open the PDF document
        doc = pymupdf.open(file_path)
        
        # Extract document metadata
        result["document_metadata"] = {
            "title": doc.metadata.get("title", ""),
            "author": doc.metadata.get("author", ""),
            "subject": doc.metadata.get("subject", ""),
            "keywords": doc.metadata.get("keywords", ""),
            "creator": doc.metadata.get("creator", ""),
            "producer": doc.metadata.get("producer", ""),
            "creation_date": doc.metadata.get("creationDate", ""),
            "modification_date": doc.metadata.get("modDate", ""),
            "page_count": len(doc),
        }
        
        # Process each page
        for page_num, page in enumerate(doc):
            page_content = {}
            
            # Extract text
            text = page.get_text()
            
            # Extract text blocks with positions
            blocks = page.get_text("blocks")
            text_blocks = []
            
            for block in blocks:
                if block[6] == 0:  # Text blocks
                    text_blocks.append({
                        "text": block[4],
                        "bbox": block[:4],
                        "block_type": "text"
                    })
            
            # Extract tables if available
            tables = []
            try:
                # Table detection requires specific algorithms
                # Here we'll use a basic approach based on text layout
                # In a real implementation, you might want to use more sophisticated methods
                
                # This is a placeholder - in a real implementation, you'd use
                # more sophisticated table detection and extraction
                tables = detect_tables(page)
            except Exception as e:
                logger.warning(f"Table extraction failed on page {page_num+1}: {e}")
            
            # Extract images
            images = []
            try:
                # Get image data from page
                img_list = page.get_images(full=True)
                
                for img_idx, img_info in enumerate(img_list):
                    xref = img_info[0]
                    base_image = doc.extract_image(xref)
                    
                    if base_image:
                        images.append({
                            "image_id": f"img_{page_num}_{img_idx}",
                            "xref": xref,
                            "bbox": img_info[1:5],  # Bounding box
                            "size": (base_image["width"], base_image["height"]),
                            "format": base_image["ext"],
                        })
            except Exception as e:
                logger.warning(f"Image extraction failed on page {page_num+1}: {e}")
            
            # Combine all page data
            page_content = {
                "page_number": page_num + 1,
                "text": text,
                "text_blocks": text_blocks,
                "tables": tables,
                "images": images,
            }
            
            # Add to the result
            result["content"]["pages"].append(page_content)
        
        # Save extracted data to JSON file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Extraction completed successfully. Output saved to: {output_path}")
        return result
    
    except Exception as e:
        logger.error(f"PDF extraction failed: {e}")
        raise

def detect_tables(page):
    """
    Detect tables in a PDF page
    
    Args:
        page: PyMuPDF page object
        
    Returns:
        list: Detected tables data
    """
    # This is a placeholder function for table detection
    # In a real implementation, you'd use a more sophisticated approach
    # such as machine learning models or heuristic algorithms
    
    # For now, we'll return an empty list
    return []

def extract_table_data(page, table_bbox):
    """
    Extract data from a detected table
    
    Args:
        page: PyMuPDF page object
        table_bbox: Bounding box of the table
        
    Returns:
        dict: Table data including headers and rows
    """
    # This is a placeholder function for table data extraction
    # In a real implementation, you'd implement actual table parsing
    
    return {
        "headers": [],
        "rows": []
    }

# For testing
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python pdf_extractor.py <pdf_file_path>")
        sys.exit(1)
        
    pdf_path = sys.argv[1]
    extract(pdf_path)