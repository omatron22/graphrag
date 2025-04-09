"""
Shared utilities for document extractors in the knowledge graph-based business consulting system.
Provides common functions for document processing, metadata extraction, and result handling.
"""

import os
import logging
import json
import hashlib
from datetime import datetime
from typing import Dict, Any, List, Tuple, Optional, Union
import re

# Set up logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def ensure_output_dir(output_dir: Optional[str] = None) -> str:
    """
    Ensure the output directory exists and return its path.
    
    Args:
        output_dir: Optional directory path. If None, uses the default.
        
    Returns:
        str: Path to the output directory
    """
    if output_dir is None:
        output_dir = os.path.join("data", "parsed")
    
    os.makedirs(output_dir, exist_ok=True)
    return output_dir

def generate_output_filename(file_path: str, suffix: str = "") -> Tuple[str, str]:
    """
    Generate a timestamped output filename based on input file.
    
    Args:
        file_path: Path to the input file
        suffix: Optional suffix to add before extension
        
    Returns:
        Tuple[str, str]: (Base filename without extension, output filename with timestamp)
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_filename = os.path.basename(file_path)
    name_without_ext = os.path.splitext(base_filename)[0]
    
    if suffix:
        output_filename = f"{name_without_ext}_{suffix}_{timestamp}.json"
    else:
        output_filename = f"{name_without_ext}_{timestamp}.json"
        
    return name_without_ext, output_filename

def save_extraction_result(result: Dict[str, Any], output_path: str) -> str:
    """
    Save extraction result to a JSON file.
    
    Args:
        result: Dictionary with extraction results
        output_path: Path to save the result
        
    Returns:
        str: Path to the saved file
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        logger.info(f"Extraction result saved to: {output_path}")
        return output_path
    except Exception as e:
        logger.error(f"Failed to save extraction result: {e}")
        raise

def validate_file(file_path: str, allowed_extensions: List[str] = None) -> bool:
    """
    Validate that a file exists and has an allowed extension.
    
    Args:
        file_path: Path to the file
        allowed_extensions: List of allowed extensions (without dot)
        
    Returns:
        bool: True if file is valid, False otherwise
    """
    if not os.path.isfile(file_path):
        logger.error(f"File not found: {file_path}")
        return False
        
    if allowed_extensions:
        ext = os.path.splitext(file_path)[1].lower()[1:]  # Remove the dot
        if ext not in allowed_extensions:
            logger.error(f"Unsupported file type: {ext}. Allowed: {allowed_extensions}")
            return False
            
    return True

def create_extraction_result_template(file_path: str, extractor_name: str) -> Dict[str, Any]:
    """
    Create a template dictionary for extraction results.
    
    Args:
        file_path: Path to the source file
        extractor_name: Name of the extractor
        
    Returns:
        dict: Template for extraction results
    """
    return {
        "metadata": {
            "source_file": file_path,
            "extraction_date": datetime.now().isoformat(),
            "extractor": extractor_name,
            "file_hash": generate_file_hash(file_path),
        },
        "document_metadata": {},
        "content": {
            "text": "",
            "pages": [],
            "tables": [],
            "images": [],
            "entities": [],
        }
    }

def generate_file_hash(file_path: str) -> str:
    """
    Generate a hash of file contents for tracking and deduplication.
    
    Args:
        file_path: Path to the file
        
    Returns:
        str: SHA-256 hash of file contents
    """
    try:
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            # Read and update hash in chunks of 4K
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception as e:
        logger.warning(f"Could not generate file hash: {e}")
        return ""

def detect_entities(text: str, entity_patterns: Dict[str, List[str]]) -> List[Dict[str, Any]]:
    """
    Detect entities in text based on regex patterns.
    
    Args:
        text: Text to analyze
        entity_patterns: Dictionary of entity types and their regex patterns
        
    Returns:
        list: Detected entities with type, text, and position
    """
    entities = []
    
    for entity_type, patterns in entity_patterns.items():
        for pattern in patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                entity = {
                    "type": entity_type,
                    "text": match.group(0),
                    "start": match.start(),
                    "end": match.end(),
                    "confidence": 1.0  # Default confidence for regex matches
                }
                entities.append(entity)
    
    # Sort entities by position
    entities.sort(key=lambda x: x["start"])
    
    return entities

def extract_document_date(text: str) -> Optional[str]:
    """
    Extract document date from text.
    
    Args:
        text: Text to analyze
        
    Returns:
        Optional[str]: ISO formatted date string if found, None otherwise
    """
    # Common date patterns
    date_patterns = [
        # MM/DD/YYYY
        r'(\d{1,2})[/\-](\d{1,2})[/\-](\d{4})',
        # Month DD, YYYY
        r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2}),?\s+(\d{4})',
        # DD Month YYYY
        r'(\d{1,2})\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})',
        # YYYY-MM-DD
        r'(\d{4})[/\-](\d{1,2})[/\-](\d{1,2})',
    ]
    
    # Try each pattern
    for pattern in date_patterns:
        matches = re.findall(pattern, text)
        if matches:
            # Process based on pattern
            if 'January|February' in pattern:
                # Month DD, YYYY
                month_name, day, year = matches[0]
                month_map = {
                    'January': 1, 'February': 2, 'March': 3, 'April': 4,
                    'May': 5, 'June': 6, 'July': 7, 'August': 8,
                    'September': 9, 'October': 10, 'November': 11, 'December': 12
                }
                month = month_map.get(month_name, 1)
                try:
                    return f"{year}-{month:02d}-{int(day):02d}"
                except ValueError:
                    continue
            elif pattern.startswith(r'(\d{1,2})\s+'):
                # DD Month YYYY
                day, month_name, year = matches[0]
                month_map = {
                    'January': 1, 'February': 2, 'March': 3, 'April': 4,
                    'May': 5, 'June': 6, 'July': 7, 'August': 8,
                    'September': 9, 'October': 10, 'November': 11, 'December': 12
                }
                month = month_map.get(month_name, 1)
                try:
                    return f"{year}-{month:02d}-{int(day):02d}"
                except ValueError:
                    continue
            elif pattern.startswith(r'(\d{4})'):
                # YYYY-MM-DD
                year, month, day = matches[0]
                try:
                    return f"{year}-{int(month):02d}-{int(day):02d}"
                except ValueError:
                    continue
            else:
                # MM/DD/YYYY
                month, day, year = matches[0]
                try:
                    return f"{year}-{int(month):02d}-{int(day):02d}"
                except ValueError:
                    continue
    
    return None

