from pydantic import BaseModel
from typing import Any, Dict, List, Optional
from datetime import datetime


# ============================================================================
# Entity Models (matching actual Neo4j schema)
# ============================================================================

class Country(BaseModel):
    """Country node from Neo4j"""
    code: str  # ISO 3166-1 alpha-3 (e.g., "USA")
    name: str
    # Enriched properties (from Wikidata)
    wikidataId: Optional[str] = None
    population: Optional[int] = None
    capital: Optional[str] = None
    continent: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    iso2: Optional[str] = None
    gdp: Optional[float] = None
    lifeExpectancy: Optional[float] = None
    areaKm2: Optional[float] = None
    officialLanguage: Optional[str] = None
    enriched: Optional[bool] = False
    enrichedAt: Optional[datetime] = None


class Disease(BaseModel):
    """Disease node from Neo4j"""
    id: str  # e.g., "covid19", "malaria"
    name: str
    dataSource: Optional[str] = "HPD Dataset"
    eradicated: Optional[bool] = False
    # Enriched properties (from Wikidata)
    wikidataId: Optional[str] = None
    fullName: Optional[str] = None
    icd10: Optional[str] = None
    mesh: Optional[str] = None
    symptoms: Optional[List[str]] = None
    transmissionMethods: Optional[List[str]] = None
    riskFactors: Optional[List[str]] = None
    treatments: Optional[List[str]] = None
    incubationPeriod: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    pathogen: Optional[str] = None
    enriched: Optional[bool] = False
    enrichedAt: Optional[datetime] = None
    externalSource: Optional[str] = None
    # DBpedia enrichment
    dbpediaUri: Optional[str] = None
    wikipediaAbstract: Optional[str] = None
    wikipediaUrl: Optional[str] = None
    thumbnailUrl: Optional[str] = None
    causativeAgent: Optional[str] = None
    medicalSpecialty: Optional[str] = None
    prevention: Optional[str] = None
    dbpediaEnriched: Optional[bool] = False


class Outbreak(BaseModel):
    """Outbreak node from Neo4j"""
    id: str  # e.g., "covid_USA_20200302"
    year: int
    # From disease cases dataset
    cases: Optional[float] = None
    # From cholera dataset
    deaths: Optional[int] = None
    # From COVID-19 dataset
    date: Optional[str] = None  # YYYY-MM-DD
    excessDeaths: Optional[float] = None
    confirmedDeaths: Optional[float] = None
    confidenceIntervalTop: Optional[float] = None
    confidenceIntervalBottom: Optional[float] = None


class VaccinationRecord(BaseModel):
    """Vaccination record node from Neo4j"""
    id: str
    year: int
    vaccineName: str
    coverage: float  # percentage
    totalVaccinated: Optional[int] = None


class Organization(BaseModel):
    """Health organization node (from enrichment)"""
    id: str  # e.g., "who", "cdc"
    name: str
    acronym: Optional[str] = None
    wikidataId: Optional[str] = None
    role: Optional[str] = None
    founded: Optional[str] = None
    headquarters: Optional[str] = None
    website: Optional[str] = None


class Vaccine(BaseModel):
    """Vaccine node (from enrichment)"""
    wikidataId: str
    name: str
    manufacturer: Optional[str] = None
    approvalDate: Optional[str] = None
    description: Optional[str] = None


class PandemicEvent(BaseModel):
    """Historical pandemic event (from DBpedia)"""
    dbpediaUri: str
    name: str
    abstract: Optional[str] = None
    startDate: Optional[str] = None
    deathToll: Optional[str] = None
    location: Optional[str] = None
    source: Optional[str] = "DBpedia"


# ============================================================================
# API Request/Response Models
# ============================================================================

class EntitySummary(BaseModel):
    """Lightweight entity for search results"""
    id: str
    label: str
    type: str  # "Country" | "Disease" | "Outbreak" | etc.
    score: Optional[float] = None
    snippet: Optional[str] = None


class EntityDetail(BaseModel):
    """Full entity details"""
    id: str
    label: str
    type: str
    summary: Optional[str] = None
    properties: Dict[str, Any]
    relations: Optional[List[Dict[str, Any]]] = None


class SearchResponse(BaseModel):
    results: List[EntitySummary]
    total: Optional[int] = None


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    include_history: Optional[bool] = True


class ChatResponse(BaseModel):
    reply: str
    sources: Optional[List[Dict[str, Any]]] = None
    session_id: Optional[str] = None


class QueryRequest(BaseModel):
    query: str
    type: str = "cypher"  # "cypher" or "sparql"


class QueryResponse(BaseModel):
    columns: List[str]
    rows: List[Dict[str, Any]]
    count: int


class SummaryRequest(BaseModel):
    entity_id: str
    query: Optional[str] = None
    include_relations: Optional[bool] = True


class SummaryResponse(BaseModel):
    summary: str
    entity_id: str
    metadata: Optional[Dict[str, Any]] = None
