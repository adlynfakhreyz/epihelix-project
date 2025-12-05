# EpiHelix (PIE) - Pandemic Insights Explorer

A production-ready knowledge graph application exploring pandemic data with Neo4j, integrating 4 CSV datasets + external knowledge graphs (Wikidata, DBpedia).

## 🎯 Overview

EpiHelix visualizes **22 diseases** across **195+ countries** using **7 entity types** from real historical data (1980-2021):
- 9 infectious diseases (malaria, tuberculosis, HIV/AIDS, cholera, etc.)
- 15 vaccine-preventable diseases (measles, polio, tetanus, etc.)
- COVID-19 excess mortality data
- Vaccination coverage statistics

**Key Features**:
- 🔍 **Hybrid Search** - Keyword + semantic search with autocomplete
- 📊 **Entity Explorer** - Browse diseases, countries, outbreaks, vaccinations, organizations
- 💬 **AI Chat** - RAG-powered chatbot for pandemic Q&A (self-hosted AI, no API keys)
- 🗺️ **Visualizations** - Interactive graphs, timelines, geographic data
- 🌐 **External Enrichment** - Wikidata (symptoms, ICD-10) + DBpedia (historical events)
- 🎨 **Modern UI** - Dark theme, glass morphism, animated particle background

## 🏗️ Architecture

### Tech Stack
- **Frontend**: Next.js 16 (JavaScript/JSX) + shadcn/ui + Tailwind v3 + Framer Motion
- **Backend**: FastAPI (layered architecture) with Strategy pattern for AI providers
- **Knowledge Graph**: Neo4j (7 node types: Country, Disease, Outbreak, VaccinationRecord, Organization, Vaccine, PandemicEvent)
- **AI**: HuggingFace self-hosted (sentence-transformers for embeddings, no API keys needed)
- **External KG**: Wikidata + DBpedia (SPARQL queries for enrichment)

### Monorepo Structure
```
/epihelix-project/
├── app/                          # Next.js frontend (port 3000)
│   ├── src/app/                  # Pages & middleware routes
│   │   ├── page.jsx              # Home (hero, features, stats)
│   │   ├── search/page.jsx       # Search results
│   │   ├── entity/[id]/page.jsx  # Entity details
│   │   ├── query/page.jsx        # Cypher/SPARQL console
│   │   ├── chat/page.jsx         # AI chatbot
│   │   └── api/                  # BFF middleware (6 routes)
│   ├── src/components/           # UI components
│   │   ├── ui/                   # shadcn/ui primitives
│   │   ├── Shared/               # Header, Footer, GlobalSearch, AnimatedBackground
│   │   ├── SearchBar/            # Autocomplete search
│   │   ├── EntityCard/           # Result cards
│   │   └── InfoBox/              # Entity detail view
│   ├── src/hooks/                # React Query hooks (useSearch, useEntity, etc.)
│   └── src/lib/                  # API client, utils, animations
│
├── backend/                      # FastAPI service (port 8000)
│   └── app/
│       ├── main.py               # FastAPI app with lifecycle management
│       ├── models.py             # 7 Pydantic models (Country, Disease, etc.)
│       ├── kg_data.py            # Real data (22 diseases, countries, orgs)
│       ├── query_examples.py     # 16 real Cypher queries
│       ├── routers/              # HTTP endpoints (search, entity, chat)
│       ├── services/             # Business logic (SearchService, RAG chatbot)
│       ├── repositories/         # Data access (Neo4j/SPARQL/Mock)
│       └── db/                   # KG clients (connection pooling)
│
├── kg-construction/              # ETL pipeline
│   ├── etl/                      # Data loaders + enrichers
│   │   ├── load_all_data.py      # Load 4 CSV datasets → Neo4j
│   │   ├── enrich_all.py         # Fetch Wikidata/DBpedia metadata
│   │   └── *.py                  # Individual dataset loaders
│   ├── data/raw/                 # CSV files (disease_cases, vaccination, etc.)
│   └── ontology/                 # Schema documentation
│
└── infrastructure/               # Docker Compose
    └── docker-compose.yml        # Neo4j + services
```

## 🚀 Quick Start

### Prerequisites
- **Docker** (for Neo4j)
- **Python 3.8+** (backend + ETL)
- **Node.js 18+** (frontend)

