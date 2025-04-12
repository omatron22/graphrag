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
    Detect tables in a PDF page using heuristic methods
    
    Args:
        page: PyMuPDF page object
        
    Returns:
        list: Detected tables data with bounding boxes
    """
    detected_tables = []
    
    # Get text blocks with their bounding boxes
    blocks = page.get_text("blocks")
    
    # Filter for potential table regions (blocks with multiple lines or aligned text)
    potential_table_regions = []
    
    # Step 1: Identify aligned text blocks
    # We'll look for blocks with similar x-coordinates (potential columns)
    x_positions = {}
    
    for block in blocks:
        if block[6] == 0:  # Text blocks only
            x0, y0, x1, y1 = block[:4]  # Bounding box
            # Round x coordinates to group nearby columns
            x_start_rounded = round(x0 / 5) * 5
            
            if x_start_rounded not in x_positions:
                x_positions[x_start_rounded] = []
            x_positions[x_start_rounded].append(block)
    
    # Find x positions with multiple blocks (potential columns)
    column_positions = {pos: blocks for pos, blocks in x_positions.items() if len(blocks) >= 3}
    
    # If we found potential columns, try to identify table regions
    if column_positions:
        # Sort columns by x position
        sorted_positions = sorted(column_positions.keys())
        
        # If we have multiple aligned columns, it's likely a table
        if len(sorted_positions) >= 2:
            # Find the table bounds
            all_column_blocks = []
            for pos in sorted_positions:
                all_column_blocks.extend(column_positions[pos])
            
            # Calculate the table bounding box
            if all_column_blocks:
                min_x = min(block[0] for block in all_column_blocks)
                min_y = min(block[1] for block in all_column_blocks)
                max_x = max(block[2] for block in all_column_blocks)
                max_y = max(block[3] for block in all_column_blocks)
                
                # Add some margin
                table_bbox = (min_x - 5, min_y - 5, max_x + 5, max_y + 5)
                
                # Check if the table has enough rows (at least 3)
                y_positions = set()
                for block in all_column_blocks:
                    y_mid = (block[1] + block[3]) / 2
                    y_rounded = round(y_mid / 10) * 10
                    y_positions.add(y_rounded)
                
                if len(y_positions) >= 3:  # At least 3 rows
                    detected_tables.append({
                        "bbox": table_bbox,
                        "columns": len(sorted_positions),
                        "rows": len(y_positions),
                        "confidence": 0.8
                    })
    
    # Step 2: Try to detect tables using horizontal and vertical lines
    # Get drawings from the page
    paths = page.get_drawings()
    if paths:
        # Look for horizontal and vertical lines that might be table borders
        horizontal_lines = []
        vertical_lines = []
        
        for path in paths:
            for item in path["items"]:
                if item[0] == "l":  # Line
                    x0, y0 = item[1]
                    x1, y1 = item[2]
                    
                    # Check if horizontal or vertical
                    if abs(y1 - y0) < 2:  # Horizontal line
                        horizontal_lines.append((min(x0, x1), y0, max(x0, x1), y1))
                    elif abs(x1 - x0) < 2:  # Vertical line
                        vertical_lines.append((x0, min(y0, y1), x1, max(y0, y1)))
        
        # If we have both horizontal and vertical lines, check for intersections
        if horizontal_lines and vertical_lines:
            # Sort lines by position
            horizontal_lines.sort(key=lambda l: l[1])
            vertical_lines.sort(key=lambda l: l[0])
            
            # Check for grid patterns (at least 2x2)
            if len(horizontal_lines) >= 3 and len(vertical_lines) >= 3:
                # Find table boundaries
                min_x = min(line[0] for line in vertical_lines)
                max_x = max(line[2] for line in vertical_lines)
                min_y = min(line[1] for line in horizontal_lines)
                max_y = max(line[3] for line in horizontal_lines)
                
                # Create table bounding box
                grid_table_bbox = (min_x, min_y, max_x, max_y)
                
                # Check if this table overlaps with any previously detected
                overlap = False
                for existing_table in detected_tables:
                    if rectangles_overlap(grid_table_bbox, existing_table["bbox"]):
                        overlap = True
                        break
                
                if not overlap:
                    detected_tables.append({
                        "bbox": grid_table_bbox,
                        "columns": len(vertical_lines) - 1,
                        "rows": len(horizontal_lines) - 1,
                        "confidence": 0.9
                    })
    
    return detected_tables

def rectangles_overlap(rect1, rect2):
    """Check if two rectangles overlap"""
    x0_1, y0_1, x1_1, y1_1 = rect1
    x0_2, y0_2, x1_2, y1_2 = rect2
    
    return not (x1_1 < x0_2 or x1_2 < x0_1 or y1_1 < y0_2 or y1_2 < y0_1)

def extract_table_data(page, table_bbox):
    """
    Extract data from a detected table
    
    Args:
        page: PyMuPDF page object
        table_bbox: Bounding box of the table (x0, y0, x1, y1)
        
    Returns:
        dict: Table data including headers and rows
    """
    x0, y0, x1, y1 = table_bbox
    
    # Extract text from the table region
    table_text = page.get_textpage().extractDICT(table_bbox)
    
    # Get all text blocks within the table region
    blocks = []
    for block in table_text.get("blocks", []):
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                text = span.get("text", "").strip()
                if text:
                    # Get the bbox (relative to the page)
                    bbox = (
                        span["origin"][0],
                        span["origin"][1] - span["ascender"],
                        span["origin"][0] + span["bbox"][2] - span["bbox"][0],
                        span["origin"][1] + span["bbox"][3] - span["bbox"][1] - span["ascender"]
                    )
                    blocks.append({
                        "text": text,
                        "bbox": bbox
                    })
    
    # If no text blocks found, return empty result
    if not blocks:
        return {"headers": [], "rows": []}
    
    # Identify rows by grouping blocks with similar y-coordinates
    # Sort blocks by y-coordinate
    blocks.sort(key=lambda b: b["bbox"][1])
    
    # Group into rows
    rows = []
    current_row = [blocks[0]]
    current_y = (blocks[0]["bbox"][1] + blocks[0]["bbox"][3]) / 2
    
    for block in blocks[1:]:
        block_y = (block["bbox"][1] + block["bbox"][3]) / 2
        
        # If this block is on a new row
        if abs(block_y - current_y) > 10:  # Threshold for new row
            rows.append(current_row)
            current_row = [block]
            current_y = block_y
        else:
            current_row.append(block)
    
    # Add the last row
    if current_row:
        rows.append(current_row)
    
    # Sort each row by x-coordinate (left to right)
    for i, row in enumerate(rows):
        rows[i] = sorted(row, key=lambda b: b["bbox"][0])
    
    # Detect columns by analyzing x-coordinate patterns
    col_starts = []
    
    # Look at all rows to find consistent column starts
    for row in rows:
        for block in row:
            col_starts.append(block["bbox"][0])
    
    # Group nearby column starts
    col_groups = {}
    for x in col_starts:
        x_rounded = round(x / 10) * 10
        if x_rounded not in col_groups:
            col_groups[x_rounded] = 0
        col_groups[x_rounded] += 1
    
    # Find the most common column starts
    common_cols = sorted([
        x for x, count in col_groups.items() 
        if count >= max(2, len(rows) * 0.3)  # Column must appear in at least 30% of rows
    ])
    
    # If no clear columns detected, try to infer from first row
    if not common_cols and rows:
        common_cols = sorted([block["bbox"][0] for block in rows[0]])
    
    # Assign each cell to the appropriate column
    table_data = []
    
    for row in rows:
        row_data = [""] * len(common_cols)
        
        for block in row:
            # Find the closest column
            block_x = block["bbox"][0]
            col_idx = 0
            
            for i, col_x in enumerate(common_cols):
                if abs(block_x - col_x) < abs(block_x - common_cols[col_idx]):
                    col_idx = i
            
            # Assign to this column
            if col_idx < len(row_data):
                # Append if there's already content (handle multi-line cells)
                if row_data[col_idx]:
                    row_data[col_idx] += " " + block["text"]
                else:
                    row_data[col_idx] = block["text"]
        
        table_data.append(row_data)
    
    # Check if the first row might be headers
    is_header = False
    if len(table_data) >= 2:
        first_row = table_data[0]
        
        # Heuristics to detect headers:
        # 1. First row has different formatting (like bold or underlined)
        # 2. First row has shorter text than other rows
        avg_len = sum(len(cell) for row in table_data[1:] for cell in row) / sum(len(row) for row in table_data[1:])
        first_row_avg = sum(len(cell) for cell in first_row) / len(first_row) if first_row else 0
        
        is_header = first_row_avg < avg_len * 0.7  # Headers tend to be shorter
    
    # Prepare result
    if is_header and table_data:
        headers = table_data[0]
        data_rows = table_data[1:]
    else:
        headers = []
        data_rows = table_data
    
    return {
        "headers": headers,
        "rows": data_rows
    }

# For testing
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python pdf_extractor.py <pdf_file_path>")
        sys.exit(1)
        
    pdf_path = sys.argv[1]
    extract(pdf_path)