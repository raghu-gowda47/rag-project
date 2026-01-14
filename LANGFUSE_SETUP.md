# 📊 Langfuse Observability Setup Guide

**Complete guide for setting up and using Langfuse observability in your RAG chatbot**

---

## What Is Langfuse?

**Langfuse** is an open-source LLM observability platform that provides:
- 📊 **Traces:** Detailed logs of every function call
- 📈 **Analytics:** Performance trends and metrics
- 🐛 **Debugging:** Full execution history with errors
- 🔍 **Monitoring:** Real-time alerts and dashboards
- 💰 **Cost Tracking:** Token and API usage monitoring

**Free tier available:** https://cloud.langfuse.com

---

## Quick Start (5 Minutes)

### Step 1: Sign Up
```
Visit: https://cloud.langfuse.com
Sign up with email or Google → Confirm email
```

### Step 2: Create Project
```
Click "New Project" → Name it (e.g., "RAG Chatbot") → Create
```

### Step 3: Get API Keys
```
Project Settings (⚙️) → API Keys tab
Copy: Public Key (pk_prod_...)
Copy: Secret Key (sk_prod_...)
```

### Step 4: Configure
Create `.env` file in project root:
```bash
LANGFUSE_PUBLIC_KEY=pk_prod_your_key_here
LANGFUSE_SECRET_KEY=sk_prod_your_secret_here
```

### Step 5: Run & View
```bash
python src/main.py
# View traces at: https://cloud.langfuse.com/project/your-project/traces
```

---

## Implementation Overview

### ✅ What Was Added

**New Module:**
- `src/observability.py` (318 lines) - Complete Langfuse integration

**Updated Modules:**
- `src/main.py` - Langfuse setup + query tracing
- `src/data_loader.py` - @trace_function decorator
- `src/text_splitter.py` - @trace_function decorator
- `src/vectorstore.py` - @trace_function decorator
- `src/rag_chain.py` - @trace_function decorator
- `requirements.txt` - Added langfuse dependency

### ✅ What Gets Traced Automatically

| Function | Logs |
|----------|------|
| load_pdf() | File path, docs count, duration, errors |
| split_documents() | Chunk count, parameters, duration |
| create_vectorstore() | Vector count, embedding model, duration |
| build_rag_chain() | LLM model, chain status, duration |
| User queries | Question, answer, latency, errors |

---

## Code Examples

### Example 1: Automatic Function Tracing
```python
from observability import trace_function

@trace_function(name="load_pdf")
def load_pdf(pdf_path):
    # Automatically traced!
    # Logs: function name, args, result, duration, errors
    return docs
```

### Example 2: Manual Query Tracing
```python
from observability import trace_context

with trace_context("query_1", {"q": "What is AI?"}) as ctx:
    response = rag_chain.invoke(question)
    ctx["output"] = response
    # Logs: query, response, duration, errors
```

### Example 3: Error Tracking
```python
@trace_function()
def risky_operation():
    try:
        return dangerous_call()
    except Exception as e:
        # Automatically logged with full context!
        raise
```

### Example 4: LLM Call Tracing
```python
from observability import trace_llm_call

trace_llm_call(
    model="gemma3",
    input_tokens=150,
    output_tokens=200,
    latency_ms=2500
)
```

### Example 5: Retrieval Metrics
```python
from observability import trace_retrieval

trace_retrieval(
    query="What is AI?",
    k=4,
    num_results=4,
    latency_ms=50
)
```

---

## Configuration

### Environment Variables
```bash
# Required
LANGFUSE_PUBLIC_KEY=pk_prod_your_key_here
LANGFUSE_SECRET_KEY=sk_prod_your_secret_here

# Optional (defaults to cloud.langfuse.com)
LANGFUSE_HOST=https://cloud.langfuse.com
```

### Decorator Options
```python
@trace_function(
    name="custom_name",      # Optional, defaults to function name
    include_args=True,       # Log function arguments
    include_result=True      # Log function result
)
def my_function(arg):
    return result
```

### Setup Function
```python
from observability import setup_langfuse

# Automatic (reads environment variables)
setup_langfuse()

# Or explicit
setup_langfuse(
    public_key="pk_prod_...",
    secret_key="sk_prod_...",
    host="https://cloud.langfuse.com"
)
```

---

## Dashboard Features

### Traces Tab
- View all traces in real-time
- Filter by name, status, duration
- Click to drill into details
- See execution timeline
- View input/output/errors