### 1️⃣ Start Neo4j Database
```bash
cd infrastructure
docker-compose up -d

# Verify Neo4j is running
docker-compose ps

# Access Neo4j Browser: http://localhost:7474
# Credentials: neo4j / epihelix123
# Bolt: bolt://localhost:7687
```

### 2️⃣ Load Knowledge Graph Data
```bash
cd kg-construction/etl

# Create Python environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r ../requirements.txt

# Load all 4 CSV datasets (disease_cases, vaccination, COVID-19, cholera)
python load_all_data.py

# Optional: Enrich with Wikidata + DBpedia (~10-15 minutes)
python enrich_all.py
```

**Loaded Data**:
- 22 diseases (9 infectious + 15 vaccine-preventable + COVID-19)
- 195+ countries with demographics
- Temporal data: cases, deaths, vaccination coverage (1980-2021)
- 3 organizations (WHO, CDC, ECDC)

### 3️⃣ Start Backend (FastAPI)
```bash
cd backend

# Create Python environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file (or use defaults)
cp .env.example .env

# Edit .env (optional - defaults work with docker-compose):
# NEO4J_URI=bolt://localhost:7687
# NEO4J_USER=neo4j
# NEO4J_PASSWORD=epihelix123
# HUGGING_FACE_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Start API server
uvicorn app.main:app --reload

# API available at http://localhost:8000
# Docs: http://localhost:8000/docs
```

**Mock Mode** (works without Neo4j): Just run `uvicorn app.main:app --reload` without configuring .env

### 4️⃣ Start Frontend (Next.js)
```bash
cd app

# Install dependencies
npm install

# Start dev server
npm run dev

# App available at http://localhost:3000
```

**Frontend Features**:
- Animated particle background (pulsing nodes, infinite space)
- Global search modal (⌘K / Ctrl+K)
- Glass morphism UI (70% card opacity, backdrop blur)
- Typewriter effect on search bars
- Responsive design (mobile, tablet, desktop)

## 📊 Knowledge Graph Schema

### Node Types (7 Total)
1. **Country** - 195+ countries
   - Properties: `name`, `iso_code`, `population`, `lat`, `lon`, `continent`
   - From: Wikidata enrichment

2. **Disease** - 22 diseases
   - Properties: `name`, `category`, `icd_code`, `symptoms`, `description`
   - Sources: disease_cases.csv (9), vaccination_coverage.csv (15), COVID data (1)

3. **Outbreak** - Temporal case/death data
   - Properties: `year`, `cases`, `deaths`, `country`, `disease`
   - From: disease_cases.csv, COVID excess deaths

4. **VaccinationRecord** - Coverage data
   - Properties: `year`, `coverage_percent`, `country`, `vaccine`
   - From: vaccination_coverage.csv

5. **Organization** - Health organizations
   - Properties: `name`, `role`, `founded`, `url`
   - Sources: WHO, CDC, ECDC (Wikidata enrichment)

6. **Vaccine** - Vaccine data
   - Properties: `name`, `manufacturer`, `type`
   - From: COVID vaccination data

7. **PandemicEvent** - Historical events
   - Properties: `name`, `start_year`, `end_year`, `description`, `wikipedia_url`
   - From: DBpedia enrichment

### Relationships
- `Country -[:HAS_OUTBREAK]-> Outbreak`
- `Outbreak -[:CAUSED_BY]-> Disease`
- `Country -[:HAS_VACCINATION_RECORD]-> VaccinationRecord`
- `VaccinationRecord -[:FOR_DISEASE]-> Disease`
- `Organization -[:MONITORS]-> Disease`
- `PandemicEvent -[:LOCATED_IN]-> Country`

### Example Cypher Queries

**Top 10 countries by COVID-19 excess deaths (2021)**:
```cypher
MATCH (c:Country)-[:HAS_OUTBREAK]->(o:Outbreak)-[:CAUSED_BY]->(d:Disease {name: 'COVID-19'})
WHERE o.year = 2021
RETURN c.name AS country, o.excess_deaths_per_million AS excess_deaths
ORDER BY excess_deaths DESC LIMIT 10
```

