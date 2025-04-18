# analysis/risk_engine.py
import json
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
        """Calculate risk scores based on graph metrics as fallback."""
        # Simple rule-based risk calculation from graph metrics
        with self.kg_manager.driver.session() as session:
            # Financial risk based on negative financial indicators
            financial_result = session.run("""
                MATCH (e:Entity)-[:HAS_REVENUE|HAS_PROFIT|HAS_CASH_FLOW]->(v)
                WHERE exists((v)<-[:DECREASED|DECLINED]-())
                WITH count(*) AS negative_indicators
                
                MATCH (e:Entity)-[:HAS_REVENUE|HAS_PROFIT|HAS_CASH_FLOW]->()
                WITH negative_indicators, count(*) AS total_indicators
                
                RETURN 
                    CASE WHEN total_indicators > 0 
                    THEN toFloat(negative_indicators) / total_indicators 
                    ELSE 0.3 END AS risk_score
            """)
            financial_risk = financial_result.single()["risk_score"]
            
            # Operational risk based on process issues
            operational_result = session.run("""
                MATCH (e:Entity)-[:HAS_PROCESS|OPERATES]->()-[:HAS_ISSUE|PROBLEM]->()
                WITH count(*) AS process_issues
                
                MATCH (e:Entity)-[:HAS_PROCESS|OPERATES]->()
                WITH process_issues, count(*) AS total_processes
                
                RETURN 
                    CASE WHEN total_processes > 0 
                    THEN toFloat(process_issues) / total_processes * 0.8
                    ELSE 0.3 END AS risk_score
            """)
            operational_risk = operational_result.single()["risk_score"]
            
            # Market risk based on negative trends
            market_result = session.run("""
                MATCH (e:Entity)-[:COMPETES_IN|OPERATES_IN]->(m)
                MATCH (m)-[:HAS_TREND|SHOWS]->(t)
                WHERE t.name CONTAINS 'declin' OR t.name CONTAINS 'decrease'
                WITH count(*) AS negative_trends
                
                MATCH (e:Entity)-[:COMPETES_IN|OPERATES_IN]->()
                WITH negative_trends, count(*) AS total_markets
                
                RETURN 
                    CASE WHEN total_markets > 0 
                    THEN toFloat(negative_trends) / total_markets * 0.9
                    ELSE 0.3 END AS risk_score
            """)
            market_risk = market_result.single()["risk_score"]
        
        # Calculate overall risk (weighted average)
        overall_risk = (financial_risk * 0.4 + operational_risk * 0.3 + market_risk * 0.3)
        
        return {
            "financial": min(financial_risk, 1.0),
            "operational": min(operational_risk, 1.0),
            "market": min(market_risk, 1.0),
            "overall": min(overall_risk, 1.0),
            "reasoning": "Risk calculated using rule-based graph metrics."
        }
    
    def analyze(self):
        """Run complete risk analysis."""
        # Use LLM for comprehensive analysis
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