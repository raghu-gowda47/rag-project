# Development Guide

## Project Structure

```
Rag Project/
├── src/
│   ├── main.py              # Entry point with CLI interface
│   ├── data_loader.py       # PDF loading logic
│   ├── text_splitter.py     # Document chunking with BPE
│   ├── vectorstore.py       # Embedding and vector DB operations
│   ├── rag_chain.py         # RAG pipeline orchestration
│   └── prompts.py           # Prompt templates and guardrails
├── Ramayana.pdf             # Sample document
├── requirements.txt         # Python dependencies
├── Dockerfile               # Container configuration
├── docker-compose.yml       # Local development setup
├── README.md                # Project overview and setup
├── DEPLOYMENT.md            # Cloud deployment guide
└── .gitignore               # Git ignore rules
```

## Setup for Development

### 1. Local Setup (Without Docker)

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Ensure Ollama is running
# Download from https://ollama.ai
ollama pull gemma3
ollama serve  # In a separate terminal

# Run the chatbot
python src/main.py
```

### 2. Docker Setup

```bash
# Build and run
docker-compose up --build

# Or without compose
docker build -t rag-chatbot .
docker run -it \
  -v ./chroma_db_bpe:/app/chroma_db_bpe \
  -e OLLAMA_HOST=host.docker.internal:11434 \
  rag-chatbot
```

## Making Changes

### Adding a New Module

If you want to add a new component (e.g., a reranker):

1. Create `src/reranker.py`
2. Add docstring explaining the module
3. Implement with logging
4. Add to imports in `main.py`
5. Update requirements.txt if new dependencies

Example:
```python
# src/reranker.py
import logging

logger = logging.getLogger(__name__)

def rerank_results(chunks, question, top_k=4):
    """Rerank retrieved chunks by relevance."""
    logger.info(f"Reranking {len(chunks)} chunks")
    # Implementation here
    return reranked_chunks
```

### Modifying the Prompt

Edit `src/prompts.py`:
```python
# Add new prompt template
NEW_PROMPT = """Your new prompt here..."""

# In rag_chain.py, change:
prompt = ChatPromptTemplate.from_template(RAG_PROMPT)
# To:
prompt = ChatPromptTemplate.from_template(NEW_PROMPT)
```

### Testing Locally

```bash
# Run with debug logging
python src/main.py  # Check console output

# Monitor logs
tail -f rag_chatbot.log

# Test specific query
python -c "
from src.main import main
# Add breakpoints or test code
"
```

### Environment Variables

Create `.env` file for local development:
```bash
# .env
OLLAMA_MODEL=gemma3
CHUNK_SIZE=500
CHUNK_OVERLAP=100
K_RETRIEVE=4
LOG_LEVEL=INFO
```

Load in main.py:
```python
from dotenv import load_dotenv
load_dotenv()

model = os.getenv('OLLAMA_MODEL', 'gemma3')
```

## Common Tasks

### Regenerate Vector Store

```bash
# Remove old store
rm -rf chroma_db_bpe/

# Run chatbot again (will recreate)
python src/main.py
```

### Change Embedding Model

In `src/vectorstore.py`:
```python
# Change from
HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# To any of:
# - sentence-transformers/all-mpnet-base-v2 (better but slower)
# - sentence-transformers/paraphrase-MiniLM-L6-v2 (good for paraphrase)
# - sentence-transformers/multi-qa-MiniLM-L6-cos-v1 (optimized for Q&A)
```

### Change LLM

In `src/rag_chain.py`:
```python
# Current (local)
llm = OllamaLLM(model="gemma3")

# Cloud alternatives
# OpenAI
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(model_name="gpt-4")

# Anthropic
from langchain_anthropic import ChatAnthropic
llm = ChatAnthropic(model="claude-3-sonnet")

# HuggingFace
from langchain_huggingface import HuggingFaceEndpoint
llm = HuggingFaceEndpoint(repo_id="meta-llama/Llama-2-7b-chat-hf")
```

### Monitor Performance

```python
# Add to main.py
import time

