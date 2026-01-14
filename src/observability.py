"""
Langfuse Observability Integration

Provides decorators and context managers for tracing function calls,
LLM invocations, and retrieval operations through Langfuse.

This module enables comprehensive monitoring and debugging of the RAG pipeline
by automatically logging execution traces, latencies, and errors.

Key Features:
- Function execution tracing with decorators
- Context manager for manual tracing
- Automatic latency and error tracking
- Langfuse integration for centralized observability
- Graceful fallback if Langfuse is unavailable
"""

import logging
import time
import functools
from typing import Any, Callable, Optional
from contextlib import contextmanager

try:
    from langfuse import Langfuse
    from langfuse.decorators import observe
    LANGFUSE_AVAILABLE = True
except ImportError:
    LANGFUSE_AVAILABLE = False
    observe = lambda *args, **kwargs: lambda f: f  # No-op decorator

logger = logging.getLogger(__name__)

# Global Langfuse client (initialized in setup_langfuse)
_langfuse_client: Optional['Langfuse'] = None


def setup_langfuse(
    public_key: Optional[str] = None,
    secret_key: Optional[str] = None,
    host: str = "https://cloud.langfuse.com"
) -> bool:
    """
    Initialize Langfuse client for observability.
    
    If public_key and secret_key are not provided, attempts to read from
    LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY environment variables.
    
    Args:
        public_key (str, optional): Langfuse public key
        secret_key (str, optional): Langfuse secret key
        host (str): Langfuse host URL (default: cloud.langfuse.com)
        
    Returns:
        bool: True if Langfuse initialized successfully, False otherwise
        
    Example:
        >>> setup_langfuse(
        ...     public_key="pk-xxx",
        ...     secret_key="sk-xxx"
        ... )
        True
    """
    global _langfuse_client
    
    if not LANGFUSE_AVAILABLE:
        logger.warning(
            "Langfuse not installed. "
            "Install with: pip install langfuse. "
            "Observability will be disabled."
        )
        return False
    
    try:
        import os
        
        # Use provided keys or fall back to environment variables
        pk = public_key or os.getenv("LANGFUSE_PUBLIC_KEY")
        sk = secret_key or os.getenv("LANGFUSE_SECRET_KEY")
        
        if not pk or not sk:
            logger.warning(
                "Langfuse credentials not provided. "
                "Set LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY environment variables. "
                "Observability will be disabled."
            )
            return False
        
        _langfuse_client = Langfuse(
            public_key=pk,
            secret_key=sk,
            host=host
        )
        
        logger.info("Langfuse initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize Langfuse: {str(e)}")
        return False


def get_langfuse_client() -> Optional['Langfuse']:
    """
    Get the global Langfuse client instance.
    
    Returns:
        Langfuse: The client instance, or None if not initialized
    """
    return _langfuse_client


