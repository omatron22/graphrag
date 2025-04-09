"""
Main orchestrator for the knowledge graph-based business consulting system.
Controls the flow of data processing, analysis, and output generation.
"""

import os
import logging
import importlib
from datetime import datetime
import config
from knowledge_graph.neo4j_manager import Neo4jManager

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Orchestrator:
    """
    Main controller for the business analysis pipeline.
    Manages the flow from document ingestion to recommendations.
    """
    
    def __init__(self):
        """Initialize the orchestrator and its components"""
        self.neo4j_manager = Neo4jManager()
        self.neo4j_manager.connect()
        self.neo4j_manager.verify_indexes()
        
        # Validate directories exist
        self._ensure_directories()
        
        logger.info("Orchestrator initialized successfully")
        
    def _ensure_directories(self):
        """Ensure all required directories exist"""
        dirs = [
            "data/uploads",
            "data/parsed",
            "data/knowledge_base",
            "knowledge_graph/exports"
        ]
        
        for directory in dirs:
            os.makedirs(directory, exist_ok=True)
        
    def process_document(self, file_path):
        """
        Process a single document through the entire pipeline
        
        Args:
            file_path: Path to the document file
            
        Returns:
            dict: Results of the analysis
        """
        logger.info(f"Processing document: {file_path}")
        
        # 1. Determine file type and select appropriate extractor
        file_ext = os.path.splitext(file_path)[1].lower()[1:]  # Remove the dot
        if file_ext not in config.EXTRACTORS:
            logger.error(f"Unsupported file type: {file_ext}")
            return {"error": f"Unsupported file type: {file_ext}"}
        
        # 2. Load the extractor dynamically
        extractor_path = config.EXTRACTORS[file_ext]
        module_path, function_name = extractor_path.rsplit('.', 1)
        extractor_module = importlib.import_module(module_path)
        extractor_function = getattr(extractor_module, function_name)
        
        # 3. Extract content from document
        try:
            extracted_data = extractor_function(file_path)
            logger.info(f"Successfully extracted data from {file_path}")
            
            # Save parsed data
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            parsed_filename = f"{os.path.basename(file_path)}_{timestamp}.json"
            parsed_path = os.path.join("data/parsed", parsed_filename)
            
            # TODO: Save extracted_data to parsed_path
            
        except Exception as e:
            logger.error(f"Extraction failed for {file_path}: {e}")
            return {"error": f"Extraction failed: {str(e)}"}
        
        # 4. Extract triplets for knowledge graph
        # TODO: Implement triplet extraction
        
        # 5. Store in knowledge graph
        # TODO: Store triplets in Neo4j
        
        # 6. Run analysis
        # TODO: Implement risk analysis
        
        # 7. Generate recommendations
        # TODO: Implement recommendation generation
        
        return {
            "status": "Processing steps outlined but not fully implemented",
            "document": file_path,
            "extraction_success": True
        }
    
    def process_directory(self, directory_path):
        """
        Process all supported documents in a directory
        
        Args:
            directory_path: Path to directory containing documents
            
        Returns:
            dict: Summary of processing results
        """
        if not os.path.isdir(directory_path):
            return {"error": f"Directory not found: {directory_path}"}
            
        results = {"processed": [], "errors": []}
        
        for filename in os.listdir(directory_path):
            file_path = os.path.join(directory_path, filename)
            
            if os.path.isfile(file_path):
                file_ext = os.path.splitext(file_path)[1].lower()[1:]
                if file_ext in config.EXTRACTORS:
                    result = self.process_document(file_path)
                    if "error" in result:
                        results["errors"].append({file_path: result["error"]})
                    else:
                        results["processed"].append(file_path)
        
        return results
    
    def generate_analysis_report(self, entity_name):
        """
        Generate a comprehensive analysis report for an entity
        
        Args:
            entity_name: Name of the entity to analyze
            
        Returns:
            dict: Analysis report data
        """
        # TODO: Implement report generation logic
        
        # Placeholder
        return {
            "entity": entity_name,
            "timestamp": datetime.now().isoformat(),
            "risks": self.neo4j_manager.get_risk_factors(entity_name),
            "recommendations": []
        }
    
    def cleanup(self):
        """Close connections and clean up resources"""
        self.neo4j_manager.close()
        logger.info("Orchestrator cleanup completed")


# For command line usage
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python orchestrator.py <file_or_directory_path>")
        sys.exit(1)
        
    path = sys.argv[1]
    
    orchestrator = Orchestrator()
    
    try:
        if os.path.isfile(path):
            result = orchestrator.process_document(path)
        elif os.path.isdir(path):
            result = orchestrator.process_directory(path)
        else:
            result = {"error": f"Path not found: {path}"}
            
        print(result)
    finally:
        orchestrator.cleanup()