start = time.time()
response = rag_chain.invoke(question)
latency = time.time() - start

logger.info(f"Query latency: {latency:.2f}s")
logger.info(f"Answer length: {len(response)} chars")
```

## Debugging

### Enable Debug Logging

In `main.py`:
```python
setup_logging(level=logging.DEBUG)  # Instead of INFO
```

### Check What's Being Retrieved

Add to `src/rag_chain.py`:
```python
def build_rag_chain(vectorstore):
    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
    
    # Debug: log retrieved documents
    def log_retrieved(question):
        docs = retriever.get_relevant_documents(question)
        logger.debug(f"Retrieved {len(docs)} chunks:")
        for i, doc in enumerate(docs):
            logger.debug(f"  [{i}] {doc.page_content[:100]}...")
        return docs
    
    # ... rest of chain
```

### Common Issues

**Issue: "PDF not found"**
- Ensure `Ramayana.pdf` is in the project root
- Check file permissions: `ls -l Ramayana.pdf`

**Issue: Ollama connection failed**
- Start Ollama: `ollama serve`
- Check port: `ollama list` (should show gemma3)
- On Docker: use `OLLAMA_HOST=host.docker.internal:11434`

**Issue: Out of memory**
- Reduce chunk_size (500 → 300)
- Reduce k (4 → 2)
- Use smaller embedding model

**Issue: Slow responses**
- CPU-bound: upgrade hardware or use cloud LLM
- I/O-bound: use caching layer (Redis)
- Embedding slow: use smaller model (e.g., all-MiniLM)

## Code Style

### Naming Conventions
- Functions: `lowercase_with_underscores`
- Classes: `PascalCase`
- Constants: `UPPERCASE_WITH_UNDERSCORES`
- Variables: `lowercase_with_underscores`

### Documentation
- Add docstrings to all functions
- Explain *why*, not just *what*
- Include examples for complex functions

Example:
```python
def split_documents(docs, chunk_size=500):
    """
    Split documents into chunks using BPE tokenization.
    
    Why BPE? Aligns with how LLMs tokenize text, avoiding mid-word splits.
    
    Args:
        docs: List of document objects
        chunk_size: Tokens per chunk (default: 500)
        
    Returns:
        List of chunked documents
    """
```

### Error Handling
- Use specific exceptions
- Log before raising
- Provide context in messages

```python
try:
    vectorstore = create_vectorstore(splits, path)
except Exception as e:
    logger.error(f"Failed to create vector store at {path}: {str(e)}")
    raise ValueError("Vector store creation failed") from e
```

## Extending the System

### Add Multi-Document Support

```python
# Modify data_loader.py
def load_pdfs_from_directory(directory):
    """Load all PDFs from a directory."""
    documents = []
    for pdf_file in glob.glob(f"{directory}/*.pdf"):
        docs = load_pdf(pdf_file)
        documents.extend(docs)
    return documents

# In main.py
docs = load_pdfs_from_directory("./pdfs/")
```

### Add Conversation History

```python
# New module: src/conversation.py
class ConversationManager:
    def __init__(self):
        self.history = []
    
    def add_query(self, question, answer):
        self.history.append({
            'question': question,
            'answer': answer,
            'timestamp': datetime.now()
        })
    
    def get_context(self):
        """Include recent history in prompt."""
        return "\n".join([
            f"Q: {item['question']}\nA: {item['answer']}"
            for item in self.history[-3:]  # Last 3 turns
        ])
```

### Add Web UI

```bash
# Install Streamlit
pip install streamlit

# Create app.py
import streamlit as st
from src.rag_chain import build_rag_chain

st.title("RAG Chatbot")
question = st.text_input("Ask a question:")

if question:
    answer = rag_chain.invoke(question)
    st.write(answer)

# Run
streamlit run app.py
```

## Resources

- [LangChain Documentation](https://python.langchain.com/)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [HuggingFace Transformers](https://huggingface.co/docs/transformers/)
- [Ollama Documentation](https://github.com/ollama/ollama)

