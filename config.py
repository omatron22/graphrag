import os
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

# Neo4j settings
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")  # Match with docker-compose.yml

# PostgreSQL settings
POSTGRES_URI = os.getenv("POSTGRES_URI", "postgresql://app:password@localhost:5432/business_consulting")

# Ollama model settings
MODELS = {
    'reasoning': {
        'name': 'deepseek-r1:8b',  # Upgraded from llama3:8b for better reasoning capabilities
        'endpoint': 'http://localhost:11434/api/generate',
        'parameters': {
            'temperature': 0.1,
            'top_p': 0.9,
            'max_tokens': 2048
        }
    },
    'vision': {
        'name': 'llama3.2-vision:11b',  # Updated to the optimal multimodal model
        'endpoint': 'http://localhost:11434/api/chat',  # Note: vision models use the chat endpoint
        'parameters': {
            'temperature': 0.1,
            'top_p': 0.9,
            'max_tokens': 512
        }
    },
    'lightweight': {
        'name': 'phi:latest',  # Updated to match the actual model name in Ollama
        'endpoint': 'http://localhost:11434/api/generate',
        'parameters': {
            'temperature': 0.1,
            'max_tokens': 256
        }
    }
}

# File processing settings
EXTRACTORS = {
    'pdf': 'extractors.pdf_extractor.extract',
    'docx': 'extractors.docx_extractor.extract',
    'xlsx': 'extractors.spreadsheet_extractor.extract',
    'csv': 'extractors.spreadsheet_extractor.extract',
    'jpg': 'extractors.image_extractor.extract',
    'png': 'extractors.image_extractor.extract'
}

# Risk analysis thresholds
RISK_THRESHOLDS = {
    'financial': {
        'low': 0.2,
        'medium': 0.5,
        'high': 0.8
    },
    'operational': {
        'low': 0.3,
        'medium': 0.6,
        'high': 0.8
    },
    'market': {
        'low': 0.25,
        'medium': 0.55,
        'high': 0.75
    }
}

# Model usage configuration
MODEL_USAGE = {
    # Map tasks to specific model types
    'document_analysis': 'reasoning',
    'risk_assessment': 'reasoning',
    'strategy_generation': 'reasoning',
    'image_processing': 'vision',
    'chart_analysis': 'vision',
    'document_routing': 'lightweight',
    'entity_classification': 'lightweight'
}

# Vision model image handling
VISION_SETTINGS = {
    'max_image_size': 1024,  # Maximum dimension for images
    'supported_formats': ['jpg', 'jpeg', 'png', 'gif', 'webp'],
    'ocr_enabled': True  # Enable OCR for text in images
}