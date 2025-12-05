# EpiHelix - 2-Minute Quickstart

Get the full stack running locally in 2 minutes, or deploy to Railway in 5 minutes.

## Prerequisites

**Local Development:**
- Docker (for Neo4j)
- Python 3.8+
- Node.js 18+

**Production Deployment:**
- GitHub account
- Railway account (free tier)
- Neo4j Aura account (free tier)

---

## 🚀 Option 1: Local Development (Fastest)

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

---

## ☁️ Option 2: Railway Deployment (Production)

### Step 1: Setup Neo4j Aura (2 minutes)

1. Go to [Neo4j Aura](https://console.neo4j.io/)
2. Click **"Create Free Database"**
3. Choose **AuraDB Free** (50k nodes, 175k relationships)
4. **Save credentials** (download text file):
   ```
   Connection URI: neo4j+s://xxxxx.databases.neo4j.io
   Username: neo4j
   Password: <random-password>
   ```

### Step 2: Load Data to Aura (3 minutes)

```bash
# On your local machine
export NEO4J_URI="neo4j+s://xxxxx.databases.neo4j.io"
export NEO4J_PASSWORD="<your-password>"

cd kg-construction/etl
python -m venv venv && source venv/bin/activate
pip install -r ../requirements.txt
python load_all_data.py
```

**Wait for:**
```
✅ Loaded 195 countries
✅ Loaded 22 diseases
✅ Loaded 50,000+ outbreak records
✅ Loaded 30,000+ vaccination records
```

### Step 3: Deploy Backend to Railway (3 minutes)

1. **Fork Repository** (if not done already)
   - Go to https://github.com/YOUR_USERNAME/epihelix-project
   - Click **Fork** (top right)

2. **Deploy Backend to Railway**
   - Go to [Railway Dashboard](https://railway.app/dashboard)
   - Click **"New Project"** → **"Deploy from GitHub repo"**
   - Choose your forked `epihelix-project`
   - Railway detects `backend/` directory with `Dockerfile`

3. **Configure Backend Environment Variables**
   
   In Railway → Service → Variables:
   ```bash
   NEO4J_URI=neo4j+s://xxxxx.databases.neo4j.io
   NEO4J_USER=neo4j
   NEO4J_PASSWORD=<your-aura-password>
   
   # AI Providers (choose one)
   RERANKER_PROVIDER=huggingface
   EMBEDDER_PROVIDER=huggingface
   LLM_PROVIDER=huggingface
   ```

4. **Get Backend URL**
   - After deployment: `https://<your-backend>.up.railway.app`
   - Test: `curl https://<your-backend>.up.railway.app/health`

### Step 4: Deploy Frontend to Vercel (2 minutes)

1. **Connect to Vercel** (already configured)
   - Go to [Vercel Dashboard](https://vercel.com/dashboard)
   - Import your forked `epihelix-project`
   - Vercel auto-detects `app/` directory as Next.js project

2. **Configure Environment Variable**
   
   In Vercel → Project → Settings → Environment Variables:
   ```bash
   NEXT_PUBLIC_API_URL=https://<your-backend>.up.railway.app
   ```
   
   Replace `<your-backend>` with your Railway backend URL.

3. **Deploy**
   - Vercel auto-deploys from GitHub pushes
   - Production URL: `https://<your-project>.vercel.app`

4. **Test Full Stack**
   ```bash
   # Visit frontend
   open https://<your-project>.vercel.app
   
   # Or test API connection
   curl https://<your-project>.vercel.app/api/search?q=malaria
   ```

**Done!** 🚀 Your app is live with:
- ✅ **Frontend**: Vercel (optimized Next.js hosting, global CDN)
- ✅ **Backend**: Railway (FastAPI with auto-scaling)
- ✅ Auto-deployment on `git push`
- ✅ Free SSL certificates
- ✅ Custom domains available

---

## 🎯 Optional: Kaggle GPU Services (Free AI Acceleration)

For faster semantic search and chatbot responses, use Kaggle's free P100 GPU:

### 1. Setup ngrok
1. Go to [ngrok Dashboard](https://dashboard.ngrok.com/get-started/your-authtoken)
2. Copy authtoken
3. Add to Kaggle:
   - Go to [Kaggle Settings](https://www.kaggle.com/settings) → **Secrets**
   - Add secret: `NGROK_TOKEN` = `<your-authtoken>`

### 2. Run Kaggle Notebook
1. Go to [Kaggle Notebooks](https://www.kaggle.com/code)
2. Upload `kaggle-notebooks/epihelix-ai-services.ipynb`
3. Enable **GPU P100** + **Internet ON**
4. Click **"Run All"**
5. Copy ngrok URL from output:
   ```
   ✅ PUBLIC URL: https://xxxx.ngrok-free.app
   ```

### 3. Update Backend Config

**Local:**
```bash
# backend/.env
KAGGLE_AI_ENDPOINT=https://xxxx.ngrok-free.app
RERANKER_PROVIDER=kaggle
EMBEDDER_PROVIDER=kaggle
LLM_PROVIDER=kaggle
```

**Railway (Backend):**
- Add `KAGGLE_AI_ENDPOINT` to Railway environment variables
- Update `*_PROVIDER` variables to `kaggle`
- Redeploy (auto-triggers on variable change)

**Vercel (Frontend):**
- No changes needed (frontend doesn't call Kaggle directly)

**Performance Boost:**
- Semantic search: 50ms (vs 2s CPU)
- Reranking: 200ms (vs 5s CPU)
- LLM generation: 2s (vs 10s CPU)

See `kaggle-notebooks/README.md` for detailed setup.

---

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

# Optional: Use Kaggle GPU
# KAGGLE_AI_ENDPOINT=https://xxxx.ngrok-free.app
# RERANKER_PROVIDER=kaggle
# EMBEDDER_PROVIDER=kaggle
# LLM_PROVIDER=kaggle
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
  -d '{
    "query": "MATCH (d:Disease) RETURN d.name LIMIT 10",
    "type": "cypher"
  }'

# Chat (RAG)
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What are the top 5 countries by COVID-19 excess deaths?",
    "session_id": "test123"
  }'
```

### Frontend Pages
- **Home**: http://localhost:3000
- **Search**: http://localhost:3000/search?q=malaria
- **Entity**: http://localhost:3000/entity/disease:malaria
- **Query Console**: http://localhost:3000/query
- **Chat**: http://localhost:3000/chat

## 🐛 Troubleshooting

### Neo4j Connection Failed
```bash
# Check if Neo4j is running
docker ps | grep neo4j

# Check logs
cd infrastructure && docker-compose logs neo4j

# Restart
docker-compose restart neo4j
```

### Backend Port Already in Use
```bash
# Find process using port 8000
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill process
kill -9 <PID>
```

### Frontend Port Already in Use
```bash
# Use different port
PORT=3001 npm run dev
```

### Data Load Failed
```bash
# Check Neo4j connection
cd kg-construction/etl
python neo4j_connection.py

# Clear database and reload
python -c "from neo4j_connection import get_driver; driver = get_driver(); driver.execute_query('MATCH (n) DETACH DELETE n')"
python load_all_data.py
```

## 📚 Next Steps

1. ✅ **Get app running** (this guide)
2. ⚠️ **Explore features**:
   - Try semantic search (toggle in search bar)
   - Ask chatbot complex questions
   - Run Cypher queries in console
   - Browse disease/country entities
3. ⚠️ **Customize**:
   - Add your own datasets (see `kg-construction/`)
   - Modify UI theme (see `app/src/app/globals.css`)
   - Create custom Cypher queries (see `backend/app/query_examples.py`)
4. ⚠️ **Deploy**:
   - Railway + Vercel (see above)
   - Or Docker Compose on VPS

---

## 🔄 Advanced: Continuous Deployment

**Backend (Railway):**
- Auto-deploys on push to `main` branch
- Build logs: Railway Dashboard → Deployments
- Typical build time: ~2-3 minutes

**Frontend (Vercel):**
- Auto-deploys on push to `main` branch
- Preview deployments for PRs
- Build logs: Vercel Dashboard → Deployments

```bash
git add .
git commit -m "Update feature"
git push origin main
# Both services auto-deploy
```

### Custom Domains

**Backend (Railway):**
1. Railway Dashboard → Service → Settings → Domains
2. Click **"Add Domain"**
3. Enter: `api.yourdomain.com`
4. Add DNS CNAME: `api.yourdomain.com → <railway-domain>`

**Frontend (Vercel):**
1. Vercel Dashboard → Project → Settings → Domains
2. Add domain: `yourdomain.com`
3. Follow Vercel's DNS instructions

### Monitoring & Logs

**Railway Dashboard:**
- **Metrics**: CPU, Memory, Network usage
- **Logs**: Real-time application logs
- **Deployments**: Build history and rollback

**Vercel Dashboard:**
- **Analytics**: Visitor stats, page views
- **Logs**: Function logs and errors
- **Performance**: Core Web Vitals

### Health Checks

Backend exposes `/health` endpoint:
```bash
curl https://<backend>.up.railway.app/health
```

Response:
```json
{
  "status": "healthy",
  "neo4j_connected": true,
  "models_loaded": {
    "embedder": true,
    "reranker": true,
    "llm": true
  }
}
```

### Common Deployment Issues

**Backend Build Failed:**
- Check Railway build logs
- Verify `requirements.txt` is up-to-date
- Ensure Python 3.11 (set in `backend/Dockerfile`)

**Backend Crashes on Start:**
- Verify Neo4j Aura URI is correct (`neo4j+s://...`)
- Check all required environment variables are set
- Test connection: Railway logs will show Neo4j connection errors

**Frontend Can't Reach Backend:**
- Verify `NEXT_PUBLIC_API_URL` in Vercel settings
- Should be: `https://<your-backend>.up.railway.app`
- Redeploy frontend after changing env vars

**Slow Performance:**
- Default: HuggingFace CPU models (slow)
- Solution: Switch to Kaggle GPU (see Optional section above)
- Update Railway env vars: `KAGGLE_AI_ENDPOINT`, `*_PROVIDER=kaggle`

### Cost Estimates

**Monthly Costs:**
- **Vercel Free**: $0 (unlimited bandwidth, sufficient for demos)
- **Railway Hobby**: $5/month (backend only, 500 execution hours)
- **Neo4j Aura Free**: $0 (50k nodes, 175k relationships)
- **Kaggle GPU**: $0 (30 hours/week free)

**Total**: ~$5/month (or $0 with free tiers during development)

**Production (scaled):**
- **Vercel Pro**: $20/month (team features, priority support)
- **Railway Pro**: $20/month (unlimited execution, 99.99% SLA)
- **Neo4j Aura Pro**: $65/month (200k nodes, 2M relationships)
- **Total**: ~$105/month

---

## 📖 Documentation

- **README.md** - Full project overview and architecture
- **kaggle-notebooks/README.md** - Kaggle GPU setup guide
- **.github/instructions/** - Technical reference for AI agents
- **kg-construction/SPARQL_QUERIES.md** - Example SPARQL queries

## 🤝 Need Help?

- Check `README.md` for architecture details
- See `backend/README.md` for API documentation (if exists)
- Open an issue on GitHub
