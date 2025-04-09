#!/bin/bash
set -e

echo "Setting up Knowledge Graph-Based Business Consulting System..."

# Create required directories
echo "Creating required directories..."
mkdir -p neo4j/data
mkdir -p neo4j/logs
mkdir -p neo4j/import
mkdir -p neo4j/plugins
mkdir -p postgres-data
mkdir -p data/uploads
mkdir -p data/parsed
mkdir -p data/knowledge_base
mkdir -p knowledge_graph/exports

# Install Python dependencies with upgraded pip
echo "Upgrading pip and installing build dependencies..."
python -m pip install --upgrade pip wheel setuptools

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Docker is not installed. Please install Docker before continuing."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "Docker Compose is not installed. Please install Docker Compose before continuing."
    exit 1
fi

# Start Docker containers
echo "Starting Neo4j and PostgreSQL containers..."
docker-compose up -d

echo "Waiting for containers to initialize (45 seconds)..."
sleep 45  # Increased wait time for better container initialization

# Test connections
echo "Testing database connections..."
python test_neo4j.py
NEO4J_STATUS=$?

python test_postgres.py
POSTGRES_STATUS=$?

if [ $NEO4J_STATUS -eq 0 ] && [ $POSTGRES_STATUS -eq 0 ]; then
    echo ""
    echo "✅ Setup completed successfully!"
    echo "Neo4j browser available at: http://localhost:7474/"
    echo "Neo4j credentials: neo4j/password"
    echo "PostgreSQL available at: localhost:5432"
    echo "PostgreSQL credentials: app/password"
    echo ""
    echo "Next steps:"
    echo "1. Configure your models in Ollama (visit https://ollama.com/library for available models)"
    echo "2. Run 'python orchestrator.py examples/sample_document.pdf' to test the system"
    echo "3. Make sure to change default passwords in docker-compose.yml for production use"
else
    echo ""
    echo "❌ Setup encountered issues. Please check the error messages above."
    echo ""
    echo "Troubleshooting tips:"
    echo "- Make sure ports 7474, 7687, and 5432 are available"
    echo "- Check Docker logs with 'docker-compose logs'"
    echo "- Ensure Neo4j and PostgreSQL containers are running with 'docker ps'"
    echo "- Try restarting the containers with 'docker-compose restart'"
fi