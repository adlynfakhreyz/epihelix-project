# EpiHelix Kaggle AI Services

Self-hosted AI services using Kaggle's free P100 GPU - no API keys required for embeddings, reranking, and LLM inference.

## Overview

This directory contains a **unified Kaggle notebook** (`epihelix-ai-services.ipynb`) that hosts all 3 GPU-accelerated AI services on a single endpoint:

- 🔍 **Embedder**: sentence-transformers/all-MiniLM-L6-v2 (384-dim embeddings)
- 🔄 **Reranker**: BAAI/bge-reranker-v2-m3 (cross-encoder for search results)
- 💬 **LLM**: Qwen/Qwen2.5-3B-Instruct (conversational AI for RAG chatbot)

**Why Kaggle?**
- ✅ **Free P100 GPU** (16GB VRAM) - 30 hours/week quota
- ✅ **All models fit in memory** (~8.4GB total VRAM)
- ✅ **Single endpoint** via ngrok (simpler than 3 separate notebooks)
- ✅ **No API costs** (unlike OpenAI, Cohere, or Anthropic)
- ✅ **Built-in secrets** management for ngrok tokens
- ✅ **Automatic restarts** if notebook sleeps

---

## Architecture Integration

```
┌─────────────────────────────────────────────────────────────┐
│ EpiHelix Backend (FastAPI)                                  │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Keyword      │  │ Semantic     │  │ Hybrid       │     │
│  │ Retriever    │  │ Retriever    │  │ Retriever    │     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
│         │                  │                  │             │
│         └──────────────────┼──────────────────┘             │
│                            │                                │
│         ┌──────────────────▼──────────────────┐            │
│         │  Utils Layer (HTTP clients)         │            │
│         ├──────────────────────────────────────┤            │
│         │  • Embedder (embedder.py)           │            │
│         │  • Reranker (reranker.py)           │            │
│         │  • LLM (llm.py)                     │            │
│         └──────────────────┬──────────────────┘            │
│                            │                                │
└────────────────────────────┼────────────────────────────────┘
                             │ HTTP/REST
                             │
              ┌──────────────▼──────────────┐
              │ Kaggle Notebook (P100 GPU)  │
              ├─────────────────────────────┤
              │ FastAPI Server (port 5000)  │
              │                             │
              │ POST /embed                 │
              │ POST /rerank                │
              │ POST /generate              │
              │                             │
              │ Models Loaded:              │
              │ - MiniLM-L6-v2 (195MB)     │
              │ - bge-reranker-v2 (2.2GB)  │
              │ - Qwen2.5-3B (6GB)         │
              └──────────────┬──────────────┘
                             │
                    ┌────────▼────────┐
                    │ ngrok Tunnel    │
                    │ (public HTTPS)  │
                    └─────────────────┘
```

**Request Flow Example (Hybrid Search)**:

1. User searches "COVID-19 USA deaths"
2. Backend `HybridRetriever` calls:
   - `KeywordRetriever` → gets 50 candidates from Neo4j
   - `SemanticRetriever` → calls `Embedder.embed_text()` → Kaggle `/embed` → gets top 50 by cosine similarity
3. Merge candidates (100 total)
4. Call `Reranker.rerank()` → Kaggle `/rerank` → cross-encoder scores
5. Return top 20 results

---

## Quick Start

### Prerequisites
- Kaggle account (free)
- ngrok account (free tier: 1 endpoint, no time limits)
- Backend already configured (FastAPI in `/backend/`)

### 1. Setup ngrok Token

