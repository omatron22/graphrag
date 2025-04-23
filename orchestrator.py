"""
Main orchestrator for the knowledge graph-based business consulting system.
Controls the flow of data processing, analysis, and output generation.
"""

import os
import json
import logging
import importlib
from datetime import datetime
import time
import config
from knowledge_graph.neo4j_manager import Neo4jManager
from knowledge_graph.triplet_extractor import TripletExtractor
from analysis.risk_engine import RiskAnalyzer
from analysis.strategy_generator import StrategyGenerator
from analysis.insight_extractor import InsightExtractor
from strategy_assessment import StrategyAssessment
from assessment_pdf_generator import AssessmentPDFGenerator

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
    
        # Add this line to initialize graph_query
        from knowledge_graph.graph_query import GraphQueryManager
        self.graph_query = GraphQueryManager(self.neo4j_manager)
    
        self.strategy_generator = StrategyGenerator(self.neo4j_manager, self.risk_analyzer)
        self.insight_extractor = InsightExtractor(self.neo4j_manager)
    
        self.strategy_assessment = StrategyAssessment(self.neo4j_manager, self.risk_analyzer, self.strategy_generator)
        self.pdf_generator = AssessmentPDFGenerator()
    
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
    
    def _generate_executive_summary(self, entity_name, strategy_data):
        """
        Generate an executive summary for the report.
    
        Args:
            entity_name: Name of the entity
            strategy_data: Strategy data including list of strategies and risk summary
        
        Returns:
            str: Executive summary text
        """
        # Extract strategy info
        strategies = strategy_data.get("strategies", [])
        strategy_count = len(strategies)
        high_priority = sum(1 for s in strategies if s.get("priority") == "high")
    
        # Extract risk info
        risk_levels = strategy_data.get("risk_summary", {})
        risk_summary = ", ".join([f"{k.capitalize()}: {v}" for k, v in risk_levels.items() 
                            if k != "reasoning"])
    
        summary = f"""
        Executive Summary for {entity_name}
    
        This report outlines {strategy_count} strategic recommendations designed to address identified risks
        and capitalize on opportunities. The risk assessment shows {risk_summary}.
    
        {high_priority} high-priority strategies have been identified that require immediate attention.
        The recommendations focus on addressing key operational, financial, and market challenges,
        with detailed implementation roadmaps and expected outcomes.
    
        The analysis leverages data from our knowledge graph which integrates information 
        from multiple business documents and market intelligence sources.
        """
    
        return summary.strip()
    
    def _get_market_context(self, entity_name):
        """
        Get market context for the entity.
    
        Args:
            entity_name: Name of the entity
        
        Returns:
            dict: Market context data
        """
        # For a real implementation, this would query external market data
        # or extract it from the knowledge graph
        # This is a placeholder implementation
    
        try:
            # Try to get actual market data from the knowledge graph
            markets_query = """
            MATCH (e:Entity {name: $entity_name})-[r:OPERATES_IN]->(m:Market)
            RETURN m.name as name, m.size as size, m.growth_rate as growth_rate, 
                r.market_position as position, r.years_present as years
            """
        
            markets = self.neo4j_manager.execute_query(markets_query, {"entity_name": entity_name})
        
            if markets:
                market_context = {
                    "markets": []
                }
            
                for market in markets:
                    market_context["markets"].append({
                        "name": market.get("name", "Unknown"),
                        "size": market.get("size", "Unknown"),
                        "growth_rate": market.get("growth_rate", "Unknown"),
                        "position": market.get("position", "Unknown"),
                        "years_present": market.get("years", "Unknown")
                    })
                
                # Add some additional context
                market_context["market_trends"] = ["Digital transformation", "Cloud adoption", "AI integration"]
                return market_context
            
        except Exception as e:
            logger.warning(f"Error getting market context: {e}")
    
        # Fallback generic market context
        return {
            "market_size": "$10B",
            "growth_rate": "5.2%",
            "competitive_landscape": {
                "major_players": ["Competitor A", "Competitor B", "Competitor C"],
                "market_shares": [23, 18, 15]
            },
            "key_trends": [
                "Digital transformation across the industry",
                "Increasing regulatory scrutiny",
                "Shift toward sustainable practices"
            ]
        }
    
    def process_document(self, file_path):
        """
        Process a single document through the entire pipeline with improved error handling
    
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
        extracted_data = None
        parsed_path = None
    
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
        triplets = []
        try:
            # Add retry logic for triplet extraction
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    triplets = self.triplet_extractor.extract_from_file(parsed_path)
                    if triplets:
                        logger.info(f"Extracted {len(triplets)} triplets from document")
                        break
                    else:
                        logger.warning(f"No triplets extracted (attempt {attempt+1}/{max_retries})")
                        if attempt < max_retries - 1:
                            time.sleep(2)  # Wait before retrying
                except Exception as e:
                    logger.error(f"Triplet extraction failed (attempt {attempt+1}/{max_retries}): {e}")
                    if attempt < max_retries - 1:
                        time.sleep(2)  # Wait before retrying
        
            # If no triplets were found after all retries, use fallback
            if not triplets:
                logger.warning("No triplets extracted after retries, adding minimal triplets")
                # Create at least one basic triplet from the document filename
                base_name = os.path.splitext(os.path.basename(file_path))[0]
                triplets = [{
                    "subject": base_name,
                    "subject_type": "Document",
                    "predicate": "CONTAINS",
                    "object": "business information",
                    "object_type": "Information",
                    "context": f"Document {base_name} contains business information",
                    "extraction_method": "fallback",
                    "confidence": 1.0
                }]
            
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
                    # Get entity insights with retry
                    insights = None
                    try:
                        insights = self.insight_extractor.extract_insights(entity)
                    except Exception as e:
                        logger.error(f"Insights extraction failed for {entity}: {e}")
                        insights = {"error": str(e)}
                
                    # Run risk analysis with retry
                    risk_analysis = None
                    try:
                        risk_analysis = self.risk_analyzer.analyze()
                    except Exception as e:
                        logger.error(f"Risk analysis failed for {entity}: {e}")
                        risk_analysis = {"error": str(e)}
                
                    # Generate strategies with retry
                    strategies = None
                    try:
                        strategies = self.strategy_generator.generate_for_entity(entity)
                    except Exception as e:
                        logger.error(f"Strategy generation failed for {entity}: {e}")
                        strategies = {"error": str(e)}
                
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
    
    # Add this method to the Orchestrator class
    def run_strategy_assessment(self, entity_name, user_inputs=None):
        """
        Run a comprehensive strategy assessment for an entity.
    
        Args:
            entity_name: Name of the entity to assess
            user_inputs: User provided inputs (risk tolerance, priorities, constraints)
        
        Returns:
            dict: Assessment results
        """
        logger.info(f"Running strategy assessment for {entity_name}")
    
        # Use default inputs if none provided
        if user_inputs is None:
            user_inputs = {
                "risk_tolerance": "Medium",
                "priorities": [],
                "constraints": []
            }
    
        # Run assessment
        assessment_results = self.strategy_assessment.assess(entity_name, user_inputs)
    
        # Generate charts
        charts = self.strategy_assessment.generate_charts(assessment_results)
    
        # Generate PDF report
        pdf_path = self.pdf_generator.generate_assessment_pdf(assessment_results, charts)
    
        logger.info(f"Strategy assessment complete for {entity_name}")
    
        return {
            "assessment_results": assessment_results,
            "charts": charts,
            "pdf_path": pdf_path
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
            logger.info(f"Risk analysis results: {risk_analysis}")

            # Generate strategies (do this only once)
            strategies = self.strategy_generator.generate_for_entity(entity_name)
            logger.info(f"Strategy type: {type(strategies)}")
            logger.info(f"Strategy keys: {strategies.keys() if isinstance(strategies, dict) else 'Not a dict'}")

            # Extract strategies list (keep this consistent)
            if isinstance(strategies, dict) and "strategies" in strategies:
                strategies_list = strategies["strategies"]
            else:
                strategies_list = strategies if isinstance(strategies, list) else []
        
            logger.info(f"Strategies list contains {len(strategies_list)} strategies")
            for i, strategy in enumerate(strategies_list):
                logger.info(f"Strategy {i+1}: {strategy.get('title', 'Untitled')}")

            # Use the SAME strategies object for comprehensive report
            report = {
                "entity": entity_name,
                "generation_date": datetime.now().isoformat(),
                "executive_summary": self._generate_executive_summary(entity_name, {"strategies": strategies_list, "risk_summary": risk_analysis.get("categories", {})}),
                "strategies": strategies_list,
                "risk_assessment": risk_analysis.get("categories", {}),
                "visualizations": strategies.get("visualization_data", {}) if isinstance(strategies, dict) else {},
                "opportunities": strategies.get("strategic_opportunities", {}) if isinstance(strategies, dict) else {},
                "supporting_data": {
                    "entity_graph": self.graph_query.export_graph_segment(entity_name, 2),
                    "market_context": self._get_market_context(entity_name)
                }
            }

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
                "strategies": strategies_list,
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

            # Process insights for PDF - be very careful with data types
            key_insights = []
            if isinstance(insights, dict) and "key_findings" in insights:
                for finding in insights["key_findings"]:
                    if isinstance(finding, dict):
                        title = finding.get("title", "")
                        explanation = finding.get("explanation", "")
                        if title and explanation:
                            key_insights.append(f"{title}: {explanation}")
                        elif title:
                            key_insights.append(title)
        
            # Create assessment results in the format expected by the PDF generator
            assessment_results = {
                "entity": entity_name,
                "summary": {
                    "overall_score": 0.7,  # This is a placeholder
                    "risk_level": risk_analysis.get("categories", {}).get("overall", "Medium"),
                    "key_insights": key_insights[:5]  # Use processed insights
                },
                "recommendations": strategies_list,
                "groups": {
                    "risk": {
                        "name": "Risk Assessment",
                        "description": "Assessment of business risks across multiple dimensions",
                        "score": 0.7,
                        "risk_level": risk_analysis.get("categories", {}).get("overall", "Medium"),
                        "findings": {}  # Initialize as empty dict
                    },
                    "market": {
                        "name": "Market Assessment",
                        "description": "Evaluation of market position and opportunities",
                        "score": 0.65,
                        "risk_level": "Medium",
                        "findings": []
                    }
                }
            }
        
            # Safely populate risk findings
            if isinstance(risk_analysis, dict) and "categories" in risk_analysis:
                risk_findings = {}
                for k, v in risk_analysis["categories"].items():
                    if k != "reasoning":
                        risk_findings[k] = v
                assessment_results["groups"]["risk"]["findings"] = risk_findings
        
            try:
                # Generate charts for visualizations - wrap in try block
                logger.info("Generating charts for PDF report")
                charts = self._generate_charts_for_report(assessment_results, strategies)
    
                # Generate PDF report
                logger.info("Generating PDF report")
                pdf_path = self.pdf_generator.generate_assessment_pdf(assessment_results, charts)
                logger.info(f"Generated PDF report for {entity_name}: {pdf_path}")
    
                # Add PDF path to return values
                return {**full_report, "report_path": report_path, "pdf_path": pdf_path}
    
            except Exception as e:
                # If PDF generation fails, still return the JSON report
                logger.error(f"PDF generation failed: {e}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
                return {**full_report, "report_path": report_path}

        except Exception as e:
            logger.error(f"Failed to generate analysis report for {entity_name}: {e}")
            return {"error": str(e)}
    
    def _generate_charts_for_report(self, assessment_results, strategies_data):
        """
        Generate chart data for the PDF report.
    
        Args:
            assessment_results: Assessment results data
            strategies_data: Strategy data with visualization information
        
        Returns:
            dict: Charts for report visualization
        """
        charts = {}
    
        # Log data types to help debug
        logger.info(f"strategies_data type: {type(strategies_data)}")
        if isinstance(strategies_data, dict) and "visualization_data" in strategies_data:
            logger.info(f"visualization_data type: {type(strategies_data['visualization_data'])}")
    
        # Risk Levels chart - handle various data formats safely
        risk_data = {}
        if isinstance(assessment_results, dict) and "groups" in assessment_results:
            risk_group = assessment_results["groups"].get("risk", {})
            if isinstance(risk_group, dict):
                risk_data = risk_group.get("findings", {})
    
        if risk_data and isinstance(risk_data, dict):
            risk_levels_data = []
            for risk_type, level in risk_data.items():
                if risk_type != "reasoning":
                    risk_levels_data.append({"label": f"{risk_type.capitalize()}: {level}", "value": 1})
        
            if risk_levels_data:
                charts["risk_levels"] = {
                    "type": "pie_chart",
                    "title": "Risk Assessment",
                    "data": risk_levels_data
                }
    
        # Strategy priority chart
        if isinstance(assessment_results, dict) and "recommendations" in assessment_results:
            recommendations = assessment_results["recommendations"]
            if isinstance(recommendations, list):
                priority_counts = {"high": 0, "medium": 0, "low": 0}
                for strategy in recommendations:
                    if isinstance(strategy, dict):
                        priority = strategy.get("priority", "medium").lower()
                        if priority in priority_counts:
                            priority_counts[priority] += 1
            
                priority_data = [
                    {"label": "High Priority", "value": priority_counts["high"]},
                    {"label": "Medium Priority", "value": priority_counts["medium"]},
                    {"label": "Low Priority", "value": priority_counts["low"]}
                ]
            
                charts["strategy_priorities"] = {
                    "type": "bar_chart",
                    "title": "Strategy Priorities",
                    "data": priority_data
                }
    
        # Add financial impact chart if available in strategies data
        if isinstance(strategies_data, dict) and "visualization_data" in strategies_data:
            viz_data = strategies_data["visualization_data"]
        
            # Financial impact chart - check each item's type
            if isinstance(viz_data, dict) and "financial_impact" in viz_data:
                financial_impact = viz_data["financial_impact"]
                logger.info(f"financial_impact type: {type(financial_impact)}")
                # Only add if it's actually a dictionary
                if isinstance(financial_impact, dict):
                    charts["financial_impact"] = financial_impact
        
            # Implementation timeline - check type
            if isinstance(viz_data, dict) and "implementation_timeline" in viz_data:
                implementation_timeline = viz_data["implementation_timeline"]
                logger.info(f"implementation_timeline type: {type(implementation_timeline)}")
                # Only add if it's actually a dictionary
                if isinstance(implementation_timeline, dict):
                    charts["implementation_timeline"] = implementation_timeline
        
            # Risk mitigation impact - check type
            if isinstance(viz_data, dict) and "risk_mitigation_impact" in viz_data:
                risk_mitigation = viz_data["risk_mitigation_impact"]
                logger.info(f"risk_mitigation_impact type: {type(risk_mitigation)}")
                # Only add if it's actually a dictionary
                if isinstance(risk_mitigation, dict):
                    charts["risk_mitigation_impact"] = risk_mitigation
    
        # Log final chart structure
        logger.info(f"Generated {len(charts)} charts")
        for chart_name in charts.keys():
            logger.info(f"Chart included: {chart_name}")
    
        return charts

    def debug_strategies(self, entity_name):
        """
        Debug function to investigate strategy structure.
    
        Args:
            entity_name: Name of the entity to analyze
        
        Returns:
            dict: Debug information
        """
        try:
            # Generate strategies
            strategies = self.strategy_generator.generate_for_entity(entity_name)
        
            # Log structure information
            logger.info(f"Strategy type: {type(strategies)}")
            if isinstance(strategies, dict):
                logger.info(f"Strategy keys: {strategies.keys()}")
                if "strategies" in strategies:
                    logger.info(f"strategies['strategies'] type: {type(strategies['strategies'])}")
                    logger.info(f"strategies['strategies'] length: {len(strategies['strategies'])}")
            elif isinstance(strategies, list):
                logger.info(f"Strategies list length: {len(strategies)}")
        
            return {
                "type": str(type(strategies)),
                "structure": strategies
            }
    
        except Exception as e:
            logger.error(f"Debug error: {e}")
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
                strategies = report.get("strategies", {})
                if isinstance(strategies, list) and strategies:
                    print("\nTop Strategies:")
                    for i, strategy in enumerate(strategies[:min(3, len(strategies))]):
                        print(f"  {i+1}. {strategy.get('title')} (Priority: {strategy.get('priority', 'medium')})")
                else:
                    print("\nNo strategies available.")
        
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