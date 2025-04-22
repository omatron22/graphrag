"""
Strategy generator for the knowledge graph-based business consulting system.
Creates actionable recommendations based on identified risks and opportunities.
"""

import os
import logging
import json
from datetime import datetime
import requests
from typing import Dict, Any, List, Optional, Tuple
import config
from knowledge_graph.graph_query import GraphQueryManager

# Set up logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class StrategyGenerator:
    """
    Generates actionable business recommendations based on risk analysis
    and knowledge graph insights.
    """
    
    def __init__(self, neo4j_manager, risk_analyzer=None):
        """
        Initialize the strategy generator.
        
        Args:
            neo4j_manager: Instance of Neo4jManager for graph access
            risk_analyzer: Optional instance of RiskAnalyzer for risk insights
        """
        self.neo4j_manager = neo4j_manager
        self.graph_query = GraphQueryManager(neo4j_manager)
        self.risk_analyzer = risk_analyzer
        self.model_config = config.MODELS['reasoning']
        
        # Create output directory for strategy documents
        self.output_dir = os.path.join("data", "knowledge_base", "strategies")
        os.makedirs(self.output_dir, exist_ok=True)
        
        logger.info("Strategy Generator initialized")
    
    def generate_for_entity(self, entity_name: str) -> Dict[str, Any]:
        """
        Generate comprehensive strategies for an entity.
        
        Args:
            entity_name: Name of the entity to generate strategies for
            
        Returns:
            dict: Strategy recommendations with supporting data
        """
        logger.info(f"Generating strategies for entity: {entity_name}")
        
        # Get entity summary from knowledge graph
        entity_summary = self.graph_query.get_entity_summary(entity_name)
        
        # Check if entity exists
        if not entity_summary.get("entity"):
            logger.warning(f"Entity not found: {entity_name}")
            return {"error": f"Entity not found: {entity_name}"}
        
        # Get risk analysis if available
        risk_data = {}
        if self.risk_analyzer:
            risk_data = self.risk_analyzer.analyze()
        
        # Get strategic opportunities
        opportunities = self.graph_query.find_strategic_opportunities(entity_name)
        
        # Generate strategies using LLM
        strategies = self._generate_llm_strategies(entity_name, entity_summary, risk_data, opportunities)
        
        # Prepare visualization data for each recommendation
        visualization_data = self._prepare_visualization_data(entity_name, strategies)
        
        # Compile the final output
        result = {
            "entity": entity_name,
            "timestamp": datetime.now().isoformat(),
            "risk_summary": risk_data.get("categories", {}),
            "strategies": strategies,
            "visualization_data": visualization_data,
            "strategic_opportunities": opportunities
        }
        
        # Save results to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"strategy_{entity_name.replace(' ', '_')}_{timestamp}.json"
        output_path = os.path.join(self.output_dir, output_filename)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Strategy recommendations saved to: {output_path}")
        
        return result
    
    def _generate_llm_strategies(self, entity_name: str, entity_summary: Dict[str, Any], 
                       risk_data: Dict[str, Any], opportunities: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate strategies using large language model with enhanced strategic focus and improved reliability.

        Args:
            entity_name: Name of the entity
            entity_summary: Entity data from knowledge graph
            risk_data: Risk analysis results
            opportunities: Strategic opportunities
    
        Returns:
            list: Generated strategies with details
        """
        # Format entity summary for LLM prompt
        entity_info = []

        # Add basic entity details
        if entity_summary.get("entity"):
            entity_info.append(f"Entity: {entity_name}")
            for key, value in entity_summary.get("entity", {}).items():
                if key != "name" and value:
                    entity_info.append(f"- {key}: {value}")

        # Add financial metrics
        if entity_summary.get("financial_metrics"):
            entity_info.append("\nFinancial Metrics:")
            for metric in entity_summary["financial_metrics"]:
                entity_info.append(f"- {metric['metric_name']}: {metric['metric_value']} {metric['metric_unit']}")

        # Add key relationships
        if entity_summary.get("outgoing_relationships"):
            entity_info.append("\nKey Relationships:")
            for rel in entity_summary["outgoing_relationships"][:5]:  # Top 5 relationships
                entity_info.append(f"- {entity_name} --[{rel['relationship_type']}]--> {rel['target_name']}")

        # Get entity strengths (new addition)
        strengths_info = []
        try:
            strengths_query = """
            MATCH (e:Entity {name: $entity_name})-[:HAS_STRENGTH]->(s:Strength)
            RETURN s.name as name, s.description as description, s.importance as importance
            """
            strengths = self.neo4j_manager.execute_query(strengths_query, {"entity_name": entity_name})
            if strengths:
                entity_info.append("\nKey Strengths:")
                for strength in strengths:
                    entity_info.append(f"- {strength.get('name', 'Unknown')}: {strength.get('description', '')} " +
                                    f"(Importance: {strength.get('importance', 'Medium')})")
        except Exception as e:
            logger.warning(f"Error retrieving strengths: {e}")

        # Get products (new addition)
        products_info = []
        try:
            products_query = """
            MATCH (e:Entity {name: $entity_name})-[:PRODUCES]->(p:Product)
            RETURN p.name as name, p.description as description, p.revenue as revenue, 
                p.growth_rate as growth_rate, p.market_share as market_share
            """
            products = self.neo4j_manager.execute_query(products_query, {"entity_name": entity_name})
            if products:
                entity_info.append("\nProducts:")
                for product in products:
                    entity_info.append(f"- {product.get('name', 'Unknown')}: {product.get('description', '')} " +
                                    f"(Revenue: {product.get('revenue', 'N/A')}, Growth: {product.get('growth_rate', 'N/A')})")
        except Exception as e:
            logger.warning(f"Error retrieving products: {e}")

        # Get markets (new addition)
        markets_info = []
        try:
            markets_query = """
            MATCH (e:Entity {name: $entity_name})-[r:OPERATES_IN]->(m:Market)
            RETURN m.name as name, m.size as size, m.growth_rate as growth_rate, 
                r.market_position as position, r.years_present as years
            """
            markets = self.neo4j_manager.execute_query(markets_query, {"entity_name": entity_name})
            if markets:
                entity_info.append("\nMarkets:")
                for market in markets:
                    entity_info.append(f"- {market.get('name', 'Unknown')}: {market.get('size', 'N/A')} market, " +
                                    f"{market.get('growth_rate', 'N/A')} growth, Position: {market.get('position', 'N/A')}")
        except Exception as e:
            logger.warning(f"Error retrieving markets: {e}")

        # Format risk data
        risk_info = []
        if risk_data:
            risk_info.append("Risk Assessment:")
            for risk_type, category in risk_data.get("categories", {}).items():
                if risk_type != "reasoning":
                    risk_score = risk_data.get("scores", {}).get(risk_type, 0)
                    risk_info.append(f"- {risk_type.capitalize()} Risk: {category} (Score: {risk_score:.2f})")
    
            if risk_data.get("reasoning"):
                risk_info.append(f"\nReasoning: {risk_data['reasoning']}")

        # Get specific risks
        risks_query = """
        MATCH (e:Entity {name: $entity_name})-[:HAS_RISK]->(r:Risk)
        RETURN r.type as type, r.description as description, r.level as level, 
            r.impact_area as impact_area, r.probability as probability
        """
        try:
            risks = self.neo4j_manager.execute_query(risks_query, {"entity_name": entity_name})
            if risks:
                risk_info.append("\nSpecific Risks:")
                for risk in risks:
                    risk_info.append(f"- {risk.get('type', 'Unknown').capitalize()}: {risk.get('description', '')} " +
                                f"(Level: {risk.get('level', 'N/A')}, Area: {risk.get('impact_area', 'N/A')})")
        except Exception as e:
            logger.warning(f"Error retrieving specific risks: {e}")

        # Format opportunities
        opportunity_info = []
        if opportunities:
            if opportunities.get("partnership_opportunities"):
                opportunity_info.append("Partnership Opportunities:")
                for partner in opportunities["partnership_opportunities"][:3]:  # Top 3
                    strengths = ", ".join(partner.get("complementary_strengths", []))
                    opportunity_info.append(f"- Partner with {partner.get('potential_partner', 'Unknown')} " + 
                                    f"(Complementary strengths: {strengths})")
    
            if opportunities.get("market_expansion_opportunities"):
                opportunity_info.append("\nMarket Expansion Opportunities:")
                for market in opportunities["market_expansion_opportunities"][:3]:  # Top 3
                    strengths = ", ".join(market.get("relevant_strengths", []))
                    opportunity_info.append(f"- Expand to {market.get('potential_market', 'Unknown')} " + 
                                    f"(Relevant strengths: {strengths})")

        # Get competitor information (new addition)
        competitor_info = []
        try:
            competitor_query = """
            MATCH (e:Entity {name: $entity_name})-[r:COMPETES_WITH]->(c:Entity)
            RETURN c.name as name, c.industry as industry, r.intensity as intensity, 
                r.overlap_areas as overlap_areas
            """
            competitors = self.neo4j_manager.execute_query(competitor_query, {"entity_name": entity_name})
            if competitors:
                opportunity_info.append("\nCompetitive Landscape:")
                for competitor in competitors:
                    opportunity_info.append(f"- Competitor: {competitor.get('name', 'Unknown')} " +
                                    f"(Industry: {competitor.get('industry', 'N/A')}, " +
                                    f"Intensity: {competitor.get('intensity', 'N/A')}, " +
                                    f"Overlap: {competitor.get('overlap_areas', 'N/A')})")
        except Exception as e:
            logger.warning(f"Error retrieving competitors: {e}")

        # Combine all information for the prompt
        entity_info_text = "\n".join(entity_info)
        risk_info_text = "\n".join(risk_info)
        opportunity_info_text = "\n".join(opportunity_info)

        # Build the enhanced LLM prompt with clearer strategic focus
        prompt = f"""
        You are a world-class business strategist with decades of experience advising Fortune 500 companies.
        Your task is to develop innovative yet practical strategic recommendations for {entity_name}.

        Analyze the following detailed information about {entity_name} and create 3-5 highly specific, 
        data-driven strategic recommendations that address the identified risks and leverage opportunities.

        IMPORTANT GUIDELINES FOR STRATEGY DEVELOPMENT:

        1. Each strategy must be directly linked to the entity's specific situation, NOT generic advice
        2. Focus on distinctive, competitive advantage-building strategies rather than obvious solutions
        3. Balance short-term risk mitigation with long-term growth opportunities
        4. Ensure recommendations are concrete and actionable, not vague or theoretical
        5. Consider potential implementation challenges and address them in your recommendations

        For each strategy recommendation:
        1. Provide a clear, specific action title (max 10 words)
        2. Explain the strategic rationale with direct references to the entity's data (2-3 sentences)
        3. Include expected outcomes with quantifiable metrics where possible (2-3 points)
        4. Outline 3-5 specific implementation steps that are practical and achievable
        5. Specify 2-3 key performance indicators to measure success
        6. Set a realistic timeline (short: 0-6 months, medium: 6-18 months, long: 18+ months)
        7. Assign an appropriate priority level (high/medium/low) based on impact and urgency

        Entity Information:
        {entity_info_text}

        Risk Assessment:
        {risk_info_text}

        Strategic Opportunities:
        {opportunity_info_text}

        Return your analysis as a JSON array with the following structure for each recommendation:
        [
            {{
                "title": "Specific recommendation title",
                "rationale": "Detailed reasoning directly referencing entity data",
                "benefits": ["Quantifiable benefit 1", "Quantifiable benefit 2"],
                "implementation_steps": ["Specific step 1", "Specific step 2", "Specific step 3"],
                "kpis": ["Specific KPI 1", "Specific KPI 2"],
                "timeline": "short|medium|long",
                "priority": "high|medium|low"
            }},
            ...
        ]

        Focus on creating strategies that are innovative, specific to this entity's unique situation, and deliver significant competitive advantage.
        ONLY return the JSON array of recommendations and nothing else.
        """

        # Call the LLM
        try:
            logger.info("Calling LLM for strategy generation")
            response = requests.post(
                self.model_config['endpoint'],
                json={
                    "model": self.model_config['name'],
                    "prompt": prompt,
                    "stream": False,
                    "temperature": 0.2,  # Lower temperature for more focused output
                    "top_p": 0.85,
                    "max_tokens": 2048  # Increased for more detailed strategies
                }
            )
    
            result = response.json()
            content = result.get('response', '')
    
            # Extract the JSON object from response
            start_idx = content.find('[')
            end_idx = content.rfind(']') + 1
    
            if start_idx >= 0 and end_idx > start_idx:
                json_str = content[start_idx:end_idx]
                strategies = json.loads(json_str)
                logger.info(f"Generated {len(strategies)} strategy recommendations")
                return strategies
            else:
                logger.warning("Could not extract JSON from LLM response")
                # Try a more aggressive JSON extraction
                import re
                json_match = re.search(r'\[\s*\{.*\}\s*\]', content, re.DOTALL)
                if json_match:
                    try:
                        strategies = json.loads(json_match.group(0))
                        logger.info(f"Generated {len(strategies)} strategy recommendations using regex extraction")
                        return strategies
                    except json.JSONDecodeError:
                        pass
            
                return self._generate_fallback_strategies(entity_name, risk_data)
        
        except Exception as e:
            logger.error(f"Error in LLM strategy generation: {e}")
            return self._generate_fallback_strategies(entity_name, risk_data)
    
    def _generate_fallback_strategies(self, entity_name: str, risk_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate fallback strategies when LLM fails with improved specificity.
    
        Args:
            entity_name: Name of the entity
            risk_data: Risk analysis results
        
        Returns:
            list: Basic strategy recommendations
        """
        logger.info("Using fallback strategy generation")
    
        # Create basic recommendations based on risk types
        strategies = []
    
        # Get risk categories
        risk_categories = risk_data.get("categories", {})
    
        # Financial risk strategies
        if risk_categories.get("financial") in ["Medium", "High"]:
            strategies.append({
                "title": "Optimize Capital Allocation Framework",
                "rationale": f"Address {entity_name}'s financial vulnerabilities by implementing a structured capital allocation framework that prioritizes investments based on risk-adjusted returns and strategic alignment.",
                "benefits": [
                    "15-20% improvement in return on invested capital",
                    "Enhanced financial flexibility during market disruptions",
                    "30% reduction in cost of capital through optimized funding sources"
                ],
                "implementation_steps": [
                    "Conduct ROI analysis of all current projects and initiatives",
                    "Develop tiered investment criteria based on risk profiles",
                    "Implement quarterly portfolio review process with clear KPIs",
                    "Establish centralized capital allocation committee with cross-functional representation"
                ],
                "kpis": [
                    "Risk-adjusted return on invested capital",
                    "Free cash flow conversion rate",
                    "Funding source diversification index"
                ],
                "timeline": "short",
                "priority": "high" if risk_categories.get("financial") == "High" else "medium"
            })
    
        # Operational risk strategies
        if risk_categories.get("operational") in ["Medium", "High"]:
            strategies.append({
                "title": "Implement Digital Process Twin Architecture",
                "rationale": f"Transform {entity_name}'s operational resilience by creating digital twins of critical business processes, enabling real-time monitoring, simulation, and proactive intervention.",
                "benefits": [
                    "40% reduction in process disruptions",
                    "25% improvement in resource utilization efficiency",
                    "60% faster response to operational anomalies"
                ],
                "implementation_steps": [
                    "Map and prioritize critical business processes based on risk impact",
                    "Develop digital twin models for top 3 high-risk processes",
                    "Deploy IoT sensors and real-time monitoring dashboards",
                    "Implement predictive analytics for early warning detection",
                    "Train cross-functional teams on intervention protocols"
                ],
                "kpis": [
                    "Mean time between process failures",
                    "Process variance reduction percentage",
                    "Predictive alert accuracy rate"
                ],
                "timeline": "medium",
                "priority": "high" if risk_categories.get("operational") == "High" else "medium"
            })
    
        # Market risk strategies
        if risk_categories.get("market") in ["Medium", "High"]:
            strategies.append({
                "title": "Develop Category Disruption Playbook",
                "rationale": f"Position {entity_name} to proactively shape market evolution rather than react to it by creating systematic approaches to identify and execute category-redefining innovations.",
                "benefits": [
                    "Capture 15-20% market share in emerging segments",
                    "Establish thought leadership position in 2-3 strategic areas",
                    "Create 30% premium pricing power through differentiation"
                ],
                "implementation_steps": [
                    "Conduct customer pain point ethnographic research",
                    "Establish cross-industry innovation scanning mechanism",
                    "Develop rapid prototyping and minimal viable product framework",
                    "Create category management and development roadmaps",
                    "Implement 90-day market experimentation cycles"
                ],
                "kpis": [
                    "First-mover advantage capture rate",
                    "Customer problem resolution score",
                    "New category revenue percentage"
                ],
                "timeline": "long",
                "priority": "high" if risk_categories.get("market") == "High" else "medium"
            })
    
        # Add a general strategy if we have fewer than 3
        if len(strategies) < 3:
            strategies.append({
                "title": "Establish Strategic Foresight System",
                "rationale": f"Enable {entity_name} to systematically identify emerging opportunities and threats through an integrated approach to environmental scanning, scenario planning, and strategic option development.",
                "benefits": [
                    "50% improvement in strategic decision speed and quality",
                    "Early identification of 80% of significant market shifts",
                    "25% increase in successful new initiative launches"
                ],
                "implementation_steps": [
                    "Deploy AI-powered competitive and market intelligence platform",
                    "Develop quarterly scenario planning process with key stakeholders",
                    "Create strategy option portfolio with pre-defined trigger conditions",
                    "Implement strategy sprint methodology for rapid adaptation",
                    "Train leadership in strategic agility principles"
                ],
                "kpis": [
                    "Strategic opportunity capitalization rate",
                    "Scenario planning accuracy index",
                    "Decision cycle time reduction"
                ],
                "timeline": "medium",
                "priority": "medium"
            })
    
        return strategies
    
    def _prepare_visualization_data(self, entity_name: str, strategies: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Prepare data for strategy visualizations.
        
        Args:
            entity_name: Name of the entity
            strategies: Generated strategy recommendations
            
        Returns:
            dict: Visualization data for charts and graphs
        """
        logger.info("Preparing visualization data for strategies")
        
        # Create visualization data structure
        visualization_data = {
            "strategy_prioritization": {
                "type": "bubble_chart",
                "description": "Strategy prioritization by impact, effort, and priority",
                "data": []
            },
            "implementation_timeline": {
                "type": "gantt_chart",
                "description": "Implementation timeline for recommended strategies",
                "data": []
            },
            "risk_mitigation_impact": {
                "type": "radar_chart",
                "description": "Expected risk reduction by category",
                "categories": ["Financial", "Operational", "Market", "Reputational", "Legal"],
                "datasets": []
            },
            "financial_impact": {
                "type": "bar_chart",
                "description": "Projected financial impact of strategies",
                "labels": [],
                "datasets": [
                    {
                        "label": "Revenue Impact (%)",
                        "data": []
                    },
                    {
                        "label": "Cost Savings (%)",
                        "data": []
                    }
                ]
            }
        }
        
        # Map timeline to numeric values for sorting and visualization
        timeline_map = {"short": 1, "medium": 2, "long": 3}
        
        # Map priority to impact/effort values for bubble chart
        priority_size_map = {"high": 50, "medium": 30, "low": 20}
        
        # Generate start/end dates for Gantt chart
        current_date = datetime.now()
        timeline_duration_map = {
            "short": 90,  # 3 months
            "medium": 180,  # 6 months
            "long": 365    # 12 months
        }
        
        # Current position for timeline layout
        current_position = 0
        
        # Populate visualization data from strategies
        for i, strategy in enumerate(strategies):
            # Strategy title for labels
            title = strategy["title"]
            priority = strategy.get("priority", "medium")
            timeline = strategy.get("timeline", "medium")
            
            # Add to bubble chart (priority matrix)
            # Use random-ish but consistent values for impact/effort based on priority
            impact = 0.5 + (0.4 * (i % 3) / 2.0)  # 0.5-0.9 range
            effort = 0.3 + (0.6 * ((i+1) % 3) / 2.0)  # 0.3-0.9 range
            
            # Adjust based on priority
            if priority == "high":
                impact += 0.1
            elif priority == "low":
                impact -= 0.1
                
            visualization_data["strategy_prioritization"]["data"].append({
                "title": title,
                "impact": min(0.95, max(0.05, impact)),  # Keep in 0.05-0.95 range
                "effort": min(0.95, max(0.05, effort)),  # Keep in 0.05-0.95 range
                "priority": priority,
                "size": priority_size_map.get(priority, 30)
            })
            
            # Add to implementation timeline (Gantt chart)
            duration = timeline_duration_map.get(timeline, 180)
            start_days = current_position
            end_days = current_position + duration
            
            visualization_data["implementation_timeline"]["data"].append({
                "title": title,
                "start_days": start_days,
                "end_days": end_days,
                "priority": priority,
                "group": i // 2  # Group related strategies together
            })
            
            # Increment position for next strategy with some overlap
            current_position += max(30, duration // 2)
            
            # Add to risk mitigation impact (radar chart)
            # Generate plausible impact values for different risk categories
            if "risk_mitigation_impact" not in visualization_data:
                visualization_data["risk_mitigation_impact"] = {
                    "categories": ["Financial", "Operational", "Market", "Reputational", "Legal"],
                    "datasets": []
                }
            
            # Create somewhat realistic impact values based on strategy focus
            impact_values = [0.1, 0.1, 0.1, 0.1, 0.1]  # Base impact
            
            # Increase impact for relevant categories based on strategy title and rationale
            title_lower = title.lower()
            rationale_lower = strategy.get("rationale", "").lower()
            
            if any(term in title_lower or term in rationale_lower 
                   for term in ["financ", "cash", "revenue", "cost", "profit"]):
                impact_values[0] += 0.3  # Financial
                
            if any(term in title_lower or term in rationale_lower 
                   for term in ["operat", "process", "efficien", "product"]):
                impact_values[1] += 0.3  # Operational
                
            if any(term in title_lower or term in rationale_lower 
                   for term in ["market", "customer", "compet", "sales"]):
                impact_values[2] += 0.3  # Market
                
            if any(term in title_lower or term in rationale_lower 
                   for term in ["brand", "reputat", "public", "customer"]):
                impact_values[3] += 0.2  # Reputational
                
            if any(term in title_lower or term in rationale_lower 
                   for term in ["regulat", "compliance", "legal", "risk"]):
                impact_values[4] += 0.2  # Legal
            
            # Add some variation
            impact_values = [min(0.8, max(0.1, val + (0.1 * (i % 3) - 0.1))) for val in impact_values]
            
            visualization_data["risk_mitigation_impact"]["datasets"].append({
                "label": title,
                "data": impact_values
            })
            
            # Add to financial impact chart
            visualization_data["financial_impact"]["labels"].append(title)
            
            # Generate plausible financial impact values
            revenue_impact = 0.02  # Base 2%
            cost_savings = 0.01   # Base 1%
            
            # Adjust based on priority and timeline
            if priority == "high":
                revenue_impact += 0.03
                cost_savings += 0.02
            
            if timeline == "long":
                revenue_impact += 0.02
                cost_savings += 0.02
            
            # Add some variation
            revenue_impact += (0.01 * (i % 3))
            cost_savings += (0.01 * ((i+1) % 3))
            
            visualization_data["financial_impact"]["datasets"][0]["data"].append(
                round(revenue_impact * 100, 1)  # Convert to percentage
            )
            visualization_data["financial_impact"]["datasets"][1]["data"].append(
                round(cost_savings * 100, 1)  # Convert to percentage
            )
        
        return visualization_data
    
    def generate_comprehensive_report(self, entity_name: str) -> Dict[str, Any]:
        """
        Generate a comprehensive strategy report with visualizations.
        
        Args:
            entity_name: Name of the entity to analyze
            
        Returns:
            dict: Complete report data
        """
        # Generate strategies first
        strategies = self.generate_for_entity(entity_name)
        
        # If there was an error, return it
        if "error" in strategies:
            return strategies
        
        # Get additional context for the report
        entity_graph = self.graph_query.export_graph_segment(entity_name, 2)
        
        # Prepare the report structure
        report = {
            "entity": entity_name,
            "generation_date": datetime.now().isoformat(),
            "executive_summary": self._generate_executive_summary(entity_name, strategies),
            "strategies": strategies.get("strategies", []),
            "risk_assessment": strategies.get("risk_summary", {}),
            "visualizations": strategies.get("visualization_data", {}),
            "opportunities": strategies.get("strategic_opportunities", {}),
            "supporting_data": {
                "entity_graph": entity_graph,
                "market_context": self._get_market_context(entity_name)
            }
        }
        
        # Save the report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"report_{entity_name.replace(' ', '_')}_{timestamp}.json"
        report_path = os.path.join(self.output_dir, report_filename)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Comprehensive report saved to: {report_path}")
        
        return report
    
    def _generate_executive_summary(self, entity_name: str, strategies: Dict[str, Any]) -> str:
        """
        Generate an executive summary for the report.
        
        Args:
            entity_name: Name of the entity
            strategies: Strategy data
            
        Returns:
            str: Executive summary text
        """
        # We could use LLM for this, but for simplicity, we'll generate a basic summary
        strategy_count = len(strategies.get("strategies", []))
        high_priority = sum(1 for s in strategies.get("strategies", []) 
                          if s.get("priority") == "high")
        
        risk_levels = strategies.get("risk_summary", {})
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
    
    def _get_market_context(self, entity_name: str) -> Dict[str, Any]:
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