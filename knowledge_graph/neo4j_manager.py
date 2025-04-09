"""
Neo4j database manager for the knowledge graph component.
Handles connection, transaction management, and query execution.
"""

import logging
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
        """Execute a Cypher query and return results"""
        if not self.driver:
            if not self.connect():
                raise ConnectionError("Failed to connect to Neo4j database")
                
        try:
            with self.driver.session() as session:
                result = session.run(query, parameters or {})
                return [record.data() for record in result]
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
        
    def clear_database(self, confirm=False):
        """Delete all nodes and relationships (use with caution!)"""
        if not confirm:
            logger.warning("Database clear operation requires confirmation")
            return False
            
        query = "MATCH (n) DETACH DELETE n"
        self.execute_query(query)
        logger.warning("Database cleared - all nodes and relationships deleted")
        return True
        
    # Additional utility methods for specific business consulting operations
    
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