#!/usr/bin/env python3
"""
Script to populate the knowledge graph with rich, realistic entities and relationships
to thoroughly test the strategy generation capabilities.
"""

import sys
import random
from datetime import datetime, timedelta
from knowledge_graph.neo4j_manager import Neo4jManager

# Add to populate_test_data.py

def populate_test_data():
    """Generate test data for the 30 assessment groups in the Qmirac Engine Guidelines."""
    # This would simulate the data that would normally come from the 30 PDF sections
    
    # Initialize Neo4j manager
    neo4j = Neo4jManager()
    neo4j.connect()
    
    try:
        print("Generating Qmirac test data...")
        
        # For each of the 30 groups, create sample data in Neo4j
        # This would represent the data that would typically come from PDFs
        
        # Group 1 - Vision
        vision_data = {
            "entity": "TechCorp",
            "vision_statement": "To transform enterprise software security through innovative cloud solutions",
            "clarity_score": 0.85,
            "conciseness_score": 0.75,
            "inspiration_score": 0.90,
            "future_focus_score": 0.95,
            "ambitious_score": 0.85,
            "achievable_score": 0.70
        }
        
        # Store vision data in Neo4j
        neo4j.execute_query(
            """
            MATCH (e:Entity {name: $entity})
            MERGE (e)-[:HAS_ASSESSMENT]->(a:Assessment {name: 'Vision'})
            SET a += $properties
            """,
            {"entity": vision_data["entity"], "properties": vision_data}
        )
        
        # Group 2 - Market Assessment
        market_segments = [
            {
                "entity": "TechCorp",
                "segment": "Enterprise Cloud Security",
                "attractiveness": 0.85,
                "value_proposition_fit": 0.80,
                "current_market_share": 0.15,
                "growth_potential": 0.90
            },
            {
                "entity": "TechCorp",
                "segment": "SMB Security Solutions",
                "attractiveness": 0.65,
                "value_proposition_fit": 0.70,
                "current_market_share": 0.08,
                "growth_potential": 0.75
            },
            {
                "entity": "TechCorp",
                "segment": "Government Cybersecurity",
                "attractiveness": 0.90,
                "value_proposition_fit": 0.60,
                "current_market_share": 0.05,
                "growth_potential": 0.85
            }
        ]
        
        # Store market segment data in Neo4j
        for segment in market_segments:
            neo4j.execute_query(
                """
                MATCH (e:Entity {name: $entity})
                MERGE (e)-[:HAS_ASSESSMENT]->(a:Assessment {name: 'Market Assessment'})
                MERGE (a)-[:HAS_SEGMENT]->(s:MarketSegment {name: $segment})
                SET s += $properties
                """,
                {
                    "entity": segment["entity"], 
                    "segment": segment["segment"],
                    "properties": segment
                }
            )
        
        # Group 3 - Strategic Assessment
        strategic_assessment_data = {
            "entity": "TechCorp",
            "most_attractive_markets": ["Enterprise Cloud Security", "Government Cybersecurity"],
            "strategic_position_score": 0.75,
            "market_share_strongest_segment": 0.15,
            "emerging_markets": ["Edge Computing Security", "IoT Security Solutions"],
            "strategic_position_enhancement_opportunities": ["Partnership with major cloud providers", "Investment in ML-based threat detection"],
            "market_growth_barriers": ["Regulatory compliance complexity", "Competition from established players"],
            "strategic_position_barriers": ["Limited enterprise customer base", "Brand recognition in government sector"],
            "growth_bottlenecks": ["Sales team capacity", "Product development cycles"],
            "strategic_constraints": ["Capital limitations", "Technical talent acquisition"],
            "ecosystem_partnership_opportunities": ["Strategic alliance with AWS", "Integration with Microsoft security suite"],
            "balance_sheet_strength": 0.65
        }
        
        # Store strategic assessment data in Neo4j
        neo4j.execute_query(
            """
            MATCH (e:Entity {name: $entity})
            MERGE (e)-[:HAS_ASSESSMENT]->(a:Assessment {name: 'Strategic Assessment'})
            SET a += $properties
            """,
            {"entity": strategic_assessment_data["entity"], "properties": strategic_assessment_data}
        )
        
        # Group 4 - Risk Assessment
        risk_factors = [
            {
                "entity": "TechCorp",
                "risk_factor": "Cybersecurity Talent Shortage",
                "risk_category": "High",
                "probability": 0.80,
                "impact": 0.85,
                "mitigation_strategies": ["Internal training program", "Offshore development centers"],
                "mitigation_effectiveness": 0.60
            },
            {
                "entity": "TechCorp",
                "risk_factor": "Emerging Competition",
                "risk_category": "Medium",
                "probability": 0.65,
                "impact": 0.70,
                "mitigation_strategies": ["Accelerate product roadmap", "Strengthen patent portfolio"],
                "mitigation_effectiveness": 0.75
            },
            {
                "entity": "TechCorp",
                "risk_factor": "Regulatory Changes",
                "risk_category": "High",
                "probability": 0.75,
                "impact": 0.90,
                "mitigation_strategies": ["Dedicated compliance team", "Regular regulatory assessments"],
                "mitigation_effectiveness": 0.65
            }
        ]
        
        # Store risk assessment data in Neo4j
        for risk in risk_factors:
            neo4j.execute_query(
                """
                MATCH (e:Entity {name: $entity})
                MERGE (e)-[:HAS_ASSESSMENT]->(a:Assessment {name: 'Risk Assessment'})
                MERGE (a)-[:HAS_RISK]->(r:RiskFactor {name: $risk})
                SET r += $properties
                """,
                {
                    "entity": risk["entity"], 
                    "risk": risk["risk_factor"],
                    "properties": risk
                }
            )
        
        # Group 5 - Competitive Assessment
        competitive_parameters = [
            {
                "entity": "TechCorp",
                "parameter": "Cloud Integration Capabilities",
                "company_score": 0.90,
                "competitive_advantage": "Major",
                "competitor1_name": "SecureTech",
                "competitor1_score": 0.65,
                "competitor2_name": "CloudGuard",
                "competitor2_score": 0.80,
                "competitor3_name": "CyberShield",
                "competitor3_score": 0.70,
                "market_importance": 0.85
            },
            {
                "entity": "TechCorp",
                "parameter": "User Interface Simplicity",
                "company_score": 0.60,
                "competitive_advantage": "Disadvantage",
                "competitor1_name": "SecureTech",
                "competitor1_score": 0.75,
                "competitor2_name": "CloudGuard",
                "competitor2_score": 0.85,
                "competitor3_name": "CyberShield",
                "competitor3_score": 0.70,
                "market_importance": 0.80
            },
            {
                "entity": "TechCorp",
                "parameter": "Threat Detection Speed",
                "company_score": 0.85,
                "competitive_advantage": "Major",
                "competitor1_name": "SecureTech",
                "competitor1_score": 0.75,
                "competitor2_name": "CloudGuard",
                "competitor2_score": 0.70,
                "competitor3_name": "CyberShield",
                "competitor3_score": 0.65,
                "market_importance": 0.90
            }
        ]
        
        # Store competitive assessment data in Neo4j
        for param in competitive_parameters:
            neo4j.execute_query(
                """
                MATCH (e:Entity {name: $entity})
                MERGE (e)-[:HAS_ASSESSMENT]->(a:Assessment {name: 'Competitive Assessment'})
                MERGE (a)-[:HAS_PARAMETER]->(p:CompetitiveParameter {name: $parameter})
                SET p += $properties
                """,
                {
                    "entity": param["entity"], 
                    "parameter": param["parameter"],
                    "properties": param
                }
            )
        
        # Group 6 - Portfolio Assessment
        portfolio_products = [
            {
                "entity": "TechCorp",
                "product": "CloudGuard Enterprise",
                "lifecycle_stage": "Mid Growth",
                "revenue_contribution": 0.45,
                "growth_rate": 0.25,
                "investment_allocation": 0.35,
                "profitability": 0.30
            },
            {
                "entity": "TechCorp",
                "product": "SecureAPI Gateway",
                "lifecycle_stage": "Early Growth",
                "revenue_contribution": 0.25,
                "growth_rate": 0.40,
                "investment_allocation": 0.40,
                "profitability": 0.15
            },
            {
                "entity": "TechCorp",
                "product": "DataVault Legacy",
                "lifecycle_stage": "Mature",
                "revenue_contribution": 0.20,
                "growth_rate": -0.05,
                "investment_allocation": 0.10,
                "profitability": 0.40
            },
            {
                "entity": "TechCorp",
                "product": "EdgeSecure IoT",
                "lifecycle_stage": "Embryonic",
                "revenue_contribution": 0.10,
                "growth_rate": 0.60,
                "investment_allocation": 0.15,
                "profitability": -0.10
            }
        ]
        
        # Store portfolio assessment data in Neo4j
        for product in portfolio_products:
            neo4j.execute_query(
                """
                MATCH (e:Entity {name: $entity})
                MERGE (e)-[:HAS_ASSESSMENT]->(a:Assessment {name: 'Portfolio Assessment'})
                MERGE (a)-[:HAS_PRODUCT]->(p:Product {name: $product})
                SET p += $properties
                """,
                {
                    "entity": product["entity"], 
                    "product": product["product"],
                    "properties": product
                }
            )
        
        # Group 7 - Strengths Assessment
        strengths = [
            {
                "entity": "TechCorp",
                "strength": "Cloud-native Architecture Expertise",
                "value_score": 0.90,
                "competitive_advantage": 0.85,
                "enhancement_opportunities": ["Establish thought leadership", "Open-source framework contributions"]
            },
            {
                "entity": "TechCorp",
                "strength": "Machine Learning Capabilities",
                "value_score": 0.80,
                "competitive_advantage": 0.75,
                "enhancement_opportunities": ["ML model refinement", "Advanced threat prediction algorithms"]
            },
            {
                "entity": "TechCorp",
                "strength": "Enterprise Integration Framework",
                "value_score": 0.85,
                "competitive_advantage": 0.80,
                "enhancement_opportunities": ["Expand connector library", "Improve API documentation"]
            }
        ]
        
        # Store strengths assessment data in Neo4j
        for strength in strengths:
            neo4j.execute_query(
                """
                MATCH (e:Entity {name: $entity})
                MERGE (e)-[:HAS_ASSESSMENT]->(a:Assessment {name: 'Strengths Assessment'})
                MERGE (a)-[:HAS_STRENGTH]->(s:Strength {name: $strength})
                SET s += $properties
                """,
                {
                    "entity": strength["entity"], 
                    "strength": strength["strength"],
                    "properties": strength
                }
            )
        
        # Group 8 - Weaknesses Assessment
        weaknesses = [
            {
                "entity": "TechCorp",
                "weakness": "User Interface Complexity",
                "competitive_disadvantage_score": 0.70,
                "impact_score": 0.65,
                "mitigation_strategies": ["UX redesign initiative", "Customer experience team"],
                "opportunity_creation": "Simplified administration dashboard"
            },
            {
                "entity": "TechCorp",
                "weakness": "Limited Mobile Support",
                "competitive_disadvantage_score": 0.75,
                "impact_score": 0.60,
                "mitigation_strategies": ["Mobile SDK development", "Progressive web app"],
                "opportunity_creation": "Cross-platform mobile security suite"
            },
            {
                "entity": "TechCorp",
                "weakness": "Customer Support Response Time",
                "competitive_disadvantage_score": 0.60,
                "impact_score": 0.80,
                "mitigation_strategies": ["Support team expansion", "Knowledge base enhancement"],
                "opportunity_creation": "Premier support offering"
            }
        ]
        
        # Store weaknesses assessment data in Neo4j
        for weakness in weaknesses:
            neo4j.execute_query(
                """
                MATCH (e:Entity {name: $entity})
                MERGE (e)-[:HAS_ASSESSMENT]->(a:Assessment {name: 'Weaknesses Assessment'})
                MERGE (a)-[:HAS_WEAKNESS]->(w:Weakness {name: $weakness})
                SET w += $properties
                """,
                {
                    "entity": weakness["entity"], 
                    "weakness": weakness["weakness"],
                    "properties": weakness
                }
            )
        
        # Group 9 - Opportunities Assessment
        opportunities = [
            {
                "entity": "TechCorp",
                "opportunity": "Federal Government Contracts",
                "size_estimate": "USD 50M",
                "catalytic_potential": 0.85,
                "strength_conversion_potential": 0.80,
                "execution_strategies": ["FedRAMP certification", "Government sales team"]
            },
            {
                "entity": "TechCorp",
                "opportunity": "Financial Services Vertical",
                "size_estimate": "USD 35M",
                "catalytic_potential": 0.75,
                "strength_conversion_potential": 0.70,
                "execution_strategies": ["FINRA compliance module", "Financial data protection framework"]
            },
            {
                "entity": "TechCorp",
                "opportunity": "AI-powered Threat Prediction",
                "size_estimate": "USD 20M",
                "catalytic_potential": 0.90,
                "strength_conversion_potential": 0.85,
                "execution_strategies": ["ML research team expansion", "Predictive security analytics product"]
            }
        ]
        
        # Store opportunities assessment data in Neo4j
        for opportunity in opportunities:
            neo4j.execute_query(
                """
                MATCH (e:Entity {name: $entity})
                MERGE (e)-[:HAS_ASSESSMENT]->(a:Assessment {name: 'Opportunities Assessment'})
                MERGE (a)-[:HAS_OPPORTUNITY]->(o:Opportunity {name: $opportunity})
                SET o += $properties
                """,
                {
                    "entity": opportunity["entity"], 
                    "opportunity": opportunity["opportunity"],
                    "properties": opportunity
                }
            )
        
        # Group 10 - Threats Assessment
        threats = [
            {
                "entity": "TechCorp",
                "threat": "New Market Entrants",
                "severity": 0.75,
                "probability": 0.80,
                "mitigation_strategies": ["Accelerate innovation", "Strengthen patent portfolio"],
                "opportunity_conversion": "Acquisition of promising startups"
            },
            {
                "entity": "TechCorp",
                "threat": "Regulatory Changes",
                "severity": 0.85,
                "probability": 0.65,
                "mitigation_strategies": ["Compliance team expansion", "Regulatory engagement"],
                "opportunity_conversion": "Compliance-as-a-service offering"
            },
            {
                "entity": "TechCorp",
                "threat": "Cloud Provider Competition",
                "severity": 0.90,
                "probability": 0.70,
                "mitigation_strategies": ["Cross-cloud functionality", "Value-added services"],
                "opportunity_conversion": "Multi-cloud management platform"
            }
        ]
        
        # Store threats assessment data in Neo4j
        for threat in threats:
            neo4j.execute_query(
                """
                MATCH (e:Entity {name: $entity})
                MERGE (e)-[:HAS_ASSESSMENT]->(a:Assessment {name: 'Threats Assessment'})
                MERGE (a)-[:HAS_THREAT]->(t:Threat {name: $threat})
                SET t += $properties
                """,
                {
                    "entity": threat["entity"], 
                    "threat": threat["threat"],
                    "properties": threat
                }
            )
        
        # Group 11 - Finance Dashboard (Revenue Growth)
        revenue_growth_data = {
            "entity": "TechCorp",
            "current_year_revenue": 25000000,
            "prior_year_revenue": 19500000,
            "two_years_prior_revenue": 15600000,
            "current_year_growth": 0.28,
            "prior_year_growth": 0.25,
            "market_growth_rate": 0.18,
            "forecasted_next_year_revenue": 32500000,
            "forecasted_two_year_revenue": 40625000,
            "forecasted_growth_rate": 0.30,
            "risk_impact_of_growth": 0.25
        }
        
        # Store revenue growth data in Neo4j
        neo4j.execute_query(
            """
            MATCH (e:Entity {name: $entity})
            MERGE (e)-[:HAS_ASSESSMENT]->(a:Assessment {name: 'Revenue Growth'})
            SET a += $properties
            """,
            {"entity": revenue_growth_data["entity"], "properties": revenue_growth_data}
        )
        
        # Group 12 - Finance Dashboard (Operating Income)
        operating_income_data = {
            "entity": "TechCorp",
            "current_year_operating_income": 3750000,
            "prior_year_operating_income": 2730000,
            "two_years_prior_operating_income": 1872000,
            "current_year_growth": 0.37,
            "prior_year_growth": 0.46,
            "market_growth_rate": 0.20,
            "forecasted_next_year_operating_income": 5200000,
            "forecasted_two_year_operating_income": 7020000,
            "forecasted_growth_rate": 0.39,
            "risk_impact_of_growth": 0.30
        }
        
        # Store operating income data in Neo4j
        neo4j.execute_query(
            """
            MATCH (e:Entity {name: $entity})
            MERGE (e)-[:HAS_ASSESSMENT]->(a:Assessment {name: 'Operating Income'})
            SET a += $properties
            """,
            {"entity": operating_income_data["entity"], "properties": operating_income_data}
        )
        
        # Group 13 - Finance Dashboard (Cash Flow)
        cash_flow_data = {
            "entity": "TechCorp",
            "current_year_operating_cash_flow": 4500000,
            "prior_year_operating_cash_flow": 3510000,
            "two_years_prior_operating_cash_flow": 2808000,
            "current_year_growth": 0.28,
            "prior_year_growth": 0.25,
            "market_growth_rate": 0.15,
            "forecasted_next_year_operating_cash_flow": 5850000,
            "forecasted_two_year_operating_cash_flow": 7605000,
            "forecasted_growth_rate": 0.30,
            "risk_impact_of_growth": 0.20
        }
        
        # Store cash flow data in Neo4j
        neo4j.execute_query(
            """
            MATCH (e:Entity {name: $entity})
            MERGE (e)-[:HAS_ASSESSMENT]->(a:Assessment {name: 'Cash Flow'})
            SET a += $properties
            """,
            {"entity": cash_flow_data["entity"], "properties": cash_flow_data}
        )
        
        # Group 14 - Finance Dashboard (Gross Margin)
        gross_margin_data = {
            "entity": "TechCorp",
            "current_year_gross_margin": 0.72,
            "prior_year_gross_margin": 0.68,
            "two_years_prior_gross_margin": 0.65,
            "current_year_growth": 0.06,
            "prior_year_growth": 0.05,
            "market_average_margin": 0.62,
            "forecasted_next_year_margin": 0.74,
            "forecasted_two_year_margin": 0.76,
            "forecasted_growth_rate": 0.03,
            "risk_impact_of_margin": 0.25
        }
        
        # Store gross margin data in Neo4j
        neo4j.execute_query(
            """
            MATCH (e:Entity {name: $entity})
            MERGE (e)-[:HAS_ASSESSMENT]->(a:Assessment {name: 'Gross Margin'})
            SET a += $properties
            """,
            {"entity": gross_margin_data["entity"], "properties": gross_margin_data}
        )
        
        # Group 15 - Finance Dashboard (Finance Metrics)
        finance_metrics_data = {
            "entity": "TechCorp",
            "current_ratio": 1.8,
            "quick_ratio": 1.5,
            "debt_to_equity": 0.4,
            "return_on_assets": 0.18,
            "return_on_equity": 0.22,
            "inventory_turnover": 8.5,
            "days_sales_outstanding": 45,
            "ebitda_margin": 0.22,
            "concerning_metrics": ["days_sales_outstanding"],
            "concerning_ratios": [],
            "strategic_improvement_areas": ["accounts receivable process", "cash conversion cycle"],
            "risk_profile_impact": 0.30
        }
        
        # Store finance metrics data in Neo4j
        neo4j.execute_query(
            """
            MATCH (e:Entity {name: $entity})
            MERGE (e)-[:HAS_ASSESSMENT]->(a:Assessment {name: 'Finance Metrics'})
            SET a += $properties
            """,
            {"entity": finance_metrics_data["entity"], "properties": finance_metrics_data}
        )
        
        # Group 16 - HR Dashboard (Time to Hire)
        time_to_hire_data = {
            "entity": "TechCorp",
            "average_time_to_hire_days": 42,
            "industry_average_days": 35,
            "engineering_time_to_hire_days": 56,
            "sales_time_to_hire_days": 30,
            "executive_time_to_hire_days": 90,
            "support_time_to_hire_days": 25,
            "critical_roles_time_to_hire_days": 65,
            "improvement_strategies": ["Talent acquisition team expansion", "Automated screening process"],
            "strategic_dependency": 0.75
        }
        
        # Store time to hire data in Neo4j
        neo4j.execute_query(
            """
            MATCH (e:Entity {name: $entity})
            MERGE (e)-[:HAS_ASSESSMENT]->(a:Assessment {name: 'Time to Hire'})
            SET a += $properties
            """,
            {"entity": time_to_hire_data["entity"], "properties": time_to_hire_data}
        )
        
        # Group 17 - HR Dashboard (Employee Turnover)
        employee_turnover_data = {
            "entity": "TechCorp",
            "overall_turnover_rate": 0.15,
            "industry_average_turnover": 0.20,
            "engineering_turnover_rate": 0.18,
            "sales_turnover_rate": 0.22,
            "executive_turnover_rate": 0.08,
            "support_turnover_rate": 0.12,
            "voluntary_turnover_rate": 0.11,
            "involuntary_turnover_rate": 0.04,
            "turnover_trend": -0.02,
            "improvement_strategies": ["Compensation review", "Career development programs"],
            "strategic_dependency": 0.70,
            "risk_impact": 0.60
        }
        
        # Store employee turnover data in Neo4j
        neo4j.execute_query(
            """
            MATCH (e:Entity {name: $entity})
            MERGE (e)-[:HAS_ASSESSMENT]->(a:Assessment {name: 'Employee Turnover'})
            SET a += $properties
            """,
            {"entity": employee_turnover_data["entity"], "properties": employee_turnover_data}
        )
        
        # Group 18 - HR Dashboard (Employee Engagement)
        employee_engagement_data = {
            "entity": "TechCorp",
            "overall_engagement_score": 7.2,
            "industry_average_engagement": 6.8,
            "engineering_engagement_score": 7.4,
            "sales_engagement_score": 7.8,
            "executive_engagement_score": 8.1,
            "support_engagement_score": 6.5,
            "engagement_trend": 0.3,
            "improvement_strategies": ["Regular town halls", "Flexible work arrangements"],
            "strategic_dependency": 0.80,
            "risk_impact": 0.65
        }
        
        # Store employee engagement data in Neo4j
        neo4j.execute_query(
            """
            MATCH (e:Entity {name: $entity})
            MERGE (e)-[:HAS_ASSESSMENT]->(a:Assessment {name: 'Employee Engagement'})
            SET a += $properties
            """,
            {"entity": employee_engagement_data["entity"], "properties": employee_engagement_data}
        )
        
        # Group 19 - HR Dashboard (Diversity)
        diversity_data = {
            "entity": "TechCorp",
            "gender_diversity_ratio": 0.32,
            "industry_gender_diversity_average": 0.28,
            "ethnic_diversity_ratio": 0.38,
            "industry_ethnic_diversity_average": 0.30,
            "leadership_diversity_ratio": 0.25,
            "diversity_trend": 0.04,
            "improvement_strategies": ["Inclusive hiring practices", "Diversity training"],
            "strategic_dependency": 0.65,
            "risk_impact": 0.55
        }
        
        # Store diversity data in Neo4j
        neo4j.execute_query(
            """
            MATCH (e:Entity {name: $entity})
            MERGE (e)-[:HAS_ASSESSMENT]->(a:Assessment {name: 'Diversity'})
            SET a += $properties
            """,
            {"entity": diversity_data["entity"], "properties": diversity_data}
        )
        
        # Group 20 - HR Dashboard (HR Metrics)
        hr_metrics_data = {
            "entity": "TechCorp",
            "cost_per_hire": 8500,
            "training_cost_per_employee": 2000,
            "revenue_per_employee": 325000,
            "profit_per_employee": 48750,
            "healthcare_costs_per_employee": 12000,
            "absenteeism_rate": 0.02,
            "overtime_percentage": 0.08,
            "concerning_metrics": ["cost_per_hire"],
            "concerning_ratios": [],
            "strategic_improvement_areas": ["Recruiting efficiency", "Benefits optimization"],
            "risk_profile_impact": 0.40
        }
        
        # Store HR metrics data in Neo4j
        neo4j.execute_query(
            """
            MATCH (e:Entity {name: $entity})
            MERGE (e)-[:HAS_ASSESSMENT]->(a:Assessment {name: 'HR Metrics'})
            SET a += $properties
            """,
            {"entity": hr_metrics_data["entity"], "properties": hr_metrics_data}
        )
        
        # Group 21 - OPS Dashboard (Inventory Turnover)
        inventory_turnover_data = {
            "entity": "TechCorp",
            "inventory_turnover_ratio": 8.5,
            "industry_average_turnover": 7.2,
            "hardware_inventory_turnover": 6.8,
            "software_inventory_turnover": 12.5,
            "turnover_trend": 0.8,
            "improvement_strategies": ["Just-in-time inventory", "Demand forecasting"],
            "strategic_improvement_potential": 0.60
        }
        
        # Store inventory turnover data in Neo4j
        neo4j.execute_query(
            """
            MATCH (e:Entity {name: $entity})
            MERGE (e)-[:HAS_ASSESSMENT]->(a:Assessment {name: 'Inventory Turnover'})
            SET a += $properties
            """,
            {"entity": inventory_turnover_data["entity"], "properties": inventory_turnover_data}
        )
        
        # Group 22 - OPS Dashboard (On Time Delivery)
        on_time_delivery_data = {
            "entity": "TechCorp",
            "on_time_delivery_rate": 0.92,
            "industry_average_rate": 0.88,
            "hardware_delivery_rate": 0.85,
            "software_delivery_rate": 0.97,
            "delivery_trend": 0.03,
            "improvement_strategies": ["Supply chain optimization", "Delivery partner reviews"],
            "strategic_improvement_potential": 0.55
        }
        
        # Store on time delivery data in Neo4j
        neo4j.execute_query(
            """
            MATCH (e:Entity {name: $entity})
            MERGE (e)-[:HAS_ASSESSMENT]->(a:Assessment {name: 'On Time Delivery'})
            SET a += $properties
            """,
            {"entity": on_time_delivery_data["entity"], "properties": on_time_delivery_data}
        )
        
        # Group 23 - OPS Dashboard (First Pass Yield)
        first_pass_yield_data = {
            "entity": "TechCorp",
            "first_pass_yield_rate": 0.88,
            "industry_average_rate": 0.82,
            "hardware_yield_rate": 0.81,
            "software_yield_rate": 0.93,
            "yield_trend": 0.02,
            "improvement_strategies": ["Quality control automation", "Development process refinement"],
            "strategic_improvement_potential": 0.70
        }
        
        # Store first pass yield data in Neo4j
        neo4j.execute_query(
            """
            MATCH (e:Entity {name: $entity})
            MERGE (e)-[:HAS_ASSESSMENT]->(a:Assessment {name: 'First Pass Yield'})
            SET a += $properties
            """,
            {"entity": first_pass_yield_data["entity"], "properties": first_pass_yield_data}
        )
        
        # Group 24 - OPS Dashboard (Total Cycle Time)
        total_cycle_time_data = {
            "entity": "TechCorp",
            "total_cycle_time_days": 65,
            "industry_average_days": 75,
            "product_development_cycle_days": 120,
            "order_fulfillment_cycle_days": 10,
            "support_resolution_cycle_days": 3,
            "cycle_time_trend": -5,
            "improvement_strategies": ["Agile methodology refinement", "Process automation"],
            "strategic_improvement_potential": 0.65
        }
        
        # Store total cycle time data in Neo4j
        neo4j.execute_query(
            """
            MATCH (e:Entity {name: $entity})
            MERGE (e)-[:HAS_ASSESSMENT]->(a:Assessment {name: 'Total Cycle Time'})
            SET a += $properties
            """,
            {"entity": total_cycle_time_data["entity"], "properties": total_cycle_time_data}
        )
        
        # Group 25 - Operations Dashboard (Operations Metrics)
        operations_metrics_data = {
            "entity": "TechCorp",
            "production_capacity_utilization": 0.78,
            "defect_rate": 0.03,
            "rework_percentage": 0.08,
            "equipment_uptime": 0.95,
            "throughput_rate": 550,
            "waste_percentage": 0.04,
            "concerning_metrics": ["rework_percentage"],
            "concerning_ratios": [],
            "strategic_improvement_areas": ["Quality control", "Process efficiency"],
            "risk_profile_impact": 0.35
        }
        
        # Store operations metrics data in Neo4j
        neo4j.execute_query(
            """
            MATCH (e:Entity {name: $entity})
            MERGE (e)-[:HAS_ASSESSMENT]->(a:Assessment {name: 'Operations Metrics'})
            SET a += $properties
            """,
            {"entity": operations_metrics_data["entity"], "properties": operations_metrics_data}
        )
        
        # Group 26 - Sales & Marketing Dashboard (Annual Recurring Revenue)
        annual_recurring_revenue_data = {
            "entity": "TechCorp",
            "current_year_arr": 18500000,
            "prior_year_arr": 13875000,
            "two_years_prior_arr": 10268750,
            "current_year_growth": 0.33,
            "prior_year_growth": 0.35,
            "market_growth_rate": 0.25,
            "forecasted_next_year_arr": 24050000,
            "forecasted_two_year_arr": 30062500,
            "forecasted_growth_rate": 0.30,
            "risk_impact_of_growth": 0.28
        }
        
        # Store annual recurring revenue data in Neo4j
        neo4j.execute_query(
            """
            MATCH (e:Entity {name: $entity})
            MERGE (e)-[:HAS_ASSESSMENT]->(a:Assessment {name: 'Annual Recurring Revenue'})
            SET a += $properties
            """,
            {"entity": annual_recurring_revenue_data["entity"], "properties": annual_recurring_revenue_data}
        )
        
        # Group 27 - Sales & Marketing Dashboard (Customer Acquisition Cost)
        customer_acquisition_cost_data = {
            "entity": "TechCorp",
            "current_year_cac": 12000,
            "prior_year_cac": 14000,
            "two_years_prior_cac": 15500,
            "current_year_reduction": 0.14,
            "prior_year_reduction": 0.10,
            "market_average_cac": 13000,
            "forecasted_next_year_cac": 10800,
            "forecasted_two_year_cac": 9720,
            "forecasted_reduction_rate": 0.10,
            "risk_impact_of_reduction": 0.25
        }
        
        # Store customer acquisition cost data in Neo4j
        neo4j.execute_query(
            """
            MATCH (e:Entity {name: $entity})
            MERGE (e)-[:HAS_ASSESSMENT]->(a:Assessment {name: 'Customer Acquisition Cost'})
            SET a += $properties
            """,
            {"entity": customer_acquisition_cost_data["entity"], "properties": customer_acquisition_cost_data}
        )
        
        # Group 28 - Sales & Marketing Dashboard (Design Win)
        design_win_data = {
            "entity": "TechCorp",
            "current_year_design_wins": 45,
            "prior_year_design_wins": 32,
            "two_years_prior_design_wins": 24,
            "current_year_growth": 0.41,
            "prior_year_growth": 0.33,
            "market_growth_rate": 0.20,
            "enterprise_segment_wins": 28,
            "smb_segment_wins": 12,
            "government_segment_wins": 5,
            "forecasted_next_year_wins": 60,
            "strategic_growth_potential": 0.75
        }
        
        # Store design win data in Neo4j
        neo4j.execute_query(
            """
            MATCH (e:Entity {name: $entity})
            MERGE (e)-[:HAS_ASSESSMENT]->(a:Assessment {name: 'Design Win'})
            SET a += $properties
            """,
            {"entity": design_win_data["entity"], "properties": design_win_data}
        )
        
        # Group 29 - Sales & Marketing Dashboard (Opportunities)
        sales_opportunities_data = {
            "entity": "TechCorp",
            "current_year_opportunities": 220,
            "prior_year_opportunities": 175,
            "two_years_prior_opportunities": 140,
            "current_year_growth": 0.26,
            "prior_year_growth": 0.25,
            "market_growth_rate": 0.15,
            "enterprise_segment_opportunities": 120,
            "smb_segment_opportunities": 75,
            "government_segment_opportunities": 25,
            "forecasted_next_year_opportunities": 275,
            "strategic_growth_potential": 0.70
        }
        
        # Store sales opportunities data in Neo4j
        neo4j.execute_query(
            """
            MATCH (e:Entity {name: $entity})
            MERGE (e)-[:HAS_ASSESSMENT]->(a:Assessment {name: 'Sales Opportunities'})
            SET a += $properties
            """,
            {"entity": sales_opportunities_data["entity"], "properties": sales_opportunities_data}
        )
        
        # Group 30 - Sales & Marketing Dashboard (Sales & Marketing Metrics)
        sales_marketing_metrics_data = {
            "entity": "TechCorp",
            "customer_lifetime_value": 85000,
            "ltv_to_cac_ratio": 7.08,
            "conversion_rate": 0.18,
            "sales_cycle_length_days": 65,
            "churn_rate": 0.08,
            "upsell_rate": 0.25,
            "marketing_roi": 3.2,
            "concerning_metrics": ["sales_cycle_length_days"],
            "concerning_ratios": [],
            "strategic_improvement_areas": ["Sales process efficiency", "Lead qualification"],
            "risk_profile_impact": 0.40
        }
        
        # Store sales & marketing metrics data in Neo4j
        neo4j.execute_query(
            """
            MATCH (e:Entity {name: $entity})
            MERGE (e)-[:HAS_ASSESSMENT]->(a:Assessment {name: 'Sales Marketing Metrics'})
            SET a += $properties
            """,
            {"entity": sales_marketing_metrics_data["entity"], "properties": sales_marketing_metrics_data}
        )
        
        print("Qmirac test data generated successfully")
        return True
    
    except Exception as e:
        print(f"Error generating Qmirac test data: {e}")
        return False
    finally:
        neo4j.close()

if __name__ == "__main__":
    success = populate_test_data()
    sys.exit(0 if success else 1)