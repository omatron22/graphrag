# Makefile for Knowledge Graph-Based Business Consulting System

.PHONY: setup populate run analyze clean help

# Default target
help:
	@echo "Knowledge Graph-Based Business Consulting System"
	@echo ""
	@echo "Available commands:"
	@echo "  make setup       - Set up the environment and dependencies"
	@echo "  make populate    - Populate Neo4j with test data"
	@echo "  make run         - Run the system in interactive mode"
	@echo "  make analyze     - Analyze TechCorp entity"
	@echo "  make visualize   - Visualize TechCorp network"
	@echo "  make clean       - Clean up temporary files"
	@echo ""

# Setup environment
setup:
	@echo "Setting up environment..."
	chmod +x setup.sh
	./setup.sh
	@echo "Setup complete."

# Populate database with test data
populate:
	@echo "Populating Neo4j with test data..."
	python populate_test_data.py
	@echo "Data population complete."

# Run the system in interactive mode
run:
	@echo "Starting the system in interactive mode..."
	python run_system.py -i
	@echo "System execution complete."

# Analyze TechCorp entity
analyze:
	@echo "Analyzing TechCorp entity..."
	python run_system.py --analyze TechCorp
	@echo "Analysis complete."

# Visualize TechCorp network
visualize:
	@echo "Visualizing TechCorp network..."
	python run_system.py --visualize TechCorp
	@echo "Visualization complete."

# Clean up temporary files
clean:
	@echo "Cleaning up..."
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete
	@echo "Cleanup complete."