"""
Main orchestrator for the knowledge graph-based business consulting system.
Controls the flow of data processing, analysis, and output generation.
"""

import os
import json
import logging
import importlib
from datetime import datetime
import config
from knowledge_graph.neo4j_manager import Neo4jManager
from knowledge_graph.triplet_extractor import TripletExtractor
from analysis.risk_engine import RiskAnalyzer
from analysis.strategy_generator import StrategyGenerator
from analysis.insight_extractor import InsightExtractor

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
        # Initialize Neo4j connection
        self.neo4j_manager = Neo4jManager()
        self.neo4j_manager.connect()
        self.neo4j_manager.verify_indexes()
        
        # Initialize components
        self.triplet_extractor = TripletExtractor()
        self.risk_analyzer = RiskAnalyzer(self.neo4j_manager)
        self.strategy_generator = StrategyGenerator(self.neo4j_manager, self.risk_analyzer)
        self.insight_extractor = InsightExtractor(self.neo4j_manager)
        
        # Validate directories exist
        self._ensure_directories()
        
        logger.info("Orchestrator initialized successfully")
        
    def _ensure_directories(self):
        """Ensure all required directories exist"""
        dirs = [
            "data/uploads",
            "data/parsed",
            "data/knowledge_base",
            "data/knowledge_base/insights",
            "data/knowledge_base/strategies",
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
        
        try:
            extractor_module = importlib.import_module(module_path)
            extractor_function = getattr(extractor_module, function_name)
        except (ImportError, AttributeError) as e:
            logger.error(f"Failed to load extractor for {file_ext}: {e}")
            return {"error": f"Extractor not implemented for {file_ext}"}
        
        # 3. Extract content from document
        try:
            # Create parsed data directory if it doesn't exist
            parsed_dir = os.path.join("data", "parsed")
            os.makedirs(parsed_dir, exist_ok=True)
            
            # Extract document content
            extracted_data = extractor_function(file_path, parsed_dir)
            logger.info(f"Successfully extracted data from {file_path}")
            
            # Save parsed data
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_filename = os.path.basename(file_path)
            parsed_filename = f"{os.path.splitext(base_filename)[0]}_{timestamp}.json"
            parsed_path = os.path.join(parsed_dir, parsed_filename)
            
            with open(parsed_path, 'w', encoding='utf-8') as f:
                json.dump(extracted_data, f, ensure_ascii=False, indent=2)
                
            logger.info(f"Saved extracted data to {parsed_path}")
            
        except Exception as e:
            logger.error(f"Extraction failed for {file_path}: {e}")
            return {"error": f"Extraction failed: {str(e)}"}
        
        # 4. Extract triplets for knowledge graph
        try:
            triplets = self.triplet_extractor.extract_from_file(parsed_path)
            logger.info(f"Extracted {len(triplets)} triplets from document")
            
            # 5. Store in knowledge graph
            entities_added = self._store_triplets_in_graph(triplets)
            logger.info(f"Added {entities_added} entities/relationships to knowledge graph")
            
        except Exception as e:
            logger.error(f"Triplet extraction or storage failed: {e}")
            return {
                "status": "partial",
                "document": file_path,
                "extraction_success": True,
                "kg_construction_error": str(e),
                "parsed_data_path": parsed_path
            }
        
        # 6. Run analysis on main entities found in document
        primary_entities = self._identify_primary_entities(triplets)
        
        analysis_results = {}
        if primary_entities:
            try:
                # For each primary entity, run risk analysis and strategy generation
                for entity in primary_entities:
                    # Get entity insights
                    insights = self.insight_extractor.extract_insights(entity)
                    
                    # Run risk analysis
                    risk_analysis = self.risk_analyzer.analyze()
                    
                    # Generate strategies
                    strategies = self.strategy_generator.generate_for_entity(entity)
                    
                    # Store analysis results
                    analysis_results[entity] = {
                        "insights": insights,
                        "risk_analysis": risk_analysis,
                        "strategies": strategies
                    }
                
                logger.info(f"Completed analysis for {len(primary_entities)} entities")
                
            except Exception as e:
                logger.error(f"Analysis failed: {e}")
                return {
                    "status": "partial",
                    "document": file_path,
                    "extraction_success": True,
                    "kg_construction_success": True,
                    "analysis_error": str(e),
                    "primary_entities": primary_entities
                }
        
        return {
            "status": "complete",
            "document": file_path,
            "extraction_success": True,
            "kg_construction_success": True,
            "primary_entities": primary_entities,
            "analysis_results": analysis_results,
            "parsed_data_path": parsed_path
        }
    
    def _store_triplets_in_graph(self, triplets):
        """
        Store extracted triplets in the Neo4j knowledge graph
        
        Args:
            triplets: List of extracted triplets
            
        Returns:
            int: Number of entities/relationships added
        """
        entities_added = 0
        
        for triplet in triplets:
            try:
                # Extract data from triplet
                subject = triplet.get("subject", "")
                subject_type = triplet.get("subject_type", "Entity")
                predicate = triplet.get("predicate", "")
                obj = triplet.get("object", "")
                object_type = triplet.get("object_type", "Entity")
                
                # Skip invalid triplets
                if not subject or not predicate or not obj:
                    continue
                
                # Clean up types for Neo4j (capitalize and remove special chars)
                subject_type = ''.join(c for c in subject_type.title() if c.isalnum())
                object_type = ''.join(c for c in object_type.title() if c.isalnum())
                predicate = ''.join(c for c in predicate.upper() if c.isalnum() or c == '_')
                
                # If types are empty, set to Entity
                if not subject_type:
                    subject_type = "Entity"
                if not object_type:
                    object_type = "Entity"
                
                # Prepare properties
                subject_props = {"name": subject}
                object_props = {"name": obj}
                
                # Add source and context if available
                rel_props = {}
                if "context" in triplet:
                    rel_props["context"] = triplet["context"]
                if "source" in triplet:
                    rel_props["source"] = triplet["source"]
                if "confidence" in triplet:
                    rel_props["confidence"] = triplet["confidence"]
                
                # Add timestamp
                rel_props["timestamp"] = datetime.now().isoformat()
                
                # Add to Neo4j
                result = self.neo4j_manager.add_triplet(
                    subject_type, subject_props, 
                    predicate, 
                    object_type, object_props,
                    rel_props
                )
                
                if result:
                    entities_added += 1
                    
            except Exception as e:
                logger.warning(f"Failed to add triplet to graph: {e}")
                continue
                
        return entities_added
    
    def _identify_primary_entities(self, triplets):
        """
        Identify primary entities from extracted triplets for analysis
        
        Args:
            triplets: List of extracted triplets
            
        Returns:
            list: Primary entity names
        """
        # Count entity occurrences
        entity_counts = {}
        
        for triplet in triplets:
            subject = triplet.get("subject", "")
            obj = triplet.get("object", "")
            
            if subject:
                entity_counts[subject] = entity_counts.get(subject, 0) + 1
            if obj:
                entity_counts[obj] = entity_counts.get(obj, 0) + 1
        
        # Sort by count and take top entities (those mentioned more than twice)
        sorted_entities = sorted(entity_counts.items(), key=lambda x: x[1], reverse=True)
        primary_entities = [entity for entity, count in sorted_entities if count > 2]
        
        # Limit to top 5 entities to avoid excessive processing
        return primary_entities[:5]
    
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
        # Check if entity exists in knowledge graph
        entity_summary = self.neo4j_manager.execute_query(
            "MATCH (e:Entity {name: $name}) RETURN e", 
            {"name": entity_name}
        )
        
        if not entity_summary:
            return {"error": f"Entity not found: {entity_name}"}
        
        try:
            # Get entity insights
            insights = self.insight_extractor.extract_insights(entity_name)
            
            # Run risk analysis
            risk_analysis = self.risk_analyzer.analyze()
            
            # Generate strategies
            strategies = self.strategy_generator.generate_for_entity(entity_name)
            
            # Generate comprehensive report
            report = self.strategy_generator.generate_comprehensive_report(entity_name)
            
            # Get connected entities
            connected_entities = self.neo4j_manager.execute_query(
                """
                MATCH (e:Entity {name: $name})-[r]-(connected:Entity)
                RETURN connected.name AS entity, type(r) AS relationship, 
                       COUNT(*) AS connection_strength
                ORDER BY connection_strength DESC
                LIMIT 10
                """,
                {"name": entity_name}
            )
            
            # Compile full report
            full_report = {
                "entity": entity_name,
                "timestamp": datetime.now().isoformat(),
                "risks": risk_analysis,
                "insights": insights,
                "strategies": strategies,
                "connected_entities": connected_entities,
                "comprehensive_report": report
            }
            
            # Save report
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_filename = f"report_{entity_name.replace(' ', '_')}_{timestamp}.json"
            report_path = os.path.join("data", "knowledge_base", report_filename)
            
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(full_report, f, ensure_ascii=False, indent=2)
                
            logger.info(f"Generated analysis report for {entity_name}: {report_path}")
            
            return {**full_report, "report_path": report_path}
            
        except Exception as e:
            logger.error(f"Failed to generate analysis report for {entity_name}: {e}")
            return {"error": str(e)}
    
    def visualize_entity_network(self, entity_name, depth=2):
        """
        Generate visualization data for entity network
        
        Args:
            entity_name: Name of the entity to visualize
            depth: Relationship depth to include
            
        Returns:
            dict: Visualization data
        """
        try:
            # Get graph data
            graph_data = self.neo4j_manager.execute_query(
                """
                MATCH path = (e:Entity {name: $name})-[*1..$depth]-(related)
                UNWIND relationships(path) AS rel
                WITH DISTINCT startNode(rel) AS source, endNode(rel) AS target, type(rel) AS type
                RETURN source.name AS source, target.name AS target, type
                """,
                {"name": entity_name, "depth": depth}
            )
            
            # Process into visualization format
            nodes = set()
            links = []
            
            for rel in graph_data:
                source = rel.get("source")
                target = rel.get("target")
                rel_type = rel.get("type")
                
                if source and target:
                    nodes.add(source)
                    nodes.add(target)
                    links.append({
                        "source": source,
                        "target": target,
                        "type": rel_type
                    })
            
            # Format nodes
            formatted_nodes = [{"id": node, "name": node} for node in nodes]
            
            # Save visualization data
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            viz_filename = f"viz_{entity_name.replace(' ', '_')}_{timestamp}.json"
            viz_path = os.path.join("knowledge_graph", "exports", viz_filename)
            
            viz_data = {
                "nodes": formatted_nodes,
                "links": links,
                "focus_entity": entity_name
            }
            
            with open(viz_path, 'w', encoding='utf-8') as f:
                json.dump(viz_data, f, ensure_ascii=False, indent=2)
                
            logger.info(f"Generated visualization for {entity_name}: {viz_path}")
            
            return {**viz_data, "visualization_path": viz_path}
            
        except Exception as e:
            logger.error(f"Failed to generate visualization for {entity_name}: {e}")
            return {"error": str(e)}
    
    def cleanup(self):
        """Close connections and clean up resources"""
        self.neo4j_manager.close()
        logger.info("Orchestrator cleanup completed")


# For command line usage
if __name__ == "__main__":
    import sys
    import argparse
    
    # Set up argument parser for more flexibility
    parser = argparse.ArgumentParser(description="Knowledge Graph Business Consulting System")
    parser.add_argument("path", help="Path to file or directory to process")
    parser.add_argument("--analyze", "-a", help="Entity name to analyze", default=None)
    parser.add_argument("--visualize", "-v", help="Entity name to visualize", default=None)
    parser.add_argument("--depth", "-d", type=int, help="Relationship depth for visualization", default=2)
    
    args = parser.parse_args()
    
    orchestrator = Orchestrator()
    
    try:
        # Process documents if path is provided
        if args.path:
            if os.path.isfile(args.path):
                print(f"Processing file: {args.path}")
                result = orchestrator.process_document(args.path)
                print(f"Processing result: {result['status']}")
                if result.get("primary_entities"):
                    print(f"Primary entities found: {', '.join(result['primary_entities'])}")
            elif os.path.isdir(args.path):
                print(f"Processing directory: {args.path}")
                result = orchestrator.process_directory(args.path)
                print(f"Processed {len(result['processed'])} files")
                if result["errors"]:
                    print(f"Encountered {len(result['errors'])} errors")
            else:
                print(f"Error: Path not found: {args.path}")
        
        # Run analysis if entity is specified
        if args.analyze:
            print(f"Generating analysis report for: {args.analyze}")
            report = orchestrator.generate_analysis_report(args.analyze)
            if "error" not in report:
                print(f"Analysis complete. Report saved to: {report.get('report_path')}")
                
                # Print risk summary
                risks = report.get("risks", {}).get("categories", {})
                if risks:
                    print("\nRisk Assessment:")
                    for risk_type, level in risks.items():
                        if risk_type != "reasoning":
                            print(f"  - {risk_type.capitalize()}: {level}")
                
                # Print top strategies
                strategies = report.get("strategies", [])
                if strategies:
                    print("\nTop Strategies:")
                    for i, strategy in enumerate(strategies[:3]):
                        print(f"  {i+1}. {strategy.get('title')} (Priority: {strategy.get('priority', 'medium')})")
            else:
                print(f"Error: {report.get('error')}")
        
        # Generate visualization if entity is specified
        if args.visualize:
            print(f"Generating network visualization for: {args.visualize} (depth: {args.depth})")
            viz = orchestrator.visualize_entity_network(args.visualize, args.depth)
            if "error" not in viz:
                print(f"Visualization complete. Saved to: {viz.get('visualization_path')}")
                print(f"Network contains {len(viz.get('nodes', []))} nodes and {len(viz.get('links', []))} relationships")
            else:
                print(f"Error: {viz.get('error')}")
                
    finally:
        orchestrator.cleanup()