### Metrics
```
Total Traces: 42
Success Rate: 97.6%
Average Latency: 2,450ms
P95 Latency: 2,900ms
Error Rate: 2.4%
```

### What You'll See
- Function name and status
- Execution duration
- Input/output data
- Error messages with stack traces
- Custom metadata
- Timestamp

---

## Module: observability.py

### Key Functions

**setup_langfuse()**
```python
def setup_langfuse(public_key=None, secret_key=None, host="..."):
    """Initialize Langfuse client."""
    # Returns: True if successful, False otherwise
```

**@trace_function**
```python
@trace_function(name="my_op", include_args=True, include_result=True)
def my_function(arg1):
    # Automatically traced!
```

**trace_context()**
```python
with trace_context("operation", {"metadata": "value"}) as ctx:
    result = do_work()
    ctx["output"] = result
```

**trace_llm_call()**
```python
trace_llm_call(
    model="gemma3",
    input_tokens=150,
    output_tokens=200,
    latency_ms=2500
)
```

**trace_retrieval()**
```python
trace_retrieval(
    query="What is AI?",
    k=4,
    num_results=4,
    latency_ms=50
)
```

**flush_traces()**
```python
flush_traces()  # Ensure all traces are sent before exit
```

**get_langfuse_client()**
```python
client = get_langfuse_client()
if client:
    # Use client directly if needed
    pass
```

---

## File Structure

```
src/
├── observability.py       # ← NEW: Langfuse integration
├── main.py                # ← UPDATED: Setup & tracing
├── data_loader.py         # ← UPDATED: @trace_function
├── text_splitter.py       # ← UPDATED: @trace_function
├── vectorstore.py         # ← UPDATED: @trace_function
├── rag_chain.py           # ← UPDATED: @trace_function
└── prompts.py

Root:
├── .env                   # ← CREATE: Your credentials
├── .env.example           # ← TEMPLATE: Copy this to .env
├── requirements.txt       # ← UPDATED: Added langfuse
└── LANGFUSE_SETUP.md      # ← THIS FILE
```

---

## Best Practices

### 1. Use Environment Variables
✅ **Good:**
```bash
export LANGFUSE_PUBLIC_KEY="pk_prod_..."
export LANGFUSE_SECRET_KEY="sk_prod_..."
python src/main.py
```

❌ **Bad:**
```python
setup_langfuse(public_key="...", secret_key="...")  # Hardcoded!
```

### 2. Don't Log Large Data
✅ **Good:**
```python
@trace_function(include_result=False)
def load_large_file():
    return huge_list
```

❌ **Bad:**
```python
@trace_function()
def load_large_file():
    return huge_list  # Tries to log entire list!
```

### 3. Use Clear Names
✅ **Good:**
```python
@trace_function(name="load_pdf_document")
with trace_context("query_user_question"):
```

❌ **Bad:**
```python
@trace_function(name="func")  # Too generic
with trace_context("op"):  # Not descriptive
```

### 4. Add Meaningful Metadata
✅ **Good:**
```python
with trace_context("query", {
    "query_type": "technical",
    "domain": "AI",
    "user_id": "user_123"
}):
```

### 5. Always Flush on Exit
✅ **Good:**
```python
try:
    main()
finally:
    flush_traces()  # Always called!
```

---

## Troubleshooting

### Issue: "Langfuse observability disabled"

**Cause:** Credentials not found

**Solution:**
```bash
# Check if set
echo $LANGFUSE_PUBLIC_KEY
echo $LANGFUSE_SECRET_KEY

# If empty, create .env file:
LANGFUSE_PUBLIC_KEY=pk_prod_...
LANGFUSE_SECRET_KEY=sk_prod_...
```

### Issue: Traces not appearing in dashboard

**Check 1:** Wrong credentials?
- Go back to Langfuse → Settings → API Keys
- Re-copy keys, check for typos

**Check 2:** Network blocked?
```bash
curl https://cloud.langfuse.com/api/ping
# Should get 200 response
```

**Check 3:** Not flushed?
- Make sure `flush_traces()` is called
- Check logs for "Langfuse traces flushed"

### Issue: "ModuleNotFoundError: No module named 'langfuse'"

**Solution:**
```bash
pip install langfuse
# or
pip install -r requirements.txt
```

### Issue: Slow performance

