#!/usr/bin/env python3
"""
Script to process BizGuru PDF reports and populate the knowledge graph.
Falls back to test data if no reports are found.
"""

import sys
import os
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

from bizguru_extractor import BizGuruExtractor
from knowledge_graph.neo4j_manager import Neo4jManager
import populate_test_data

# Set up logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_for_reports(reports_dir: str = None) -> List[str]:
    """
    Check for BizGuru PDF reports in the specified directory.
    
    Args:
        reports_dir: Directory to check for reports (default: data/uploads/bizguru)
        
    Returns:
        list: Paths to found PDF files or empty list if none found
    """
    if reports_dir is None:
        reports_dir = os.path.join("data", "uploads", "bizguru")
    
    if not os.path.exists(reports_dir):
        logger.info(f"Reports directory not found: {reports_dir}")
        return []
    
    # Get all PDF files in the directory
    pdf_files = [f for f in os.listdir(reports_dir) if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        logger.info(f"No PDF files found in {reports_dir}")
        return []
    
    return [os.path.join(reports_dir, pdf) for pdf in pdf_files]

def process_bizguru_report(pdf_path: str, neo4j_manager: Neo4jManager) -> Dict[str, Any]:
    """
    Process a single BizGuru report and populate Neo4j.
    
    Args:
        pdf_path: Path to the PDF file
        neo4j_manager: Neo4j database manager
        
    Returns:
        dict: Processing results
    """
    logger.info(f"Processing BizGuru report: {pdf_path}")
    
    # Initialize extractor
    extractor = BizGuruExtractor()
    
    try:
        # Extract data from PDF
        report_data = extractor.extract_from_file(pdf_path)
        
        # Get entity name
        entity_name = report_data.get("entity", "Unknown Entity")
        
        # Store extracted data in Neo4j
        store_report_data(neo4j_manager, entity_name, report_data)
        
        logger.info(f"Successfully processed {entity_name} report")
        
        return {
            "status": "success",
            "entity": entity_name,
            "pdf_path": pdf_path,
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error processing report {pdf_path}: {e}")
        return {
            "status": "error",
            "pdf_path": pdf_path,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

def store_report_data(neo4j_manager: Neo4jManager, entity_name: str, report_data: Dict[str, Any]) -> None:
    """
    Store extracted report data in Neo4j with improved robustness.
    
    Args:
        neo4j_manager: Neo4j database manager
        entity_name: Name of the entity
        report_data: Extracted report data
    """
    try:
        # Create entity if it doesn't exist
        create_entity_query = """
        MERGE (e:Entity {name: $entity_name})
        ON CREATE SET e.created_at = datetime()
        RETURN e
        """
        
        neo4j_manager.execute_query(create_entity_query, {"entity_name": entity_name})
        logger.info(f"Entity node created/found: {entity_name}")
        
        # Process each group in the report
        for group_id, group_data in report_data.get("groups", {}).items():
            try:
                # Store assessment data
                assessment_query = """
                MATCH (e:Entity {name: $entity_name})
                MERGE (e)-[:HAS_ASSESSMENT]->(a:Assessment {name: $group_name})
                SET a.score = $score,
                    a.risk_level = $risk_level,
                    a.updated_at = datetime()
                """
                
                score = group_data.get("score", 0.5)
                risk_level = group_data.get("risk_level", "Medium")
                
                neo4j_manager.execute_query(assessment_query, {
                    "entity_name": entity_name,
                    "group_name": group_id,
                    "score": score,
                    "risk_level": risk_level
                })
                logger.info(f"Assessment created for group: {group_id}")
                
                # Store findings if present
                for finding in group_data.get("findings", []):
                    try:
                        finding_query = """
                        MATCH (e:Entity {name: $entity_name})-[:HAS_ASSESSMENT]->(a:Assessment {name: $group_name})
                        MERGE (a)-[:HAS_FINDING]->(:Finding {description: $description})
                        """
                        
                        neo4j_manager.execute_query(finding_query, {
                            "entity_name": entity_name,
                            "group_name": group_id,
                            "description": finding.get("description", "")
                        })
                    except Exception as e:
                        logger.warning(f"Error storing finding for {group_id}: {e}")
                
                # Process vision data
                if group_id == "vision" and "vision_statement" in group_data:
                    try:
                        vision_query = """
                        MATCH (e:Entity {name: $entity_name})
                        SET e.vision_statement = $vision_statement
                        """
                        
                        neo4j_manager.execute_query(vision_query, {
                            "entity_name": entity_name,
                            "vision_statement": group_data["vision_statement"]
                        })
                    except Exception as e:
                        logger.warning(f"Error storing vision statement: {e}")
                
                # Process risk data
                if group_id == "risk_assessment" and "risks" in group_data:
                    for risk in group_data["risks"]:
                        try:
                            risk_query = """
                            MATCH (e:Entity {name: $entity_name})
                            MERGE (e)-[:HAS_RISK]->(r:Risk {type: $risk_type})
                            SET r.description = $description,
                                r.level = $level
                            """
                            
                            neo4j_manager.execute_query(risk_query, {
                                "entity_name": entity_name,
                                "risk_type": risk.get("risk_type", "Unknown"),
                                "description": risk.get("description", ""),
                                "level": risk.get("level", 0.5)
                            })
                        except Exception as e:
                            logger.warning(f"Error storing risk: {e}")
                
                # Handle market segments
                if group_id in ["market_assessment", "strategic_assessment"] and "segments" in group_data:
                    for segment in group_data["segments"]:
                        try:
                            segment_query = """
                            MATCH (e:Entity {name: $entity_name})
                            MERGE (m:Market {name: $segment_name})
                            MERGE (e)-[r:OPERATES_IN]->(m)
                            SET r.attractiveness = $attractiveness,
                                r.updated_at = datetime()
                            """
                            
                            neo4j_manager.execute_query(segment_query, {
                                "entity_name": entity_name,
                                "segment_name": segment.get("name", "Unknown"),
                                "attractiveness": segment.get("attractiveness", 0.5)
                            })
                        except Exception as e:
                            logger.warning(f"Error storing market segment: {e}")
                
                # Store financial metrics
                if "metrics" in group_data:
                    for metric in group_data["metrics"]:
                        try:
                            metric_query = """
                            MATCH (e:Entity {name: $entity_name})
                            MERGE (e)-[:HAS_METRIC]->(m:Metric {name: $metric_name})
                            SET m.value = $value,
                                m.raw_value = $raw_value,
                                m.timestamp = datetime()
                            """
                            
                            neo4j_manager.execute_query(metric_query, {
                                "entity_name": entity_name,
                                "metric_name": metric.get("name", "Unknown"),
                                "value": metric.get("value", 0),
                                "raw_value": metric.get("raw_value", "")
                            })
                        except Exception as e:
                            logger.warning(f"Error storing metric: {e}")
                
            except Exception as e:
                logger.warning(f"Error processing group {group_id}: {e}")
        
        logger.info(f"Successfully stored all data for entity: {entity_name}")
    
    except Exception as e:
        logger.error(f"Error storing report data for {entity_name}: {e}")

def main():
    """Main entry point for BizGuru report processing"""
    print("\n" + "="*80)
    print(" BizGuru Report Processor ".center(80, "="))
    print("="*80 + "\n")
    
    # Initialize Neo4j connection
    neo4j_manager = Neo4jManager()
    connected = neo4j_manager.connect()
    
    if not connected:
        logger.error("Failed to connect to Neo4j database")
        return 1
    
    try:
        # Check for BizGuru reports
        reports = check_for_reports()
        
        if reports:
            print(f"Found {len(reports)} BizGuru reports. Processing...")
            
            results = []
            for report in reports:
                result = process_bizguru_report(report, neo4j_manager)
                results.append(result)
            
            # Print summary
            success_count = sum(1 for r in results if r["status"] == "success")
            error_count = sum(1 for r in results if r["status"] == "error")
            
            print(f"\nProcessing complete: {success_count} successful, {error_count} errors")
            
            for result in results:
                status = "✅" if result["status"] == "success" else "❌"
                if result["status"] == "success":
                    print(f"{status} {result['entity']}")
                else:
                    print(f"{status} {result['pdf_path']} - Error: {result['error']}")
            
            return 0
        else:
            print("No BizGuru reports found. Falling back to test data...")
            
            # Fall back to populate_test_data.py
            success = populate_test_data.populate_test_data()
            
            if success:
                print("Test data populated successfully.")
                return 0
            else:
                print("Error populating test data.")
                return 1
    
    finally:
        neo4j_manager.close()

if __name__ == "__main__":
    sys.exit(main())