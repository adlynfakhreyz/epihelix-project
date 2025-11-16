# EpiHelix - Pandemic Insights Explorer

A comprehensive knowledge graph application for exploring pandemic data, integrating historical pandemic datasets with external knowledge bases (Wikidata, DBpedia).

## 🏗️ Project Structure

```
epihelix-project/
├── app/                      # Next.js Frontend
│   ├── src/                  # React components, pages, hooks
│   ├── public/               # Static assets
│   └── package.json
│
├── services/                 # Backend Services
│   ├── api/                  # FastAPI REST API (main backend)
│   ├── kaggle-connector/     # Kaggle data fetching service
│   └── wikidata-connector/   # Wikidata SPARQL queries
│
├── kg-construction/          # Knowledge Graph Pipeline
│   ├── etl/                  # ETL scripts (CSV → RDF/Neo4j)
│   ├── notebooks/            # Jupyter notebooks for exploration
│   ├── data/                 # Data files
│   │   ├── raw/              # Raw CSV files
│   │   ├── processed/        # Processed RDF triples
│   │   └── external/         # External data (Wikidata, DBpedia)
│   ├── ontology/             # RDF ontology definitions
│   └── scripts/              # Utility scripts
│
└── infrastructure/           # Docker & Deployment
    └── docker-compose.yml    # Orchestrate all services
```

## 🚀 Quick Start

### Frontend (App)
```bash
cd app
npm install
npm run dev
# Visit http://localhost:3000
```

### Backend API
```bash
cd services/api
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
# API at http://localhost:8000
```

### Knowledge Graph Construction
```bash
cd kg-construction
jupyter notebook  # Explore notebooks
# or run ETL scripts
python etl/csv_to_rdf.py
```

## 🛠️ Tech Stack

**Frontend:**
- Next.js 16.0.3 + React 19.2.0
- Tailwind CSS + shadcn/ui
- Framer Motion
- React Query

**Backend:**
- FastAPI (Python)
- Neo4j / Apache Jena Fuseki (RDF)
- Python: pandas, rdflib, SPARQLWrapper

**Knowledge Graph:**
- RDF/OWL for ontology
- Neo4j for graph database (or Fuseki for RDF triple store)
- Vector embeddings for semantic search

## 📚 Documentation

See individual README files in each directory:
- [Frontend Documentation](./app/README.md)
- [API Documentation](./services/api/README.md)
- [KG Construction Guide](./kg-construction/README.md)

## 🔗 Related Resources

- Course instructions: `.github/instructions/epihelix-instructions.instructions.md`
- Setup guide: `app/SETUP.md`
- API specification: TBD
- Ontology design: `kg-construction/ontology/README.md`

## 📝 License

Educational project for coursework.
