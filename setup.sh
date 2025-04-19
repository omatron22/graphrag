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
mkdir -p data/knowledge_base/insights
mkdir -p data/knowledge_base/strategies
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
sleep 45  # Wait time for container initialization

# Check for Ollama
if ! command -v ollama &> /dev/null; then
    echo "⚠️ Ollama not found. Please install Ollama for LLM functionality."
    echo "Visit https://ollama.com/ for installation instructions."
else
    echo "✅ Ollama found. Checking for required models..."
    # Attempt to check for required models
    if ollama list &>/dev/null; then
        REQUIRED_MODELS=("deepseek-r1:8b" "llama3.2-vision:11b" "phi")
        
        for MODEL in "${REQUIRED_MODELS[@]}"; do
            if ! ollama list | grep -q "$MODEL"; then
                echo "⚠️ Model $MODEL not found. Please install with: ollama pull $MODEL"
            else
                echo "✅ Model $MODEL is available."
            fi
        done
    else
        echo "⚠️ Unable to list Ollama models. Please ensure Ollama server is running."
    fi
fi

echo ""
echo "✅ Setup completed!"
echo "Neo4j browser available at: http://localhost:7474/"
echo "Neo4j credentials: neo4j/password"
echo ""
echo "Next steps:"
echo "1. Run 'python populate_test_data.py' to fill Neo4j with sample data"
echo "2. Run 'python run_system.py --analyze TechCorp' to analyze entity"
echo "3. Run 'python run_system.py -i' for interactive mode"