1. Go to [ngrok Dashboard](https://dashboard.ngrok.com/get-started/your-authtoken)
2. Copy your authtoken
3. In Kaggle:
   - Go to **Settings** → **Secrets**
   - Click **Add Secret**
   - Name: `NGROK_TOKEN`
   - Value: `<your-authtoken>`

### 2. Upload & Run Notebook

1. Go to [Kaggle Notebooks](https://www.kaggle.com/code)
2. Click **"New Notebook"** → **"Import Notebook"**
3. Upload `epihelix-ai-services.ipynb` from this directory
4. **Configure Settings** (right sidebar):
   - ✅ **Accelerator**: GPU P100
   - ✅ **Internet**: ON
   - ✅ **Persistence**: Files only (default)

### 3. Run & Get Public URL

1. Click **"Run All"** (takes ~3 minutes)
2. Wait for models to load:
   ```
   🔄 Loading reranker...  [DONE]
   🔍 Loading embedder...  [DONE]
   💬 Loading LLM...       [DONE]
   🚀 Server ready on port 5000
   ```
3. Look for ngrok output:
   ```
   ✅ PUBLIC URL: https://xxxx-xx-xxx-xxx-xx.ngrok-free.app
   
   📝 Add this to your backend .env file:
   
      KAGGLE_AI_ENDPOINT=https://xxxx-xx-xxx-xxx-xx.ngrok-free.app
   ```

### 4. Configure Backend

Add to `/backend/.env`:

```bash
# Kaggle AI Services (copy URL from notebook output)
KAGGLE_AI_ENDPOINT=https://xxxx-xx-xxx-xxx-xx.ngrok-free.app

# Strategy Pattern: Use Kaggle providers
RERANKER_PROVIDER=kaggle
EMBEDDER_PROVIDER=kaggle
LLM_PROVIDER=kaggle
```

**Alternative: Use HuggingFace (local CPU)**
```bash
# For development without Kaggle GPU
RERANKER_PROVIDER=huggingface
EMBEDDER_PROVIDER=huggingface
LLM_PROVIDER=huggingface
```

### 5. Restart Backend

```bash
cd backend
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
uvicorn app.main:app --reload
```

**✅ Check logs for successful initialization:**
```
INFO: 🎯 KAGGLE RERANKER initialized: https://xxxx.ngrok-free.app
INFO: 🎯 KAGGLE EMBEDDER initialized: https://xxxx.ngrok-free.app
INFO: 🎯 KAGGLE LLM initialized: https://xxxx.ngrok-free.app
INFO: ✅ All AI services initialized successfully
```

### 6. Test Integration

```bash
# Test embedding
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "COVID-19 deaths USA", "semantic": true, "limit": 10}'

# Test reranking
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "malaria Africa trends", "semantic": true, "rerank": true, "limit": 20}'

# Test chatbot (RAG)
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What was the COVID-19 excess mortality in USA?", "session_id": "test123"}'
```

---

## API Endpoints

The Kaggle notebook exposes a FastAPI server with 4 endpoints:

### 1. Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "models_loaded": {
    "embedder": true,
    "reranker": true,
    "llm": true
  },
  "gpu_available": true,
  "memory_allocated_gb": 8.4
}
```

### 2. Text Embedding
```http
POST /embed
Content-Type: application/json

{
  "texts": ["COVID-19 pandemic", "influenza outbreak"],
  "normalize": true
}
```

**Response:**
```json
{
  "embeddings": [
    [0.023, -0.145, 0.678, ...],  // 384 dimensions
    [0.012, -0.098, 0.543, ...]
  ],
  "model": "sentence-transformers/all-MiniLM-L6-v2",
  "dimensions": 384
}
```

**Used by:** `SemanticRetriever` for vector search

### 3. Reranking
```http
POST /rerank
Content-Type: application/json

{
  "query": "COVID-19 deaths USA",
  "documents": [
    {"id": "1", "text": "United States COVID-19 mortality data..."},
    {"id": "2", "text": "Influenza deaths in Canada..."}
  ],
  "top_k": 10
}
```

**Response:**
```json
{
  "results": [
    {"id": "1", "score": 0.89, "text": "United States COVID-19..."},
    {"id": "2", "score": 0.12, "text": "Influenza deaths..."}
  ],
  "model": "BAAI/bge-reranker-v2-m3"
}
```

**Used by:** `HybridRetriever` to reorder search results

### 4. Text Generation (LLM)
```http
POST /generate
Content-Type: application/json

