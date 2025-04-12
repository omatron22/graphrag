import os
import logging
from extractors.pdf_extractor import extract as extract_pdf
from knowledge_graph.triplet_extractor import TripletExtractor
from knowledge_graph.neo4j_manager import Neo4jManager
from analysis.risk_engine import RiskAnalyzer
from analysis.strategy_generator import StrategyGenerator

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("test_script")

def test_pdf_extraction(pdf_path):
    """Test PDF extraction functionality"""
    logger.info(f"Testing PDF extraction on: {pdf_path}")
    
    if not os.path.exists(pdf_path):
        logger.error(f"PDF file not found: {pdf_path}")
        return False
    
    try:
        extracted_data = extract_pdf(pdf_path)
        logger.info(f"Successfully extracted data from {pdf_path}")
        
        # Verify basic extraction results
        page_count = len(extracted_data.get("content", {}).get("pages", []))
        logger.info(f"Extracted {page_count} pages")
        
        # Check for tables
        tables_found = False
        for page in extracted_data.get("content", {}).get("pages", []):
            if page.get("tables"):
                tables_found = True
                logger.info(f"Found tables on page {page.get('page_number')}")
        
        if not tables_found:
            logger.info("No tables detected in the document")
        
        return extracted_data
        
    except Exception as e:
        logger.error(f"PDF extraction failed: {e}")
        return False

def test_triplet_extraction(parsed_data_path):
    """Test triplet extraction from parsed document"""
    logger.info(f"Testing triplet extraction on: {parsed_data_path}")
    
    try:
        extractor = TripletExtractor()
        triplets = extractor.extract_from_file(parsed_data_path)
        
        logger.info(f"Extracted {len(triplets)} triplets")
        
        # Print a few sample triplets
        for i, triplet in enumerate(triplets[:3]):
            logger.info(f"Triplet {i+1}: {triplet['subject']} --[{triplet['predicate']}]--> {triplet['object']}")
        
        return triplets
        
    except Exception as e:
        logger.error(f"Triplet extraction failed: {e}")
        return False

def test_knowledge_graph(triplets):
    """Test knowledge graph construction with extracted triplets"""
    logger.info("Testing knowledge graph construction")
    
    try:
        neo4j_manager = Neo4jManager()
        if not neo4j_manager.connect():
            logger.error("Failed to connect to Neo4j")
            return False
        
        # Import triplets in batch
        if hasattr(neo4j_manager, 'import_triplets_batch'):
            import_stats = neo4j_manager.import_triplets_batch(triplets)
            logger.info(f"Batch import stats: {import_stats}")
        else:
            # Fall back to one-by-one import
            for triplet in triplets:
                neo4j_manager.add_triplet(
                    triplet.get("subject_type", "Entity"),
                    {"name": triplet.get("subject")},
                    triplet.get("predicate", "RELATED_TO"),
                    triplet.get("object_type", "Entity"),
                    {"name": triplet.get("object")},
                    {"context": triplet.get("context", "")}
                )
            logger.info(f"Imported {len(triplets)} triplets")
        
        # Test simple query to verify data was imported
        result = neo4j_manager.execute_query(
            "MATCH (n) RETURN count(n) as node_count"
        )
        node_count = result[0]["node_count"] if result else 0
        logger.info(f"Knowledge graph contains {node_count} nodes")
        
        neo4j_manager.close()
        return True
        
    except Exception as e:
        logger.error(f"Knowledge graph test failed: {e}")
        return False

def test_analytics(entity_name):
    """Test analytics and strategy generation"""
    logger.info(f"Testing analytics for entity: {entity_name}")
    
    try:
        # Initialize components
        neo4j_manager = Neo4jManager()
        if not neo4j_manager.connect():
            logger.error("Failed to connect to Neo4j")
            return False
        
        # Verify entity exists
        entities = neo4j_manager.find_entity(entity_name)
        if not entities:
            logger.warning(f"Entity not found: {entity_name}")
            logger.info("Creating test entity")
            neo4j_manager.create_entity("Entity", {"name": entity_name})
        
        # Test risk analysis
        risk_analyzer = RiskAnalyzer(neo4j_manager)
        risk_data = risk_analyzer.analyze()
        logger.info(f"Risk analysis results: {risk_data}")
        
        # Test strategy generation
        strategy_generator = StrategyGenerator(neo4j_manager, risk_analyzer)
        strategies = strategy_generator.generate_for_entity(entity_name)
        logger.info(f"Generated {len(strategies.get('strategies', []))} strategies")
        
        neo4j_manager.close()
        return True
        
    except Exception as e:
        logger.error(f"Analytics test failed: {e}")
        return False

def run_full_test(pdf_path, entity_name):
    """Run a full test of the entire pipeline"""
    logger.info("Starting full pipeline test")
    
    # Step 1: PDF extraction
    extracted_data = test_pdf_extraction(pdf_path)
    if not extracted_data:
        return False
    
    # Get the output path from extracted_data if available
    parsed_data_path = extracted_data.get("parsed_data_path")
    if not parsed_data_path:
        # Try to infer output path based on timestamp
        timestamp = extracted_data.get("metadata", {}).get("extraction_date", "")
        base_filename = os.path.basename(pdf_path)
        name_without_ext = os.path.splitext(base_filename)[0]
        parsed_data_path = os.path.join("data", "parsed", f"{name_without_ext}_{timestamp}.json")
    
    # Step 2: Triplet extraction
    triplets = test_triplet_extraction(parsed_data_path)
    if not triplets:
        return False
    
    # Step 3: Knowledge graph construction
    if not test_knowledge_graph(triplets):
        return False
    
    # Step 4: Analytics and strategy generation
    if not test_analytics(entity_name):
        return False
    
    logger.info("Full pipeline test completed successfully")
    return True

if __name__ == "__main__":
    # Sample document path
    pdf_path = "data/uploads/sample_financial_report.pdf"
    entity_name = "Sample Company"
    
    run_full_test(pdf_path, entity_name)