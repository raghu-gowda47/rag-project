import os
import logging
import sys
import shutil
from data_loader import load_pdf, has_pdf_changed, update_pdf_checkpoint
from text_splitter import split_documents
from vectorstore import create_vectorstore
from rag_chain import build_rag_chain
from observability import setup_langfuse, trace_function, trace_context, flush_traces


# Configure logging
def setup_logging(level=logging.INFO):
    """Configure logging for the application."""
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('rag_chatbot.log')
        ]
    )
    
    # Suppress verbose logs from external libraries
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('langchain').setLevel(logging.WARNING)


logger = logging.getLogger(__name__)


@trace_function(name="initialize_rag_pipeline", include_args=False, include_result=False)
def main():
    """Main entry point for the RAG chatbot."""
    try:
        logger.info("=" * 50)
        logger.info("RAG Chatbot Initialization Started")
        logger.info("=" * 50)
        
        # Initialize Langfuse observability
        logger.info("Initializing Langfuse observability...")
        langfuse_initialized = setup_langfuse()
        if langfuse_initialized:
            logger.info("✓ Langfuse observability enabled")
        else:
            logger.info("⚠ Langfuse observability disabled (will continue without it)")
        
        # Paths
        pdf_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Ramayana.pdf")
        persist_directory = os.path.join(os.path.dirname(os.path.dirname(__file__)), "chroma_db_bpe")
        
        logger.info(f"PDF path: {pdf_path}")
        logger.info(f"Vector store path: {persist_directory}")
        
        # Check if PDF has changed since last run
        if has_pdf_changed(pdf_path):
            logger.info("PDF is new or has been modified - rebuilding vector database")
            if os.path.exists(persist_directory):
                logger.info("Deleting outdated vector database")
                shutil.rmtree(persist_directory)
        else:
            logger.info("PDF unchanged - using existing vector database")
        
        # Initialize pipeline
        logger.info("Step 1: Loading PDF documents")
        docs = load_pdf(pdf_path)
        
        logger.info("Step 2: Splitting documents into chunks")
        splits = split_documents(docs)
        
        logger.info("Step 3: Creating vector store with embeddings")
        vectorstore = create_vectorstore(splits, persist_directory)
        
        # Update checkpoint to indicate PDF was processed
        update_pdf_checkpoint(pdf_path)
        
        logger.info("Step 4: Building RAG chain")
        rag_chain = build_rag_chain(vectorstore)
        
        logger.info("=" * 50)
        logger.info("RAG Chatbot Ready for Queries")
        logger.info("=" * 50)
        
        # Interactive loop
        print("\n" + "=" * 50)
        print("RAG Chatbot - Ask questions about your PDF")
        print("Type 'exit' to quit")
        print("=" * 50 + "\n")
        
        query_count = 0
        while True:
            try:
                user_question = input("Question: ").strip()
                
                if not user_question:
                    print("Please enter a question.\n")
                    continue
                
                if user_question.lower() == 'exit':
                    logger.info("User exited chatbot")
                    flush_traces()
                    print("Goodbye!")
                    break
                
                query_count += 1
                logger.info(f"Query #{query_count}: {user_question}")
                
                # Trace the entire query processing
                with trace_context(f"query_{query_count}", {"query": user_question[:100]}) as ctx:
                    print("\nSearching and generating response...\n")
                    response = rag_chain.invoke(user_question)
                    
                    print(f"Answer: {response}\n")
                    ctx["output"] = response
                    logger.info(f"Response generated for query #{query_count}")
                
            except Exception as e:
                logger.error(f"Error processing query: {str(e)}")
                print(f"Error: {str(e)}\n")
                
    except Exception as e:
        logger.critical(f"Fatal error: {str(e)}")
        flush_traces()
        print(f"Fatal error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    setup_logging(level=logging.INFO)
    main()