**Malaria trends over time**:
```cypher
MATCH (d:Disease {name: 'Malaria'})<-[:CAUSED_BY]-(o:Outbreak)
RETURN o.year AS year, SUM(o.cases) AS total_cases
ORDER BY year
```

More queries in `backend/app/query_examples.py` (16 total)

## 💬 AI Features

### RAG Chatbot Architecture
```
User Query
    ↓
┌─────────────────────────────┐
│ Semantic Retrieval          │
│ - Embed query               │
│ - Search vector DB          │
│ - Find top-K entities       │
└─────────────┬───────────────┘
              ↓
┌─────────────────────────────┐
│ Context Formatting          │
│ - Convert entities to text  │
│ - Add conversation history  │
└─────────────┬───────────────┘
              ↓
┌─────────────────────────────┐
│ LLM Generation              │
│ - HuggingFace self-hosted   │
│ - Returns answer + sources  │
└─────────────────────────────┘
```

**Supported AI Providers** (Strategy pattern):
- HuggingFace (default, self-hosted, no API key)
- OpenAI (optional, requires API key)
- Mock (testing)

### Semantic Search
- **Embeddings**: `sentence-transformers/all-MiniLM-L6-v2` (384 dimensions)
- **Vector DB**: Neo4j native vectors (or Qdrant/FAISS)
- **Reranking**: Cross-encoder for top-K results

## 🧪 Testing

### Backend
```bash
cd backend
pytest                    # Unit tests
pytest --cov=app          # With coverage
```

### Frontend
```bash
cd app
npm test                  # Jest + React Testing Library
npm run test:e2e          # Cypress (if configured)
```

### Integration
```bash
# Test full stack
curl http://localhost:8000/api/search?q=malaria
curl http://localhost:8000/api/entity/disease:malaria
```

## 📚 Documentation

- **QUICKSTART.md** - 2-minute setup guide with configuration examples
- **Instructions** - [.github/instructions/epihelix-instructions.instructions.md](.github/instructions/epihelix-instructions.instructions.md) - Complete technical reference for AI agents

## 🐳 Deployment

### Vercel + Railway (Recommended)

**Frontend on Vercel + Backend on Railway** - Best of both platforms:

