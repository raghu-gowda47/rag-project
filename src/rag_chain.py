import logging
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from prompts import RAG_PROMPT
from observability import trace_function, trace_context

logger = logging.getLogger(__name__)


@trace_function(name="build_rag_chain", include_args=False, include_result=False)
def build_rag_chain(vectorstore):
    """
    Build the RAG (Retrieval-Augmented Generation) chain.
    
    Pipeline:
    1. Retriever: Fetch top-4 most relevant chunks from vector store
    2. Prompt: Format context + user question using RAG_PROMPT template
    3. LLM: Generate answer using Ollama (Gemma3)
    4. Parser: Extract text from LLM response
    
    Args:
        vectorstore: Chroma vector store with embedded documents
        
    Returns:
        LCEL chain: Runnable RAG pipeline
        
    Raises:
        Exception: If LLM or chain construction fails
    """
    try:
        logger.info("Building RAG chain components")
        
        # Retriever: k=4 provides ~2000 tokens of context
        # Balances relevance vs. context window management
        retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
        logger.debug("Retriever configured (k=4)")
        
        # LLM: Ollama with Gemma3 (local, privacy-first)
        logger.info("Initializing Ollama LLM (Gemma3)")
        llm = OllamaLLM(model="gemma3")
        
        # Prompt: Explicit instructions to prevent hallucination
        prompt = ChatPromptTemplate.from_template(RAG_PROMPT)
        logger.debug("Prompt template loaded from prompts.py")
        
        # Build LCEL chain
        logger.info("Constructing LCEL chain")
        rag_chain = (
            {"context": retriever, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )
        logger.info("RAG chain successfully constructed")
        return rag_chain
        
    except Exception as e:
        logger.error(f"Failed to build RAG chain: {str(e)}")
        raise
