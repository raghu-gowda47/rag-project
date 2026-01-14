# Quick Reference Guide

## Project Overview
RAG (Retrieval-Augmented Generation) chatbot that answers questions about PDF documents using semantic search and local LLMs.

**Tech Stack:**
- **LLM**: Ollama + Gemma3 (local, privacy-first)
- **Embeddings**: sentence-transformers/all-MiniLM-L6-v2
- **Vector DB**: Chroma (local, persistent)
- **Framework**: LangChain
- **Chunking**: BPE tokenization (500 tokens, 100 overlap)
- **Retrieval**: Semantic search (k=4)

## File Structure

```
src/
├── main.py          # CLI entry point, logging setup, interactive loop
├── data_loader.py   # PDF loading with error handling
├── text_splitter.py # BPE tokenization chunking
├── vectorstore.py   # Embedding + ChromaDB operations
├── rag_chain.py     # LLM + retrieval orchestration
└── prompts.py       # Centralized prompt templates

Root:
├── README.md            # Comprehensive guide (start here)
├── DEPLOYMENT.md        # Cloud deployment (AWS/GCP/Azure)
├── DEVELOPMENT.md       # Dev setup & extensions
├── Dockerfile           # Container image
├── docker-compose.yml   # Local compose setup
└── requirements.txt     # Python dependencies
```

## Quick Start

### 1. Local Setup (No Docker)
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
ollama pull gemma3  # In separate terminal
ollama serve        # Start Ollama
python src/main.py  # Run chatbot
```

### 2. Docker Setup
```bash
docker-compose up --build
# Or manually:
docker build -t rag-chatbot .
docker run -it -e OLLAMA_HOST=host.docker.internal:11434 rag-chatbot
```

## Key Configuration Parameters

| Parameter | Value | Why |
|-----------|-------|-----|
| chunk_size | 500 tokens | Fits Gemma3 context window |
| chunk_overlap | 100 tokens | Prevents losing context at boundaries |
| k_retrieve | 4 chunks | ~2000 tokens, balances relevance |
| embedding_model | all-MiniLM-L6-v2 | Fast, high quality |
| llm_model | gemma3 | Good instruction-following, local |
| vector_db | Chroma | Lightweight, persistent |

## Module Responsibilities

### data_loader.py
- Load PDF files
- Extract text with page metadata
- Error handling for missing/corrupt files

### text_splitter.py
- Initialize BPE tokenizer (gpt2)
- Split documents into overlapping chunks
- Maintain text structure integrity

### vectorstore.py
- Initialize embedding model
- Create vector embeddings
- Persist to Chroma database
- Handle DB operations

### rag_chain.py
- Setup retriever (top-k semantic search)
- Initialize LLM (Ollama)
- Create prompt template
- Orchestrate LCEL chain

### prompts.py
- RAG_PROMPT: Main prompt with guardrails
- Configurable, versionable, A/B testable

### main.py
- Logging setup
- Pipeline orchestration
- Interactive CLI loop
- Error handling

## Common Tasks

### Change LLM
```python
# In rag_chain.py
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(model_name="gpt-4")  # Use OpenAI instead
```

### Change Embedding Model
```python
# In vectorstore.py
HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
```

### Adjust Chunking
```python
# In main.py or text_splitter.py
splits = split_documents(docs, chunk_size=300, chunk_overlap=50)
```

### Change Retrieval k
```python
# In rag_chain.py
retriever = vectorstore.as_retriever(search_kwargs={"k": 2})  # Was k=4
```

### Modify Prompt
```python
# In prompts.py
RAG_PROMPT = """Your new prompt here..."""
```

## Architecture Flow

```
User Input
    ↓
[CLI] main.py
    ↓
[Retrieval] vectorstore.as_retriever()
    ├→ Embed user question
    ├→ Semantic search in Chroma
    └→ Return top-4 chunks
    ↓
