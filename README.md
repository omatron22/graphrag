# Knowledge Graph-Based Business Consulting System

A knowledge graph-powered system for business risk analysis and strategic recommendations using local LLMs.

## Overview

This system analyzes business entities using a knowledge graph built in Neo4j, generates risk assessments, and provides strategic recommendations using offline large language models via Ollama.

## Features

- **Knowledge Graph Analysis**: Discover relationships and patterns between business entities
- **Risk Assessment**: Identify financial, operational, and market risks
- **Strategy Generation**: Create actionable recommendations based on identified risks
- **Insights Extraction**: Find patterns, trends, and anomalies in entity relationships
- **PDF Report Generation**: Generate comprehensive assessment reports
- **Offline Operation**: All processing happens locally with no data sent to external services

## Architecture

The system is organized into these core components:

1. **Knowledge Graph Module** (`knowledge_graph/`):
   - `neo4j_manager.py`: Handles Neo4j database operations
   - `triplet_extractor.py`: Extracts subject-predicate-object relationships from documents
   - `graph_query.py`: Provides Cypher queries for business analysis

2. **Document Processing** (`extractors/`):
   - Supports multiple document formats (PDF, DOCX, XLSX, CSV, images)
   - Extracts text, tables, and structured data
   - Feeds information to the knowledge graph

3. **Analysis Module** (`analysis/`):
   - `risk_engine.py`: Analyzes business risks using graph data
   - `strategy_generator.py`: Generates strategic recommendations
   - `insight_extractor.py`: Identifies patterns and opportunities

4. **Orchestration Layer**:
   - `orchestrator.py`: Controls the system workflow
   - `run_system.py`: Command-line interface
   - `populate_test_data.py`: Adds sample data for testing

5. **Output Generation**:
   - `assessment_pdf_generator.py`: Creates PDF reports of analyses
   - `strategy_assessment.py`: Structured assessment framework

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
```

3. Install required models in Ollama:

```bash
ollama pull deepseek-r1:8b
ollama pull llama3.2-vision:11b
ollama pull phi
```

4. Populate the knowledge graph with test data:

```bash
python populate_test_data.py
```

5. Analyze a business entity:

```bash
python run_system.py --analyze TechCorp
```

6. Run with additional parameters:

```bash
python run_system.py --analyze TechCorp --risk-tolerance high --priorities market,finance
```

7. Or run in interactive mode:

```bash
python run_system.py -i
```

## Command Line Options

- `python run_system.py -i`: Run in interactive mode
- `python run_system.py --analyze [ENTITY]`: Analyze a specific entity
- `python run_system.py --risk-tolerance [low|medium|high]`: Set risk tolerance
- `python run_system.py --priorities [PRIORITIES]`: Comma-separated list of priorities
- `python run_system.py --visualize [ENTITY]`: Generate entity network visualization
- `python run_system.py --list-entities`: List top entities in knowledge graph

## Databases

- **Neo4j**: Knowledge graph database (accessible at http://localhost:7474/)
- **PostgreSQL**: Metadata storage for future expansion

## Models

This system uses three types of offline language models via Ollama:

- **Reasoning/Risk Analysis**: DeepSeek-R1 8B
  - Used for risk assessment and strategy generation

- **Multimodal Processing**: Llama 3.2 Vision 11B
  - For image and chart analysis

- **Lightweight Tasks**: Phi
  - For simpler preprocessing tasks

## Project Structure

```
├── analysis/              # Risk assessment and recommendation generation
│   ├── insight_extractor.py  # Finds patterns in graph
│   ├── risk_engine.py        # Risk classification logic
│   └── strategy_generator.py # Creates recommendations
│
├── extractors/            # Document processing components
│   ├── docx_extractor.py     # Word document processing
│   ├── extractor_utils.py    # Shared utilities
│   ├── image_extractor.py    # Image processing
│   ├── pdf_extractor.py      # PDF processing
│   └── spreadsheet_extractor.py # Excel/CSV processing
│
├── knowledge_graph/       # Knowledge graph construction and query logic
│   ├── graph_query.py        # Cypher queries for analysis
│   ├── neo4j_manager.py      # Neo4j database management
│   └── triplet_extractor.py  # Entity-relation extraction
│
├── data/                  # Data storage directories
│   ├── knowledge_base/       # Output directories for insights and strategies
│   ├── parsed/               # Processed document data
│   └── uploads/              # Input documents
│
├── assessment_pdf_generator.py # PDF report generation
├── config.py                   # System configuration
├── docker-compose.yml          # Container setup for Neo4j and PostgreSQL
├── Makefile                    # Build automation
├── orchestrator.py             # Main pipeline controller
├── populate_test_data.py       # Script to fill Neo4j with test data
├── run_system.py               # Command-line interface
├── setup.sh                    # Environment setup script
└── strategy_assessment.py      # Strategy assessment framework
```

## License

This project is intended for educational and research purposes.

## Acknowledgments

- Neo4j for the graph database
- Ollama for local LLM serving
- DeepSeek for the DeepSeek-R1 model
- Meta for the Llama 3.2 Vision model