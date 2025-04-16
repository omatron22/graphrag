# Makefile for Business Strategy Assessment System

.PHONY: setup test run clean assessment help

# Default target
help:
	@echo "Business Strategy Assessment System"
	@echo ""
	@echo "Available commands:"
	@echo "  make setup       - Set up the environment and dependencies"
	@echo "  make test        - Run system tests"
	@echo "  make run         - Run the system in interactive mode"
	@echo "  make assessment  - Run the strategy assessment CLI"
	@echo "  make clean       - Clean up temporary files"
	@echo ""

# Setup environment
setup:
	@echo "Setting up environment..."
	chmod +x setup.sh
	./setup.sh
	@echo "Setup complete."

# Run system tests
test:
	@echo "Running system tests..."
	python test_system.py
	@echo "Tests complete."

# Run the system in interactive mode
run:
	@echo "Starting the system in interactive mode..."
	python run_system.py -i
	@echo "System execution complete."

# Run the strategy assessment CLI
assessment:
	@echo "Starting the strategy assessment CLI..."
	python strategy_assessment_cli.py -i
	@echo "Assessment execution complete."

# Clean up temporary files
clean:
	@echo "Cleaning up..."
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete
	@echo "Cleanup complete."