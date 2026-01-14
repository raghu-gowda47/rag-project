# RAG Project: Chat With Your Docs

A conversational AI system that answers questions about document content using Retrieval-Augmented Generation (RAG). Ask questions about your PDFs and get context-aware answers powered by local LLMs.

## Quick Setup Instructions

### Prerequisites
- Python 3.10+
- Ollama installed and running (download from https://ollama.ai)
- Gemma3 model pulled in Ollama: `ollama pull gemma3`

### Installation & Running

1. Clone the repository:
   ```bash
   git clone <your-repo-url>
   cd "Rag Project"
   ```

2. Create virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Place your PDF in the project root (e.g., `Ramayana.pdf`)

5. Run the chatbot:
   ```bash
   python src/main.py
   ```

6. Start asking questions:
   ```
   Question: What is the main theme of the story?
   Answer: [Response based on PDF content]
   ```

## Architecture Overview

The system follows a standard RAG pipeline with clear separation of concerns:

```
┌─────────────┐
│   PDF       │
│  Upload     │
└──────┬──────┘
       │
       ▼
┌──────────────────────┐
│  Text Splitting      │ (BPE Tokenization)
│  chunk_size=500      │ Aligns with LLM context
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│  Embeddings          │ (all-MiniLM-L6-v2)
│  384-dim vectors     │ Fast & memory efficient
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│  ChromaDB Vector     │ (Persisted locally)
│  Store               │ Fast similarity search
└──────┬───────────────┘
       │
       │  ◄─── User Query
       │
       ▼
┌──────────────────────┐
│  Semantic Retriever  │ (Top-4 chunks)
│  (k=4)               │ Balances coverage & context
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│  Prompt Template     │ (Context + Question)
│  + Retrieved Context │ Explicit instructions
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│  Ollama LLM          │ (Gemma3)
│  (Local/Replaceable) │ Privacy-first approach
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│  Generated Answer    │
│  (Context-aware)     │
└──────────────────────┘
```

### Component Breakdown

- **data_loader.py**: Loads PDF documents and extracts text
- **text_splitter.py**: Chunks text using BPE tokenization for optimal LLM consumption
- **vectorstore.py**: Manages embeddings and vector database operations
- **rag_chain.py**: Orchestrates the retrieval and generation pipeline
- **prompts.py**: Centralized prompt management with safety guardrails
- **main.py**: CLI interface for interactive Q&A

## Productionization & Scalability

- Containerize with Docker for portability.
- Use managed vector DB (e.g., Pinecone, Weaviate) for scale.
- Deploy LLM via managed service (SageMaker, Vertex AI, Azure OpenAI).
- Add API layer (FastAPI, Flask) for serving.
- Use cloud storage for documents.
- Implement monitoring, logging, and autoscaling.

## RAG/LLM Approach & Decisions

### LLM Choice: Ollama + Gemma3
**Why:** Privacy-first, runs locally without sending data to cloud services. Gemma3 offers good instruction-following at minimal resource cost.

**Alternatives Considered:**
- OpenAI GPT-4: Better quality but cloud dependency, higher costs
- Anthropic Claude: Excellent reasoning but overkill for retrieval tasks
- Llama2: Good, but Gemma3 had better instruction-following in testing

**Trade-off:** Local inference is slower but acceptable for this use case; can swap to cloud LLM by changing 2 lines of code.

### Embedding Model: sentence-transformers/all-MiniLM-L6-v2
**Why:** 384-dimensional vectors, lightweight (22MB), fast inference, excellent quality for semantic similarity.

**Alternatives Considered:**
- BAAI/bge-base-en-v1.5: Larger, better performance but slower
- OpenAI text-embedding-3-small: Cloud dependency
- Contriever: Optimized for retrieval but overkill for local setup

**Decision:** MiniLM offers 95% of performance at 10% of the cost—perfect for resource-constrained scenarios.

### Vector Database: Chroma
**Why:** Lightweight, serverless, persistent storage. No setup overhead. Great for prototyping and small-to-medium datasets.

**Alternatives Considered:**
- Pinecone: Managed, scales well but costs money + cloud dependency
- Weaviate: Full-featured but heavier, requires more configuration
- FAISS: Faster but no persistence, harder to update

**Decision:** Chroma is the sweet spot for development. Easily replaceable with Pinecone for production (same API).

### Orchestration: LangChain
**Why:** Modular components, minimal boilerplate, great for rapid prototyping. The piping syntax (`|`) is elegant and composable.

**Alternatives Considered:**
- LlamaIndex: More opinionated about RAG, heavier dependencies
- Langsmith: Overkill for this scope
- Custom implementation: Too much reinvention

**Decision:** LangChain's flexibility allows easy swapping of components without rewriting orchestration logic.

### Chunking Strategy: BPE Tokenization
**Why:** Aligns with how LLMs tokenize text. Ensures chunks map cleanly to token boundaries, avoiding mid-word splits.

**Parameters:**
- `chunk_size=500`: Fits ~2000 tokens in Gemma3's context window with room for system prompt
- `chunk_overlap=100`: Ensures context continuity across chunk boundaries, prevents losing important relationships

**Reasoning:** Empirically tested on Ramayana—500 tokens captures coherent passages without excessive redundancy.

### Retrieval Strategy: Top-k=4
**Why:** 4 chunks (~2000 tokens total) provides enough context without diluting relevance or overwhelming the LLM.

**Decision Logic:**
- k=1: Too narrow, misses valid context
- k=4: Balanced relevance + coverage
- k>4: Diminishing returns, increases hallucination risk

### Prompt Engineering: Explicit Instructions + Context Limiting
**Current Prompt Strategy:**
```
You are a helpful assistant answering questions based on provided context.
- Answer ONLY using information from the context
- Be concise and direct
- If not available, say "The information is not available"
- Do not use external knowledge
```

**Design Decisions:**
1. **Role Definition**: Establishes helper persona
2. **Explicit Constraints**: "ONLY" and "Do not" prevents hallucination
3. **Fallback Behavior**: Tells LLM what to do when uncertain
4. **Brevity Instruction**: Prevents verbose rambling

**Why not few-shot?** Current approach is lightweight and general. Few-shot would help with domain-specific formats but adds complexity.

### Guardrails & Safety

**Built-in:**
1. Context-only answers (prompt enforces this)
2. Explicit "I don't know" instruction
3. No system prompt injection (LLM doesn't see user queries in system context)
4. Limited context window (prevents overwhelming the model)

**Not Implemented (Future):**
- Token counting before query
- Rate limiting
- Input validation/sanitization
- Output content filtering
- Audit logging

### Quality & Observability

**Current Approach:**
- Print statements for debugging
- PDF page count validation
- Chunk count visibility

**Gaps:**
- No structured logging (should use `logging` module)
- No metrics on retrieval quality (recall, precision)
- No latency monitoring
- No error tracking

**Why minimal now:** Keeping prototype simple. Production would need these.

## Key Technical Decisions & Reasoning

### 1. Modular Architecture Over Monolith
**Decision:** Split into `data_loader`, `text_splitter`, `vectorstore`, `rag_chain`, `prompts` modules.

**Why:** 
- Easier to test each component independently
- Can swap implementations without touching other modules
- Clear responsibility boundaries (SoC)
- Reduces cognitive load when reading code

**Trade-off:** Slightly more files vs. simpler mental model

### 2. BPE Tokenization Over Character/Word Splitting
**Decision:** Used HuggingFace tokenizers instead of simple character/word chunking.

**Why:**
- Token boundaries matter to LLMs—splitting mid-token wastes context
- BPE aligns input structure to how model processes text
- More reliable chunking across languages

**Evidence:** Tested on Ramayana; character splitting created incoherent chunks at boundaries.

### 3. Local First, Cloud-Ready Architecture
**Decision:** Used local Ollama + ChromaDB + HuggingFace embeddings, but with replaceable imports.

**Why:**
- No cloud bills during development
- Data privacy (especially important for sensitive documents)
- Faster iteration (no network latency)
- But: LLM/embedding imports are abstracted, so replacing with cloud is trivial

**Migration Path:** Change 2 lines in `rag_chain.py` to use `ChatOpenAI` instead of `OllamaLLM`.

### 4. Centralized Prompt Management
**Decision:** Created `prompts.py` to store all prompt templates.

**Why:**
- Prompts are configuration, not code
- Easy to version and compare prompt variations
- Single source of truth for guardrails
- Supports A/B testing different prompts

### 5. Error Handling: Fail Fast vs. Graceful Degradation
**Current:** Fail fast (exit on missing PDF).

**Rationale:** 
- Simpler to debug
- Better for development/testing
- Production would have retries and fallbacks

### 6. No Caching Layer (Yet)
**Decision:** Every query re-retrieves from vector DB.

**Why:** 
- Keeps code simple
- ChromaDB is already fast enough for prototyping
- Could add Redis caching later for repeated queries

## Engineering Standards

### Applied:
✅ **Modular code structure** - Each function does one thing  
✅ **Clear naming** - Functions and variables are self-documenting  
✅ **Dependency injection** - Functions take dependencies as arguments  
✅ **Requirements.txt** - Clear dependency management  
✅ **Separated concerns** - Data, embedding, chain logic are distinct  
✅ **Configuration externalization** - Hardcoded values in functions (can be moved to config file)

### Deliberately Skipped:
❌ **Type hints** - Would add verbosity; Python's duck typing works here  
❌ **Unit tests** - Added complexity; manual testing was sufficient for MVP  
❌ **Logging framework** - `print()` works for prototyping; would add `logging` module in production  
❌ **Config file** - Hardcoded values are fine for single-document setup  
❌ **API/Web UI** - CLI is sufficient for assessment; would add FastAPI for production  
❌ **CI/CD pipeline** - Not needed for single-developer project  

**Philosophy:** Start simple, add complexity when justified by requirements.

## Use of AI Tools in Development

### GitHub Copilot
**What it was good for:**
- Boilerplate code (imports, function signatures)
- Repetitive patterns (similar functions with variations)
- LangChain API suggestions (knows the syntax better than I do)

**What I had to fix:**
- Overly verbose docstrings ("This function loads a PDF..." → just the code)
- Generic variable names (`result`, `data`) → renamed to `splits`, `vectorstore`
- Comment quality ("Extract the last digit" → just let code speak)

**My approach:** Accept Copilot suggestions, then edit ruthlessly. No LLM-generated prose in final code.

### ChatGPT/Claude
**Used for:**
- Understanding LangChain's LCEL syntax (piping operator `|`)
- Explaining embedding dimensions and why MiniLM's 384-d works
- Brainstorming chunking strategies (token-based vs. semantic)

**How I validated:** Tested recommendations on actual Ramayana data before committing.

### What I Won't Use AI For:
- README documentation (must be my voice)
- Decision rationale (these need my actual thinking)
- Architectural choices (requires tradeoff analysis)
- Testing & edge cases (need domain knowledge)

**Principle:** Use AI for acceleration, not delegation. I should be able to explain every decision.

## Productionization & Scalability for Cloud (AWS/GCP/Azure)

### Current Limitations
- Single-document setup (Ramayana only)
- No multi-user support
- No API layer
- No authentication
- Single-threaded processing

### AWS Deployment Architecture

```
┌────────────────┐
│  S3 (Docs)     │
└────────┬───────┘
         │
         ▼
┌─────────────────────────────────────┐
│  Lambda (Doc Processing)            │
│  - Trigger: S3 upload               │
│  - Split & embed documents          │
│  - Store in RDS (metadata)          │
└─────────┬───────────────────────────┘
          │
          ▼
┌─────────────────────────────────────┐
│  RDS PostgreSQL (Vector Storage)    │
│  - pgvector extension for embedding │
│  - Horizontal scaling via Aurora    │
└─────────┬───────────────────────────┘
          │
          ▼
┌─────────────────────────────────────┐
│  API Gateway + Lambda (Query Handler)│
│  - REST endpoint                    │
│  - Auth via API Gateway + Cognito   │
│  - Retrieve + Generate              │
└─────────┬───────────────────────────┘
          │
          ▼
┌──────────────────────────────────────┐
│  SageMaker Endpoint (LLM)            │
│  - Llama2/Mistral (or bring your own)│
│  - Auto-scaling based on load       │
└──────────────────────────────────────┘
```

### GCP Alternative

```
Cloud Storage (PDFs) 
  ▼
Cloud Functions (Chunking/Embedding)
  ▼
Vertex AI Vector Search (Replacement for ChromaDB)
  ▼
Cloud Run (API + Query Handler)
  ▼
Vertex AI LLM APIs (Or custom model)
```

### Azure Alternative

```
Blob Storage (PDFs)
  ▼
Azure Functions (Processing)
  ▼
Azure Cognitive Search (Vector Search)
  ▼
App Service / ACI (API)
  ▼
Azure OpenAI or MLflow deployment
```

### Key Changes for Production

**1. Storage**
```python
# Current
docs = load_pdf("local_path.pdf")

# Production
from google.cloud import storage
bucket = storage.Client().bucket("my-docs")
blob = bucket.blob("Ramayana.pdf")
docs = load_from_stream(blob.download_as_bytes())
```

**2. Vector Store**
```python
# Current
vectorstore = Chroma(...)

# Production (AWS)
from langchain_community.vectorstores import RDS
vectorstore = RDS.from_documents(..., connection=rds_connection)

# Or cloud-native
from langchain_community.vectorstores import VertexAIVectorSearch
```

**3. LLM**
```python
# Current
llm = OllamaLLM(model="gemma3")

# Production (AWS)
from langchain_community.llms.bedrock import Bedrock
llm = Bedrock(model_id="anthropic.claude-3-sonnet")

# Or managed endpoint
from langchain_community.llms.sagemaker_endpoint import SagemakerEndpoint
```

**4. Logging & Monitoring**
```python
import logging
from aws_lambda_logging import setup
import watchtower

setup(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.addHandler(watchtower.CloudWatchLogHandler())
```

**5. API Layer**
```python
from fastapi import FastAPI
from mangum import Mangum  # ASGI adapter for Lambda

app = FastAPI()

@app.post("/query")
async def query(question: str, doc_id: str):
    result = rag_chain.invoke(question)
    return {"answer": result}

handler = Mangum(app)  # AWS Lambda handler
```

**6. Multi-tenancy**
```python
# Current: Single document
vectorstore = Chroma(persist_directory="./db")

# Production: Per-user/org isolation
vectorstore = Chroma(
    persist_directory=f"./db/{org_id}/",
    client_id=user_id  # Tenant isolation
)
```

### Cost Estimates (AWS Monthly)

| Component | Current | Production |
|-----------|---------|-----------|
| Lambda (doc processing) | Free | $20-50 |
| RDS (vector DB) | - | $200-500 |
| Bedrock LLM | - | $0.001/input token, $0.003/output token |
| CloudWatch Logs | Free | $50-100 |
| **Total** | **Free** | **$300-1000** |

### Scalability Checklist

- [ ] Use managed vector DB (RDS with pgvector or Vertex AI Vector Search)
- [ ] Implement connection pooling for DB access
- [ ] Add caching layer (Redis/ElastiCache)
- [ ] Rate limiting on API endpoints
- [ ] Request queuing (SQS/Pub-Sub) for async processing
- [ ] Monitoring & alerting (CloudWatch/Stackdriver)
- [ ] Auto-scaling policies for Lambda/App Service
- [ ] Cost optimization (reserved instances, spot instances)

## Edge Cases & Limitations

### Known Issues
1. **Large PDFs**: Memory usage grows linearly with document size. Chunking helps but not a permanent solution.
2. **Slow Inference**: Local Ollama is ~2-5x slower than cloud LLMs. Acceptable for demo, not for production.
3. **Fixed k=4 Retrieval**: Optimal k varies by document; future work could make this adaptive.
4. **No context awareness between queries**: Each question is independent; no conversation history.
5. **No document updates**: Vector store is immutable once created. Updating requires full re-indexing.

### What I'd Do Differently With More Time

**Short-term (1-2 weeks):**
- [ ] Add logging module (structured logs, metrics)
- [ ] Implement FastAPI endpoint for HTTP queries
- [ ] Unit tests for each module (pytest)
- [ ] Docker containerization
- [ ] Query validation and error handling
- [ ] Prompt version management (A/B testing)

**Medium-term (1 month):**
- [ ] Multi-document support with document metadata
- [ ] Conversation history (context across queries)
- [ ] Web UI (React/Streamlit for demo)
- [ ] Retrieval evaluation metrics (NDCG, MRR)
- [ ] Query re-ranking using cross-encoder
- [ ] Implement HyDE (Hypothetical Document Embeddings) for better retrieval

**Long-term (Production):**
- [ ] Deploy to AWS with CI/CD pipeline
- [ ] Managed vector DB (RDS pgvector or Pinecone)
- [ ] Multi-tenancy support
- [ ] Document versioning and update mechanism
- [ ] Usage tracking and cost optimization
- [ ] Advanced guardrails (content filtering, PII detection)
- [ ] Fine-tune embedding model on domain-specific data
- [ ] Implement RAG variants (RAPTOR, Self-RAG for better quality)
