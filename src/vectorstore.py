import logging
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from observability import trace_function

logger = logging.getLogger(__name__)


@trace_function(name="create_vectorstore", include_args=False, include_result=False)
def create_vectorstore(splits, persist_directory):
    """
    Create and persist a vector store from document chunks.
    
    Embedding model: sentence-transformers/all-MiniLM-L6-v2
    - 384-dimensional vectors
    - Fast inference (~5ms per chunk)
    - Excellent semantic similarity quality
    
    Args:
        splits (list): List of document chunks to embed
        persist_directory (str): Path to store vector database
        
    Returns:
        Chroma: Vector store object with embedded documents
    """
    try:
        logger.info("Initializing embedding model (all-MiniLM-L6-v2)")
        embeddings_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        
        logger.info(f"Creating ChromaDB vector store at {persist_directory}")
        vectorstore = Chroma.from_documents(
            documents=splits,
            embedding=embeddings_model,
            persist_directory=persist_directory
        )
        logger.info(f"Vector store created with {len(splits)} embedded documents")
        return vectorstore
    except Exception as e:
        logger.error(f"Failed to create vector store: {str(e)}")
        raise
