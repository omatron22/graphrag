import sys
from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable
import config

def test_connection():
    print("Testing Neo4j connection...")
    print(f"URI: {config.NEO4J_URI}")
    print(f"User: {config.NEO4J_USER}")
    
    try:
        # Try to establish a connection
        driver = GraphDatabase.driver(
            config.NEO4J_URI, 
            auth=(config.NEO4J_USER, config.NEO4J_PASSWORD)
        )
        
        # Test if the connection works by running a simple query
        with driver.session() as session:
            result = session.run("RETURN 'Connection established!' AS message")
            message = result.single()["message"]
            print(f"Success: {message}")
            
            # Test APOC plugin (should be available based on docker-compose.yml)
            try:
                plugin_result = session.run("CALL apoc.help('apoc')")
                print("APOC plugin is available and working")
            except Exception as e:
                print(f"APOC plugin test failed: {e}")
                
            # Test GDS plugin (Graph Data Science)
            try:
                gds_result = session.run("CALL gds.list()")
                print("Graph Data Science plugin is available and working")
            except Exception as e:
                print(f"GDS plugin test failed: {e}")
                
        # Close the driver
        driver.close()
        return True
    
    except ServiceUnavailable as e:
        print(f"Connection failed: {e}")
        print("Make sure the Neo4j container is running and healthy")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)