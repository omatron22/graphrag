import sys
import psycopg2
import config

def test_connection():
    print("Testing PostgreSQL connection...")
    print(f"Connection string: {config.POSTGRES_URI}")
    
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(config.POSTGRES_URI)
        cursor = conn.cursor()
        
        # Test connection with a simple query
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"Successfully connected to PostgreSQL")
        print(f"PostgreSQL version: {version}")
        
        # Create a test table to ensure we have write permissions
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS connection_test (
                    id SERIAL PRIMARY KEY,
                    test_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                INSERT INTO connection_test (id) VALUES (DEFAULT) RETURNING id;
            """)
            inserted_id = cursor.fetchone()[0]
            conn.commit()
            print(f"Successfully created test table and inserted row with ID: {inserted_id}")
            
            # Clean up
            cursor.execute("DROP TABLE connection_test;")
            conn.commit()
            print("Test table removed")
        except Exception as e:
            conn.rollback()
            print(f"Table test failed: {e}")
        
        # Close the connection
        cursor.close()
        conn.close()
        return True
    
    except psycopg2.OperationalError as e:
        print(f"Connection failed: {e}")
        print("Make sure the PostgreSQL container is running and healthy")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)