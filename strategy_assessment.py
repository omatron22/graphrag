# strategy_assessment.py
"""
Strategy Assessment Framework for business consulting system.
Implements structured assessment across business dimensions.
"""

import os
import logging
import json
from datetime import datetime
from typing import Dict, Any, List, Optional

# Set up logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class StrategyAssessment:
    """
    Implements the strategy assessment framework with all assessment groups.
    """
    
    def __init__(self, neo4j_manager, risk_analyzer=None, strategy_generator=None):
        """Initialize the strategy assessment framework."""
        self.neo4j_manager = neo4j_manager
        self.risk_analyzer = risk_analyzer
        self.strategy_generator = strategy_generator
        
        # Create output directory for assessment results
        self.output_dir = os.path.join("data", "knowledge_base", "assessments")
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Initialize assessment groups from paste.txt
        self.assessment_groups = self._initialize_assessment_groups()
        
        logger.info("Strategy Assessment Framework initialized")
    
    def _initialize_assessment_groups(self) -> Dict[str, Dict[str, Any]]:
        """
        Initialize the assessment groups structure based on paste.txt.
        
        Returns:
            dict: Assessment groups with their questions and metrics
        """
        groups = {
            "vision": {
                "name": "Vision",
                "description": "Assessment of company vision statement",
                "questions": [
                    "Is the Vision Statement Clear, concise, inspiring, future-focused, Ambitious and Achievable?"
                ]
            },
            "market": {
                "name": "Market Assessment",
                "description": "Assessment of market segments and value proposition",
                "questions": [
                    "Are the market segments you are participating in the most attractive segments?",
                    "Is your Value critical to the most attractive market segments?",
                    "Can you create a new market segment that could become the most attractive segment in the industry?",
                    "Can you disrupt the attractive market segments to increase your share in those segments or to drive market structure change in a segment or across multiple segments?",
                    "Are your Business Competencies a strong fit for the targetted markets?"
                ]
            },
            "strategic": {
                "name": "Strategic Assessment",
                "description": "Assessment of strategic positioning and opportunities",
                "questions": [
                    "Which Markets are most attractive?",
                    "Do you have a strong strategic position in the most attractive markets?",
                    "Do you have a leading Market Share in the most attractive markets? Can you further enhance your position within the overall ecosystem?",
                    "Are any of the lesser attractive markets likely to become more attractive in the next 3 to 5 years? Can you develop a leadership position in these markets?",
                    "Do you have a strong strategic position and leading market share in a lesser attractive market? Can you create a new ecosystem and architect its structure and operation?",
                    "Can you enhance your strategic position in the most attractive markets?",
                    "Can you create/develop a new market and establish a leading and defendable strategic position in this market?",
                    "Are there sub-segments within the overall market that could be more attractive than the markets you have currently selected?",
                    "What factors are a barrier to market growth and market size?",
                    "What factors are a barrier to enhancing your overall strategic position?",
                    "Can you increase the importance/weighting of your specific competencies in the overall ecosystem that drives your Business?",
                    "Have you demonstrated an ability to create/grow/develop a new or existing market? Can you/your team execute on a market growth strategy?",
                    "Have you demonstrated an ability to build a strong strategic position in a market? Can you/your team execute on a strategy to enhance the strategic position in a market?",
                    "What are the main bottlenecks to growth in your business?",
                    "What are the constraints that exist in your business that limit your ability to enhance your overall strategic position?",
                    "Can you influence/partner with key ecosystem partners to enhance your strategic position?",
                    "Do you have the Balance Sheet to execute on your desired strategy?"
                ]
            }
        }
        
        # Add other assessment groups based on paste.txt
        # Risk Assessment
        groups["risk"] = {
            "name": "Risk Assessment",
            "description": "Assessment of risk factors and mitigation strategies",
            "questions": [
                "Are any Risk Factors in the High Risk category",
                "Can you reduce or mitigate the probabilty of occurrence of any High Risk Factors",
                "Can you reduce or mitigate the impact of any High Risk Factors",
                "What is the overall Risk impact on the Strategy?",
                "Can you enhance your overall Strategic Position while maintaining or minimizing the overall Risk profile of the Business?",
                "Is the company leadership/Board/shareholder base generally open to more Risky Strategies?",
                "Is the Risk/Reward ratio favorable for any strategic shifts?"
            ]
        }
        
        # Competitive Assessment
        groups["competitive"] = {
            "name": "Competitive Assessment",
            "description": "Assessment of competitive advantages and positioning",
            "questions": [
                "Does your Product/Service/Business have a major competitive advantage on any parameter? Can you enhance the competitive advantage further?",
                "Does your Product/Service/Business have a major competitive disadvantage on any parameter? Can you improve the Competitive advantage?",
                "How does your position compare against each of the 3 major competitors?",
                "Which competitor has the best competitive position for each of the critical parameters?",
                "Does your current Strategy take into consideration your Competitive advantage and disadvantage?",
                "Are all the parameters of equal importance and value to the market? Can you make your competitive advantage the most important parameter for your market?",
                "Can you shape/architect the future competitive position in the markets you participate in?",
                "Is your view of your competitive position and your competitors position homest and realistic, upto date and unbiased?",
                "Can you innovate and/or create more value to drive greater competitive advantage?"
            ]
        }
        
        # Portfolio Assessment
        groups["portfolio"] = {
            "name": "Portfolio Assessment",
            "description": "Assessment of business portfolio balance and growth",
            "questions": [
                "Is the Portfolio Perfectly Balanced? - small embryonic and small emerging businesses, larger early growth, Larger mid growth and larger late growth, smaller mature business and smaller declining business.",
                "Is the largest business in its growth phase?",
                "Is the smallest business in its embryonic or emerging phase or in decline?",
                "What can be done to increase the size of your growth businesses?",
                "What can be done to ensure that your embryonic and emerging businesses become growth businesses",
                "Can you make your mature and declining businesses very profitable?",
                "Are your investments in line with your portfolio? Largest investments should be in your emerging, and growth businesses. The smallest investments should be in your embryonic and mature and declining businesses."
            ]
        }
        
        # Strengths Assessment
        groups["strengths"] = {
            "name": "Strengths Assessment",
            "description": "Assessment of business strengths and advantages",
            "questions": [
                "How much Value is there to each of your Strengths?",
                "Does your major strength give your business a significant competitive advantage",
                "Does your portfolio of Strengths enable significant competitive advantage?",
                "What can you do to increase the value of your strength and turn into greater competitive advantage?"
            ]
        }
        
        # Add financial, HR, operations, and S&M dashboard groups
        # Finance Dashboard
        groups["finance"] = {
            "name": "Finance Dashboard",
            "description": "Financial metrics and performance",
            "metrics": [
                "Revenue Growth",
                "Operating Income",
                "Cash Flow",
                "Gross Margin",
                "Finance Metrics"
            ],
            "questions": [
                "Has the Business grown revenues over the last few years?",
                "Are you forecasting revenue growth for the next few years?",
                "Has the last 2 years revenue growth been above market or below market?",
                "Does the strategy drive future revenue growth for the Business?",
                "Is the lack of revenue growth impacting the business profitabiltiy and what is the risk impact of this lack of growth?"
            ]
        }
        
        # HR Dashboard
        groups["hr"] = {
            "name": "HR Dashboard",
            "description": "Human resources metrics and performance",
            "metrics": [
                "Time to Hire",
                "Employee Turnover",
                "Employee Engagement",
                "Diversity",
                "HR Metrics"
            ],
            "questions": [
                "Is the Time to Hire critical resources an issue for the Business?",
                "Is the Time to Hire critical resources in the business competitive.",
                "Does the Strategy rely on hiring critical resources and if so can the time to hire critical resources be improved."
            ]
        }
        
        # Operations Dashboard
        groups["operations"] = {
            "name": "Operations Dashboard",
            "description": "Operational metrics and performance",
            "metrics": [
                "Inventory Turnover",
                "On Time Delivery",
                "First Pass Yield",
                "Total Cycle Time",
                "Operations Metrics"
            ],
            "questions": [
                "Is the Business Inventory Turnover competitive?",
                "Is Inventory Turnover trending positively?",
                "Does the Strategy drive improved inventory turonver for the business?"
            ]
        }
        
        # Sales & Marketing Dashboard
        groups["sales_marketing"] = {
            "name": "Sales & Marketing Dashboard",
            "description": "Sales and marketing metrics and performance",
            "metrics": [
                "Annual Recurring Revenue",
                "Customer Acquisition Cost",
                "Design Win",
                "Opportunities",
                "Sales & Marketing Metrics"
            ],
            "questions": [
                "Has the Business grown annual recurring revenues over the last few years?",
                "Are you forecasting annual recurring revenue growth for the next few years?",
                "Has the last 2 years annual recurring revenue growth been above market or below market?",
                "Does the strategy drive future annual recurring revenue growth for the Business?",
                "Is the lack of annual recurring revenue growth impacting the business profitabiltiy and what is the risk impact of this lack of growth?"
            ]
        }
        
        return groups
    
    def assess(self, entity_name: str, user_inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform a complete strategy assessment for an entity.
        
        Args:
            entity_name: Name of the entity to assess
            user_inputs: User provided risk tolerance, priorities, and constraints
            
        Returns:
            dict: Complete assessment results
        """
        logger.info(f"Starting strategy assessment for entity: {entity_name}")
        
        # Initialize assessment results
        assessment_results = {
            "entity": entity_name,
            "timestamp": datetime.now().isoformat(),
            "user_inputs": user_inputs,
            "groups": {},
            "summary": {},
            "recommendations": []
        }
        
        # Process user inputs
        risk_tolerance = user_inputs.get("risk_tolerance", "Medium")
        priorities = user_inputs.get("priorities", [])
        constraints = user_inputs.get("constraints", [])
        
        # Perform assessment for each group
        for group_id, group_data in self.assessment_groups.items():
            group_result = self._assess_group(entity_name, group_id, group_data, user_inputs)
            assessment_results["groups"][group_id] = group_result
        
        # Generate overall assessment summary
        assessment_results["summary"] = self._generate_assessment_summary(entity_name, assessment_results["groups"], user_inputs)
        
        # Generate strategic recommendations
        assessment_results["recommendations"] = self._generate_recommendations(entity_name, assessment_results["groups"], user_inputs)
        
        # Save assessment results
        self._save_assessment_results(entity_name, assessment_results)
        
        return assessment_results
    
    def _assess_group(self, entity_name: str, group_id: str, group_data: Dict[str, Any], user_inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess an entity for a specific group.
    
        Args:
            entity_name: Name of the entity
            group_id: ID of the assessment group
            group_data: Assessment group data and questions
            user_inputs: User provided inputs
        
        Returns:
            dict: Group assessment results
        """
        logger.info(f"Assessing {group_id} for entity: {entity_name}")
    
        # Initialize group result
        group_result = {
            "name": group_data.get("name", group_id.capitalize()),
            "description": group_data.get("description", ""),
            "questions": [],
            "findings": [],
            "score": 0,
            "risk_level": "Low"
        }
    
        # Process each question in the group
        for question in group_data.get("questions", []):
            # Use the knowledge graph to find relevant data
            relevant_data = self._find_relevant_data(entity_name, group_id, question)
        
            # Formulate answer using the data
            answer = self._formulate_answer(question, relevant_data, user_inputs)
        
            # Add to results
            group_result["questions"].append({
                "question": question,
                "answer": answer,
                "data": relevant_data
            })
    
        # For dashboard groups, calculate metrics
        if "metrics" in group_data:
            group_result["metrics"] = self._calculate_metrics(entity_name, group_id, group_data.get("metrics", []))
    
        # Special handling for risk group to extract detailed risk data
        if group_id == "risk":
            # Get detailed risk data from Neo4j with deduplication
            detailed_risks_query = """
            MATCH (e:Entity {name: $entity_name})-[:HAS_RISK]->(r:Risk)
            WITH DISTINCT r.type as risk_type, r.level as risk_level, r.description as description,
                r.impact_area as impact_area, r.probability as probability,
                r.mitigation_status as mitigation_status
            RETURN risk_type, risk_level, description, impact_area, probability, mitigation_status
            """
            detailed_risks = self.neo4j_manager.execute_query(
                detailed_risks_query, {"entity_name": entity_name}
            )
    
            # Add the detailed risks to the findings
            if detailed_risks:
                for risk in detailed_risks:
                    group_result["findings"].append({
                        "type": "risk",
                        "risk_type": risk.get("risk_type", "unknown"),
                        "level": risk.get("risk_level", 0.5),
                        "description": risk.get("description", ""),
                        "impact_area": risk.get("impact_area", ""),
                        "probability": risk.get("probability", ""),
                        "mitigation_status": risk.get("mitigation_status", "")
                    })
        else:
            # Generate key findings for non-risk groups
            group_result["findings"] = self._generate_group_findings(entity_name, group_id, group_result)
    
        # Calculate overall group score and risk level
        group_result["score"] = self._calculate_group_score(group_result)
        group_result["risk_level"] = self._determine_risk_level(group_result["score"], user_inputs.get("risk_tolerance", "Medium"))
    
        return group_result
    
    def _find_relevant_data(self, entity_name: str, group_id: str, question: str) -> List[Dict[str, Any]]:
        """
        Find relevant data from the knowledge graph for a specific question.
        
        Args:
            entity_name: Name of the entity
            group_id: ID of the assessment group
            question: Assessment question
            
        Returns:
            list: Relevant data for the question
        """
        # Parse the question to identify key concepts
        keywords = self._extract_keywords(question)
        
        # Query the knowledge graph for relevant data
        query = f"""
        MATCH (e:Entity {{name: $entity_name}})-[r]-(n)
        WHERE ANY(keyword IN $keywords WHERE 
            toLower(n.name) CONTAINS toLower(keyword) OR
            toLower(type(r)) CONTAINS toLower(keyword))
        RETURN n, type(r) as relationship_type, r
        LIMIT 20
        """
        
        results = self.neo4j_manager.execute_query(query, {
            "entity_name": entity_name,
            "keywords": keywords
        })
        
        return results
    
    def _extract_keywords(self, text: str) -> List[str]:
        """
        Extract relevant keywords from text.
        
        Args:
            text: Text to analyze
            
        Returns:
            list: Extracted keywords
        """
        # In a real implementation, this would use NLP techniques
        # For now, use a simple approach
        
        # Remove common words and punctuation
        common_words = ["the", "is", "and", "or", "to", "a", "in", "that", "it", "of", "you", "your", "can", "for", "on", "are", "have"]
        words = text.lower().replace("?", "").replace(".", "").replace(",", "").split()
        
        # Filter out common words and short words
        keywords = [word for word in words if word not in common_words and len(word) > 3]
        
        # Remove duplicates and return
        return list(set(keywords))
    
    def _formulate_answer(self, question: str, relevant_data: List[Dict[str, Any]], user_inputs: Dict[str, Any]) -> str:
        """
        Formulate an answer to an assessment question.
        
        Args:
            question: Assessment question
            relevant_data: Relevant data from knowledge graph
            user_inputs: User provided inputs
            
        Returns:
            str: Formulated answer
        """
        # In a real implementation, this would use an LLM to generate answers
        # For now, use a template-based approach
        
        if not relevant_data:
            return "Insufficient data to provide a detailed answer. Additional information needed."
        
        # Basic template-based response
        entity_names = set()
        relationship_types = set()
        
        for item in relevant_data:
            if "n" in item and "name" in item["n"]:
                entity_names.add(item["n"]["name"])
            if "relationship_type" in item:
                relationship_types.add(item["relationship_type"])
        
        # Create a simple answer based on the data
        entities_text = ", ".join(list(entity_names)[:3])
        relationships_text = ", ".join(list(relationship_types)[:3])
        
        answer = f"Based on the available data, we found relationships with {entities_text} "
        answer += f"through {relationships_text}. "
        
        # Add a conclusion based on the question type
        if "advantage" in question.lower():
            answer += "This suggests potential competitive advantages that can be leveraged."
        elif "growth" in question.lower():
            answer += "This indicates growth opportunities that align with the strategic direction."
        elif "risk" in question.lower():
            answer += "This highlights potential risk factors that should be monitored."
        else:
            answer += "Further analysis would provide more specific insights on this question."
        
        return answer
    
    def _calculate_metrics(self, entity_name: str, group_id: str, metrics: List[str]) -> Dict[str, Any]:
        """
        Calculate metrics for a dashboard group.
        
        Args:
            entity_name: Name of the entity
            group_id: ID of the assessment group
            metrics: List of metrics to calculate
            
        Returns:
            dict: Calculated metrics with values
        """
        metric_results = {}
        
        # Query the knowledge graph for metrics data
        query = f"""
        MATCH (e:Entity {{name: $entity_name}})-[:HAS_METRIC]->(m:Metric)
        WHERE m.name IN $metrics
        RETURN m.name as name, m.value as value, m.unit as unit, m.timestamp as timestamp
        """
        
        results = self.neo4j_manager.execute_query(query, {
            "entity_name": entity_name,
            "metrics": metrics
        })
        
        # Process results
        for metric in metrics:
            metric_data = next((r for r in results if r.get("name") == metric), None)
            
            if metric_data:
                metric_results[metric] = {
                    "value": metric_data.get("value"),
                    "unit": metric_data.get("unit", ""),
                    "timestamp": metric_data.get("timestamp", ""),
                    "trend": "stable"  # Would calculate trend in a real implementation
                }
            else:
                metric_results[metric] = {
                    "value": "No data",
                    "unit": "",
                    "timestamp": "",
                    "trend": "unknown"
                }
        
        return metric_results
    
    def _generate_group_findings(self, entity_name: str, group_id: str, group_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate key findings for an assessment group.
        
        Args:
            entity_name: Name of the entity
            group_id: ID of the assessment group
            group_result: Assessment results for the group
            
        Returns:
            list: Key findings with explanations
        """
        findings = []
        
        # Extract insights from answers
        for q_data in group_result.get("questions", []):
            question = q_data.get("question", "")
            answer = q_data.get("answer", "")
            
            # Look for significant insights in the answer
            if "suggests potential competitive advantages" in answer:
                findings.append({
                    "type": "strength",
                    "description": f"Potential competitive advantage identified relating to: {question}",
                    "importance": "high"
                })
            elif "indicates growth opportunities" in answer:
                findings.append({
                    "type": "opportunity",
                    "description": f"Growth opportunity identified relating to: {question}",
                    "importance": "medium"
                })
            elif "highlights potential risk factors" in answer:
                findings.append({
                    "type": "risk",
                    "description": f"Potential risk factor identified relating to: {question}",
                    "importance": "high"
                })
        
        # Add metric-based findings if available
        if "metrics" in group_result:
            for metric_name, metric_data in group_result["metrics"].items():
                if metric_data.get("trend") == "increasing":
                    findings.append({
                        "type": "positive_trend",
                        "description": f"{metric_name} is showing a positive trend",
                        "importance": "medium"
                    })
                elif metric_data.get("trend") == "decreasing":
                    findings.append({
                        "type": "negative_trend",
                        "description": f"{metric_name} is showing a negative trend",
                        "importance": "high"
                    })
        
        return findings
    
    def _calculate_group_score(self, group_result: Dict[str, Any]) -> float:
        """
        Calculate an overall score for an assessment group.
    
        Args:
            group_result: Assessment results for the group
        
        Returns:
            float: Score between 0.0 and 1.0
        """
        # In a real implementation, this would use more sophisticated scoring logic
        # For now, use a simple approach based on findings
    
        # Default score
        score = 0.5
    
        # Adjust based on findings
        finding_scores = {
            "strength": 0.1,
            "opportunity": 0.05,
            "risk": -0.05,  # Reduced from -0.1 to prevent scores from going too low
            "positive_trend": 0.05,
            "negative_trend": -0.05
        }
    
        for finding in group_result.get("findings", []):
            finding_type = finding.get("type", "")
            importance = finding.get("importance", "medium")
        
            # Apply importance multiplier
            multiplier = 1.0
            if importance == "high":
                multiplier = 1.5
            elif importance == "low":
                multiplier = 0.5
            
            # Add to score
            if finding_type in finding_scores:
                score += finding_scores[finding_type] * multiplier
    
        # Ensure score is between 0.1 and 1.0 (minimum 0.1 instead of 0.0)
        return max(0.1, min(1.0, score))
    
    def _determine_risk_level(self, score: float, risk_tolerance: str) -> str:
        """
        Determine risk level based on score and tolerance.
    
        Args:
            score: Group score between 0.0 and 1.0
            risk_tolerance: User's risk tolerance (Low, Medium, High)
        
        Returns:
            str: Risk level (Low, Medium, High)
        """
        # Adjust thresholds based on risk tolerance
        if risk_tolerance == "Low":
            # Conservative thresholds
            if score >= 0.7:
                return "Low"
            elif score >= 0.4:
                return "Medium"
            else:
                return "High"
        elif risk_tolerance == "High":
            # Aggressive thresholds (more lenient)
            if score >= 0.5:
                return "Low"
            elif score >= 0.25:
                return "Medium"
            else:
                return "High"
        else:
            # Medium tolerance (default)
            if score >= 0.65:
                return "Low"
            elif score >= 0.35:
                return "Medium"
            else:
                return "High"
    
    def _generate_assessment_summary(self, entity_name: str, group_results: Dict[str, Dict[str, Any]], user_inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate an overall assessment summary.
        
        Args:
            entity_name: Name of the entity
            group_results: Assessment results for all groups
            user_inputs: User provided inputs
            
        Returns:
            dict: Assessment summary
        """
        # Calculate overall scores
        overall_score = 0.0
        total_weight = 0.0
        
        group_weights = {
            "vision": 0.05,
            "market": 0.15,
            "strategic": 0.20,
            "risk": 0.15,
            "competitive": 0.15,
            "portfolio": 0.10,
            "strengths": 0.10,
            "finance": 0.05,
            "hr": 0.02,
            "operations": 0.02,
            "sales_marketing": 0.01
        }
        
        # Adjust weights based on user priorities
        priorities = user_inputs.get("priorities", [])
        for priority in priorities:
            if priority in group_weights:
                group_weights[priority] *= 1.5  # Increase weight for prioritized groups
        
        # Normalize weights
        weight_sum = sum(group_weights.values())
        normalized_weights = {k: v/weight_sum for k, v in group_weights.items()}
        
        # Calculate weighted average score
        for group_id, group_data in group_results.items():
            if group_id in normalized_weights:
                weight = normalized_weights[group_id]
                score = group_data.get("score", 0.5)
                
                overall_score += score * weight
                total_weight += weight
        
        # Calculate final score
        if total_weight > 0:
            final_score = overall_score / total_weight
        else:
            final_score = 0.5
        
        # Determine overall risk level
        risk_tolerance = user_inputs.get("risk_tolerance", "Medium")
        risk_level = self._determine_risk_level(final_score, risk_tolerance)
        
        # Count findings by type
        findings_by_type = {}
        for group_id, group_data in group_results.items():
            for finding in group_data.get("findings", []):
                finding_type = finding.get("type", "other")
                if finding_type not in findings_by_type:
                    findings_by_type[finding_type] = 0
                findings_by_type[finding_type] += 1
        
        # Generate summary
        summary = {
            "overall_score": final_score,
            "risk_level": risk_level,
            "findings_summary": findings_by_type,
            "top_areas": self._identify_top_areas(group_results, "low", 3),  # Top performing areas
            "concern_areas": self._identify_top_areas(group_results, "high", 3),  # Areas of concern
            "key_insights": self._generate_key_insights(entity_name, group_results, user_inputs)
        }
        
        return summary
    
    def _identify_top_areas(self, group_results: Dict[str, Dict[str, Any]], risk_level: str, limit: int) -> List[str]:
        """
        Identify top performing areas or areas of concern.
        
        Args:
            group_results: Assessment results for all groups
            risk_level: Risk level to filter by (low for top areas, high for concerns)
            limit: Maximum number of areas to return
            
        Returns:
            list: Top areas or concerns
        """
        # Filter groups by risk level
        filtered_groups = [group_id for group_id, data in group_results.items() 
                        if data.get("risk_level", "").lower() == risk_level.lower()]
        
        # Sort by score (ascending for high risk, descending for low risk)
        if risk_level.lower() == "high":
            sorted_groups = sorted(filtered_groups, 
                                key=lambda g: group_results[g].get("score", 0.5))
        else:
            sorted_groups = sorted(filtered_groups, 
                                key=lambda g: group_results[g].get("score", 0.5), 
                                reverse=True)
        
        # Return top N groups
        return sorted_groups[:limit]
    
    def _generate_key_insights(self, entity_name: str, group_results: Dict[str, Dict[str, Any]], user_inputs: Dict[str, Any]) -> List[str]:
        """
        Generate key insights from assessment results.
    
        Args:
            entity_name: Name of the entity
            group_results: Assessment results for all groups
            user_inputs: User provided inputs
        
        Returns:
            list: Key insights
        """
        insights = []
    
        # Add insights based on risk levels
        high_risk_groups = [group_id for group_id, data in group_results.items() 
                        if data.get("risk_level", "") == "High"]
    
        if high_risk_groups:
            insights.append(f"High risk areas identified in {len(high_risk_groups)} assessment groups, requiring immediate attention.")
    
        # Add insights based on scores
        low_score_groups = [group_id for group_id, data in group_results.items() 
                        if data.get("score", 0.5) < 0.4]
    
        if low_score_groups:
            insights.append(f"Significant improvement opportunities exist in {len(low_score_groups)} assessment areas.")
    
        # Add insights based on findings
        strength_count = 0
        opportunity_count = 0
        risk_count = 0
    
        for group_id, data in group_results.items():
            for finding in data.get("findings", []):
                if finding.get("type") == "strength":
                    strength_count += 1
                elif finding.get("type") == "opportunity":
                    opportunity_count += 1
                elif finding.get("type") == "risk":
                    risk_count += 1
    
        if strength_count > 0:
            insights.append(f"Identified {strength_count} strengths that can be leveraged for strategic advantage.")
    
        if opportunity_count > 0:
            insights.append(f"Discovered {opportunity_count} opportunities for growth and improvement.")
    
        if risk_count > 0:
            insights.append(f"Found {risk_count} potential risk factors that should be addressed.")
    
        # Add custom insight based on user priorities
        priorities = user_inputs.get("priorities", [])
        if priorities:
            priorities_text = ", ".join(priorities[:3])
            insights.append(f"Strategy aligned with key priorities: {priorities_text}.")
    
        # Add custom insight based on constraints
        constraints = user_inputs.get("constraints", [])
        if constraints:
            constraints_text = ", ".join(constraints[:3])
            insights.append(f"Strategy development constrained by: {constraints_text}.")
    
        return insights

    def _generate_recommendations(self, entity_name: str, group_results: Dict[str, Dict[str, Any]], user_inputs: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate strategic recommendations based on assessment results.
    
        Args:
            entity_name: Name of the entity
            group_results: Assessment results for all groups
            user_inputs: User provided inputs
        
        Returns:
            list: Strategic recommendations
        """
        # Get risk tolerance from user inputs
        risk_tolerance = user_inputs.get("risk_tolerance", "Medium")
    
        # Use strategy generator if available
        if self.strategy_generator:
            return self.strategy_generator.generate_for_entity(entity_name).get("strategies", [])
    
        # Otherwise, generate basic recommendations
        recommendations = []
    
        # Generate recommendations based on risk areas
        high_risk_areas = []
        for group_id, data in group_results.items():
            if data.get("risk_level") == "High":
                high_risk_areas.append({
                    "group_id": group_id,
                    "name": data.get("name", group_id.capitalize()),
                    "findings": data.get("findings", [])
                })
    
        # Add recommendations for high risk areas
        for area in high_risk_areas:
            recommendations.append({
                "title": f"Address {area['name']} Risks",
                "rationale": f"High risk identified in {area['name']} assessment area.",
                "benefits": [
                    "Reduced risk exposure",
                    "Improved strategic positioning"
                ],
                "implementation_steps": [
                    f"Conduct detailed {area['name'].lower()} analysis",
                    "Develop mitigation strategies",
                    "Implement monitoring mechanisms"
                ],
                "kpis": [
                    f"{area['name']} risk score",
                    "Implementation progress"
                ],
                "timeline": "short",
                "priority": "high"
            })
    
        # Generate growth-oriented recommendations
        opportunity_areas = []
        for group_id, data in group_results.items():
            opportunities = [f for f in data.get("findings", []) if f.get("type") == "opportunity"]
            if opportunities:
                opportunity_areas.append({
                    "group_id": group_id,
                    "name": data.get("name", group_id.capitalize()),
                    "opportunities": opportunities
                })
    
        # Add recommendations for opportunity areas
        for area in opportunity_areas:
            recommendations.append({
                "title": f"Capitalize on {area['name']} Opportunities",
                "rationale": f"Growth opportunities identified in {area['name']} assessment area.",
                "benefits": [
                    "Increased market share",
                    "Revenue growth",
                    "Competitive advantage"
                ],
                "implementation_steps": [
                    f"Develop detailed {area['name'].lower()} action plan",
                    "Allocate resources for implementation",
                    "Establish tracking metrics"
                ],
                "kpis": [
                    "Revenue growth",
                    "Market share",
                    "Return on investment"
                ],
                "timeline": "medium",
                "priority": "medium"
            })
    
        # Generate strength-leveraging recommendations
        strength_areas = []
        for group_id, data in group_results.items():
            strengths = [f for f in data.get("findings", []) if f.get("type") == "strength"]
            if strengths:
                strength_areas.append({
                    "group_id": group_id,
                    "name": data.get("name", group_id.capitalize()),
                    "strengths": strengths
                })
    
        # Add recommendations for strength areas
        for area in strength_areas:
            recommendations.append({
                "title": f"Leverage {area['name']} Strengths",
                "rationale": f"Significant strengths identified in {area['name']} assessment area.",
                "benefits": [
                    "Enhanced competitive positioning",
                    "Improved market differentiation",
                    "Increased customer value"
                ],
                "implementation_steps": [
                    f"Develop {area['name'].lower()} enhancement strategy",
                    "Integrate strengths into marketing approach",
                    "Train team on leverage opportunities"
                ],
                "kpis": [
                    "Strength utilization metrics",
                    "Customer perception metrics",
                    "Competitive win rate"
                ],
                "timeline": "medium",
                "priority": "medium"
            })
    
        # Ensure we have at least 3 recommendations
        if len(recommendations) < 3:
            # Add a general improvement recommendation
            recommendations.append({
                "title": "Implement Comprehensive Strategy Monitoring",
                "rationale": "Enhance strategic execution through better monitoring and management.",
                "benefits": [
                    "Improved strategic alignment",
                    "Early risk identification",
                    "Better decision making"
                ],
                "implementation_steps": [
                    "Establish key strategic metrics",
                    "Implement dashboards for real-time monitoring",
                    "Set up regular strategy review meetings"
                ],
                "kpis": [
                    "Strategy implementation rate",
                    "Risk mitigation effectiveness",
                    "Decision response time"
                ],
                "timeline": "short",
                "priority": "medium"
            })
    
        # Adjust priorities based on risk tolerance
        if risk_tolerance == "Low":
            # Prioritize risk mitigation
            for rec in recommendations:
                if "Risk" in rec["title"]:
                    rec["priority"] = "high"
        elif risk_tolerance == "High":
            # Prioritize growth opportunities
            for rec in recommendations:
                if "Opportunities" in rec["title"]:
                    rec["priority"] = "high"
    
        # Sort by priority
        priority_order = {"high": 0, "medium": 1, "low": 2}
        recommendations.sort(key=lambda r: priority_order.get(r["priority"], 1))
    
        return recommendations

    def _save_assessment_results(self, entity_name: str, assessment_results: Dict[str, Any]) -> str:
        """
        Save assessment results to a file.
    
        Args:
            entity_name: Name of the entity
            assessment_results: Assessment results to save
        
        Returns:
            str: Path to the saved file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"assessment_{entity_name.replace(' ', '_')}_{timestamp}.json"
        filepath = os.path.join(self.output_dir, filename)
    
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(assessment_results, f, ensure_ascii=False, indent=2)
    
        logger.info(f"Saved assessment results to: {filepath}")
        return filepath

    def generate_charts(self, assessment_results: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """
        Generate chart configurations for assessment results visualization.
    
        Args:
            assessment_results: Assessment results
        
        Returns:
            dict: Chart configurations for visualization
        """
        # Create charts for different assessment aspects
        charts = {}
    
        # 1. Risk Level Chart
        risk_levels = {}
        for group_id, group_data in assessment_results.get("groups", {}).items():
            risk_level = group_data.get("risk_level", "Medium")
            if risk_level not in risk_levels:
                risk_levels[risk_level] = 0
            risk_levels[risk_level] += 1
    
        charts["risk_levels"] = {
            "type": "pie_chart",
            "title": "Risk Levels by Assessment Area",
            "data": [
                {"label": level, "value": count}
                for level, count in risk_levels.items()
            ]
        }
    
        # 2. Group Scores Chart
        charts["group_scores"] = {
            "type": "bar_chart",
            "title": "Assessment Area Scores",
            "data": [
                {
                    "label": group_data.get("name", group_id.capitalize()),
                    "value": group_data.get("score", 0.5),
                    "color": "#ff9999" if group_data.get("risk_level") == "High" else 
                            "#ffcc99" if group_data.get("risk_level") == "Medium" else "#99cc99"
                }
                for group_id, group_data in assessment_results.get("groups", {}).items()
            ]
        }
    
        # 3. Strategic Goals Chart
        # This would be populated with actual strategic goals in a real implementation
        charts["strategic_goals"] = {
            "type": "radar_chart",
            "title": "Strategic Goals Assessment",
            "categories": ["Market Share", "Revenue Growth", "Innovation", "Efficiency", "Customer Satisfaction"],
            "datasets": [
                {
                    "label": "Current",
                    "data": [0.6, 0.7, 0.4, 0.5, 0.8]
                },
                {
                    "label": "Target",
                    "data": [0.8, 0.9, 0.7, 0.8, 0.9]
                }
            ]
        }
    
        # 4. Metrics Trend Chart
        # Simple example - would use real metrics in production
        charts["metrics_trends"] = {
            "type": "line_chart",
            "title": "Key Metrics Trends",
            "labels": ["Q1", "Q2", "Q3", "Q4"],
            "datasets": [
                {
                    "label": "Revenue Growth",
                    "data": [0.05, 0.07, 0.08, 0.1]
                },
                {
                    "label": "Market Share",
                    "data": [0.12, 0.13, 0.15, 0.17]
                },
                {
                    "label": "Customer Satisfaction",
                    "data": [0.75, 0.78, 0.8, 0.82]
                }
            ]
        }
    
        return charts