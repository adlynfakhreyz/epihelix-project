# Quick Start Guide - EpiHelix Backend

## TL;DR - Get Running in 2 Minutes

```bash
# 1. Setup
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Run (mock mode - no configuration needed)
uvicorn app.main:app --reload --port 8000

# 3. Test
curl http://localhost:8000/health
open http://localhost:8000/docs
```

Done! Backend is running with mock data.

---

## Using Real AI Models (HuggingFace)

### Step 1: Get Free HuggingFace API Key
1. Go to https://huggingface.co/settings/tokens
2. Click "New token"
3. Copy the token (starts with `hf_`)

### Step 2: Configure
```bash
# Edit backend/.env
LLM_PROVIDER=huggingface
EMBEDDER_PROVIDER=huggingface
HUGGINGFACE_API_KEY=hf_your_token_here
```

### Step 3: Restart
```bash
uvicorn app.main:app --reload --port 8000
```

Now using real AI! 🎉

---

## Features Available

### 1. Search (Keyword + Semantic)
```bash
# Keyword search
curl "http://localhost:8000/api/search/?q=influenza&limit=10"

# Semantic search (requires embedder)
curl "http://localhost:8000/api/search/?q=influenza&limit=10&semantic=true"

# Suggestions
curl "http://localhost:8000/api/search/suggestions?q=flu"
```

### 2. Entity Details (InfoBox)
```bash
curl "http://localhost:8000/api/entity/d1"
curl "http://localhost:8000/api/entity/d1?include_related=true"
```

### 3. LLM Summarization
```bash
curl -X POST http://localhost:8000/api/summary/generate \
  -H "Content-Type: application/json" \
  -d '{
    "entity_id": "d1",
    "include_relations": true
  }'
```

### 4. RAG Chatbot
```bash
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is influenza?",
    "session_id": "test_session"
  }'
```

---

## Configuration Options

### Mock Mode (Development - No Keys Needed)
```bash
LLM_PROVIDER=mock
EMBEDDER_PROVIDER=mock
NEO4J_URI=
```
**Use case:** Frontend development, testing, no AI API costs

### HuggingFace Mode (Production - Free Tier)
```bash
HUGGINGFACE_API_KEY=hf_xxxxx
LLM_PROVIDER=huggingface
EMBEDDER_PROVIDER=huggingface
```
**Use case:** Real AI without hosting costs

### Neo4j Aura Mode (Real Knowledge Graph)
```bash
NEO4J_URI=neo4j+s://xxxxx.databases.neo4j.io
NEO4J_PASSWORD=your_password
```
**Use case:** Production with real pandemic data

---

## Project Structure

```
backend/
├── app/
│   ├── main.py                    # FastAPI app entry
│   ├── models.py                  # Pydantic schemas
│   ├── mock_data.py               # Development data
│   │
│   ├── config/
│   │   └── settings.py           # Environment config
│   │
│   ├── core/
│   │   └── dependencies.py       # DI container
│   │
│   ├── db/
│   │   └── kg_client.py          # Neo4j/Mock clients
│   │
│   ├── repositories/
│   │   └── entity_repository.py  # Data access layer
│   │
│   ├── services/                 # Business logic
│   │   ├── llm_service.py       # ← NEW: LLM abstraction
│   │   ├── embedder_service.py  # ← NEW: Embeddings
│   │   ├── search_service.py    # ← UPDATED: Semantic search
│   │   ├── entity_service.py
│   │   ├── summary_service.py   # ← UPDATED: LLM summaries
│   │   └── chatbot_service.py   # ← UPDATED: RAG pipeline
│   │
│   └── routers/                  # HTTP endpoints
│       ├── search.py
│       ├── entity.py
│       └── chat.py
│
├── .env                          # ← UPDATED: New AI config
├── requirements.txt              # ← UPDATED: Added numpy
├── README.md
├── ARCHITECTURE.md
├── COMPLETE_ARCHITECTURE.md      # ← NEW: Full design docs
└── IMPLEMENTATION_SUMMARY.md
```

---

## What Changed (Latest Update)

### ✅ Added Self-Hosted AI Support
- **LLM Service** (`llm_service.py`)
  - Strategy pattern (swap providers)
  - HuggingFace Inference API
  - HuggingFace Spaces (Gradio)
  - Mock for development

- **Embedder Service** (`embedder_service.py`)
  - Sentence transformers via HF API
  - Cosine similarity search
  - Batch embedding support

### ✅ Enhanced Services
- **SearchService**: Added semantic + hybrid search
- **SummaryService**: LLM-powered entity summaries
- **ChatbotService**: Complete RAG pipeline

### ✅ Configuration
- New `.env` with HuggingFace settings
- Provider selection (mock/huggingface/space)
- Model configuration (Llama, Mistral, etc.)

---

## Recommended Models

### For Development (Fast, Free)
```bash
HUGGINGFACE_LLM_MODEL=meta-llama/Llama-3.2-3B-Instruct
HUGGINGFACE_EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

### For Production (Better Quality)
```bash
HUGGINGFACE_LLM_MODEL=mistralai/Mistral-7B-Instruct-v0.2
HUGGINGFACE_EMBEDDING_MODEL=BAAI/bge-small-en-v1.5
```

---

## API Documentation

**Interactive Docs:** http://localhost:8000/docs
**Health Check:** http://localhost:8000/health

---

## Troubleshooting

### "Module not found: httpx"
```bash
pip install -r requirements.txt
```

### "HuggingFace API error"
- Check your API key in `.env`
- Verify model name is correct
- Check HF API status: https://status.huggingface.co

### "Neo4j connection failed"
- Leave `NEO4J_URI` empty to use mock mode
- Or set up Neo4j Aura: https://neo4j.com/cloud/aura-free/

---

## Next: Frontend Integration

Now that backend is complete, next steps:
1. ✅ Backend complete (you are here)
2. ⏳ Build Next.js API client
3. ⏳ Create middleware for LLM routes
4. ⏳ Connect frontend to backend

See `app/ARCHITECTURE_DECISION.md` for frontend plan.
