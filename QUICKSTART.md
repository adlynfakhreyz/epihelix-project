# EpiHelix - 2-Minute Quickstart

Get the full stack running in under 2 minutes.

## Prerequisites

- Docker (for Neo4j)
- Python 3.8+
- Node.js 18+

## 🚀 Fastest Path to Running App

### Terminal 1: Start Neo4j
```bash
cd infrastructure
docker-compose up -d
# Neo4j Browser: http://localhost:7474 (neo4j/epihelix123)
```

### Terminal 2: Load Data + Start Backend
```bash
# Load KG data
cd kg-construction/etl
python -m venv venv && source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r ../requirements.txt
python load_all_data.py

# Start API
cd ../../backend
pip install -r requirements.txt
uvicorn app.main:app --reload
# API Docs: http://localhost:8000/docs
```

### Terminal 3: Start Frontend
```bash
cd app
npm install
npm run dev
# App: http://localhost:3000
```

**Done!** 🎉 You now have:
- Neo4j with 22 diseases, 195+ countries, temporal data (1980-2021)
- FastAPI backend with RAG chatbot (self-hosted AI, no API keys)
- Next.js frontend with dark theme, animations, global search

## 🔧 Configuration Options

### Backend (.env)
```bash
cd backend
cp .env.example .env
```

Edit `.env`:
```bash
# Neo4j (defaults work with docker-compose)
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=epihelix123

# AI Models (self-hosted, no API keys)
HUGGING_FACE_MODEL=sentence-transformers/all-MiniLM-L6-v2
HUGGING_FACE_LLM=google/flan-t5-base

# Optional: Use OpenAI instead
# OPENAI_API_KEY=sk-...
# LLM_PROVIDER=openai
```

### Frontend
Next.js automatically uses `http://localhost:8000` in development. For production:
```bash
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
```

## 📊 What Gets Loaded

**From 4 CSV Datasets**:
- 22 diseases: 9 infectious (malaria, tuberculosis, HIV/AIDS, cholera, etc.) + 15 vaccine-preventable (measles, polio, tetanus, etc.) + COVID-19
- 195+ countries with temporal data (cases, deaths, vaccination coverage)
- Time range: 1980-2021

**Optional Enrichment** (run after `load_all_data.py`):
```bash
cd kg-construction/etl
python enrich_all.py  # ~10-15 min, adds Wikidata symptoms/ICD-10, DBpedia historical events
```

## 🧪 Test Endpoints

### Backend API
```bash
# Search for malaria
curl "http://localhost:8000/api/search?q=malaria"

# Get entity details
curl "http://localhost:8000/api/entity/disease:malaria"

# Run Cypher query
curl -X POST "http://localhost:8000/api/query" \
  -H "Content-Type: application/json" \
  -d '{"type":"cypher","query":"MATCH (d:Disease) RETURN d.name LIMIT 5"}'

# Chat with AI
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"session_id":"test","message":"What are the symptoms of malaria?"}'
```

### Frontend
1. Visit http://localhost:3000
2. Press **⌘K** / **Ctrl+K** for global search
3. Try searches: "malaria", "COVID-19", "measles"
4. Click entity cards → see details with visualizations
5. Go to `/query` → run Cypher queries
6. Go to `/chat` → ask pandemic questions

## 🐳 Docker All-in-One

**Start everything** (Neo4j + Backend + Frontend):
```bash
docker-compose -f infrastructure/docker-compose.yml up
```

## 🛠️ Troubleshooting

### Neo4j Connection Failed
```bash
# Check Neo4j is running
docker-compose -f infrastructure/docker-compose.yml ps

# View logs
docker-compose -f infrastructure/docker-compose.yml logs neo4j

# Restart
docker-compose -f infrastructure/docker-compose.yml restart neo4j
```

### Backend Errors
```bash
# Check Python version (need 3.8+)
python --version

# Reinstall dependencies
cd backend
pip install --upgrade -r requirements.txt

# Run in mock mode (no Neo4j needed)
unset NEO4J_URI && uvicorn app.main:app --reload
```

### Frontend Build Errors
```bash
# Clear cache and reinstall
cd app
rm -rf node_modules package-lock.json .next
npm install
npm run dev
```

### ETL Load Errors
```bash
# Check CSV files exist
ls -lh kg-construction/data/raw/
# Should see: disease_cases.csv, vaccination_coverage.csv, excess_deaths_cumulative_per_million_covid.csv, number-of-deaths-from-cholera.csv

# Test Neo4j connection
cd kg-construction/etl
python -c "from neo4j_connection import Neo4jConnection; Neo4jConnection.test_connection()"
```

## 📚 Next Steps

- **Load more data**: Run `python enrich_all.py` for Wikidata/DBpedia enrichment
- **Explore queries**: See `backend/app/query_examples.py` for 16 real Cypher examples
- **Customize UI**: Edit `app/src/components/` and `app/src/app/globals.css`
- **Add graph viz**: Implement `app/src/components/GraphView/` (Cytoscape or react-force-graph)
- **Deploy**: See main README for Docker deployment

## 📖 Full Documentation

- **README.md** - Complete project overview, architecture, schema
- **.github/instructions/epihelix-instructions.instructions.md** - Technical reference for AI agents

## 🎯 Key Features Available

- ✅ **Hybrid Search** - Keyword + semantic search
- ✅ **Entity Explorer** - 7 entity types (Country, Disease, Outbreak, VaccinationRecord, Organization, Vaccine, PandemicEvent)
- ✅ **AI Chat** - RAG-powered Q&A with source attribution
- ✅ **Query Console** - Direct Cypher/SPARQL queries
- ✅ **Dark Theme UI** - Glass morphism, animated particle background
- ✅ **External KG** - Wikidata + DBpedia integration

Happy exploring! 🦠🔬
