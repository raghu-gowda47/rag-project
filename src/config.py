"""
Centralized configuration for RAG Chatbot.

This module manages all configuration constants and paths,
making it easy to adjust settings without editing multiple files.
"""

import os
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
SRC_DIR = Path(__file__).parent

# Data directories
DATA_DIR = PROJECT_ROOT / "data"
DOCUMENTS_DIR = DATA_DIR / "documents"
VECTOR_DB_DIR = DATA_DIR / "vector_db"
LOGS_DIR = DATA_DIR / "logs"

# Create directories if they don't exist
DATA_DIR.mkdir(exist_ok=True)
DOCUMENTS_DIR.mkdir(exist_ok=True)
VECTOR_DB_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# File paths
PDF_PATH = DOCUMENTS_DIR / "Ramayana.pdf"
VECTOR_DB_PATH = VECTOR_DB_DIR / "chroma_db_bpe"
LOG_FILE_PATH = LOGS_DIR / "rag_chatbot.log"
CHECKPOINT_FILE_PATH = DATA_DIR / ".pdf_checkpoint"

# LLM Configuration
LLM_CONFIG = {
    "model": "gemma3",
    "base_url": "http://127.0.0.1:11434",
    "temperature": 0.7,
}

# Text Splitting Configuration
TEXT_SPLIT_CONFIG = {
    "chunk_size": 500,
    "chunk_overlap": 100,
}

# Retrieval Configuration
RETRIEVAL_CONFIG = {
    "k": 4,  # Number of chunks to retrieve
    "search_type": "similarity",
}

# Embedding Model Configuration
EMBEDDING_CONFIG = {
    "model_name": "sentence-transformers/all-MiniLM-L6-v2",
    "model_kwargs": {"device": "cpu"},
}

# Langfuse Configuration
LANGFUSE_CONFIG = {
    "public_key": os.getenv("LANGFUSE_PUBLIC_KEY"),
    "secret_key": os.getenv("LANGFUSE_SECRET_KEY"),
    "host": os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com"),
}

# Logging Configuration
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file_path": str(LOG_FILE_PATH),
}

# External library logging levels
EXTERNAL_LOGGER_LEVELS = {
    "httpx": "WARNING",
    "urllib3": "WARNING",
    "langchain": "WARNING",
}
