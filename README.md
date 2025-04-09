# Knowledge Graph-Based Business Consulting System

A complete offline business risk analysis system leveraging knowledge graphs for transparent, auditable insights.

## Overview

This system processes business documents (PDFs, spreadsheets, images, etc.), extracts structured information, builds a knowledge graph using Neo4j, and generates business risk assessments and recommendations using offline large language models.

## Features

- **Document Processing**: Extract text, tables, and structural information from various file formats
- **Knowledge Graph Construction**: Build a semantic network of business entities and relationships
- **Risk Analysis**: Identify financial, operational, and market risks
- **Strategy Generation**: Create actionable recommendations based on identified risks
- **Offline Operation**: All processing happens locally with no data sent to external services
- **Vision Analysis**: Process charts, diagrams, and visual business elements with multimodal AI

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

4. Process a document:

```bash
python orchestrator.py data/uploads/your_document.pdf
```

## Project Structure

- `data/`: Document storage and processed outputs
  - `uploads/`: Raw uploaded documents
  - `parsed/`: Extracted structured content
  - `knowledge_base/`: Static reference data for recommendations
- `extractors/`: Document parsing and information extraction
  - `pdf_extractor.py`: PDF document processing
  - `docx_extractor.py`: Word document processing
  - `spreadsheet_extractor.py`: Excel and CSV processing
  - `image_extractor.py`: Image and chart analysis (uses vision models)
  - `extractor_utils.py`: Shared extraction utilities
- `knowledge_graph/`: Knowledge graph construction and query logic
  - `triplet_extractor.py`: Entity-relation extraction
  - `neo4j_manager.py`: Neo4j database management
  - `graph_query.py`: Cypher queries for analysis
  - `exports/`: For visualization exports
- `analysis/`: Risk assessment and recommendation generation
  - `risk_engine.py`: Risk classification logic
  - `strategy_generator.py`: Creates recommendations
  - `insight_extractor.py`: Finds patterns in graph
- `neo4j/`: Neo4j database files and configuration
- `postgres-data/`: PostgreSQL data directory
- `orchestrator.py`: Main pipeline controller
- `config.py`: System configuration

## Databases

- **Neo4j**: Knowledge graph database (accessible at http://localhost:7474/)
- **PostgreSQL**: Structured metadata storage

## Models

This system uses three types of offline language models:

1. **Reasoning/Risk Analysis**: DeepSeek-R1 8B
   - Used for core analysis, strategy development, and reasoning
   - Advanced reasoning capabilities for business risk assessment

2. **Multimodal Processing**: Llama 3.2 Vision 11B
   - Processes images, charts, diagrams, and visual documents
   - Offers visual recognition, captioning, and question answering

3. **Lightweight Tasks**: Phi
   - Handles routing, preprocessing, and simple classification tasks
   - Low resource requirements for quick decisions

## Usage Example

Process a financial report PDF:

```bash
python orchestrator.py data/uploads/financial_report_2024.pdf
```

Process all documents in a directory:

```bash
python orchestrator.py data/uploads/quarterly_reports/
```

## License

This project is intended for educational and research purposes.

## Acknowledgments

- [Neo4j](https://neo4j.com/) for the graph database
- [Ollama](https://ollama.com/) for local LLM serving
- [PyMuPDF](https://pymupdf.readthedocs.io/) for PDF processing
- [DeepSeek](https://deepseek.ai/) for the DeepSeek-R1 model
- [Meta](https://meta.com/) for the Llama 3.2 Vision model