{
  "messages": [
    {"role": "system", "content": "You are a pandemic data assistant."},
    {"role": "user", "content": "What was COVID-19 excess mortality in USA?"}
  ],
  "max_tokens": 512,
  "temperature": 0.7
}
```

**Response:**
```json
{
  "response": "Based on the data, the United States experienced approximately...",
  "model": "Qwen/Qwen2.5-3B-Instruct",
  "tokens_used": 87
}
```

**Used by:** `ChatbotService` for RAG responses

---

## Troubleshooting

### Issue: ngrok URL changes every restart
**Solution:** Save the new URL and update backend `.env` file. Restart backend.

**Automation (optional):** Add a webhook endpoint in your backend that Kaggle can POST the new URL to on startup.

### Issue: Kaggle session expires
**Symptom:** Backend errors: `ConnectionError: Failed to connect to Kaggle endpoint`

**Solution:** 
1. Go to Kaggle notebook
2. Click **"Run All"** again (models reload from cache - faster)
3. Copy new ngrok URL
4. Update backend `.env`
5. Restart backend

**Prevention:** Kaggle notebooks auto-sleep after 60 mins of inactivity. Keep the notebook open or use cron to ping `/health` every 30 mins.

### Issue: Quota exceeded (30h/week)
**Solution:** Switch to HuggingFace provider (CPU-based, slower but unlimited):

```bash
# backend/.env
RERANKER_PROVIDER=huggingface
EMBEDDER_PROVIDER=huggingface
LLM_PROVIDER=huggingface
```

Restart backend - it will load models locally (requires 8GB+ RAM).

### Issue: Models fail to load
**Error:** `OutOfMemoryError` or `RuntimeError: CUDA out of memory`

**Solution:**
- Ensure P100 GPU is selected (not T4 or CPU)
- Clear Kaggle session output and restart
- Check if other notebooks are using GPU in your account

### Issue: Slow inference times
**Expected Latencies:**
- Embedding (1 text): ~50ms
- Embedding (batch of 100): ~500ms
- Reranking (20 documents): ~200ms
- LLM generation (100 tokens): ~2s

**If slower:**
- Check Kaggle notebook logs for errors
- Verify GPU is being used (look for CUDA messages)
- Test ngrok latency: `ping <your-ngrok-domain>`

---

## Development Tips

### Local Testing (Without Kaggle)

For rapid development without GPU dependency:

```bash
# backend/.env
RERANKER_PROVIDER=huggingface
EMBEDDER_PROVIDER=huggingface
LLM_PROVIDER=huggingface

# Optional: Use mock provider for testing
RERANKER_PROVIDER=mock
EMBEDDER_PROVIDER=mock
LLM_PROVIDER=mock
```

Mock provider returns dummy data - useful for frontend integration testing.

### Monitor Kaggle Usage

Check your quota at [Kaggle Settings](https://www.kaggle.com/settings):
- GPU hours used this week
- Remaining quota

**Tip:** Use Kaggle GPU only for demos/testing. For production, deploy models to cloud GPU (AWS SageMaker, GCP Vertex AI, Hugging Face Inference Endpoints).

### Modify Models

To change models, edit `epihelix-ai-services.ipynb`:

```python
# Cell: Load Models
EMBEDDER_MODEL = "sentence-transformers/all-MiniLM-L6-v2"  # Change here
RERANKER_MODEL = "BAAI/bge-reranker-v2-m3"
LLM_MODEL = "Qwen/Qwen2.5-3B-Instruct"
```

**Recommended alternatives:**
- **Embedder**: `sentence-transformers/all-mpnet-base-v2` (768-dim, better accuracy)
- **Reranker**: `cross-encoder/ms-marco-MiniLM-L-6-v2` (lighter, faster)
- **LLM**: `microsoft/Phi-3-mini-4k-instruct` (3.8B params, good quality)

Re-run notebook and update backend `.env` if needed.

---

## File Structure

```
kaggle-notebooks/
├── epihelix-ai-services.ipynb   # Unified AI services notebook
└── README.md                     # This file
```

**Notebook Contents:**
1. Install dependencies (FastAPI, transformers, torch, ngrok)
2. Load 3 models into GPU memory
3. Define FastAPI endpoints (/embed, /rerank, /generate, /health)
4. Start ngrok tunnel
5. Run FastAPI server (port 5000)
6. Keep-alive loop (prevents auto-sleep)

---

## Next Steps

1. ✅ **Setup Kaggle notebook** (this guide)
2. ✅ **Configure backend** to use Kaggle endpoints
3. ⚠️ **Test search integration** (keyword + semantic + reranking)
4. ⚠️ **Test chatbot** (RAG with LLM)
5. ⚠️ **Deploy backend** to Vercel (production)
6. ⚠️ **Optional:** Migrate to dedicated GPU hosting for 24/7 uptime

**For production deployment**, see root `README.md` → Deployment section.

---

## Alternative: Self-Hosted Models (No Kaggle)

If you prefer not to use Kaggle, run models locally or in cloud:

### Option 1: Local CPU (Development)
```bash
# backend/.env
RERANKER_PROVIDER=huggingface
EMBEDDER_PROVIDER=huggingface
LLM_PROVIDER=huggingface
```

Models load from HuggingFace Hub on first run (~2GB download). Requires 8GB+ RAM.

### Option 2: Cloud GPU (Production)
Deploy models to:
- **Hugging Face Inference Endpoints** ($0.60/hr for GPU)
- **AWS SageMaker** (ml.g4dn.xlarge ~$0.70/hr)
- **GCP Vertex AI** (n1-standard-4 + T4 GPU ~$0.50/hr)
- **Modal** (serverless GPU - pay per request)

Update `backend/app/utils/` clients to use cloud endpoints.

---

## Support

**Issues with Kaggle setup?**
- Check [Kaggle Notebooks Documentation](https://www.kaggle.com/docs/notebooks)
- Verify GPU quota at [Kaggle Settings](https://www.kaggle.com/settings)

**Issues with backend integration?**
- See `backend/README.md` for API client debugging
- Check backend logs for HTTP errors
- Test Kaggle endpoint directly: `curl https://<ngrok-url>/health`

