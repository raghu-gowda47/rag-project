import os
import logging
from langchain_community.document_loaders import PyPDFLoader
from observability import trace_function

logger = logging.getLogger(__name__)


def has_pdf_changed(pdf_path, checkpoint_file=".pdf_checkpoint"):
    """
    Check if PDF has been modified since last run.
    
    Args:
        pdf_path: Path to the PDF file
        checkpoint_file: File to store the last modification time
        
    Returns:
        True if PDF is new or has changed, False if unchanged
    """
    if not os.path.exists(checkpoint_file):
        return True  # First run, no checkpoint exists
    
    if not os.path.exists(pdf_path):
        logger.warning(f"PDF not found: {pdf_path}")
        return True
    
    current_mtime = os.path.getmtime(pdf_path)
    try:
        with open(checkpoint_file, 'r') as f:
            last_mtime = float(f.read().strip())
        
        if current_mtime != last_mtime:
            logger.info(f"PDF modified detected (previous: {last_mtime}, current: {current_mtime})")
            return True
        return False
    except Exception as e:
        logger.warning(f"Error reading checkpoint file: {e}. Rebuilding vector database.")
        return True


def update_pdf_checkpoint(pdf_path, checkpoint_file=".pdf_checkpoint"):
    """Update the checkpoint file with current PDF modification time."""
    try:
        mtime = os.path.getmtime(pdf_path)
        with open(checkpoint_file, 'w') as f:
            f.write(str(mtime))
        logger.info(f"PDF checkpoint updated (mtime: {mtime})")
    except Exception as e:
        logger.error(f"Error updating checkpoint: {e}")



@trace_function(name="load_pdf", include_args=True, include_result=False)
def load_pdf(pdf_path):
    """
    Load and extract text from a PDF file.
    
    Args:
        pdf_path (str): Path to the PDF file
        
    Returns:
        list: List of Document objects with extracted text and metadata
        
    Raises:
        FileNotFoundError: If PDF file does not exist
        Exception: If PDF parsing fails
    """
    if not os.path.exists(pdf_path):
        logger.error(f"PDF not found at {pdf_path}")
        raise FileNotFoundError(f"PDF not found: {pdf_path}")
    
    try:
        logger.info(f"Loading PDF from {pdf_path}")
        loader = PyPDFLoader(pdf_path)
        docs = loader.load()
        logger.info(f"Successfully loaded {len(docs)} pages from PDF")
        return docs
    except Exception as e:
        logger.error(f"Failed to load PDF: {str(e)}")
        raise
