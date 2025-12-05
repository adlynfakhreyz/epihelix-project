# Deployment Guide

This guide covers deploying both the frontend (Next.js) and backend (FastAPI) applications.

## Prerequisites

- **Frontend**: Node.js 18.17+ and npm 9.0+
- **Backend**: Python 3.10+ and pip
- Neo4j Aura database instance
- Groq API key
- (Optional) Kaggle API endpoints for custom embeddings/LLM

## Backend Deployment

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the `backend/` directory:

```bash
cp .env.example .env
```

Edit `.env` with your actual credentials:
- Neo4j connection details
- Groq API key
- Kaggle endpoints (if using)
- CORS origins (add your frontend URL)

### 3. Run Backend

**Development:**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Production:**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 4. Deploy to Cloud

#### Railway (Recommended)
1. Push your code to GitHub
2. Connect Railway to your repository
3. Add environment variables in Railway dashboard
4. Railway will automatically detect the Dockerfile and deploy

#### Render
1. Create a new Web Service
2. Connect your repository
3. Use these settings:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Add environment variables

#### Docker
```bash
cd backend
docker build -t epihelix-backend .
docker run -p 8000:8000 --env-file .env epihelix-backend
```

## Frontend Deployment

### 1. Install Dependencies

```bash
cd app
npm install
```

### 2. Configure Environment Variables

Create a `.env.local` file in the `app/` directory:

```bash
cp .env.example .env.local
```

Update `NEXT_PUBLIC_API_URL` to your backend URL.

### 3. Build Frontend

```bash
npm run build
```

### 4. Run Frontend

**Development:**
```bash
npm run dev
```

**Production:**
```bash
npm start
```

### 5. Deploy to Cloud

#### Vercel (Recommended for Next.js)
1. Install Vercel CLI: `npm i -g vercel`
2. Run: `vercel` in the `app/` directory
3. Add environment variable in Vercel dashboard:
   - `NEXT_PUBLIC_API_URL`: Your backend URL

#### Netlify
1. Build command: `npm run build`
2. Publish directory: `.next`
3. Add environment variables in Netlify dashboard

#### Railway
1. Push your code to GitHub
2. Create a new Railway project
3. Add environment variables
4. Deploy

## Environment Variables Checklist

### Backend (.env)
- [ ] NEO4J_URI
- [ ] NEO4J_USERNAME
- [ ] NEO4J_PASSWORD
- [ ] GROQ_API_KEY
- [ ] CORS_ORIGINS (include your frontend URL)
- [ ] KAGGLE_EMBEDDER_URL (optional)
- [ ] KAGGLE_RERANKER_URL (optional)
- [ ] KAGGLE_LLM_URL (optional)

### Frontend (.env.local)
- [ ] NEXT_PUBLIC_API_URL (your backend URL)

## Post-Deployment Checklist

1. **Test API Health Check**: `https://your-backend-url.com/health`
2. **Test CORS**: Ensure frontend can make requests to backend
3. **Verify Database Connection**: Check logs for Neo4j connection
4. **Test Core Features**:
   - Search functionality
   - Entity retrieval
   - Chat/Query features
   - Heatmap visualization

## Troubleshooting

### CORS Errors
- Ensure your frontend URL is in `CORS_ORIGINS` in backend `.env`
- Include both `http://` and `https://` variants if needed

### Database Connection Issues
- Verify Neo4j credentials
- Check if Neo4j instance is running
- Ensure IP whitelist includes your deployment server

### Build Failures
- Check Node.js version (18.17+)
- Clear npm cache: `npm cache clean --force`
- Delete `node_modules` and reinstall

### API Not Responding
- Check backend logs
- Verify environment variables are set
- Ensure port is not blocked by firewall

## Monitoring

- Backend logs: Check your hosting platform's log viewer
- Frontend logs: Check Vercel/Netlify deployment logs
- Database: Monitor Neo4j Aura console

## Scaling

- **Backend**: Increase uvicorn workers or enable auto-scaling on your platform
- **Frontend**: Vercel/Netlify handle this automatically
- **Database**: Upgrade Neo4j Aura plan if needed