def trace_function(name: Optional[str] = None, include_args: bool = True, include_result: bool = True):
    """
    Decorator to trace function execution with Langfuse.
    
    Automatically logs:
    - Function name and arguments
    - Execution time
    - Return value
    - Errors and exceptions
    
    Args:
        name (str, optional): Custom name for the trace (defaults to function name)
        include_args (bool): Whether to log function arguments (default: True)
        include_result (bool): Whether to log function result (default: True)
        
    Returns:
        Callable: Decorated function
        
    Example:
        >>> @trace_function(name="load_documents")
        ... def load_pdf(pdf_path):
        ...     # implementation
        ...     return docs
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            trace_name = name or func.__name__
            start_time = time.time()
            
            try:
                # Log execution start
                logger.debug(f"[TRACE START] {trace_name}")
                if include_args:
                    logger.debug(f"  Args: {args}, Kwargs: {kwargs}")
                
                # Execute function
                result = func(*args, **kwargs)
                
                # Log success
                elapsed = time.time() - start_time
                logger.info(f"[TRACE END] {trace_name} completed in {elapsed:.2f}s")
                if include_result:
                    logger.debug(f"  Result: {result}")
                
                # Trace to Langfuse if available
                if _langfuse_client:
                    try:
                        _langfuse_client.trace(
                            name=trace_name,
                            user_id="rag-chatbot",
                            metadata={
                                "function": func.__name__,
                                "status": "success",
                                "duration_seconds": elapsed,
                            },
                            input={"args": str(args)[:100], "kwargs": str(kwargs)[:100]} if include_args else None,
                            output={"result": str(result)[:100]} if include_result else None,
                        )
                    except Exception as e:
                        logger.debug(f"Failed to send trace to Langfuse: {str(e)}")
                
                return result
                
            except Exception as e:
                elapsed = time.time() - start_time
                logger.error(f"[TRACE ERROR] {trace_name} failed after {elapsed:.2f}s: {str(e)}")
                
                # Log error to Langfuse if available
                if _langfuse_client:
                    try:
                        _langfuse_client.trace(
                            name=trace_name,
                            user_id="rag-chatbot",
                            metadata={
                                "function": func.__name__,
                                "status": "error",
                                "duration_seconds": elapsed,
                                "error": str(e)[:100],
                            },
                        )
                    except Exception as trace_error:
                        logger.debug(f"Failed to send error trace to Langfuse: {str(trace_error)}")
                
                raise
        
        return wrapper
    return decorator


@contextmanager
def trace_context(name: str, metadata: Optional[dict] = None):
    """
    Context manager for manual tracing of code blocks.
    
    Args:
        name (str): Name of the operation being traced
        metadata (dict, optional): Additional metadata to log
        
    Yields:
        dict: Trace context that can be used to add inputs/outputs
        
    Example:
        >>> with trace_context("retrieve_documents", {"k": 4}) as ctx:
        ...     docs = vectorstore.search(query)
        ...     ctx["output"] = docs
    """
    start_time = time.time()
    ctx = {"metadata": metadata or {}}
    
    try:
        logger.debug(f"[CONTEXT START] {name}")
        yield ctx
        
        elapsed = time.time() - start_time
        logger.info(f"[CONTEXT END] {name} completed in {elapsed:.2f}s")
        
        # Trace to Langfuse if available
        if _langfuse_client:
            try:
                _langfuse_client.trace(
                    name=name,
                    user_id="rag-chatbot",
                    metadata={
                        **ctx.get("metadata", {}),
                        "status": "success",
                        "duration_seconds": elapsed,
                    },
                    input=ctx.get("input"),
                    output=ctx.get("output"),
                )
            except Exception as e:
                logger.debug(f"Failed to send context trace to Langfuse: {str(e)}")
    
    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(f"[CONTEXT ERROR] {name} failed after {elapsed:.2f}s: {str(e)}")
        
        # Log error to Langfuse if available
        if _langfuse_client:
            try:
                _langfuse_client.trace(
                    name=name,
                    user_id="rag-chatbot",
                    metadata={
                        **ctx.get("metadata", {}),
                        "status": "error",
                        "duration_seconds": elapsed,
                        "error": str(e)[:100],
                    },
                )
            except Exception as trace_error:
                logger.debug(f"Failed to send error trace to Langfuse: {str(trace_error)}")
        
        raise


def trace_llm_call(model: str, input_tokens: int = 0, output_tokens: int = 0, latency_ms: float = 0):
    """
    Log an LLM call to Langfuse for detailed observability.
    
    Args:
        model (str): Model name (e.g., "gemma3")
        input_tokens (int): Number of input tokens
        output_tokens (int): Number of output tokens
        latency_ms (float): Latency in milliseconds
    """
    if not _langfuse_client:
        return
    
    try:
        _langfuse_client.trace(
            name=f"llm_call_{model}",
            user_id="rag-chatbot",
            metadata={
                "model": model,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "latency_ms": latency_ms,
                "total_tokens": input_tokens + output_tokens,
            },
        )
    except Exception as e:
        logger.debug(f"Failed to log LLM call to Langfuse: {str(e)}")


def trace_retrieval(query: str, k: int, num_results: int, latency_ms: float = 0):
    """
    Log a retrieval operation to Langfuse for detailed observability.
    
    Args:
        query (str): The query that was executed
        k (int): Number of results requested
        num_results (int): Number of results returned
        latency_ms (float): Latency in milliseconds
    """
    if not _langfuse_client:
        return
    
    try:
        _langfuse_client.trace(
            name="retrieval",
            user_id="rag-chatbot",
            metadata={
                "query": query[:100],  # Truncate for logging
                "k": k,
                "num_results": num_results,
                "latency_ms": latency_ms,
                "query_length": len(query),
            },
        )
    except Exception as e:
        logger.debug(f"Failed to log retrieval to Langfuse: {str(e)}")


def flush_traces():
    """
    Flush any pending traces to Langfuse.
    
    Call this before application shutdown to ensure all traces are sent.
    """
    if _langfuse_client:
        try:
            _langfuse_client.flush()
            logger.debug("Langfuse traces flushed successfully")
        except Exception as e:
            logger.error(f"Failed to flush Langfuse traces: {str(e)}")
