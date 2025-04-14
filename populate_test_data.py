#!/usr/bin/env python3
"""
Script to populate the knowledge graph with sample entities and relationships for testing.
"""

import sys
from knowledge_graph.neo4j_manager import Neo4jManager

def populate_test_data():
    """Add sample business entities and relationships to the knowledge graph."""
    # Initialize Neo4j manager
    neo4j = Neo4jManager()
    neo4j.connect()
    
    try:
        print("Adding sample entities and relationships to knowledge graph...")
        
        # Create company entities
        companies = [
            {"name": "TechCorp", "industry": "Technology", "revenue": "500M", "employees": 1200},
            {"name": "FinanceGroup", "industry": "Financial Services", "revenue": "1.2B", "employees": 3500},
            {"name": "ManufactureX", "industry": "Manufacturing", "revenue": "800M", "employees": 5000},
            {"name": "RetailPro", "industry": "Retail", "revenue": "350M", "employees": 2800},
            {"name": "HealthServices", "industry": "Healthcare", "revenue": "600M", "employees": 4200}
        ]
        
        # Create market entities
        markets = [
            {"name": "North America", "size": "Large", "growth_rate": "4.5%"},
            {"name": "Europe", "size": "Large", "growth_rate": "3.2%"},
            {"name": "Asia Pacific", "size": "Very Large", "growth_rate": "7.8%"},
            {"name": "Latin America", "size": "Medium", "growth_rate": "5.1%"}
        ]
        
        # Create metric entities
        metrics = [
            {"name": "revenue", "type": "financial"},
            {"name": "profit", "type": "financial"},
            {"name": "cash flow", "type": "financial"},
            {"name": "ROI", "type": "financial"},
            {"name": "customer acquisition cost", "type": "marketing"},
            {"name": "employee turnover", "type": "operational"},
            {"name": "production efficiency", "type": "operational"}
        ]
        
        # Create entities
        for company in companies:
            neo4j.execute_query(
                "MERGE (c:Entity:Company {name: $name}) SET c += $properties",
                {"name": company["name"], "properties": company}
            )
        
        for market in markets:
            neo4j.execute_query(
                "MERGE (m:Entity:Market {name: $name}) SET m += $properties",
                {"name": market["name"], "properties": market}
            )
        
        for metric in metrics:
            neo4j.execute_query(
                "MERGE (m:Entity:Metric {name: $name}) SET m += $properties",
                {"name": metric["name"], "properties": metric}
            )
        
        # Create relationships
        
        # Companies operating in markets
        market_relationships = [
            ("TechCorp", "OPERATES_IN", "North America"),
            ("TechCorp", "OPERATES_IN", "Europe"),
            ("TechCorp", "OPERATES_IN", "Asia Pacific"),
            ("FinanceGroup", "OPERATES_IN", "North America"),
            ("FinanceGroup", "OPERATES_IN", "Europe"),
            ("ManufactureX", "OPERATES_IN", "Asia Pacific"),
            ("ManufactureX", "OPERATES_IN", "North America"),
            ("RetailPro", "OPERATES_IN", "North America"),
            ("RetailPro", "OPERATES_IN", "Latin America"),
            ("HealthServices", "OPERATES_IN", "North America"),
            ("HealthServices", "OPERATES_IN", "Europe")
        ]
        
        for source, rel_type, target in market_relationships:
            neo4j.execute_query(
                f"MATCH (s:Entity {{name: $source}}), (t:Entity {{name: $target}}) "
                f"MERGE (s)-[:{rel_type}]->(t)",
                {"source": source, "target": target}
            )
        
        # Company competition
        competition_relationships = [
            ("TechCorp", "COMPETES_WITH", "FinanceGroup"),
            ("ManufactureX", "COMPETES_WITH", "RetailPro"),
            ("HealthServices", "COMPETES_WITH", "FinanceGroup")
        ]
        
        for source, rel_type, target in competition_relationships:
            neo4j.execute_query(
                f"MATCH (s:Entity {{name: $source}}), (t:Entity {{name: $target}}) "
                f"MERGE (s)-[:{rel_type}]->(t)",
                {"source": source, "target": target}
            )
        
        # Company metrics
        metric_values = [
            ("TechCorp", "revenue", 525000000, "USD", "2024-03-31"),
            ("TechCorp", "profit", 78000000, "USD", "2024-03-31"),
            ("TechCorp", "cash flow", 105000000, "USD", "2024-03-31"),
            ("TechCorp", "employee turnover", 15.3, "%", "2024-03-31"),
            ("FinanceGroup", "revenue", 1200000000, "USD", "2024-03-31"),
            ("FinanceGroup", "profit", 350000000, "USD", "2024-03-31"),
            ("ManufactureX", "production efficiency", 78.5, "%", "2024-03-31"),
            ("RetailPro", "customer acquisition cost", 85.2, "USD", "2024-03-31"),
            ("HealthServices", "revenue", 612000000, "USD", "2024-03-31")
        ]
        
        for company, metric, value, unit, date in metric_values:
            metric_id = f"{company}_{metric}_{date}"
            neo4j.execute_query(
                "MATCH (c:Entity {name: $company}), (m:Entity {name: $metric}) "
                "MERGE (c)-[:HAS_METRIC]->(mv:MetricValue {id: $metric_id}) "
                "SET mv.value = $value, mv.unit = $unit, mv.date = $date, mv.name = $metric",
                {
                    "company": company, 
                    "metric": metric,
                    "metric_id": metric_id,
                    "value": value,
                    "unit": unit,
                    "date": date
                }
            )
        
        # Add some risks
        risks = [
            ("TechCorp", "financial", "decreasing market share", 0.65),
            ("TechCorp", "operational", "talent retention issues", 0.45),
            ("FinanceGroup", "market", "regulatory changes", 0.78),
            ("ManufactureX", "operational", "supply chain disruption", 0.82),
            ("RetailPro", "financial", "high debt levels", 0.71),
            ("HealthServices", "market", "new entrants", 0.53)
        ]
        
        for company, risk_type, description, level in risks:
            risk_id = f"{company}_{risk_type}_{description.replace(' ', '_')}"
            neo4j.execute_query(
                "MATCH (c:Entity {name: $company}) "
                "MERGE (c)-[:HAS_RISK]->(r:Risk {id: $risk_id}) "
                "SET r.type = $risk_type, r.description = $description, r.level = $level",
                {
                    "company": company,
                    "risk_id": risk_id,
                    "risk_type": risk_type,
                    "description": description,
                    "level": level
                }
            )
        
        print("Sample data added successfully!")
        
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