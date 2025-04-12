#!/usr/bin/env python3
"""
Run the full knowledge graph-based business consulting system
on all files in the uploads directory.
"""

import os
import logging
import json
from datetime import datetime
from orchestrator import Orchestrator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("processing_results.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("run_system")

def process_all_files(directory="data/uploads"):
    """Process all supported files in a directory"""
    logger.info(f"Processing all files in {directory}")
    
    # Initialize the orchestrator
    orchestrator = Orchestrator()
    
    try:
        # Process directory
        results = orchestrator.process_directory(directory)
        
        # Log processing summary
        logger.info(f"Processed {len(results.get('processed', []))} files successfully")
        if results.get("errors"):
            logger.warning(f"Encountered {len(results.get('errors', []))} errors")
            for error in results.get("errors", []):
                logger.warning(f"Error: {error}")
        
        # Identify primary entities from the knowledge graph
        primary_entities = identify_primary_entities(orchestrator)
        
        # Generate reports for main entities
        if primary_entities:
            logger.info(f"Generating reports for {len(primary_entities)} primary entities")
            reports = []
            
            for entity in primary_entities:
                logger.info(f"Generating comprehensive report for: {entity}")
                report = orchestrator.generate_analysis_report(entity)
                if "error" not in report:
                    reports.append(report)
                    logger.info(f"Report generated successfully: {report.get('report_path')}")
                else:
                    logger.warning(f"Failed to generate report for {entity}: {report.get('error')}")
            
            # Save summary of all reports
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            summary_path = f"data/knowledge_base/summary_report_{timestamp}.json"
            
            with open(summary_path, 'w', encoding='utf-8') as f:
                summary = {
                    "timestamp": datetime.now().isoformat(),
                    "processed_files": results.get("processed", []),
                    "primary_entities": primary_entities,
                    "reports_generated": [r.get("report_path") for r in reports if "report_path" in r]
                }
                json.dump(summary, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Processing summary saved to: {summary_path}")
            
            # Return processing results
            return {
                "success": True,
                "processed_files": len(results.get("processed", [])),
                "primary_entities": primary_entities,
                "reports": reports,
                "summary_path": summary_path
            }
        else:
            logger.warning("No primary entities identified for reporting")
            return {
                "success": True,
                "processed_files": len(results.get("processed", [])),
                "primary_entities": [],
                "reports": []
            }
    
    except Exception as e:
        logger.error(f"Processing failed: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": str(e)
        }
    finally:
        # Always clean up
        orchestrator.cleanup()

def identify_primary_entities(orchestrator, limit=5):
    """Identify the most significant entities in the knowledge graph"""
    try:
        # Use Neo4j manager to find the most connected entities
        with orchestrator.neo4j_manager.driver.session() as session:
            result = session.run("""
                MATCH (e:Entity)
                WITH e, size((e)--()) AS connections
                WHERE connections > 2
                RETURN e.name AS entity, connections
                ORDER BY connections DESC
                LIMIT $limit
            """, {"limit": limit})
            
            entities = [record["entity"] for record in result]
            
            logger.info(f"Identified {len(entities)} primary entities in the knowledge graph")
            for entity in entities:
                logger.info(f"  - {entity}")
                
            return entities
    except Exception as e:
        logger.error(f"Failed to identify primary entities: {e}")
        return []

if __name__ == "__main__":
    # Run the system
    result = process_all_files()
    
    if result.get("success", False):
        print("\n===== PROCESSING COMPLETE =====")
        print(f"Processed {result.get('processed_files', 0)} files")
        print(f"Identified {len(result.get('primary_entities', []))} primary entities")
        print(f"Generated {len(result.get('reports', []))} reports")
        
        if result.get("summary_path"):
            print(f"\nSummary saved to: {result.get('summary_path')}")
            
        if result.get("primary_entities"):
            print("\nPrimary entities:")
            for entity in result.get("primary_entities", []):
                print(f"  - {entity}")
    else:
        print("\n===== PROCESSING FAILED =====")
        print(f"Error: {result.get('error', 'Unknown error')}")