[Formatting] ChatPromptTemplate
    ├→ Add retrieved context
    ├→ Add user question
    └→ Apply guardrails
    ↓
[Generation] OllamaLLM
    ├→ Process prompt
    ├→ Generate answer
    └→ Parse output
    ↓
[Response] StrOutputParser
    └→ Display to user
```

## Logging

### Log Levels
- `DEBUG`: Detailed info for troubleshooting
- `INFO`: Normal operations (default)
- `WARNING`: Something unexpected but not critical
- `ERROR`: Error occurred, but application continues
- `CRITICAL`: Fatal error, application may stop

### View Logs
```bash
# Real-time
tail -f rag_chatbot.log

# View recent entries
tail -20 rag_chatbot.log

# Search logs
grep "Error" rag_chatbot.log
grep "Query #1" rag_chatbot.log
```

## Performance Tuning

### Faster Responses
1. Reduce chunk_size (500 → 300)
2. Reduce k (4 → 2)
3. Use smaller embedding model
4. Increase chunk_overlap (diminishes benefit)
5. Add caching layer (Redis)

### Better Quality
1. Use larger embedding model (bge-base-en)
2. Increase k (4 → 6-8)
3. Fine-tune prompt
4. Implement query re-ranking
5. Add conversation history

### Memory Optimization
1. Reduce chunk_size
2. Use smaller LLM or cloud service
3. Implement document streaming
4. Add pagination

## Debugging

### Enable Debug Logging
```python
# In main.py
setup_logging(level=logging.DEBUG)
```

### Check Retrieved Chunks
Add to `rag_chain.py`:
```python
docs = retriever.get_relevant_documents("Your question")
for doc in docs:
    print(f"Chunk: {doc.page_content[:100]}...")
```

### Common Issues

**"PDF not found"**
- Ensure Ramayana.pdf is in project root
- Check file permissions

**"Ollama connection failed"**
- Start Ollama: `ollama serve`
- Verify gemma3: `ollama list`
- Check OLLAMA_HOST env var

**"Out of memory"**
- Reduce chunk_size
- Reduce k parameter
- Use smaller embedding model

**"Slow responses"**
- Ollama is CPU-bound (expected)
- Use cloud LLM for faster responses
- Implement caching

## Deployment Checklist

### Local
- [ ] `python -m venv venv`
- [ ] `pip install -r requirements.txt`
- [ ] `ollama pull gemma3 && ollama serve`
- [ ] `python src/main.py`

### Docker
- [ ] `docker build -t rag-chatbot .`
- [ ] `docker run -it -e OLLAMA_HOST=host.docker.internal:11434 rag-chatbot`

### Cloud (AWS)
- [ ] Create Lambda functions (doc processing + query)
- [ ] Setup RDS with pgvector
- [ ] Deploy to SageMaker (LLM) or use Bedrock
- [ ] Create API Gateway
- [ ] Setup CloudWatch monitoring
- See DEPLOYMENT.md for details

## Key Metrics to Monitor

| Metric | Target | Tool |
|--------|--------|------|
| Query latency | <5s | CloudWatch |
| Retrieval quality | >0.8 NDCG | Custom eval |
| Error rate | <1% | Logging |
| Token usage | Cost tracking | CloudWatch |
| Vector DB latency | <100ms | Monitoring |

## Resources

- [LangChain Docs](https://python.langchain.com/)
- [Chroma Docs](https://docs.trychroma.com/)
- [Ollama Docs](https://github.com/ollama/ollama)
- [HuggingFace Models](https://huggingface.co/sentence-transformers/)
- [Gemma Model Card](https://huggingface.co/google/gemma-7b-it)

## Support

1. Check README.md for setup issues
2. Check DEVELOPMENT.md for dev questions
3. Check DEPLOYMENT.md for production questions
4. Check logs: `tail -f rag_chatbot.log`
5. Enable DEBUG logging for troubleshooting

---

**Start with README.md for full details. This is just a quick reference!**
