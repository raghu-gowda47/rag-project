"""
RAG Chatbot Package - Retrieval-Augmented Generation System

This package provides a complete RAG pipeline with:
- PDF document loading and processing
- Text splitting with BPE tokenization
- Vector embeddings with Chroma
- RAG chain orchestration
- Langfuse observability integration
"""

__version__ = "1.0.0"
__author__ = "Raghavendra"

# Export main components for easier imports
from .main import main
from .data_loader import load_pdf, has_pdf_changed, update_pdf_checkpoint
from .text_splitter import split_documents
from .vectorstore import create_vectorstore
from .rag_chain import build_rag_chain
from .observability import (
    setup_langfuse,
    trace_function,
    trace_context,
    flush_traces,
    get_langfuse_client,
)
from .prompts import RAG_PROMPT, GUARDRAILS

__all__ = [
    "main",
    "load_pdf",
    "has_pdf_changed",
    "update_pdf_checkpoint",
    "split_documents",
    "create_vectorstore",
    "build_rag_chain",
    "setup_langfuse",
    "trace_function",
    "trace_context",
    "flush_traces",
    "get_langfuse_client",
    "RAG_PROMPT",
    "GUARDRAILS",
]
