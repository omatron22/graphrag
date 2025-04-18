#!/usr/bin/env python3
"""
Script to populate the knowledge graph with rich, realistic entities and relationships
to thoroughly test the strategy generation capabilities.
"""

import sys
import random
from datetime import datetime, timedelta
from knowledge_graph.neo4j_manager import Neo4jManager

def populate_test_data():
    """Add detailed business entities and relationships to the knowledge graph."""
    # Initialize Neo4j manager
    neo4j = Neo4jManager()
    neo4j.connect()
    
    try:
        print("Adding comprehensive test data to knowledge graph...")
        
        # Create company entities with detailed attributes
        companies = [
            {
                "name": "TechCorp", 
                "industry": "Technology", 
                "revenue": "525M", 
                "employees": 1200,
                "founded": "2005",
                "headquarters": "San Francisco",
                "market_cap": "2.1B",
                "ceo": "Sarah Chen",
                "business_model": "SaaS",
                "description": "Enterprise software solutions focusing on cloud infrastructure and security"
            },
            {
                "name": "FinanceGroup", 
                "industry": "Financial Services", 
                "revenue": "1.2B", 
                "employees": 3500,
                "founded": "1995",
                "headquarters": "New York",
                "market_cap": "5.7B",
                "ceo": "Michael Rodriguez",
                "business_model": "B2B/B2C",
                "description": "Financial technology solutions for banking, insurance, and investment management"
            },
            {
                "name": "ManufactureX", 
                "industry": "Manufacturing", 
                "revenue": "800M", 
                "employees": 5000,
                "founded": "1982",
                "headquarters": "Detroit",
                "market_cap": "1.8B",
                "ceo": "James Wu",
                "business_model": "B2B",
                "description": "Advanced manufacturing technologies for automotive and aerospace industries"
            },
            {
                "name": "RetailPro", 
                "industry": "Retail", 
                "revenue": "350M", 
                "employees": 2800,
                "founded": "2010",
                "headquarters": "Chicago",
                "market_cap": "780M",
                "ceo": "Lisa Thompson",
                "business_model": "B2C",
                "description": "Omnichannel retail platform focusing on fashion and home goods"
            },
            {
                "name": "HealthServices", 
                "industry": "Healthcare", 
                "revenue": "600M", 
                "employees": 4200,
                "founded": "1998",
                "headquarters": "Boston",
                "market_cap": "2.4B",
                "ceo": "Robert Kim",
                "business_model": "B2B/B2C",
                "description": "Healthcare technology services for hospitals and clinical research"
            }
        ]
        
        # Create market entities with detailed attributes
        markets = [
            {
                "name": "North America", 
                "size": "Large", 
                "growth_rate": "4.5%",
                "competition_level": "High",
                "regulatory_environment": "Moderate",
                "consumer_spending": "Strong",
                "dominant_segments": ["Technology", "Healthcare", "Financial Services"],
                "emerging_trends": ["Digital Transformation", "Sustainability", "Remote Work"]
            },
            {
                "name": "Europe", 
                "size": "Large", 
                "growth_rate": "3.2%",
                "competition_level": "High",
                "regulatory_environment": "Strong",
                "consumer_spending": "Moderate",
                "dominant_segments": ["Manufacturing", "Renewable Energy", "Financial Services"],
                "emerging_trends": ["Green Technologies", "Digital Services", "Remote Healthcare"]
            },
            {
                "name": "Asia Pacific", 
                "size": "Very Large", 
                "growth_rate": "7.8%",
                "competition_level": "Moderate to High",
                "regulatory_environment": "Variable",
                "consumer_spending": "Rapidly Increasing",
                "dominant_segments": ["Technology", "Manufacturing", "E-commerce"],
                "emerging_trends": ["5G Adoption", "Smart Cities", "Digital Payments"]
            },
            {
                "name": "Latin America", 
                "size": "Medium", 
                "growth_rate": "5.1%",
                "competition_level": "Moderate",
                "regulatory_environment": "Variable",
                "consumer_spending": "Improving",
                "dominant_segments": ["Agriculture", "Mining", "Financial Services"],
                "emerging_trends": ["Financial Inclusion", "E-commerce", "Renewable Energy"]
            }
        ]
        
        # Create product entities
        products = [
            {
                "name": "CloudSecure", 
                "company": "TechCorp",
                "category": "Security Software",
                "launch_date": "2020-05-15",
                "revenue": "180M",
                "growth_rate": "35%",
                "market_share": "12%",
                "description": "Cloud-based security platform for enterprise systems"
            },
            {
                "name": "DataAnalyzer", 
                "company": "TechCorp",
                "category": "Analytics Software",
                "launch_date": "2018-11-03",
                "revenue": "140M",
                "growth_rate": "25%",
                "market_share": "8%",
                "description": "Data analytics and business intelligence solution"
            },
            {
                "name": "InvestPro", 
                "company": "FinanceGroup",
                "category": "Financial Software",
                "launch_date": "2019-02-28",
                "revenue": "350M",
                "growth_rate": "18%",
                "market_share": "15%",
                "description": "Investment management platform for financial institutions"
            },
            {
                "name": "ManufactureOS", 
                "company": "ManufactureX",
                "category": "Manufacturing Software",
                "launch_date": "2021-08-12",
                "revenue": "220M",
                "growth_rate": "40%",
                "market_share": "18%",
                "description": "Operating system for smart manufacturing facilities"
            },
            {
                "name": "RetailConnect", 
                "company": "RetailPro",
                "category": "Retail Software",
                "launch_date": "2022-01-20",
                "revenue": "85M",
                "growth_rate": "65%",
                "market_share": "5%",
                "description": "Omnichannel retail management platform"
            },
            {
                "name": "HealthTrack", 
                "company": "HealthServices",
                "category": "Healthcare Software",
                "launch_date": "2020-10-30",
                "revenue": "150M",
                "growth_rate": "45%",
                "market_share": "10%",
                "description": "Patient management and clinical trial platform"
            }
        ]
        
        # Create detailed strength entities
        strengths = [
            # TechCorp strengths
            {
                "name": "Cloud Security Expertise",
                "company": "TechCorp",
                "description": "Industry-leading expertise in cloud security architectures and threat mitigation",
                "importance": "High"
            },
            {
                "name": "Scalable Infrastructure",
                "company": "TechCorp",
                "description": "Highly scalable and resilient infrastructure supporting millions of users",
                "importance": "High"
            },
            {
                "name": "Data Analytics Capabilities",
                "company": "TechCorp",
                "description": "Advanced data analytics and machine learning capabilities",
                "importance": "Medium"
            },
            
            # FinanceGroup strengths
            {
                "name": "Regulatory Compliance Framework",
                "company": "FinanceGroup",
                "description": "Comprehensive framework for ensuring compliance with financial regulations",
                "importance": "High"
            },
            {
                "name": "Financial Risk Management",
                "company": "FinanceGroup",
                "description": "Sophisticated risk management models and practices",
                "importance": "High"
            },
            
            # ManufactureX strengths
            {
                "name": "Supply Chain Optimization",
                "company": "ManufactureX",
                "description": "Advanced supply chain optimization algorithms and practices",
                "importance": "High"
            },
            {
                "name": "Manufacturing Automation",
                "company": "ManufactureX",
                "description": "Cutting-edge manufacturing automation technologies",
                "importance": "High"
            },
            
            # RetailPro strengths
            {
                "name": "Customer Experience Design",
                "company": "RetailPro",
                "description": "Superior customer experience design across digital and physical channels",
                "importance": "High"
            },
            {
                "name": "Inventory Management",
                "company": "RetailPro",
                "description": "AI-driven inventory management and forecasting",
                "importance": "Medium"
            },
            
            # HealthServices strengths
            {
                "name": "Clinical Data Management",
                "company": "HealthServices",
                "description": "Secure and compliant clinical data management systems",
                "importance": "High"
            },
            {
                "name": "Healthcare Interoperability",
                "company": "HealthServices",
                "description": "Leading capabilities in healthcare system interoperability",
                "importance": "Medium"
            }
        ]
        
        # Create metric entities
        metrics = [
            {"name": "revenue", "type": "financial", "description": "Total revenue generated by the company"},
            {"name": "profit", "type": "financial", "description": "Net profit after all expenses"},
            {"name": "cash flow", "type": "financial", "description": "Net cash flow from operations"},
            {"name": "ROI", "type": "financial", "description": "Return on investment for major initiatives"},
            {"name": "debt to equity", "type": "financial", "description": "Ratio of total debt to shareholders' equity"},
            {"name": "customer acquisition cost", "type": "marketing", "description": "Cost to acquire a new customer"},
            {"name": "customer lifetime value", "type": "marketing", "description": "Projected revenue from a customer over their lifetime"},
            {"name": "market share", "type": "strategic", "description": "Percentage share of the target market"},
            {"name": "employee turnover", "type": "operational", "description": "Rate at which employees leave the company"},
            {"name": "production efficiency", "type": "operational", "description": "Efficiency of production processes"},
            {"name": "innovation index", "type": "strategic", "description": "Measure of company's innovation capabilities"},
            {"name": "customer satisfaction", "type": "customer", "description": "Measure of customer satisfaction with products/services"}
        ]
        
        # Create entities in database
        for company in companies:
            neo4j.execute_query(
                "MERGE (c:Entity:Company {name: $name}) SET c += $properties",
                {"name": company["name"], "properties": company}
            )
        
        for market in markets:
            # Handle array properties for Neo4j
            market_props = market.copy()
            dominant_segments = market_props.pop("dominant_segments", [])
            emerging_trends = market_props.pop("emerging_trends", [])
            
            # Create market node
            neo4j.execute_query(
                "MERGE (m:Entity:Market {name: $name}) SET m += $properties",
                {"name": market["name"], "properties": market_props}
            )
            
            # Add array properties as separate nodes with relationships
            for segment in dominant_segments:
                neo4j.execute_query(
                    """
                    MATCH (m:Market {name: $market_name})
                    MERGE (s:Segment {name: $segment})
                    MERGE (m)-[:HAS_DOMINANT_SEGMENT]->(s)
                    """,
                    {"market_name": market["name"], "segment": segment}
                )
            
            for trend in emerging_trends:
                neo4j.execute_query(
                    """
                    MATCH (m:Market {name: $market_name})
                    MERGE (t:Trend {name: $trend})
                    MERGE (m)-[:HAS_EMERGING_TREND]->(t)
                    """,
                    {"market_name": market["name"], "trend": trend}
                )
        
        for product in products:
            company_name = product.pop("company", None)
            
            # Create product node
            neo4j.execute_query(
                "MERGE (p:Entity:Product {name: $name}) SET p += $properties",
                {"name": product["name"], "properties": product}
            )
            
            # Link product to company
            if company_name:
                neo4j.execute_query(
                    """
                    MATCH (c:Company {name: $company_name}), (p:Product {name: $product_name})
                    MERGE (c)-[:PRODUCES]->(p)
                    """,
                    {"company_name": company_name, "product_name": product["name"]}
                )
        
        for strength in strengths:
            company_name = strength.pop("company", None)
            
            # Create strength node
            neo4j.execute_query(
                "MERGE (s:Entity:Strength {name: $name}) SET s += $properties",
                {"name": strength["name"], "properties": strength}
            )
            
            # Link strength to company
            if company_name:
                neo4j.execute_query(
                    """
                    MATCH (c:Company {name: $company_name}), (s:Strength {name: $strength_name})
                    MERGE (c)-[:HAS_STRENGTH]->(s)
                    """,
                    {"company_name": company_name, "strength_name": strength["name"]}
                )
        
        for metric in metrics:
            neo4j.execute_query(
                "MERGE (m:Entity:Metric {name: $name}) SET m += $properties",
                {"name": metric["name"], "properties": metric}
            )
        
        # Create relationships
        
        # Companies operating in markets
        market_relationships = [
            ("TechCorp", "OPERATES_IN", "North America", {"market_position": "Strong", "years_present": 15}),
            ("TechCorp", "OPERATES_IN", "Europe", {"market_position": "Growing", "years_present": 8}),
            ("TechCorp", "OPERATES_IN", "Asia Pacific", {"market_position": "Emerging", "years_present": 3}),
            ("FinanceGroup", "OPERATES_IN", "North America", {"market_position": "Strong", "years_present": 25}),
            ("FinanceGroup", "OPERATES_IN", "Europe", {"market_position": "Strong", "years_present": 20}),
            ("ManufactureX", "OPERATES_IN", "Asia Pacific", {"market_position": "Strong", "years_present": 12}),
            ("ManufactureX", "OPERATES_IN", "North America", {"market_position": "Strong", "years_present": 40}),
            ("RetailPro", "OPERATES_IN", "North America", {"market_position": "Growing", "years_present": 10}),
            ("RetailPro", "OPERATES_IN", "Latin America", {"market_position": "Emerging", "years_present": 2}),
            ("HealthServices", "OPERATES_IN", "North America", {"market_position": "Strong", "years_present": 22}),
            ("HealthServices", "OPERATES_IN", "Europe", {"market_position": "Growing", "years_present": 15})
        ]
        
        for source, rel_type, target, properties in market_relationships:
            neo4j.execute_query(
                f"""
                MATCH (s:Entity {{name: $source}}), (t:Entity {{name: $target}}) 
                MERGE (s)-[r:{rel_type}]->(t)
                SET r += $properties
                """,
                {"source": source, "target": target, "properties": properties}
            )
        
        # Company competition with relationship details
        competition_relationships = [
            ("TechCorp", "COMPETES_WITH", "FinanceGroup", {"intensity": "Medium", "overlap_areas": "Financial Technology"}),
            ("TechCorp", "COMPETES_WITH", "HealthServices", {"intensity": "Low", "overlap_areas": "Healthcare Technology"}),
            ("ManufactureX", "COMPETES_WITH", "RetailPro", {"intensity": "Low", "overlap_areas": "Supply Chain"}),
            ("FinanceGroup", "COMPETES_WITH", "HealthServices", {"intensity": "Medium", "overlap_areas": "Healthcare Financing"})
        ]
        
        for source, rel_type, target, properties in competition_relationships:
            neo4j.execute_query(
                f"""
                MATCH (s:Entity {{name: $source}}), (t:Entity {{name: $target}}) 
                MERGE (s)-[r:{rel_type}]->(t)
                SET r += $properties
                """,
                {"source": source, "target": target, "properties": properties}
            )
        
        # Create partnership relationships
        partnership_relationships = [
            ("TechCorp", "PARTNERED_WITH", "ManufactureX", {"purpose": "Industry 4.0 Solutions", "start_date": "2022-03-15", "strength": "Strong"}),
            ("FinanceGroup", "PARTNERED_WITH", "RetailPro", {"purpose": "Payment Solutions", "start_date": "2021-08-10", "strength": "Medium"}),
            ("HealthServices", "PARTNERED_WITH", "TechCorp", {"purpose": "Healthcare Data Security", "start_date": "2023-01-22", "strength": "Growing"})
        ]
        
        for source, rel_type, target, properties in partnership_relationships:
            neo4j.execute_query(
                f"""
                MATCH (s:Entity {{name: $source}}), (t:Entity {{name: $target}}) 
                MERGE (s)-[r:{rel_type}]->(t)
                SET r += $properties
                """,
                {"source": source, "target": target, "properties": properties}
            )
        
        # Generate historical metric data (quarterly for 2 years)
        # This creates a richer dataset for trends and pattern analysis
        today = datetime.today()
        companies_list = [company["name"] for company in companies]
        relevant_metrics = ["revenue", "profit", "cash flow", "customer acquisition cost", 
                           "market share", "employee turnover", "production efficiency",
                           "customer satisfaction"]
        
        # Create historical metric values
        for company_name in companies_list:
            for metric_name in relevant_metrics:
                # Skip irrelevant metrics for some companies
                if (metric_name == "production efficiency" and company_name not in ["ManufactureX"]):
                    continue
                
                # Generate values for 8 quarters (2 years)
                for i in range(8):
                    quarter_date = (today - timedelta(days=90 * (8-i))).strftime("%Y-%m-%d")
                    
                    # Base values for different metrics
                    if metric_name == "revenue":
                        if company_name == "TechCorp":
                            base_value = 120000000 + (i * 5000000)  # Growing revenue
                        elif company_name == "FinanceGroup":
                            base_value = 280000000 + (i * 10000000)
                        elif company_name == "ManufactureX":
                            base_value = 190000000 + (i * 4000000)
                        elif company_name == "RetailPro":
                            base_value = 85000000 + (i * 1500000)
                        else:  # HealthServices
                            base_value = 140000000 + (i * 6000000)
                        unit = "USD"
                            
                    elif metric_name == "profit":
                        if company_name == "TechCorp":
                            base_value = 18000000 + (i * 800000)
                        elif company_name == "FinanceGroup":
                            base_value = 82000000 + (i * 1500000)
                        elif company_name == "ManufactureX":
                            base_value = 22000000 + (i * 600000)
                        elif company_name == "RetailPro":
                            base_value = 5000000 + (i * 300000)
                        else:  # HealthServices
                            base_value = 25000000 + (i * 1000000)
                        unit = "USD"
                            
                    elif metric_name == "cash flow":
                        if company_name == "TechCorp":
                            base_value = 22000000 + (i * 1000000)
                        elif company_name == "FinanceGroup":
                            base_value = 90000000 + (i * 2000000)
                        elif company_name == "ManufactureX":
                            base_value = 25000000 + (i * 800000)
                        elif company_name == "RetailPro":
                            base_value = 8000000 + (i * 400000)
                        else:  # HealthServices
                            base_value = 30000000 + (i * 1200000)
                        unit = "USD"
                            
                    elif metric_name == "customer acquisition cost":
                        if company_name == "TechCorp":
                            base_value = 5000 - (i * 200)  # Improving (decreasing) CAC
                        elif company_name == "FinanceGroup":
                            base_value = 8000 - (i * 300)
                        elif company_name == "ManufactureX":
                            base_value = 12000 - (i * 400)
                        elif company_name == "RetailPro":
                            base_value = 80 - (i * 2)
                        else:  # HealthServices
                            base_value = 9000 - (i * 350)
                        unit = "USD"
                            
                    elif metric_name == "market share":
                        if company_name == "TechCorp":
                            base_value = 8.5 + (i * 0.5)  # Growing market share
                        elif company_name == "FinanceGroup":
                            base_value = 15.2 + (i * 0.3)
                        elif company_name == "ManufactureX":
                            base_value = 12.8 + (i * 0.4)
                        elif company_name == "RetailPro":
                            base_value = 4.2 + (i * 0.2)
                        else:  # HealthServices
                            base_value = 9.5 + (i * 0.3)
                        unit = "%"
                            
                    elif metric_name == "employee turnover":
                        if company_name == "TechCorp":
                            base_value = 18.0 - (i * 0.5)  # Improving (decreasing) turnover
                        elif company_name == "FinanceGroup":
                            base_value = 12.0 - (i * 0.3)
                        elif company_name == "ManufactureX":
                            base_value = 10.0 - (i * 0.2)
                        elif company_name == "RetailPro":
                            base_value = 25.0 - (i * 0.6)
                        else:  # HealthServices
                            base_value = 14.0 - (i * 0.4)
                        unit = "%"
                            
                    elif metric_name == "production efficiency":
                        # Only relevant for ManufactureX
                        base_value = 72.0 + (i * 0.8)  # Improving efficiency
                        unit = "%"
                            
                    elif metric_name == "customer satisfaction":
                        if company_name == "TechCorp":
                            base_value = 7.8 + (i * 0.1)  # Improving satisfaction
                        elif company_name == "FinanceGroup":
                            base_value = 8.2 + (i * 0.05)
                        elif company_name == "ManufactureX":
                            base_value = 7.9 + (i * 0.08)
                        elif company_name == "RetailPro":
                            base_value = 8.0 + (i * 0.15)
                        else:  # HealthServices
                            base_value = 8.5 + (i * 0.05)
                        unit = "score"
                    else:
                        continue  # Skip unknown metrics
                    
                    # Add some variance to the data for more realism
                    variance = random.uniform(-0.05, 0.05)
                    value = base_value * (1 + variance)
                    
                    # Create the metric value node
                    metric_id = f"{company_name}_{metric_name}_{quarter_date}"
                    
                    neo4j.execute_query(
                        """
                        MATCH (c:Entity {name: $company}), (m:Entity {name: $metric})
                        MERGE (c)-[:HAS_METRIC]->(mv:MetricValue {id: $metric_id})
                        SET mv.value = $value, mv.unit = $unit, mv.timestamp = $timestamp, 
                            mv.name = $metric, mv.quarter = $quarter
                        """,
                        {
                            "company": company_name,
                            "metric": metric_name,
                            "metric_id": metric_id,
                            "value": value,
                            "unit": unit,
                            "timestamp": quarter_date,
                            "quarter": f"Q{(i % 4) + 1} {int(today.year - 2 + (i/4))}"
                        }
                    )
        
        # Add risks with more detailed information
        risks = [
            # TechCorp risks
            ("TechCorp", "financial", "decreasing market share in legacy products", 0.65, {
                "impact_area": "Revenue",
                "probability": "Medium",
                "description": "Market share for legacy software products is declining as competitors offer cloud-native alternatives",
                "mitigation_status": "In Progress"
            }),
            ("TechCorp", "operational", "talent retention issues in engineering", 0.45, {
                "impact_area": "Product Development",
                "probability": "Medium",
                "description": "Higher than industry average turnover among senior engineers",
                "mitigation_status": "Early Stage"
            }),
            ("TechCorp", "market", "new market entrants with disruptive technology", 0.58, {
                "impact_area": "Market Position",
                "probability": "Medium",
                "description": "Startups with AI-driven security solutions are gaining traction in key markets",
                "mitigation_status": "Monitoring"
            }),
            
            # FinanceGroup risks
            ("FinanceGroup", "market", "regulatory changes in EU markets", 0.78, {
                "impact_area": "Compliance",
                "probability": "High",
                "description": "New EU financial regulations will require significant changes to current offerings",
                "mitigation_status": "Advanced Planning"
            }),
            ("FinanceGroup", "operational", "legacy system integration challenges", 0.62, {
                "impact_area": "Operations",
                "probability": "Medium",
                "description": "Difficulty integrating modern solutions with legacy banking systems",
                "mitigation_status": "In Progress"
            }),
            
            # ManufactureX risks
            ("ManufactureX", "operational", "supply chain disruption", 0.82, {
                "impact_area": "Production",
                "probability": "High",
                "description": "Global supply chain disruptions affecting key component availability",
                "mitigation_status": "Active Mitigation"
            }),
            ("ManufactureX", "financial", "increasing raw material costs", 0.70, {
                "impact_area": "Cost Structure",
                "probability": "High",
                "description": "Raw material costs have increased 15% over the past year",
                "mitigation_status": "In Progress"
            }),
            
            # RetailPro risks
            ("RetailPro", "financial", "high debt levels", 0.71, {
                "impact_area": "Financial Stability",
                "probability": "High",
                "description": "Significant debt from recent expansion affecting financial flexibility",
                "mitigation_status": "Active Mitigation"
            }),
            ("RetailPro", "market", "e-commerce competition", 0.68, {
                "impact_area": "Market Share",
                "probability": "High",
                "description": "Increasing pressure from pure e-commerce players in key markets",
                "mitigation_status": "In Progress"
            }),
            
            # HealthServices risks
            ("HealthServices", "market", "new entrants in telehealth", 0.53, {
                "impact_area": "Market Position",
                "probability": "Medium",
                "description": "Technology companies entering the telehealth space with innovative solutions",
                "mitigation_status": "Early Stage"
            }),
            ("HealthServices", "operational", "data security compliance", 0.64, {
                "impact_area": "Compliance",
                "probability": "Medium",
                "description": "Increasingly complex data security and privacy regulations",
                "mitigation_status": "Ongoing"
            })
        ]
        
        for company, risk_type, description, level, properties in risks:
            risk_id = f"{company}_{risk_type}_{description.replace(' ', '_')}"
            
            # Create base risk properties
            risk_properties = {
                "type": risk_type,
                "description": description,
                "level": level
            }
            
            # Add additional properties
            risk_properties.update(properties)
            
            neo4j.execute_query(
                """
                MATCH (c:Entity {name: $company})
                MERGE (c)-[:HAS_RISK]->(r:Risk {id: $risk_id})
                SET r = $properties
                """,
                {
                    "company": company,
                    "risk_id": risk_id,
                    "properties": risk_properties
                }
            )
        
        print("Enhanced sample data added successfully!")
        
        # Count entities and relationships
        entity_count = neo4j.execute_query("MATCH (n) RETURN count(n) as count")[0]["count"]
        rel_count = neo4j.execute_query("MATCH ()-[r]->() RETURN count(r) as count")[0]["count"]
        
        print(f"Graph now contains {entity_count} entities and {rel_count} relationships")
        
        return True
    
    except Exception as e:
        print(f"Error adding sample data: {e}")
        return False
    finally:
        neo4j.close()

if __name__ == "__main__":
    success = populate_test_data()
    sys.exit(0 if success else 1)