[![Deploy Backend on Railway](https://railway.app/button.svg)](https://railway.app/new)
[![Deploy Frontend on Vercel](https://vercel.com/button)](https://vercel.com/new/clone)

#### Architecture
```
User → Vercel (Next.js) → Railway (FastAPI) → Neo4j Aura
                                ↓
                          Kaggle GPU (optional)
```

#### Setup Steps

1. **Deploy Backend to Railway**
   - Fork this repo to your GitHub account
   - Go to [Railway Dashboard](https://railway.app/dashboard)
   - Click **"New Project"** → **"Deploy from GitHub repo"**
   - Select `epihelix-project`
   - Railway auto-detects `backend/Dockerfile`
   
   **Environment Variables:**
   ```bash
   NEO4J_URI=neo4j+s://<your-aura-instance>.databases.neo4j.io
   NEO4J_USER=neo4j
   NEO4J_PASSWORD=<your-password>
   
   # AI Providers (choose one)
   RERANKER_PROVIDER=huggingface  # CPU-based, no GPU
   EMBEDDER_PROVIDER=huggingface
   LLM_PROVIDER=huggingface
   
   # Or: Kaggle GPU (faster)
   # KAGGLE_AI_ENDPOINT=https://xxxx.ngrok-free.app
   # RERANKER_PROVIDER=kaggle
   # EMBEDDER_PROVIDER=kaggle
   # LLM_PROVIDER=kaggle
   ```
   
   Backend URL: `https://<your-backend>.up.railway.app`

2. **Deploy Frontend to Vercel**
   - Go to [Vercel Dashboard](https://vercel.com/dashboard)
   - Import your forked `epihelix-project`
   - Vercel auto-detects `app/` as Next.js project
   
   **Environment Variable:**
   ```bash
   NEXT_PUBLIC_API_URL=https://<your-backend>.up.railway.app
   ```
   
   Frontend URL: `https://<your-project>.vercel.app`

3. **Setup Neo4j Aura** (Free Tier)
   - Go to [Neo4j Aura](https://console.neo4j.io/)
   - Create free instance (50k nodes, 175k relationships)
   - Copy connection URI and password
   - Add to Railway backend environment variables

4. **Load Data**
   ```bash
   # From local machine
   export NEO4J_URI=neo4j+s://<aura-uri>
   export NEO4J_PASSWORD=<password>
   cd kg-construction/etl
   python load_all_data.py
   ```

#### Why This Setup?
- ✅ **Vercel**: Optimized for Next.js (Edge Network, ISR, Image Optimization)
- ✅ **Railway**: Perfect for FastAPI (WebSocket support, long-running processes)
- ✅ **Auto-deployment** from GitHub on both platforms
- ✅ **Free SSL** certificates on both
- ✅ **Generous free tiers** (Vercel: unlimited bandwidth, Railway: $5 credit)

#### Cost Estimate
- **Vercel Pro**: $20/month (optional - free tier sufficient for demos)
- **Railway Hobby**: $5/month (backend only)
- **Neo4j Aura Free**: $0 (50k nodes limit)
- **Total**: ~$5/month (or $0 with free tiers)

---

### Docker Compose (Local Development)

#### All Services
```bash
# Start everything (Neo4j + Backend + Frontend)
docker-compose -f infrastructure/docker-compose.yml up

# Or production mode
docker-compose -f infrastructure/docker-compose.prod.yml up -d
```

#### Individual Services
```bash
# Neo4j only
cd infrastructure && docker-compose up neo4j

# Backend only (requires Neo4j running)
cd backend && docker build -t epihelix-api . && docker run -p 8000:8000 epihelix-api

# Frontend only
cd app && docker build -t epihelix-frontend . && docker run -p 3000:3000 epihelix-frontend
```

---

### Alternative: Railway Only (Both Services)

**Deploy both frontend and backend to Railway:**

1. Configure Railway to build both services separately
2. Railway builds `backend/` and `app/` from their respective Dockerfiles
3. Less optimal for Next.js (Vercel has better edge optimization)

**When to use:**
- Single platform preference
- Need backend-frontend in same private network
- Simpler billing (one platform)

---

### Other Cloud Options

- **AWS**: ECS Fargate (backend) + Amplify (frontend) + Neptune (graph DB)
- **GCP**: Cloud Run (both) + Compute Engine (Neo4j)
- **Azure**: App Service (both) + Cosmos DB (graph API)

See `QUICKSTART.md` for complete deployment guide.

## 🔧 Configuration

### Backend (.env)
```bash
# Neo4j
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=epihelix123

# AI (self-hosted HuggingFace, no API key needed)
HUGGING_FACE_MODEL=sentence-transformers/all-MiniLM-L6-v2
HUGGING_FACE_LLM=google/flan-t5-base

# Optional: OpenAI (if not using HuggingFace)
# OPENAI_API_KEY=sk-...
```

### Frontend (environment variables)
```bash
# Next.js automatically uses http://localhost:8000 in development
# For production, set:
NEXT_PUBLIC_API_URL=https://api.epihelix.com
```

## 📈 Data Sources

1. **Disease Cases** (disease_cases.csv) - 9 diseases, 1980-2021
2. **Vaccination Coverage** (vaccination_coverage.csv) - 15 vaccines, global coverage
3. **COVID-19 Excess Deaths** (excess_deaths_cumulative_per_million_covid.csv)
4. **Cholera Deaths** (number-of-deaths-from-cholera.csv)

**External Sources**:
- Wikidata: Disease metadata, country demographics, organization data
- DBpedia: Historical pandemic events, Wikipedia links

## 🎨 UI Screenshots

**Home Page**: Gradient hero, typewriter search, animated particle background  
**Search**: Google-style results with Knowledge Panel  
**Entity Details**: Card-based layout with properties, relations, visualizations  
**Query Console**: Monaco editor with Cypher/SPARQL syntax highlighting  
**Chat**: Full-page ChatGPT-style interface with suggested prompts

## 🤝 Contributing

1. Fork the repo
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📝 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- **Data**: WHO, CDC, OWID, Kaggle pandemic datasets
- **Knowledge Graphs**: Wikidata, DBpedia
- **UI**: shadcn/ui, Tailwind CSS, Framer Motion
- **Backend**: FastAPI, Neo4j, HuggingFace