**General questions?**
- See root `README.md` for architecture overview
- See `QUICKSTART.md` for full setup guide
Response:
```json
{
  "status": "healthy",
  "gpu_available": true,
  "gpu_memory_used_gb": 8.4,
  "models_loaded": true
}
```

### Rerank Documents
```http
POST /rerank
Content-Type: application/json

{
  "query": "COVID-19 pandemic",
  "documents": ["text1", "text2", "text3"],
  "top_k": 20
}
```

Response:
```json
{
  "results": [
    {"index": 0, "score": 0.94},
    {"index": 2, "score": 0.87}
  ],
  "model": "BAAI/bge-reranker-v2-m3"
}
```

### Generate Embeddings
```http
POST /embed
Content-Type: application/json

{
  "texts": ["COVID-19", "Influenza"],
  "normalize": true
}
```

Response:
```json
{
  "embeddings": [[0.1, 0.2, ...], [0.3, 0.4, ...]],
  "dimension": 384,
  "model": "sentence-transformers/all-MiniLM-L6-v2"
}
```

### Chat Completion
```http
POST /chat
Content-Type: application/json

{
  "messages": [
    {"role": "user", "content": "What is a pandemic?"}
  ],
  "temperature": 0.7,
  "max_tokens": 512
}
```

Response:
```json
{
  "response": "A pandemic is a global outbreak...",
  "model": "meta-llama/Llama-3.2-3B-Instruct"
}
```

---

## Memory Usage

On Kaggle P100 (16GB):

| Model | Memory | Speed |
|-------|--------|-------|
| Reranker (BAAI) | ~2GB | ~50ms/pair |
| Embedder (MiniLM) | ~400MB | ~20ms/text |
| LLM (Llama-3.2-3B) | ~6GB | ~2s/response |
| **Total** | **~8.4GB** | Good headroom |

---

## Limitations & Workarounds

### Session Duration
- **Limit**: 12 hours max per session
- **Workaround**: Click "Run All" to restart (keeps same URL via ngrok)

