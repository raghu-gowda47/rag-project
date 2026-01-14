import logging
from langchain_text_splitters import TokenTextSplitter
from transformers import AutoTokenizer
from observability import trace_function

logger = logging.getLogger(__name__)


@trace_function(name="split_documents", include_args=False, include_result=False)
def split_documents(docs, chunk_size=500, chunk_overlap=100):
    """
    Split documents into chunks using BPE tokenization.
    
    Chunking strategy:
    - chunk_size=500: Aligns with Gemma3 context window (~2000 tokens)
    - chunk_overlap=100: Prevents losing context at chunk boundaries
    - BPE tokenization: Avoids splitting mid-word, aligns with LLM tokenization
    
    Args:
        docs (list): List of Document objects to split
        chunk_size (int): Number of tokens per chunk (default: 500)
        chunk_overlap (int): Number of overlapping tokens between chunks (default: 100)
        
    Returns:
        list: List of Document chunks
    """
    try:
        logger.debug("Loading BPE tokenizer (gpt2)")
        tokenizer = AutoTokenizer.from_pretrained("gpt2")
        
        logger.info(f"Splitting {len(docs)} documents into chunks (size={chunk_size}, overlap={chunk_overlap})")
        text_splitter = TokenTextSplitter.from_huggingface_tokenizer(
            tokenizer=tokenizer,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        splits = text_splitter.split_documents(docs)
        logger.info(f"Created {len(splits)} chunks from {len(docs)} documents")
        return splits
    except Exception as e:
        logger.error(f"Error splitting documents: {str(e)}")
        raise
