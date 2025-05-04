# analysis/risk_engine.py
import json
from typing import Any, Dict
import requests
import logging
from config import MODELS, RISK_THRESHOLDS

class RiskAnalyzer:
    """Analyzes knowledge graph to determine business risks."""
    
    def __init__(self, neo4j_manager):
        self.kg_manager = neo4j_manager
        self.logger = logging.getLogger(__name__)
        self.risk_scores = {
            'financial': 0.0,
            'operational': 0.0,
            'market': 0.0,
            'overall': 0.0
        }
    
    def _get_graph_summary(self):
        """Extract a summary of the knowledge graph for LLM analysis."""
        # Get key financial indicators
        financial_risks = self.kg_manager.run_risk_query("financial")
        
        # Get operational risks
        operational_risks = self.kg_manager.run_risk_query("operational")
        
        # Get market risks
        market_risks = self.kg_manager.run_risk_query("market")
        
        # Get central entities (most connected nodes)
        with self.kg_manager.driver.session() as session:
            central_entities = session.run("""
                MATCH (e:Entity)
                WITH e, COUNT {(e)--()} AS connections
                ORDER BY connections DESC
                LIMIT 10
                RETURN e.name AS entity, connections
            """)
            central_entities = [record.data() for record in central_entities]
        
        # Prepare a text summary for the LLM
        summary = []
        
        # Add central entities
        summary.append("Key entities in the business:")
        for entity in central_entities:
            summary.append(f"- {entity['entity']} (connections: {entity['connections']})")
        
        # Add financial risks
        if financial_risks:
            summary.append("\nFinancial risk indicators:")
            for risk in financial_risks:
                summary.append(f"- {risk['entity']} has {risk['metric'].lower().replace('_', ' ')} " 
                              f"of {risk['value']} (risk count: {risk['risk_count']})")
        
        # Add operational risks
        if operational_risks:
            summary.append("\nOperational risk indicators:")
            for risk in operational_risks:
                summary.append(f"- {risk['entity']} has process {risk['process']} " 
                              f"with issue: {risk['issue']} (risk count: {risk['risk_count']})")
        
        # Add market risks
        if market_risks:
            summary.append("\nMarket risk indicators:")
            for risk in market_risks:
                summary.append(f"- {risk['entity']} operates in {risk['market']} " 
                              f"which shows trend: {risk['trend']} (risk count: {risk['risk_count']})")
        
        return "\n".join(summary)
    
    def _use_llm_for_risk_analysis(self):
        """Use LLM to analyze the graph for risks."""
        model_config = MODELS['reasoning']
    
        # Get graph summary for LLM
        graph_summary = self._get_graph_summary()
    
        prompt = f"""
        You are a business risk analysis expert. Analyze the following business data 
        represented as a knowledge graph summary.
    
        Based on these relationships, assess the risk levels in these categories:
        1. Financial Risk - Issues related to revenue, profit, budget, cash flow, etc.
        2. Operational Risk - Issues related to processes, staff, equipment, supply chain, etc.
        3. Market Risk - Issues related to competition, market trends, customer demand, etc.
        4. Overall Risk - A comprehensive assessment considering all factors.
    
        Knowledge Graph Summary:
        {graph_summary}
    
        Return your analysis as a JSON object with scores between 0.0 (no risk) and 1.0 (extreme risk):
        {{
            "financial": 0.0,
            "operational": 0.0,
            "market": 0.0,
            "overall": 0.0,
            "reasoning": "Your detailed explanation here"
        }}
    
        ONLY return the JSON object and nothing else.
        """
    
        # Call the LLM
        try:
            self.logger.info("Calling LLM for risk analysis")
            response = requests.post(
                model_config['endpoint'],
                json={
                    "model": model_config['name'],
                    "prompt": prompt,
                    "stream": False,
                    **model_config['parameters']
                }
            )
        
            result = response.json()
            content = result.get('response', '')
        
            # Find the JSON object in the response
            start_idx = content.find('{')
            end_idx = content.rfind('}') + 1
        
            if start_idx >= 0 and end_idx > start_idx:
                json_str = content[start_idx:end_idx]
                risk_data = json.loads(json_str)
            
                # Add detailed logging to understand risk values
                self.logger.info(f"Raw risk data from LLM: {risk_data}")
                # Log all risk values explicitly
                self.logger.info(f"Financial risk: {risk_data.get('financial', 'not set')}")
                self.logger.info(f"Operational risk: {risk_data.get('operational', 'not set')}")
                self.logger.info(f"Market risk: {risk_data.get('market', 'not set')}")
                self.logger.info(f"Overall risk: {risk_data.get('overall', 'not set')}")
            
                self.logger.info("Successfully parsed LLM risk analysis")
                return risk_data
            else:
                self.logger.warning("Could not extract JSON from LLM response")
                # Fallback to rule-based calculation
                return self._calculate_rule_based_risk()
            
        except Exception as e:
            self.logger.error(f"Error in LLM risk analysis: {e}")
            # Fallback to rule-based analysis
            return self._calculate_rule_based_risk()
        
        
    
    def _calculate_rule_based_risk(self):
        """Calculate risk scores based on graph metrics as fallback with improved error handling."""
        try:
            # Initialize default risk values (medium-low instead of low)
            financial_risk = 0.4
            operational_risk = 0.5
            market_risk = 0.45
        
            with self.kg_manager.driver.session() as session:
                # Financial risk based on entities with financial risk type
                try:
                    financial_result = session.run("""
                        MATCH (e:Entity)-[:HAS_RISK]->(r:Risk)
                        WHERE r.type = 'financial'
                        WITH AVG(r.level) as avg_risk_level
                        RETURN 
                            CASE WHEN avg_risk_level IS NOT NULL 
                            THEN avg_risk_level
                            ELSE 0.4 END AS risk_score
                    """)
                    financial_record = financial_result.single()
                    if financial_record:
                        financial_risk = financial_record["risk_score"]
                except Exception as e:
                    self.logger.warning(f"Error calculating financial risk: {e}")
        
                # Operational risk based on operational risk entities
                try:
                    operational_result = session.run("""
                        MATCH (e:Entity)-[:HAS_RISK]->(r:Risk)
                        WHERE r.type = 'operational'
                        WITH AVG(r.level) as avg_risk_level
                        RETURN 
                            CASE WHEN avg_risk_level IS NOT NULL 
                            THEN avg_risk_level
                            ELSE 0.5 END AS risk_score
                    """)
                    operational_record = operational_result.single()
                    if operational_record:
                        operational_risk = operational_record["risk_score"]
                except Exception as e:
                    self.logger.warning(f"Error calculating operational risk: {e}")
        
                # Market risk based on market risk entities and trends
                try:
                    market_result = session.run("""
                        MATCH (e:Entity)-[:HAS_RISK]->(r:Risk)
                        WHERE r.type = 'market'
                        WITH AVG(r.level) as avg_risk_level
                        RETURN 
                            CASE WHEN avg_risk_level IS NOT NULL 
                            THEN avg_risk_level
                            ELSE 0.45 END AS risk_score
                    """)
                    market_record = market_result.single()
                    if market_record:
                        market_risk = market_record["risk_score"]
                except Exception as e:
                    self.logger.warning(f"Error calculating market risk: {e}")
        
            # Calculate overall risk (weighted average)
            overall_risk = (financial_risk * 0.4 + operational_risk * 0.3 + market_risk * 0.3)
        
            # Ensure all values are between 0 and 1
            financial_risk = min(max(financial_risk, 0.0), 1.0)
            operational_risk = min(max(operational_risk, 0.0), 1.0) 
            market_risk = min(max(market_risk, 0.0), 1.0)
            overall_risk = min(max(overall_risk, 0.0), 1.0)
        
            return {
                "financial": financial_risk,
                "operational": operational_risk,
                "market": market_risk,
                "overall": overall_risk,
                "reasoning": "Risk calculated based on explicit risk nodes and relationships in the knowledge graph."
            }
        except Exception as e:
            self.logger.error(f"Error in rule-based risk calculation: {e}")
            # Return medium risk as fallback
            return {
                "financial": 0.4,    # Medium-low
                "operational": 0.5,  # Medium
                "market": 0.45,      # Medium
                "overall": 0.45,     # Medium
                "reasoning": "Risk calculated using fallback values due to data retrieval issues."
            }
    
    def analyze(self):
        """Run complete risk analysis with support for the 30 group assessment structure."""
        # Try to get assessment data from Neo4j
        try:
            assessment_query = """
            MATCH (e:Entity)-[:HAS_ASSESSMENT]->(a)
            RETURN e.name as entity, a.name as assessment_name, a.risk_score as risk_score
            """
        
            assessment_data = self.kg_manager.execute_query(assessment_query)
        
            if assessment_data and len(assessment_data) > 0:
                # If we have assessment data, use that for risk analysis
                self.logger.info("Using assessment data for risk analysis")
            
                # Group assessment data
                groups = {}
                for item in assessment_data:
                    entity = item.get("entity")
                    assessment = item.get("assessment_name")
                    risk_score = item.get("risk_score", 0.5)
                
                    if entity not in groups:
                        groups[entity] = {}
                
                    groups[entity][assessment] = risk_score
            
                # Process the data
                if groups:
                    # Just use first entity for now
                    entity = list(groups.keys())[0]
                
                    # Calculate risk categories
                    financial_scores = []
                    operational_scores = []
                    market_scores = []
                
                    for assessment, score in groups[entity].items():
                        # Financial categories
                        if any(term in assessment.lower() for term in ["revenue", "income", "cash", "margin", "finance"]):
                            financial_scores.append(float(score))
                    
                        # Operational categories
                        elif any(term in assessment.lower() for term in ["time", "employee", "inventory", "delivery", "yield", "cycle", "operation"]):
                            operational_scores.append(float(score))
                    
                        # Market categories
                        elif any(term in assessment.lower() for term in ["market", "competitive", "annual", "customer", "design", "sales"]):
                            market_scores.append(float(score))
                
                    # Calculate average scores
                    risk_scores = {
                        'financial': sum(financial_scores) / max(1, len(financial_scores)),
                        'operational': sum(operational_scores) / max(1, len(operational_scores)),
                        'market': sum(market_scores) / max(1, len(market_scores))
                    }
                
                    # Calculate overall risk
                    risk_scores['overall'] = (
                        risk_scores['financial'] * 0.4 + 
                        risk_scores['operational'] * 0.3 + 
                        risk_scores['market'] * 0.3
                    )
                
                    # Determine risk categories based on thresholds
                    risk_categories = {}
                    for category, score in risk_scores.items():
                        thresholds = RISK_THRESHOLDS.get(category, RISK_THRESHOLDS.get('financial'))
                    
                        if score <= thresholds['low']:
                            risk_categories[category] = 'Low'
                        elif score <= thresholds['medium']:
                            risk_categories[category] = 'Medium'
                        else:
                            risk_categories[category] = 'High'
                
                    # Add reasoning
                    risk_categories['reasoning'] = "Risk calculated based on assessment group scores across the 30 evaluation areas."
                
                    return {
                        'scores': risk_scores,
                        'categories': risk_categories,
                        'reasoning': risk_categories['reasoning']
                    }
        except Exception as e:
            self.logger.warning(f"Error processing assessment data: {e}")
    
        # Use LLM for comprehensive analysis as fallback
        self.logger.info("Using LLM for risk analysis (fallback)")
        risk_data = self._use_llm_for_risk_analysis()
    
        # Determine risk categories based on thresholds
        risk_categories = {}
        for category, score in risk_data.items():
            if category == 'reasoning':
                risk_categories['reasoning'] = score
                continue
            
            thresholds = RISK_THRESHOLDS.get(category, RISK_THRESHOLDS.get('financial'))
        
            if score <= thresholds['low']:
                risk_categories[category] = 'Low'
            elif score <= thresholds['medium']:
                risk_categories[category] = 'Medium'
            else:
                risk_categories[category] = 'High'
    
        return {
            'scores': risk_data,
            'categories': risk_categories,
            'reasoning': risk_data.get('reasoning', '')
        }
        
    def analyze_assessment_data(self, assessment_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze assessment results from the 30 group structure.
    
        Args:
            assessment_results: Results from the strategy assessment
        
        Returns:
            dict: Risk analysis with categories and scores
        """
        # Initialize risk scores
        risk_scores = {
            'financial': 0.0,
            'operational': 0.0,
            'market': 0.0,
            'overall': 0.0
        }
    
        # Extract assessment groups
        groups = assessment_results.get("groups", {})
    
        # Process financial risk
        financial_groups = ["revenue_growth", "operating_income", "cash_flow", 
                        "gross_margin", "finance_metrics"]
        financial_scores = []
    
        for group_id in financial_groups:
            if group_id in groups:
                group_data = groups[group_id]
                # Convert score to risk (higher score = lower risk)
                risk_score = 1.0 - group_data.get("score", 0.5)
                financial_scores.append(risk_score)
    
        if financial_scores:
            risk_scores['financial'] = sum(financial_scores) / len(financial_scores)
    
        # Process operational risk
        operational_groups = ["time_to_hire", "employee_turnover", "employee_engagement",
                            "inventory_turnover", "on_time_delivery", "first_pass_yield",
                            "total_cycle_time", "operations_metrics"]
        operational_scores = []
    
        for group_id in operational_groups:
            if group_id in groups:
                group_data = groups[group_id]
                # Convert score to risk (higher score = lower risk)
                risk_score = 1.0 - group_data.get("score", 0.5)
                operational_scores.append(risk_score)
    
        if operational_scores:
            risk_scores['operational'] = sum(operational_scores) / len(operational_scores)
    
        # Process market risk
        market_groups = ["market_assessment", "competitive_assessment", 
                        "annual_recurring_revenue", "customer_acquisition_cost",
                        "design_win", "sales_opportunities", "sales_marketing_metrics"]
        market_scores = []
    
        for group_id in market_groups:
            if group_id in groups:
                group_data = groups[group_id]
                # Convert score to risk (higher score = lower risk)
                risk_score = 1.0 - group_data.get("score", 0.5)
                market_scores.append(risk_score)
    
        if market_scores:
            risk_scores['market'] = sum(market_scores) / len(market_scores)
    
        # Calculate overall risk (weighted average)
        risk_scores['overall'] = (
            risk_scores['financial'] * 0.4 + 
            risk_scores['operational'] * 0.3 + 
            risk_scores['market'] * 0.3
        )
    
        # Determine risk categories based on thresholds
        risk_categories = {}
        for category, score in risk_scores.items():
            thresholds = RISK_THRESHOLDS.get(category, RISK_THRESHOLDS.get('financial'))
        
            if score <= thresholds['low']:
                risk_categories[category] = 'Low'
            elif score <= thresholds['medium']:
                risk_categories[category] = 'Medium'
            else:
                risk_categories[category] = 'High'
    
        # Add reasoning
        risk_categories['reasoning'] = "Risk calculated based on assessment group scores across the 30 evaluation areas."
    
        return {
            'scores': risk_scores,
            'categories': risk_categories,
            'reasoning': risk_categories['reasoning']
        }