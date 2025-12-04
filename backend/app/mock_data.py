"""
Mock data loader using real KG schema from kg_data.py
Based on actual Neo4j schema with 22 diseases, countries, organizations
"""
from .kg_data import (
    DISEASES, COUNTRIES, ORGANIZATIONS, VACCINES,
    get_all_diseases, get_disease_by_id,
    get_all_countries, get_country_by_code,
    get_all_organizations, get_all_vaccines
)

DATA = {
    "entities": {},
    "snippets": [],
}


def load_mock():
    """Load mock data from kg_data module"""
    entities = {}
    snippets = []
    
    # Load diseases
    for disease_id, disease in DISEASES.items():
        entities[disease_id] = {
            "id": disease_id,
            "label": disease["name"],
            "type": "Disease",
            "summary": disease.get("description", f"{disease['name']} disease"),
            "props": disease
        }
        snippets.append({
            "id": f"snippet_{disease_id}",
            "entity_id": disease_id,
            "text": disease.get("description", disease["name"])
        })
    
    # Load countries
    for code, country in COUNTRIES.items():
        entities[code] = {
            "id": code,
            "label": country["name"],
            "type": "Country",
            "summary": f"{country['name']} ({code})",
            "props": country
        }
        snippets.append({
            "id": f"snippet_{code}",
            "entity_id": code,
            "text": f"{country['name']} country"
        })
    
    # Load organizations
    for org_id, org in ORGANIZATIONS.items():
        entities[org_id] = {
            "id": org_id,
            "label": org["name"],
            "type": "Organization",
            "summary": f"{org['name']} - {org.get('role', 'Health organization')}",
            "props": org
        }
        snippets.append({
            "id": f"snippet_{org_id}",
            "entity_id": org_id,
            "text": f"{org['name']} {org.get('role', '')}"
        })
    
    DATA["entities"] = entities
    DATA["snippets"] = snippets


def get_entities():
    """Get all entities"""
    if not DATA["entities"]:
        load_mock()
    return DATA.get("entities", {})


def search_snippets(q: str):
    """Search snippets by text"""
    if not DATA["snippets"]:
        load_mock()
    ql = q.lower()
    results = []
    for s in DATA.get("snippets", []):
        text = s.get("text", "").lower()
        if ql in text:
            # Calculate simple score based on position and length
            score = 1.0
            if text.startswith(ql):
                score = 1.0
            elif ql in text[:len(text)//2]:
                score = 0.8
            else:
                score = 0.6
            results.append({"score": score, **s})
    return sorted(results, key=lambda x: x["score"], reverse=True)