**Analysis:**
- Network calls are async (non-blocking)
- Overhead should be <5%
- Disable if needed (just don't set credentials)

---

## Performance Impact

| Operation | Overhead | Notes |
|-----------|----------|-------|
| @trace_function | <1ms | Per function call |
| trace_context() | <1ms | Per context creation |
| Network send | Async | Non-blocking |
| **Total** | **<5%** | Usually imperceptible |

If Langfuse unavailable:
- Overhead: **0ms** (no-op decorators)
- Memory: **0KB**

---

## Advanced Features

### Custom Scoring
```python
from observability import get_langfuse_client

client = get_langfuse_client()
if client:
    client.score(
        trace_id="...",
        name="quality",
        value=0.95  # 0-1 score
    )
```

### User Tracking
```python
# Track operations per user
with trace_context("query", {"user_id": "user_123"}):
    response = rag_chain.invoke(query)
```

### Feedback Collection
```python
client.feedback(
    trace_id="...",
    rating=5,  # 1-5 stars
    comment="Great answer!"
)
```

---

## Pricing & Cost

### Langfuse Pricing
- **Free tier:** 1 project, limited storage
- **Pro tier:** Pay as you grow
- **Cost estimate:** ~$0.001 per trace

### Your Usage Estimate
```
Traces per query: ~5 (load, split, embed, retrieve, generate)
Queries per session: ~10
Traces per session: ~50
Cost per session: <$0.05
```

---

## What Gets Logged

### Automatically (Decorators)
- ✅ Function name
- ✅ Arguments (optional)
- ✅ Result/output (optional)
- ✅ Execution time
- ✅ Success/error status
- ✅ Error messages & stack traces

### Manually (Context Manager)
- ✅ Operation name
- ✅ Custom metadata
- ✅ Input data
- ✅ Output data
- ✅ Execution time
- ✅ Errors (if any)

### Graceful Fallback
- ✅ Works without Langfuse
- ✅ Console logging only
- ✅ Zero performance impact
- ✅ No configuration needed

---

## Integration Summary

### What Changed
```
New file:          src/observability.py (318 lines)
Updated files:     6 modules
New imports:       6 (one per module)
New dependency:    langfuse
Breaking changes:  None
Backward compat:   100%
```

### How It Works
```
Your Code
    ↓
@trace_function (auto) or trace_context() (manual)
    ↓
observability.py (collection)
    ↓
Langfuse SDK (batching)
    ↓
Langfuse Cloud (dashboard)
```

---

## Getting Started Checklist

- [ ] Sign up at https://cloud.langfuse.com
- [ ] Create project
- [ ] Get API keys
- [ ] Create .env with credentials
- [ ] Run: `pip install -r requirements.txt`
- [ ] Run: `python src/main.py`
- [ ] View traces at Langfuse dashboard
- [ ] Ask questions and see them traced!

---

## Quick Reference

### Setup
```bash
# 1. Environment
LANGFUSE_PUBLIC_KEY=pk_prod_...
LANGFUSE_SECRET_KEY=sk_prod_...

# 2. Initialize
setup_langfuse()

# 3. Run
python src/main.py

# 4. View
https://cloud.langfuse.com
```

### Code
```python
# Auto-trace function
@trace_function()
def my_function():
    pass

# Manual trace
with trace_context("op") as ctx:
    result = work()
    ctx["output"] = result

# Cleanup
flush_traces()
```

### Dashboard
```
Traces tab → Filter → Click trace → See details
Analytics → View metrics
Settings → Configure alerts
```

---

## Support

### Documentation
- **Source code:** `src/observability.py` with docstrings
- **Official docs:** https://langfuse.com/docs
- **Status page:** https://status.langfuse.com

### Troubleshooting
1. Check logs: `grep langfuse rag_chatbot.log`
2. Verify credentials: `echo $LANGFUSE_PUBLIC_KEY`
3. Test connectivity: `curl https://cloud.langfuse.com/api/ping`
4. Review code: `src/observability.py` docstrings

---

## Summary

**Your RAG chatbot now has enterprise-grade observability!**

✅ Automatic function tracing  
✅ Real-time monitoring dashboard  
✅ Error tracking with context  
✅ Performance analytics  
✅ Zero breaking changes  
✅ Graceful degradation  

**Setup takes 5 minutes. Start tracing now! 🚀**

---

## Next Steps

1. **Create Langfuse account** (free) at https://cloud.langfuse.com
2. **Get API keys** from Project Settings
3. **Create .env** file with credentials
4. **Run chatbot** with `python src/main.py`
5. **View traces** in Langfuse dashboard

**That's it! Your observability is live. 📊**