def merge_overlapping_entities(entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Merge overlapping entity references.
    
    Args:
        entities: List of detected entities
        
    Returns:
        list: Entities with overlaps resolved
    """
    if not entities:
        return []
        
    # Sort by start position
    sorted_entities = sorted(entities, key=lambda x: (x["start"], -x["end"]))
    
    # Initialize result with the first entity
    result = [sorted_entities[0]]
    
    # Check each entity for overlap with the last entity in result
    for current in sorted_entities[1:]:
        previous = result[-1]
        
        # Check for overlap
        if current["start"] <= previous["end"]:
            # If current entity is longer, replace previous
            if current["end"] > previous["end"]:
                # If same type, merge
                if current["type"] == previous["type"]:
                    previous["text"] = current["text"]
                    previous["end"] = current["end"]
                    previous["confidence"] = max(previous["confidence"], current["confidence"])
                else:
                    # If different type, keep the one with higher confidence
                    if current["confidence"] > previous["confidence"]:
                        result[-1] = current
        else:
            # No overlap, add to result
            result.append(current)
    
    return result

def clean_text(text: str) -> str:
    """
    Clean and normalize text by removing extra whitespace and control characters.
    
    Args:
        text: Text to clean
        
    Returns:
        str: Cleaned text
    """
    # Replace multiple whitespace with a single space
    text = re.sub(r'\s+', ' ', text)
    
    # Remove control characters except newlines and tabs
    text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
    
    # Normalize quotes and dashes
    text = text.replace('"', '"').replace('"', '"')
    text = text.replace(''', "'").replace(''', "'")
    text = text.replace('–', '-').replace('—', '-')
    
    return text.strip()

def detect_language(text: str, sample_length: int = 1000) -> str:
    """
    Detect the primary language of the text.
    Simple implementation - for production use, consider using a library like langdetect.
    
    Args:
        text: Text to analyze
        sample_length: Length of text sample to analyze
        
    Returns:
        str: ISO 639-1 language code (default: 'en')
    """
    # This is a placeholder implementation
    # In a real implementation, you'd use a proper language detection library
    # For now, we'll just assume English
    return "en"

def split_into_sentences(text: str) -> List[str]:
    """
    Split text into sentences for better processing.
    
    Args:
        text: Text to split
        
    Returns:
        list: List of sentences
    """
    # Basic sentence splitting
    # Not perfect but handles common cases
    text = clean_text(text)
    sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!)\s', text)
    return [s.strip() for s in sentences if s.strip()]

def is_likely_header(text: str) -> bool:
    """
    Determine if text is likely a header based on characteristics.
    
    Args:
        text: Text to analyze
        
    Returns:
        bool: True if likely a header, False otherwise
    """
    # Check if text is all uppercase
    all_upper = text.isupper()
    
    # Check if text is short (fewer than 10 words)
    short_text = len(text.split()) < 10
    
    # Check if text ends without punctuation
    no_end_punctuation = not text.rstrip()[-1:] in '.!?:;,'
    
    # Headers usually don't contain sentences
    contains_sentence = '.' in text[:-1] and not text.endswith('Ltd.') and not re.search(r'\b[A-Z]\.\s', text)
    
    return (all_upper or (short_text and no_end_punctuation)) and not contains_sentence

# Common entity patterns for business documents
COMMON_ENTITY_PATTERNS = {
    "organization": [
        r'([A-Z][a-z]+ )?([A-Z][a-z]+ )?([A-Z][a-zA-Z0-9\'\-&]+(?: Inc\.| Corp\.| LLC| Ltd\.| Limited| GmbH)?)',
        r'([A-Z][A-Z&]+)',  # Acronyms like IBM, AT&T
    ],
    "person": [
        r'(?:[A-Z][a-z]+ ){1,2}[A-Z][a-z]+',  # Simple name patterns
    ],
    "date": [
        r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
        r'\b(January|February|March|April|May|June|July|August|September|October|November|December) \d{1,2},? \d{4}\b',
    ],
    "money": [
        r'\$\d+(?:,\d+)*(?:\.\d+)?',
        r'\d+(?:,\d+)*(?:\.\d+)? (dollars|USD)',
    ],
    "percentage": [
        r'\d+(?:\.\d+)?%',
        r'\d+(?:\.\d+)? percent',
    ],
    "location": [
        r'\b[A-Z][a-zA-Z]+(?:,\s+[A-Z][a-zA-Z]+)?\b',  # Simple location patterns
    ],
}