"""
Triplet extractor for the knowledge graph-based business consulting system.
Extracts subject-predicate-object relationships from parsed document content.
"""

import os
import time
import logging
import json
import re
from datetime import datetime
import config
import requests

# Set up logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TripletExtractor:
    """
    Extracts subject-predicate-object relationships from document content
    to populate the knowledge graph.
    """
    
    def __init__(self):
        """Initialize the triplet extractor"""
        # Load common business entities and relationships for pattern matching
        self._load_patterns()
        
        # Initialize LLM client
        self.llm_endpoint = config.MODELS['reasoning']['endpoint']
        self.llm_name = config.MODELS['reasoning']['name']
        self.llm_params = config.MODELS['reasoning']['parameters']
        
    def _load_patterns(self):
        """Load entity and relationship patterns"""
        # In a production system, these would be loaded from files or a database
        # Here we define some simple patterns for demonstration
        
        self.entity_patterns = {
            "companies": [
                r"([A-Z][a-z]+ )?([A-Z][a-z]+ )?([A-Z][a-zA-Z0-9\'\-&]+(?: Inc\.| Corp\.| LLC| Ltd\.| Limited| GmbH)?)",
                r"([A-Z][A-Z&]+)",  # Acronyms like IBM, AT&T
            ],
            "financial_metrics": [
                r"revenue",
                r"profit",
                r"income",
                r"EBITDA",
                r"margin",
                r"cash flow",
                r"ROI",
                r"ROE",
                r"debt",
                r"equity",
                r"assets",
                r"liabilities",
            ],
            "percentages": [
                r"(\d+\.?\d*)%",
                r"(\d+\.?\d*) percent",
            ],
            "monetary_values": [
                r"\$(\d+\.?\d*)(?: million| billion| trillion)?",
                r"(\d+\.?\d*) (million|billion|trillion) dollars",
            ],
            "dates": [
                r"\b(January|February|March|April|May|June|July|August|September|October|November|December) \d{1,2},? \d{4}\b",
                r"\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b",
                r"\b\d{4}\b",  # Years
            ],
        }
        
        self.relationship_patterns = {
            "increased": [
                r"increased (by )?",
                r"grew (by )?",
                r"rose (by )?",
                r"gained",
                r"improved",
            ],
            "decreased": [
                r"decreased (by )?",
                r"declined (by )?",
                r"fell (by )?",
                r"dropped (by )?",
                r"reduced (by )?",
            ],
            "acquired": [
                r"acquired",
                r"purchased",
                r"bought",
                r"took over",
            ],
            "partnered": [
                r"partnered with",
                r"formed (a|an) (partnership|alliance) with",
                r"collaborated with",
            ],
            "launched": [
                r"launched",
                r"released",
                r"introduced",
                r"unveiled",
            ],
            "invested": [
                r"invested",
                r"funded",
                r"financed",
            ],
        }
        
    def extract_from_file(self, parsed_file_path):
        """
        Extract triplets from a parsed document file
        
        Args:
            parsed_file_path (str): Path to the parsed document JSON file
            
        Returns:
            list: Extracted triplets (subject, predicate, object)
        """
        if not os.path.isfile(parsed_file_path):
            raise FileNotFoundError(f"File not found: {parsed_file_path}")
        
        # Load the parsed document
        with open(parsed_file_path, 'r', encoding='utf-8') as f:
            doc_data = json.load(f)
        
        # Extract text content from all pages
        text_content = ""
        for page in doc_data.get("content", {}).get("pages", []):
            text_content += page.get("text", "") + "\n"
        
        # Extract triplets using multiple methods
        triplets = []
        
        # Method 1: Pattern-based extraction
        pattern_triplets = self._extract_pattern_based(text_content)
        triplets.extend(pattern_triplets)
        
        # Method 2: LLM-based extraction
        llm_triplets = self._extract_llm_based(text_content)
        triplets.extend(llm_triplets)
        
        # Deduplicate triplets
        unique_triplets = []
        seen = set()
        
        for triplet in triplets:
            triplet_key = f"{triplet['subject']}|{triplet['predicate']}|{triplet['object']}"
            if triplet_key not in seen:
                seen.add(triplet_key)
                unique_triplets.append(triplet)
        
        # Save results
        output_dir = os.path.join("data", "knowledge_base")
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = os.path.basename(parsed_file_path)
        output_filename = f"triplets_{os.path.splitext(base_filename)[0]}_{timestamp}.json"
        output_path = os.path.join(output_dir, output_filename)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(unique_triplets, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Extracted {len(unique_triplets)} unique triplets from {parsed_file_path}")
        logger.info(f"Saved triplets to {output_path}")
        
        return unique_triplets
        
    def _extract_pattern_based(self, text):
        """
        Extract triplets using pattern matching
        
        Args:
            text (str): Document text content
            
        Returns:
            list: Extracted triplets
        """
        triplets = []
        
        # Split text into sentences for better context
        sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', text)
        
        for sentence in sentences:
            # Try to find entities in the sentence
            entities = {}
            
            for entity_type, patterns in self.entity_patterns.items():
                entities[entity_type] = []
                for pattern in patterns:
                    matches = re.finditer(pattern, sentence)
                    for match in matches:
                        entity = match.group(0)
                        entities[entity_type].append({
                            "text": entity,
                            "start": match.start(),
                            "end": match.end()
                        })
            
            # Try to find relationships in the sentence
            for rel_type, patterns in self.relationship_patterns.items():
                for pattern in patterns:
                    rel_matches = re.finditer(pattern, sentence, re.IGNORECASE)
                    
                    for rel_match in rel_matches:
                        # Look for entities before and after the relationship
                        rel_start = rel_match.start()
                        rel_end = rel_match.end()
                        
                        # Find the closest entity before the relationship
                        closest_subject = None
                        min_subject_distance = float('inf')
                        
                        for entity_type, entity_list in entities.items():
                            for entity in entity_list:
                                if entity["end"] <= rel_start:
                                    distance = rel_start - entity["end"]
                                    if distance < min_subject_distance:
                                        min_subject_distance = distance
                                        closest_subject = {
                                            "text": entity["text"],
                                            "type": entity_type
                                        }
                        
                        # Find the closest entity after the relationship
                        closest_object = None
                        min_object_distance = float('inf')
                        
                        for entity_type, entity_list in entities.items():
                            for entity in entity_list:
                                if entity["start"] >= rel_end:
                                    distance = entity["start"] - rel_end
                                    if distance < min_object_distance:
                                        min_object_distance = distance
                                        closest_object = {
                                            "text": entity["text"],
                                            "type": entity_type
                                        }
                        
                        # Create triplet if we have both subject and object
                        if closest_subject and closest_object:
                            triplet = {
                                "subject": closest_subject["text"],
                                "subject_type": closest_subject["type"],
                                "predicate": rel_type,
                                "object": closest_object["text"],
                                "object_type": closest_object["type"],
                                "context": sentence.strip(),
                                "extraction_method": "pattern_based"
                            }
                            triplets.append(triplet)
        
        return triplets
    
    def _extract_llm_based(self, text):
        """
        Extract triplets using large language model
    
        Args:
            text (str): Document text content
        
        Returns:
            list: Extracted triplets
        """
        logger.info("Extracting triplets using LLM")
    
        # Handle empty text
        if not text or len(text.strip()) < 50:
            logger.warning("Text too short for meaningful LLM extraction")
            return []
    
        # Initialize results list
        triplets = []
    
        # Process text in chunks if it's too long
        max_chunk_size = 3000  # Adjust based on the LLM's context window
        text_chunks = []
    
        if len(text) > max_chunk_size:
            # Split text into sentences
            sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!)\s', text)
        
            # Group sentences into chunks
            current_chunk = ""
            for sentence in sentences:
                if len(current_chunk) + len(sentence) < max_chunk_size:
                    current_chunk += sentence + " "
                else:
                    if current_chunk:
                        text_chunks.append(current_chunk.strip())
                    current_chunk = sentence + " "
        
            # Add the last chunk if it's not empty
            if current_chunk:
                text_chunks.append(current_chunk.strip())
        else:
            text_chunks = [text]
    
        logger.info(f"Processing {len(text_chunks)} text chunks with LLM")
    
        # Process each chunk
        for i, chunk in enumerate(text_chunks):
            logger.info(f"Processing chunk {i+1}/{len(text_chunks)}")
        
            # Create prompt for the LLM
            prompt = f"""
            You are an expert in knowledge extraction. Extract business-related subject-predicate-object triplets from the following text.
            For each assertion in the text, identify:
        
            1. The SUBJECT entity (who/what is the statement about)
            2. The PREDICATE (relationship or action)
            3. The OBJECT entity (what is being affected or related to the subject)
        
            Only extract triplets that represent factual business relationships or events.
        
            Format your response as a JSON array of triplet objects, with each having these fields:
            - "subject": The entity that is the subject (e.g., company name, person, product)
            - "subject_type": Category of the subject (company, person, financial_metric, product, etc.)
            - "predicate": The relationship or action (e.g., acquired, increased, invested_in)
            - "object": The entity that is the object of the relationship
            - "object_type": Category of the object
            - "confidence": A number between 0.0 and 1.0 indicating your confidence in this extraction
        
            Example format:
            [
            {{
                "subject": "Microsoft",
                "subject_type": "company",
                "predicate": "acquired",
                "object": "GitHub",
                "object_type": "company",
                "confidence": 0.95
            }},
            {{
                "subject": "revenue",
                "subject_type": "financial_metric",
                "predicate": "increased_by",
                "object": "15%",
                "object_type": "percentage",
                "confidence": 0.85
            }}
            ]
        
            Text to analyze:
            {chunk}
        
            Respond ONLY with the JSON array of triplets. If no valid triplets can be extracted, return an empty array [].
            """
        
            try:
                # Call the LLM API (Ollama)
                response = requests.post(
                    self.llm_endpoint,
                    json={
                        "model": self.llm_name,
                        "prompt": prompt,
                        "stream": False,
                        **self.llm_params
                    }
                )
            
                # Parse the response
                result = response.json()
                content = result.get('response', '')
            
                # Extract JSON from the response
                json_start = content.find('[')
                json_end = content.rfind(']') + 1
            
                if json_start >= 0 and json_end > json_start:
                    json_str = content[json_start:json_end]
                
                    try:
                        chunk_triplets = json.loads(json_str)
                    
                        # Add extraction source metadata
                        for triplet in chunk_triplets:
                            triplet["extraction_method"] = "llm_based"
                        
                            # Extract a short context if possible
                            subject = triplet.get("subject", "")
                            predicate = triplet.get("predicate", "")
                            obj = triplet.get("object", "")
                        
                            if subject and predicate and obj:
                                # Try to find a sentence containing all three
                                pattern = re.compile(r'[^.!?]*(?:\b' + re.escape(subject) + r'\b.*\b' + 
                                               re.escape(obj) + r'\b|' + r'\b' + re.escape(obj) + 
                                               r'\b.*\b' + re.escape(subject) + r'\b)[^.!?]*[.!?]')
                                context_match = pattern.search(chunk)
                            
                                if context_match:
                                    triplet["context"] = context_match.group(0).strip()
                    
                        triplets.extend(chunk_triplets)
                        logger.info(f"Extracted {len(chunk_triplets)} triplets from chunk {i+1}")
                    
                    except json.JSONDecodeError as e:
                        logger.warning(f"Failed to parse JSON from LLM response: {e}")
                        logger.debug(f"Problematic JSON string: {json_str}")
                else:
                    logger.warning("No valid JSON found in LLM response")
                
            except Exception as e:
                logger.error(f"Error calling LLM API: {e}")
            
            # Throttle API calls to avoid rate limits
            if i < len(text_chunks) - 1:
                time.sleep(1)  # Add a short delay between requests
    
        # Filter out low-confidence triplets
        confidence_threshold = 0.6
        filtered_triplets = [t for t in triplets if t.get("confidence", 0) >= confidence_threshold]
    
        logger.info(f"LLM extraction complete. Extracted {len(filtered_triplets)} triplets with confidence >= {confidence_threshold}")
        return filtered_triplets

# For testing
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python triplet_extractor.py <parsed_document.json>")
        sys.exit(1)
        
    parsed_file = sys.argv[1]
    extractor = TripletExtractor()
    triplets = extractor.extract_from_file(parsed_file)
    
    print(f"Extracted {len(triplets)} triplets")
    for i, triplet in enumerate(triplets[:5]):  # Print first 5 triplets
        print(f"{i+1}. {triplet['subject']} --[{triplet['predicate']}]--> {triplet['object']}")