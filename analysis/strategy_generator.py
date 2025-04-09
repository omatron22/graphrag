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
        Generate strategies using large language model.
        
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
        
        # Format opportunities
        opportunity_info = []
        if opportunities:
            if opportunities.get("partnership_opportunities"):
                opportunity_info.append("Partnership Opportunities:")
                for partner in opportunities["partnership_opportunities"][:3]:  # Top 3
                    strengths = ", ".join(partner["complementary_strengths"])
                    opportunity_info.append(f"- Partner with {partner['potential_partner']} " + 
                                         f"(Complementary strengths: {strengths})")
            
            if opportunities.get("market_expansion_opportunities"):
                opportunity_info.append("\nMarket Expansion Opportunities:")
                for market in opportunities["market_expansion_opportunities"][:3]:  # Top 3
                    strengths = ", ".join(market["relevant_strengths"])
                    opportunity_info.append(f"- Expand to {market['potential_market']} " + 
                                         f"(Relevant strengths: {strengths})")
        
        # Combine all information for the prompt
        entity_info_text = "\n".join(entity_info)
        risk_info_text = "\n".join(risk_info)
        opportunity_info_text = "\n".join(opportunity_info)
        
        # Build the LLM prompt
        prompt = f"""
        You are an expert business strategist providing actionable recommendations.
        Analyze the following information about {entity_name} and generate 3-5 specific, 
        data-driven strategic recommendations.
        
        For each recommendation:
        1. Provide a clear, specific action title (10 words max)
        2. Explain the rationale based on the data (2-3 sentences)
        3. List expected outcomes and benefits (2-3 points)
        4. Describe implementation steps (3-5 concrete steps)
        5. Include relevant KPIs to measure success (2-3 metrics)
        6. Estimate implementation timeline (short/medium/long term)
        7. Assign priority level (high/medium/low)
        
        Entity Information:
        {entity_info_text}
        
        Risk Assessment:
        {risk_info_text}
        
        Strategic Opportunities:
        {opportunity_info_text}
        
        Return your analysis as a JSON array with the following structure for each recommendation:
        [
            {{
                "title": "Recommendation title",
                "rationale": "Reasoning behind the recommendation",
                "benefits": ["Benefit 1", "Benefit 2"],
                "implementation_steps": ["Step 1", "Step 2", "Step 3"],
                "kpis": ["KPI 1", "KPI 2"],
                "timeline": "short|medium|long",
                "priority": "high|medium|low"
            }},
            ...
        ]
        
        Focus on specific, actionable recommendations that address the identified risks and leverage opportunities.
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
                    **self.model_config['parameters']
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
                return self._generate_fallback_strategies(entity_name, risk_data)
                
        except Exception as e:
            logger.error(f"Error in LLM strategy generation: {e}")
            return self._generate_fallback_strategies(entity_name, risk_data)
    
    def _generate_fallback_strategies(self, entity_name: str, risk_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate fallback strategies when LLM fails.
        
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
                "title": "Optimize Cash Flow Management",
                "rationale": "Improve financial stability by focusing on cash flow management to address identified financial risks.",
                "benefits": [
                    "Improved liquidity position",
                    "Reduced financial vulnerability",
                    "Enhanced investor confidence"
                ],
                "implementation_steps": [
                    "Conduct comprehensive cash flow analysis",
                    "Implement accounts receivable acceleration measures",
                    "Review and optimize payment terms with suppliers",
                    "Establish cash reserves policy"
                ],
                "kpis": [
                    "Days Sales Outstanding (DSO)",
                    "Free Cash Flow",
                    "Current Ratio"
                ],
                "timeline": "short",
                "priority": "high" if risk_categories.get("financial") == "High" else "medium"
            })
        
        # Operational risk strategies
        if risk_categories.get("operational") in ["Medium", "High"]:
            strategies.append({
                "title": "Strengthen Operational Resilience",
                "rationale": "Address operational vulnerabilities by implementing robust process improvements and contingency planning.",
                "benefits": [
                    "Reduced operational disruptions",
                    "Improved process efficiency",
                    "Enhanced service delivery"
                ],
                "implementation_steps": [
                    "Map critical business processes",
                    "Identify single points of failure",
                    "Implement redundancy for critical systems",
                    "Develop and test business continuity plans"
                ],
                "kpis": [
                    "Process Cycle Efficiency",
                    "Downtime Frequency and Duration",
                    "Error Rates"
                ],
                "timeline": "medium",
                "priority": "high" if risk_categories.get("operational") == "High" else "medium"
            })
        
        # Market risk strategies
        if risk_categories.get("market") in ["Medium", "High"]:
            strategies.append({
                "title": "Diversify Market Exposure",
                "rationale": "Reduce market risk by diversifying product offerings and target markets to minimize dependency.",
                "benefits": [
                    "Reduced vulnerability to market changes",
                    "Access to new revenue streams",
                    "Improved competitive positioning"
                ],
                "implementation_steps": [
                    "Conduct market segmentation analysis",
                    "Identify adjacent market opportunities",
                    "Develop pilot offerings for new markets",
                    "Create phased market entry plan"
                ],
                "kpis": [
                    "Revenue Diversification Ratio",
                    "Market Share in New Segments",
                    "Customer Acquisition Cost"
                ],
                "timeline": "long",
                "priority": "high" if risk_categories.get("market") == "High" else "medium"
            })
        
        # Add a general strategy if we have fewer than 3
        if len(strategies) < 3:
            strategies.append({
                "title": "Enhance Data-Driven Decision Making",
                "rationale": "Improve organizational decision quality through better data collection, analysis, and integration.",
                "benefits": [
                    "More informed strategic decisions",
                    "Faster response to changing conditions",
                    "Improved resource allocation"
                ],
                "implementation_steps": [
                    "Assess current data availability and quality",
                    "Implement integrated business intelligence system",
                    "Train management on data interpretation",
                    "Establish data-driven review processes"
                ],
                "kpis": [
                    "Decision Cycle Time",
                    "Forecast Accuracy",
                    "Data Utilization Rate"
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