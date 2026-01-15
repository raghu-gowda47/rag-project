# RAG Project: Chat With Your Docs

A conversational AI system that answers questions about document content using Retrieval-Augmented Generation (RAG). Ask questions about your PDFs and get context-aware answers powered by local LLMs(Can be upgraded to cloud based LLM's)

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

4. Place your PDF in the data directory:
   ```bash
   mkdir -p data/documents
   cp your_pdf.pdf data/documents/Ramayana.pdf
   ```
   The system auto-creates `data/vector_db/` and `data/logs/` directories on first run.

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

- **data_loader.py**: PDF loading with automatic change detection via checkpoint tracking
- **text_splitter.py**: Chunks text using BPE tokenization for optimal LLM consumption
- **vectorstore.py**: Manages embeddings and ChromaDB vector operations
- **rag_chain.py**: Orchestrates the retrieval and generation pipeline
- **prompts.py**: Centralized prompt management with safety guardrails
- **main.py**: CLI interface with Langfuse tracing and logging
- **config.py**: Centralized configuration (paths, LLM settings, logging levels)
- **observability.py**: Langfuse integration with @trace_function decorators and context managers
- **__init__.py**: Package initialization and API exports

## Productionization & Scalability

- Containerize with Docker for portability.
- Use managed vector DB (e.g., Pinecone, Weaviate) for scale.
- Deploy LLM via managed service (SageMaker, Vertex AI, Azure OpenAI).
- Add API layer (FastAPI, Flask) for serving.
- Use cloud storage for documents.
- Observability (Langfuse) provides monitoring, logging, and performance tracking for production systems.

## RAG/LLM Approach & Decisions

### LLM Choice: Ollama + Gemma3
**Why:** Privacy-first, runs locally without sending data to cloud services. Gemma3 offers good instruction-following at minimal resource cost.

**Alternatives Considered:**
- OpenAI GPT-4: Better quality but cloud dependency, higher costs
- Anthropic Claude: Excellent reasoning but overkill for retrieval tasks

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
- Langsmith: Overkill for this scope
- Custom implementation: Too much reinvention

**Decision:** LangChain's flexibility allows easy swapping of components without rewriting orchestration logic.

### Chunking Strategy: BPE Tokenization
**Why:** Aligns with how LLMs tokenize text. Ensures chunks map cleanly to token boundaries, avoiding mid-word splits.

**Parameters:**
- `chunk_size=500`: Fits ~2000 tokens in Gemma3's context window with room for system prompt
- `chunk_overlap=100`: Ensures context continuity across chunk boundaries, prevents losing important relationships

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

**Current Implementation:**
- ✅ Structured logging with Python `logging` module (main.py, all modules)
- ✅ Langfuse integration for tracing all function calls with @trace_function decorator
- ✅ Latency monitoring via Langfuse traces (automatic timing of all operations)
- ✅ Error tracking via Langfuse and logging with try-catch blocks
- ✅ PDF change detection with checkpoint tracking
- ✅ External library log filtering (httpx, urllib3, langchain)
- ✅ Query context tracking with metadata (Langfuse trace_context)

**Langfuse Provides:**
- Distributed tracing across the entire RAG pipeline
- Latency metrics for each step (retrieval, LLM generation, etc.)
- Error and exception tracking
- Custom metrics via trace annotations
- Analytics dashboard for monitoring production

**Future Enhancements:**
- Retrieval quality metrics (recall, precision, NDCG)
- Custom scoring and feedback collection
- A/B testing different prompt variations
- User behavior analytics

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
✅ **Structured logging** - Python logging module with file and console output
✅ **Observability** - Langfuse integration with decorators and context managers
✅ **Config file** - Centralized src/config.py for all settings
✅ **PDF change detection** - Automatic vector DB rebuilding when PDF changes
✅ **Package structure** - Proper __init__.py for Python package
✅ **Error handling** - Comprehensive try-catch with logging

### Deliberately Kept Simple (For MVP):
❌ **Type hints** - Would add verbosity; not critical for prototype
❌ **Unit tests** - Manual testing sufficient for single-document setup
❌ **REST API** - CLI is functional; can add FastAPI for production
❌ **Web UI** - Can add Streamlit when needed
❌ **CI/CD pipeline** - Not needed for single-developer project  



## Use of AI Tools in Development

**My approach:** Accept Copilot(chat GPT/Claude) suggestions, ask the co-pilot to generate the code with suitable prompts, validate if its achieving the results desired, optmise the soultion, repeat if needed.


### What I Won't Use AI For:
- Decision rationale (these need my actual thinking)
- Architectural choices (requires tradeoff analysis, what is best suited for project)
- Testing & edge cases (need domain knowledge)

**Principle:** Use AI for acceleration, not delegation. I should be able to explain every decision and provide the sign off.

## Productionization & Scalability for Cloud (AWS/GCP/Azure)

### Current Limitations
- Single-document setup (Ramayana only)
- No multi-user support
- No API layer
- No authentication
- Single-threaded processing

### What I'd Do Differently With More Time

**Short-term (Still Pending):**
- [ ] Implement FastAPI endpoint for HTTP queries
- [ ] Unit tests for each module (pytest)
- [ ] Web UI (Streamlit demo)
- [ ] Query validation and error handling improvements
- [ ] Prompt version management (A/B testing)
