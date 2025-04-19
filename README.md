# Knowledge Graph-Based Business Consulting System

A knowledge graph-powered system for business risk analysis and strategic recommendations using local LLMs.

## Overview

This system analyzes business entities using a knowledge graph built in Neo4j, generates risk assessments, and provides strategic recommendations using offline large language models via Ollama.

## Features

- **Knowledge Graph Analysis**: Discover relationships and patterns between business entities
- **Risk Assessment**: Identify financial, operational, and market risks
- **Strategy Generation**: Create actionable recommendations based on identified risks
- **Insights Extraction**: Find patterns, trends, and anomalies in entity relationships
- **Offline Operation**: All processing happens locally with no data sent to external services

## Prerequisites

- Python 3.9+
- Docker and Docker Compose
- 16+ GB RAM (for running larger LLMs)
- [Ollama](https://ollama.com/) for local LLM serving

## Quick Start

1. Clone this repository
2. Run the setup script:

```bash
chmod +x setup.sh
./setup.sh

Install required models in Ollama:

bashollama pull deepseek-r1:8b
ollama pull llama3.2-vision:11b
ollama pull phi

Populate the knowledge graph with test data:

bashpython populate_test_data.py

Analyze a business entity:

bashpython run_system.py --analyze TechCorp

Or run in interactive mode:

bashpython run_system.py -i

Project Structure

analysis/: Risk assessment and recommendation generation

insight_extractor.py: Finds patterns in graph
risk_engine.py: Risk classification logic
strategy_generator.py: Creates recommendations


knowledge_graph/: Knowledge graph construction and query logic

graph_query.py: Cypher queries for analysis
neo4j_manager.py: Neo4j database management
triplet_extractor.py: Entity-relation extraction


data/: Data storage

knowledge_base/: Output directories for insights and strategies


neo4j/: Neo4j database files
postgres-data/: PostgreSQL data directory
orchestrator.py: Main pipeline controller
run_system.py: Command-line interface for the system
populate_test_data.py: Script to fill Neo4j with test data
config.py: System configuration

Databases

Neo4j: Knowledge graph database (accessible at http://localhost:7474/)
PostgreSQL: Metadata storage (if used)

Models
This system uses three types of offline language models via Ollama:

Reasoning/Risk Analysis: DeepSeek-R1 8B

Used for risk assessment and strategy generation


Multimodal Processing: Llama 3.2 Vision 11B

For image and chart analysis (if used)


Lightweight Tasks: Phi

For simpler preprocessing tasks



Command Line Options

python run_system.py -i: Run in interactive mode
python run_system.py --analyze [ENTITY]: Analyze a specific entity
python run_system.py --visualize [ENTITY]: Generate entity network visualization
python run_system.py --list-entities: List top entities in knowledge graph

License
This project is intended for educational and research purposes.
Acknowledgments

Neo4j for the graph database
Ollama for local LLM serving
DeepSeek for the DeepSeek-R1 model
Meta for the Llama 3.2 Vision model