### Weekly Quota
- **Limit**: 30 GPU hours/week
- **Workaround**: 
  - Use mock providers during development
  - Only enable Kaggle for production testing
  - Monitor usage at [kaggle.com/account](https://www.kaggle.com/account)

### ngrok URL Changes
- **Issue**: New URL on each restart
- **Workaround**: Update `.env` with new `KAGGLE_AI_ENDPOINT`
- **Future**: Use ngrok static domains (requires account)

### Cold Starts
- **Issue**: First request after idle takes ~5s
- **Workaround**: Notebook keeps alive with 60s heartbeat

---

## Troubleshooting

### Backend can't reach Kaggle endpoint

1. **Check notebook is running:**
   ```bash
   curl https://xxxx.ngrok-free.app/health
   ```

2. **Check firewall/CORS:**
   - Kaggle endpoint allows all origins
   - ngrok URLs are public

3. **Check if models are loaded:**
   - Visit `{KAGGLE_ENDPOINT}/health` in browser
   - Should show `models_loaded: true`

### Out of GPU memory

1. **Check usage in notebook:**
   ```python
   import torch
   print(f"GPU Memory: {torch.cuda.memory_allocated(0) / 1e9:.2f}GB")
   ```

2. **Clear cache and restart:**
   - Click "Interrupt" → "Run All"

### Model loading fails

1. **Check internet is enabled** in notebook settings
2. **Check HuggingFace is accessible:**
   ```python
   !curl -I https://huggingface.co
   ```
3. **Use cached models** (first run downloads, subsequent runs use cache)

---

## Development Workflow

### Local Development (No GPU)
```bash
# Use mock providers
RERANKER_PROVIDER=mock
EMBEDDER_PROVIDER=mock
LLM_PROVIDER=mock
```

### Testing (Kaggle GPU)
```bash
# Enable Kaggle for specific features
RERANKER_PROVIDER=kaggle  # Most important
EMBEDDER_PROVIDER=mock    # Local is fast enough
LLM_PROVIDER=mock         # Save quota
```

### Production (Full GPU)
```bash
# Enable all features
RERANKER_PROVIDER=kaggle
EMBEDDER_PROVIDER=kaggle
LLM_PROVIDER=kaggle
```

---

## Alternative: Self-Hosted GPU

For production, consider migrating to:

1. **AWS SageMaker** - Managed inference endpoints
2. **Modal.com** - Serverless GPU functions
3. **Replicate** - Pay-per-use GPU API
4. **Banana.dev** - Dedicated GPU containers

**Migration path:**
- Code is provider-agnostic (Strategy pattern)
- Add new provider class (e.g., `ModalReranker`)
- Update `dependencies.py` factory
- No frontend changes needed

---

## Cost Comparison

| Provider | Cost/hour | Quota | Best For |
|----------|-----------|-------|----------|
| **Kaggle** | FREE | 30h/week | Development, demos |
| Google Colab | FREE | ~12h/session | Quick tests |
| Modal | $0.60/h | Pay-as-you-go | Production |
| AWS SageMaker | $0.90/h | Pay-as-you-go | Enterprise |
| Replicate | $0.0002/s | Pay-per-second | Bursty loads |

**Recommendation**: Start with Kaggle (free), migrate to Modal/Replicate for production.

---

## Monitoring

### Check Service Health

```bash
# Quick health check
curl https://xxxx.ngrok-free.app/health

# API documentation
open https://xxxx.ngrok-free.app/docs
```

### Check Backend Logs

```bash
# Look for Kaggle initialization
tail -f logs/backend.log | grep KAGGLE

# Expected output:
# 🎯 KAGGLE RERANKER initialized: https://xxxx.ngrok-free.app
# 🔄 KAGGLE RERANKER: Reranking 200 docs...
# ✅ KAGGLE RERANKER: Successfully reranked → 20 results
```

### Monitor GPU Usage

In Kaggle notebook, add cell:
```python
import time
while True:
    if torch.cuda.is_available():
        used = torch.cuda.memory_allocated(0) / 1e9
        total = torch.cuda.get_device_properties(0).total_memory / 1e9
        print(f"💓 GPU: {used:.2f}GB / {total:.2f}GB")
    time.sleep(60)
```

---

## Support

- **Kaggle Issues**: [kaggle.com/product-feedback](https://www.kaggle.com/product-feedback)
- **ngrok Issues**: [ngrok.com/docs](https://ngrok.com/docs)
- **Backend Issues**: Check `/backend/logs/` or open GitHub issue

---

## Next Steps

1. ✅ Upload notebook to Kaggle
2. ✅ Enable GPU + Internet
3. ✅ Run All and copy ngrok URL
4. ✅ Update backend `.env`
5. ✅ Test search with real reranking
6. 📊 Monitor performance and GPU usage
7. 🚀 Consider migration to paid GPU for production
