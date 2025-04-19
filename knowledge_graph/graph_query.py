"""
Graph query module for the knowledge graph-based business consulting system.
Provides specialized Cypher queries for business risk analysis and insights.
"""

import logging
from typing import List, Dict, Any, Optional
import json
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GraphQueryManager:
    """
    Manages specialized Cypher queries for business analysis.
    Works with Neo4jManager to execute queries and return structured results.
    """
    
    def __init__(self, neo4j_manager):
        """
        Initialize with a Neo4jManager instance.
        
        Args:
            neo4j_manager: Instance of Neo4jManager to execute queries
        """
        self.neo4j_manager = neo4j_manager
        logger.info("Graph Query Manager initialized")
    
    def get_entity_summary(self, entity_name: str) -> Dict[str, Any]:
        """
        Get a comprehensive summary of an entity from the knowledge graph.
        
        Args:
            entity_name: Name of the entity to analyze
            
        Returns:
            dict: Entity summary data including relationships and metrics
        """
        # Query to get basic entity information
        entity_query = """
        MATCH (e:Entity {name: $entity_name})
        RETURN e
        """
        
        # Query to get entity relationships
        relationships_query = """
        MATCH (e:Entity {name: $entity_name})-[r]->(target)
        WITH type(r) AS relationship_type, 
            target.name AS target_name,
            labels(target) AS target_types, 
            COUNT(*) AS count
        ORDER BY count DESC
        RETURN relationship_type, target_name, target_types, count
        """

        # Query to get incoming relationships
        incoming_query = """
        MATCH (source)-[r]->(e:Entity {name: $entity_name})
        WITH type(r) AS relationship_type, 
            source.name AS source_name,
            labels(source) AS source_types,
            COUNT(*) AS count
        ORDER BY count DESC
        RETURN relationship_type, source_name, source_types, count
        """
        
        # Query to get financial metrics if they exist
        financials_query = """
        MATCH (e:Entity {name: $entity_name})-[:HAS_METRIC]->(m:Metric)
        RETURN m.name AS metric_name, m.value AS metric_value, 
               m.unit AS metric_unit, m.timestamp AS metric_date
        """
        
        # Execute queries
        try:
            entity_data = self.neo4j_manager.execute_query(
                entity_query, {"entity_name": entity_name})
            
            relationships = self.neo4j_manager.execute_query(
                relationships_query, {"entity_name": entity_name})
            
            incoming = self.neo4j_manager.execute_query(
                incoming_query, {"entity_name": entity_name})
            
            financials = self.neo4j_manager.execute_query(
                financials_query, {"entity_name": entity_name})
            
            # Compile results
            summary = {
                "entity": entity_data[0]["e"] if entity_data else None,
                "outgoing_relationships": relationships,
                "incoming_relationships": incoming,
                "financial_metrics": financials,
                "timestamp": datetime.now().isoformat()
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting entity summary for {entity_name}: {e}")
            return {"error": str(e)}
    
    def search_entities(self, name_pattern: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for entities by name pattern.
        
        Args:
            name_pattern: Pattern to search for
            limit: Maximum number of results to return
            
        Returns:
            list: Matching entities with basic information
        """
        query = """
        MATCH (e:Entity)
        WHERE e.name =~ $pattern
        RETURN e.name AS name, labels(e) AS types, 
               COUNT {(e)--()} AS connection_count
        ORDER BY connection_count DESC
        LIMIT $limit
        """
        
        pattern = f"(?i).*{name_pattern}.*"  # Case-insensitive pattern match
        
        try:
            results = self.neo4j_manager.execute_query(
                query, {"pattern": pattern, "limit": limit})
            return results
        except Exception as e:
            logger.error(f"Error searching entities with pattern {name_pattern}: {e}")
            return []
    
    def get_risk_metrics(self, risk_type: str) -> List[Dict[str, Any]]:
        """
        Get risk-related metrics from the knowledge graph.
        
        Args:
            risk_type: Type of risk to analyze (financial, operational, market)
            
        Returns:
            list: Risk metrics data
        """
        # Different queries based on risk type
        queries = {
            "financial": """
                MATCH (e:Entity)-[:HAS_METRIC]->(m:Metric)
                WHERE m.name IN ['revenue', 'profit', 'cash_flow', 'debt_to_equity', 'current_ratio']
                WITH e, m, 
                    CASE
                        WHEN m.name = 'debt_to_equity' AND m.value > 2.0 THEN 1
                        WHEN m.name = 'current_ratio' AND m.value < 1.0 THEN 1
                        WHEN (m.name = 'revenue' OR m.name = 'profit') AND EXISTS((m)<-[:DECREASED]-()) THEN 1
                        WHEN m.name = 'cash_flow' AND m.value < 0 THEN 1
                        ELSE 0
                    END AS risk_count
                WHERE risk_count > 0
                RETURN e.name AS entity, m.name AS metric, m.value AS value, 
                       risk_count, m.unit AS unit
                ORDER BY risk_count DESC, m.value ASC
                LIMIT 20
            """,
            
            "operational": """
                MATCH (e:Entity)-[:HAS_PROCESS]->(p:Process)-[:HAS_ISSUE]->(i)
                RETURN e.name AS entity, p.name AS process, i.description AS issue,
                       COUNT(i) AS risk_count
                ORDER BY risk_count DESC
                LIMIT 20
            """,
            
            "market": """
                MATCH (e:Entity)-[:OPERATES_IN|COMPETES_WITH]->(m)
                MATCH (m)-[:HAS_EMERGING_TREND]->(t)
                WHERE t.name CONTAINS 'declin' OR t.name CONTAINS 'decrease' 
                      OR t.name CONTAINS 'disrupt' OR t.name CONTAINS 'threat'
                RETURN e.name AS entity, m.name AS market, t.name AS trend,
                       COUNT(t) AS risk_count
                ORDER BY risk_count DESC
                LIMIT 20
            """
        }
        
        if risk_type not in queries:
            logger.warning(f"Invalid risk type: {risk_type}")
            return []
        
        try:
            results = self.neo4j_manager.execute_query(queries[risk_type])
            return results
        except Exception as e:
            logger.error(f"Error getting {risk_type} risk metrics: {e}")
            return []
    
    def find_strategic_opportunities(self, entity_name: str) -> List[Dict[str, Any]]:
        """
        Find strategic opportunities for an entity based on graph patterns.
    
        Args:
            entity_name: Name of the entity to analyze
        
        Returns:
            list: Strategic opportunities with supporting evidence
        """
        # Query for potential partnership opportunities
        partnership_query = """
        MATCH (e:Entity {name: $entity_name})-[:COMPETES_WITH]->(m:Market)<-[:COMPETES_WITH]-(partner:Entity)
        WHERE NOT (e)-[:PARTNERED_WITH]-(partner)
        AND COUNT {(partner)--()} > 5  // Only well-connected entities
        WITH e, partner, COUNT(m) AS shared_markets
        MATCH (partner)-[:HAS_STRENGTH]->(s:Strength)
        WHERE NOT (e)-[:HAS_STRENGTH]->(:Strength {name: s.name})
        RETURN partner.name AS potential_partner, 
            COLLECT(DISTINCT s.name) AS complementary_strengths,
            shared_markets
        ORDER BY shared_markets DESC, SIZE(complementary_strengths) DESC
        LIMIT 10
        """
        
        # Query for potential expansion markets
        expansion_query = """
        MATCH (e:Entity {name: $entity_name})-[:HAS_STRENGTH]->(s:Strength)
        MATCH (m:Market)
        WHERE NOT (e)-[:COMPETES_WITH|OPERATES_IN]->(m)
        AND EXISTS {
            MATCH (other:Entity)-[:COMPETES_WITH]->(m)
            WHERE (other)-[:HAS_STRENGTH]->(:Strength {name: s.name})
        }
        RETURN m.name AS potential_market,
               COLLECT(DISTINCT s.name) AS relevant_strengths,
               COUNT(DISTINCT s) AS strength_count
        ORDER BY strength_count DESC
        LIMIT 10
        """
        
        try:
            partnerships = self.neo4j_manager.execute_query(
                partnership_query, {"entity_name": entity_name})
            
            expansions = self.neo4j_manager.execute_query(
                expansion_query, {"entity_name": entity_name})
            
            return {
                "partnership_opportunities": partnerships,
                "market_expansion_opportunities": expansions
            }
        except Exception as e:
            logger.error(f"Error finding opportunities for {entity_name}: {e}")
            return {"error": str(e)}
    
    def export_graph_segment(self, entity_name: str, depth: int = 2) -> Dict[str, Any]:
        """
        Export a segment of the graph centered on an entity for visualization.
    
        Args:
            entity_name: Center entity name
            depth: Traversal depth from center entity (ignored in query)
        
        Returns:
            dict: Graph data in a visualization-friendly format
        """
        # Use fixed depths in Neo4j 5.x which doesn't allow dynamic path lengths via parameters
        max_depth = min(depth, 3)  # Limit depth to 3 max for performance
    
        if max_depth == 1:
            query = """
            MATCH path = (e:Entity {name: $entity_name})-[*1..1]-(related)
            WITH nodes(path) AS nodes, relationships(path) AS rels
            UNWIND nodes AS node
            WITH COLLECT(DISTINCT node) AS nodes, rels
            UNWIND rels AS rel
            WITH nodes, COLLECT(DISTINCT rel) AS relationships
            RETURN nodes, relationships
            """
        elif max_depth == 2:
            query = """
            MATCH path = (e:Entity {name: $entity_name})-[*1..2]-(related)
            WITH nodes(path) AS nodes, relationships(path) AS rels
            UNWIND nodes AS node
            WITH COLLECT(DISTINCT node) AS nodes, rels
            UNWIND rels AS rel
            WITH nodes, COLLECT(DISTINCT rel) AS relationships
            RETURN nodes, relationships
            """
        else:  # max_depth == 3
            query = """
            MATCH path = (e:Entity {name: $entity_name})-[*1..3]-(related)
            WITH nodes(path) AS nodes, relationships(path) AS rels
            UNWIND nodes AS node
            WITH COLLECT(DISTINCT node) AS nodes, rels
            UNWIND rels AS rel
            WITH nodes, COLLECT(DISTINCT rel) AS relationships
            RETURN nodes, relationships
            """
        
        try:
            result = self.neo4j_manager.execute_query(
                query, {"entity_name": entity_name, "depth": depth})
            
            if not result:
                return {"nodes": [], "links": []}
            
            # Process nodes and relationships into visualization format
            nodes_set = set()
            nodes = []
            links = []
            
            for node in result[0]["nodes"]:
                if id(node) not in nodes_set:
                    nodes_set.add(id(node))
                    node_data = dict(node)
                    node_data["id"] = id(node)
                    # Extract labels
                    if hasattr(node, "labels"):
                        node_data["labels"] = list(node.labels)
                    nodes.append(node_data)
            
            for rel in result[0]["relationships"]:
                try:
                    # First try accessing as an object with attributes (Neo4j 4.x style)
                    source_node = rel.start_node
                    target_node = rel.end_node
                    rel_type = type(rel).__name__
        
                    links.append({
                        "source": id(source_node),
                        "target": id(target_node),
                        "type": rel_type
                    })
                except AttributeError:
                    # If the relationship is a tuple or different structure
                    logger.warning(f"Relationship returned in unexpected format: {type(rel)}")
                    # Try to extract nodes from the query result in a different way
                    # This is a simplified fallback - you might need to adjust based on your Neo4j version
                    links.append({
                        "source": id(result[0]["nodes"][0]),  # Use first node as source
                        "target": id(result[0]["nodes"][-1]), # Use last node as target
                        "type": "RELATED_TO"  # Generic type
                    })
            
            # Save to file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"entity_{entity_name.replace(' ', '_')}_{timestamp}.json"
            filepath = f"knowledge_graph/exports/{filename}"
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump({"nodes": nodes, "links": links}, f, indent=2)
            
            logger.info(f"Exported graph segment for {entity_name} to {filepath}")
            
            return {
                "nodes": nodes,
                "links": links,
                "exported_file": filepath
            }
        except Exception as e:
            logger.error(f"Error exporting graph for {entity_name}: {e}")
            return {"error": str(e)}
    
    def run_risk_query(self, risk_type: str) -> List[Dict[str, Any]]:
        """
        Run a specialized risk query for the risk engine.
        
        Args:
            risk_type: Type of risk to analyze
            
        Returns:
            list: Risk data for analysis
        """
        # This method is called by the risk_engine.py module
        return self.get_risk_metrics(risk_type)