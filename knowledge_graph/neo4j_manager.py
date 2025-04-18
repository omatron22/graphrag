"""
Neo4j database manager for the knowledge graph component.
Handles connection, transaction management, and query execution.
"""

import logging
import json
from datetime import datetime
import re
from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable, AuthError
import config

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Neo4jManager:
    """Manages Neo4j database operations for the knowledge graph"""
    
    def __init__(self, uri=None, user=None, password=None):
        """Initialize with connection parameters"""
        self.uri = uri or config.NEO4J_URI
        self.user = user or config.NEO4J_USER
        self.password = password or config.NEO4J_PASSWORD
        self.driver = None
        
    def connect(self):
        """Establish connection to Neo4j database"""
        try:
            self.driver = GraphDatabase.driver(
                self.uri,
                auth=(self.user, self.password)
            )
            # Test connection
            with self.driver.session() as session:
                result = session.run("RETURN 'Connection test' AS message")
                result.single()
            logger.info(f"Connected to Neo4j at {self.uri}")
            return True
        except (ServiceUnavailable, AuthError) as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            return False
            
    def close(self):
        """Close the Neo4j connection"""
        if self.driver:
            self.driver.close()
            logger.info("Neo4j connection closed")
            
    def verify_indexes(self):
        """Create necessary indexes if they don't exist"""
        indexes = [
            "CREATE INDEX entity_name IF NOT EXISTS FOR (e:Entity) ON (e.name)",
            "CREATE INDEX document_id IF NOT EXISTS FOR (d:Document) ON (d.id)",
            "CREATE INDEX concept_name IF NOT EXISTS FOR (c:Concept) ON (c.name)",
            "CREATE INDEX risk_type IF NOT EXISTS FOR (r:Risk) ON (r.type)"
        ]
        
        with self.driver.session() as session:
            for index_query in indexes:
                session.run(index_query)
            logger.info("Verified all required indexes")
            
    def execute_query(self, query, parameters=None):
        """Execute a Cypher query and return results with better error handling"""
        if not self.driver:
            if not self.connect():
                raise ConnectionError("Failed to connect to Neo4j database")
                
        try:
            with self.driver.session() as session:
                result = session.run(query, parameters or {})
                # Explicitly collect all records before closing the session
                records = [record.data() for record in result]
                return records
        except Exception as e:
            logger.error(f"Query execution failed: {query}")
            logger.error(f"Error: {e}")
            raise
            
    def create_entity(self, entity_type, properties):
        """Create a new entity node in the graph"""
        query = f"""
        CREATE (e:{entity_type} $properties)
        RETURN e
        """
        return self.execute_query(query, {"properties": properties})
        
    def create_relationship(self, from_node, relationship, to_node, properties=None):
        """Create a relationship between two nodes"""
        query = f"""
        MATCH (a), (b)
        WHERE id(a) = $from_id AND id(b) = $to_id
        CREATE (a)-[r:{relationship} $properties]->(b)
        RETURN r
        """
        params = {
            "from_id": from_node,
            "to_id": to_node,
            "properties": properties or {}
        }
        return self.execute_query(query, params)
        
    def add_triplet(self, subject_type, subject_props, predicate, object_type, object_props, 
                   rel_props=None):
        """Add a subject-predicate-object triplet to the graph"""
        query = f"""
        MERGE (s:{subject_type} {{name: $subject_name}})
        ON CREATE SET s += $subject_props
        
        MERGE (o:{object_type} {{name: $object_name}})
        ON CREATE SET o += $object_props
        
        CREATE (s)-[r:{predicate} $rel_props]->(o)
        RETURN s, r, o
        """
        
        params = {
            "subject_name": subject_props.get("name"),
            "subject_props": subject_props,
            "object_name": object_props.get("name"),
            "object_props": object_props,
            "rel_props": rel_props or {}
        }
        
        return self.execute_query(query, params)
        
    def get_connected_nodes(self, node_id):
        """Get all nodes connected to the specified node"""
        query = """
        MATCH (n)-[r]-(m)
        WHERE id(n) = $node_id
        RETURN m, r, n
        """
        return self.execute_query(query, {"node_id": node_id})
    
    def fix_cypher_query(query):
        """Fix common Cypher syntax issues for Neo4j 5.x compatibility"""
        # Fix SIZE pattern expressions
        query = re.sub(r'SIZE\(\(([a-zA-Z0-9_]+)\)--\(\)\)', r'size([(\1)--() | 1])', query)
    
        # Fix GROUP BY clauses
        if "GROUP BY" in query:
            parts = query.split("GROUP BY")
            before_group = parts[0].strip()
            group_clause = parts[1].strip()
        
            # Find RETURN clause
            return_parts = group_clause.split("RETURN")
        
            if len(return_parts) > 1:
                group_columns = return_parts[0].strip()
                return_clause = "RETURN" + return_parts[1]
            
                # Recreate with WITH instead of GROUP BY
                query = f"{before_group}\nWITH {group_columns}\n{return_clause}"
    
        return query

    
    def clear_database(self, confirm=False):
        """Delete all nodes and relationships (use with caution!)"""
        if not confirm:
            logger.warning("Database clear operation requires confirmation")
            return False
            
        query = "MATCH (n) DETACH DELETE n"
        self.execute_query(query)
        logger.warning("Database cleared - all nodes and relationships deleted")
        return True
        
    def get_risk_factors(self, entity_name):
        """Get all risk factors associated with an entity"""
        query = """
        MATCH (e:Entity {name: $name})-[:HAS_RISK]->(r:Risk)
        RETURN r.type as risk_type, r.level as risk_level, r.description as description
        ORDER BY r.level DESC
        """
        return self.execute_query(query, {"name": entity_name})
        
    def get_related_strategies(self, risk_id):
        """Get recommended strategies for a given risk"""
        query = """
        MATCH (r:Risk)-[:HAS_STRATEGY]->(s:Strategy)
        WHERE id(r) = $risk_id
        RETURN s.name as name, s.description as description, s.impact as impact
        ORDER BY s.impact DESC
        """
        return self.execute_query(query, {"risk_id": risk_id})
    
    def find_entity(self, entity_name, entity_types=None):
        """
        Find entity nodes by name, optionally filtering by type
        
        Args:
            entity_name (str): Name of the entity to find
            entity_types (list, optional): List of entity types to filter by
            
        Returns:
            list: Matching entity nodes
        """
        if entity_types:
            # Convert list of types to Cypher label expression
            type_filter = " OR ".join([f"n:{entity_type}" for entity_type in entity_types])
            query = f"""
            MATCH (n)
            WHERE (n.name = $name OR n.name =~ $fuzzy_name) AND ({type_filter})
            RETURN n, labels(n) as types
            LIMIT 10
            """
        else:
            query = """
            MATCH (n)
            WHERE n.name = $name OR n.name =~ $fuzzy_name
            RETURN n, labels(n) as types
            LIMIT 10
            """
            
        # Add case-insensitive and fuzzy matching
        fuzzy_name = f"(?i).*{entity_name}.*"
        
        return self.execute_query(query, {"name": entity_name, "fuzzy_name": fuzzy_name})

    def import_triplets_batch(self, triplets, batch_size=100):
        """
        Import a large batch of triplets efficiently
        
        Args:
            triplets (list): List of triplet dictionaries 
                            with subject, predicate, object data
            batch_size (int): Number of triplets to process in each transaction
            
        Returns:
            dict: Import statistics
        """
        if not triplets:
            return {"imported": 0, "errors": 0}
        
        stats = {"imported": 0, "errors": 0}
        batches = [triplets[i:i+batch_size] for i in range(0, len(triplets), batch_size)]
        
        logger.info(f"Importing {len(triplets)} triplets in {len(batches)} batches")
        
        for batch_idx, batch in enumerate(batches):
            try:
                with self.driver.session() as session:
                    # Create unwind query for batch insertion
                    query = """
                    UNWIND $batch AS triplet
                    
                    MERGE (s {name: triplet.subject})
                    ON CREATE SET s:Entity, s.created_at = datetime(), 
                                  s += triplet.subject_props
                    
                    MERGE (o {name: triplet.object})
                    ON CREATE SET o:Entity, o.created_at = datetime(), 
                                  o += triplet.object_props
                    
                    // Check if relationship already exists to avoid duplicates
                    OPTIONAL MATCH (s)-[existing:PLACEHOLDER {context: triplet.context}]->(o)
                    WHERE type(existing) = triplet.predicate
                    
                    // Create relationship if it doesn't exist
                    FOREACH(_ IN CASE WHEN existing IS NULL THEN [1] ELSE [] END |
                        CREATE (s)-[r:PLACEHOLDER]->(o)
                        SET r = triplet.rel_props,
                            r.created_at = datetime(),
                            r.context = triplet.context,
                            r.confidence = triplet.confidence
                    )
                    
                    WITH s, o, triplet
                    // Set the proper relationship type using apoc.create.relationship
                    CALL apoc.create.relationship(s, triplet.predicate, 
                        {context: triplet.context, 
                         created_at: datetime(), 
                         confidence: triplet.confidence}, o) 
                    YIELD rel
                    
                    RETURN COUNT(*) as added
                    """
                    
                    # Format batch data
                    batch_data = []
                    for t in batch:
                        batch_item = {
                            "subject": t.get("subject", ""),
                            "subject_props": {
                                "name": t.get("subject", ""),
                                "type": t.get("subject_type", "Entity")
                            },
                            "predicate": t.get("predicate", "RELATED_TO"),
                            "object": t.get("object", ""),
                            "object_props": {
                                "name": t.get("object", ""),
                                "type": t.get("object_type", "Entity")
                            },
                            "rel_props": {
                                "source": t.get("extraction_method", "unknown"),
                                "timestamp": t.get("timestamp", datetime.now().isoformat())
                            },
                            "context": t.get("context", ""),
                            "confidence": t.get("confidence", 0.5)
                        }
                        batch_data.append(batch_item)
                    
                    result = session.run(query.replace("PLACEHOLDER", "TEMP_REL"), 
                                       {"batch": batch_data})
                    added = result.single().get("added", 0)
                    stats["imported"] += added
                    
                    logger.info(f"Batch {batch_idx+1}/{len(batches)}: Imported {added} triplets")
                    
            except Exception as e:
                logger.error(f"Error importing batch {batch_idx+1}: {e}")
                stats["errors"] += len(batch)
        
        return stats

    def run_graph_analytics(self, algorithm, parameters=None):
        """
        Run graph analytics algorithms using the Neo4j Graph Data Science library
        
        Args:
            algorithm (str): Name of the algorithm to run
            parameters (dict, optional): Algorithm parameters
            
        Returns:
            dict: Algorithm results
        """
        supported_algorithms = {
            "pagerank": {
                "query": """
                CALL gds.pageRank.stream($config)
                YIELD nodeId, score
                MATCH (n) WHERE id(n) = nodeId
                RETURN n.name AS entity, score
                ORDER BY score DESC
                LIMIT 20
                """,
                "default_config": {
                    "nodeProjection": "*",
                    "relationshipProjection": "*",
                    "maxIterations": 20,
                    "dampingFactor": 0.85
                }
            },
            "community_detection": {
                "query": """
                CALL gds.louvain.stream($config)
                YIELD nodeId, communityId
                MATCH (n) WHERE id(n) = nodeId
                RETURN n.name AS entity, communityId, count(*) as community_size
                ORDER BY communityId
                """,
                "default_config": {
                    "nodeProjection": "*",
                    "relationshipProjection": "*",
                    "includeIntermediateCommunities": False
                }
            },
            "centrality": {
                "query": """
                CALL gds.betweenness.stream($config)
                YIELD nodeId, score
                MATCH (n) WHERE id(n) = nodeId
                RETURN n.name AS entity, score
                ORDER BY score DESC
                LIMIT 20
                """,
                "default_config": {
                    "nodeProjection": "*",
                    "relationshipProjection": "*"
                }
            },
            "similarity": {
                "query": """
                CALL gds.nodeSimilarity.stream($config)
                YIELD node1, node2, similarity
                MATCH (n1) WHERE id(n1) = node1
                MATCH (n2) WHERE id(n2) = node2
                RETURN n1.name AS entity1, n2.name AS entity2, similarity
                ORDER BY similarity DESC
                LIMIT 100
                """,
                "default_config": {
                    "nodeProjection": "*",
                    "relationshipProjection": "*",
                    "topK": 10,
                    "similarityCutoff": 0.5
                }
            }
        }
        
        if algorithm not in supported_algorithms:
            raise ValueError(f"Unsupported algorithm: {algorithm}. " +
                           f"Supported algorithms: {list(supported_algorithms.keys())}")
        
        algo_config = supported_algorithms[algorithm]
        config = algo_config["default_config"].copy()
        
        # Update with user parameters if provided
        if parameters:
            config.update(parameters)
        
        return self.execute_query(algo_config["query"], {"config": config})

    def get_business_competitors(self, company_name, limit=10):
        """
        Find competitors for a given company
        
        Args:
            company_name (str): Name of the company
            limit (int): Maximum number of competitors to return
            
        Returns:
            list: Competitor entities with relationship data
        """
        query = """
        MATCH (c:Entity {name: $company_name})-[:COMPETES_IN]->(m:Market)
        MATCH (competitor:Entity)-[:COMPETES_IN]->(m)
        WHERE competitor <> c
        WITH competitor, count(m) as shared_markets
        
        // Get strengths of competitor
        OPTIONAL MATCH (competitor)-[:HAS_STRENGTH]->(s:Strength)
        WITH competitor, shared_markets, collect(s.name) as strengths
        
        // Get any direct competitor relationships
        OPTIONAL MATCH (c:Entity {name: $company_name})-[r:COMPETES_WITH|COMPETITOR_OF]->(competitor)
        
        RETURN competitor.name as name, 
               shared_markets,
               strengths,
               EXISTS(r) as direct_competitor,
               CASE WHEN EXISTS(r) THEN r.context ELSE NULL END as context
        ORDER BY shared_markets DESC, direct_competitor DESC
        LIMIT $limit
        """
        return self.execute_query(query, {"company_name": company_name, "limit": limit})
    def run_risk_query(self, risk_type):
        """
        Execute risk-specific queries for the risk analyzer
    
        Args:
            risk_type (str): Type of risk to analyze (financial, operational, market)
        
        Returns:
            list: Risk data for analysis
        """
        if risk_type == "financial":
            query = """
            MATCH (e:Entity)-[:HAS_METRIC]->(m:Metric)
            WHERE m.name IN ['revenue', 'profit', 'cash_flow', 'debt_to_equity', 'current_ratio']
            WITH e, m, COUNT(*) as risk_count
            RETURN e.name as entity, m.name as metric, m.value as value, 
                m.unit as unit, risk_count
            ORDER BY risk_count DESC
            LIMIT 20
            """
        elif risk_type == "operational":
            query = """
            MATCH (e:Entity)-[:HAS_PROCESS]->(p:Process)-[:HAS_ISSUE]->(i)
            WITH e, p, i, COUNT(*) as risk_count
            RETURN e.name as entity, p.name as process, i.description as issue, risk_count
            ORDER BY risk_count DESC
            LIMIT 20
            """
        elif risk_type == "market":
            query = """
            MATCH (e:Entity)-[:OPERATES_IN|COMPETES_IN]->(m)
            MATCH (m)-[:HAS_TREND|SHOWS]->(t)
            WHERE t.name CONTAINS 'declin' OR t.name CONTAINS 'decrease'
            WITH e, m, t, COUNT(*) as risk_count
            RETURN e.name as entity, m.name as market, t.name as trend, risk_count
            ORDER BY risk_count DESC
            LIMIT 20
            """
        else:
            return []
        
        return self.execute_query(query)

    def get_business_risks(self, entity_name=None, risk_types=None, min_level=None):
        """
        Get business risks from the knowledge graph
        
        Args:
            entity_name (str, optional): Name of specific entity
            risk_types (list, optional): List of risk types to filter by
            min_level (float, optional): Minimum risk level (0-1)
            
        Returns:
            list: Risk entities with related data
        """
        params = {}
        
        if entity_name:
            entity_filter = "AND (e.name = $entity_name)"
            params["entity_name"] = entity_name
        else:
            entity_filter = ""
        
        if risk_types:
            type_filter = "AND r.type IN $risk_types"
            params["risk_types"] = risk_types
        else:
            type_filter = ""
        
        if min_level is not None:
            level_filter = "AND r.level >= $min_level"
            params["min_level"] = min_level
        else:
            level_filter = ""
        
        query = f"""
        MATCH (e:Entity)-[:HAS_RISK]->(r:Risk)
        WHERE true {entity_filter} {type_filter} {level_filter}
        
        // Get related mitigation strategies if any
        OPTIONAL MATCH (r)-[:HAS_MITIGATION]->(s:Strategy)
        
        WITH e, r, collect(s) as strategies
        
        RETURN e.name as entity,
               r.type as risk_type,
               r.level as risk_level,
               r.description as description,
               r.impact as impact,
               r.source as source,
               strategies
        ORDER BY risk_level DESC
        """
        
        return self.execute_query(query, params)

    def export_subgraph(self, center_entity, relationship_types=None, 
                      max_distance=2, format="json"):
        """
        Export a subgraph around a central entity
        
        Args:
            center_entity (str): Central entity name
            relationship_types (list, optional): List of relationship types to include
            max_distance (int): Maximum path length from center entity
            format (str): Output format (json, graphml, cypher)
            
        Returns:
            dict: Exported subgraph data
        """
        params = {
            "center_entity": center_entity,
            "max_distance": max_distance
        }
        
        if relationship_types:
            rel_filter = "WHERE type(r) IN $relationship_types"
            params["relationship_types"] = relationship_types
        else:
            rel_filter = ""
        
        query = f"""
        MATCH path = (center:Entity {{name: $center_entity}})-[r*1..$max_distance]-(connected)
        {rel_filter}
        WITH nodes(path) as nodes, relationships(path) as rels
        UNWIND nodes as node
        WITH COLLECT(DISTINCT node) as nodes, rels
        UNWIND rels as rel
        RETURN COLLECT(DISTINCT nodes) as nodes, COLLECT(DISTINCT rel) as relationships
        """
        
        result = self.execute_query(query, params)
        
        if not result or not result[0]['nodes']:
            logger.warning(f"No subgraph found for entity: {center_entity}")
            return {"nodes": [], "relationships": []}
        
        # Process result based on requested format
        if format == "json":
            # Convert to a simpler JSON structure
            nodes_data = []
            for node in result[0]['nodes']:
                node_properties = dict(node)
                node_id = node_properties.pop('id', None)
                node_data = {
                    "id": node_id,
                    "labels": list(node.labels),
                    "properties": node_properties
                }
                nodes_data.append(node_data)
                
            relationships_data = []
            for rel in result[0]['relationships']:
                rel_properties = dict(rel)
                source_id = rel.start_node.id
                target_id = rel.end_node.id
                rel_type = getattr(rel, "type", None) or type(rel).__name__
                
                rel_data = {
                    "source": source_id,
                    "target": target_id,
                    "type": rel_type,
                    "properties": rel_properties
                }
                relationships_data.append(rel_data)
                
            return {
                "nodes": nodes_data,
                "relationships": relationships_data,
                "metadata": {
                    "center_entity": center_entity,
                    "max_distance": max_distance,
                    "format": format,
                    "exported_at": datetime.now().isoformat()
                }
            }
        
        elif format == "graphml":
            # Return data for GraphML conversion
            # (would typically be processed further to create GraphML XML)
            return {"result": result[0], "format": "graphml"}
        
        elif format == "cypher":
            # Generate Cypher script to recreate this subgraph
            return {"result": result[0], "format": "cypher"}
        
        else:
            raise ValueError(f"Unsupported export format: {format}")