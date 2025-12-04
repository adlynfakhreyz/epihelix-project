"""
Real Knowledge Graph Data
Based on actual Neo4j ETL schema from kg-construction/
"""

# ============================================================================
# ACTUAL DISEASES (22 total from HPD dataset)
# ============================================================================

DISEASES = {
    # From Disease Cases Dataset (9 diseases)
    "yaws": {
        "id": "yaws",
        "name": "Yaws",
        "dataSource": "HPD Dataset",
        "eradicated": False,
        "wikidataId": "Q1415196",
        "description": "Tropical infection affecting skin, bone and cartilage",
        "category": "Infectious Disease"
    },
    "polio": {
        "id": "polio",
        "name": "Poliomyelitis",
        "dataSource": "HPD Dataset",
        "eradicated": False,
        "wikidataId": "Q12195",
        "description": "Viral disease affecting the nervous system",
        "category": "Viral Infection"
    },
    "guinea_worm": {
        "id": "guinea_worm",
        "name": "Guinea Worm Disease",
        "dataSource": "HPD Dataset",
        "eradicated": False,
        "wikidataId": "Q913399",
        "description": "Parasitic infection caused by drinking contaminated water",
        "category": "Parasitic Disease"
    },
    "rabies": {
        "id": "rabies",
        "name": "Rabies",
        "dataSource": "HPD Dataset",
        "eradicated": False,
        "wikidataId": "Q39552",
        "description": "Viral disease spread by animal bites",
        "category": "Viral Infection"
    },
    "malaria": {
        "id": "malaria",
        "name": "Malaria",
        "dataSource": "HPD Dataset",
        "eradicated": False,
        "wikidataId": "Q12156",
        "description": "Mosquito-borne infectious disease",
        "category": "Parasitic Disease",
        "pathogen": "Plasmodium parasites"
    },
    "hiv_aids": {
        "id": "hiv_aids",
        "name": "HIV/AIDS",
        "dataSource": "HPD Dataset",
        "eradicated": False,
        "wikidataId": "Q12199",
        "description": "Human immunodeficiency virus infection",
        "category": "Viral Infection"
    },
    "tuberculosis": {
        "id": "tuberculosis",
        "name": "Tuberculosis",
        "dataSource": "HPD Dataset",
        "eradicated": False,
        "wikidataId": "Q12204",
        "description": "Bacterial infection primarily affecting lungs",
        "category": "Bacterial Infection",
        "pathogen": "Mycobacterium tuberculosis"
    },
    "smallpox": {
        "id": "smallpox",
        "name": "Smallpox",
        "dataSource": "HPD Dataset",
        "eradicated": True,
        "wikidataId": "Q12214",
        "description": "Eradicated viral disease (WHO declared eradication in 1980)",
        "category": "Viral Infection"
    },
    "cholera": {
        "id": "cholera",
        "name": "Cholera",
        "dataSource": "HPD Dataset",
        "eradicated": False,
        "wikidataId": "Q12090",
        "description": "Bacterial disease causing severe diarrhea",
        "category": "Bacterial Infection",
        "pathogen": "Vibrio cholerae"
    },
    
    # From Vaccination Dataset (15 vaccine-preventable diseases)
    "diphtheria": {
        "id": "diphtheria",
        "name": "Diphtheria",
        "dataSource": "Vaccination Dataset",
        "eradicated": False,
        "wikidataId": "Q134041",
        "description": "Bacterial infection affecting throat and nose"
    },
    "pertussis": {
        "id": "pertussis",
        "name": "Pertussis",
        "dataSource": "Vaccination Dataset",
        "eradicated": False,
        "wikidataId": "Q37933",
        "description": "Whooping cough"
    },
    "tetanus": {
        "id": "tetanus",
        "name": "Tetanus",
        "dataSource": "Vaccination Dataset",
        "eradicated": False,
        "wikidataId": "Q81133"
    },
    "measles": {
        "id": "measles",
        "name": "Measles",
        "dataSource": "Vaccination Dataset",
        "eradicated": False,
        "wikidataId": "Q8274"
    },
    "hepatitis_b": {
        "id": "hepatitis_b",
        "name": "Hepatitis B",
        "dataSource": "Vaccination Dataset",
        "eradicated": False,
        "wikidataId": "Q6853"
    },
    "haemophilus_influenzae": {
        "id": "haemophilus_influenzae",
        "name": "Haemophilus influenzae",
        "dataSource": "Vaccination Dataset",
        "eradicated": False,
        "wikidataId": "Q165663"
    },
    "rotavirus": {
        "id": "rotavirus",
        "name": "Rotavirus",
        "dataSource": "Vaccination Dataset",
        "eradicated": False,
        "wikidataId": "Q808"
    },
    "pneumonia": {
        "id": "pneumonia",
        "name": "Pneumonia",
        "dataSource": "Vaccination Dataset",
        "eradicated": False,
        "wikidataId": "Q12192"
    },
    "rubella": {
        "id": "rubella",
        "name": "Rubella",
        "dataSource": "Vaccination Dataset",
        "eradicated": False,
        "wikidataId": "Q48143"
    },
    "mumps": {
        "id": "mumps",
        "name": "Mumps",
        "dataSource": "Vaccination Dataset",
        "eradicated": False,
        "wikidataId": "Q36956"
    },
    "yellow_fever": {
        "id": "yellow_fever",
        "name": "Yellow Fever",
        "dataSource": "Vaccination Dataset",
        "eradicated": False,
        "wikidataId": "Q154874"
    },
    "japanese_encephalitis": {
        "id": "japanese_encephalitis",
        "name": "Japanese Encephalitis",
        "dataSource": "Vaccination Dataset",
        "eradicated": False,
        "wikidataId": "Q190711"
    },
    "typhoid": {
        "id": "typhoid",
        "name": "Typhoid",
        "dataSource": "Vaccination Dataset",
        "eradicated": False,
        "wikidataId": "Q161549"
    },
    
    # Special: COVID-19 (dedicated dataset)
    "covid19": {
        "id": "covid19",
        "name": "COVID-19",
        "fullName": "Coronavirus Disease 2019",
        "dataSource": "COVID-19 Dataset",
        "eradicated": False,
        "wikidataId": "Q84263196",
        "description": "Respiratory illness caused by SARS-CoV-2",
        "category": "Viral Infection",
        "pathogen": "SARS-CoV-2",
        "firstIdentified": "2019-12-01",
        "pandemic": True
    }
}

# ============================================================================
# SAMPLE COUNTRIES
# ============================================================================

COUNTRIES = {
    "USA": {"code": "USA", "name": "United States", "iso2": "US"},
    "GBR": {"code": "GBR", "name": "United Kingdom", "iso2": "GB"},
    "CHN": {"code": "CHN", "name": "China", "iso2": "CN"},
    "IND": {"code": "IND", "name": "India", "iso2": "IN"},
    "BRA": {"code": "BRA", "name": "Brazil", "iso2": "BR"},
    "RUS": {"code": "RUS", "name": "Russia", "iso2": "RU"},
    "DEU": {"code": "DEU", "name": "Germany", "iso2": "DE"},
    "JPN": {"code": "JPN", "name": "Japan", "iso2": "JP"},
    "FRA": {"code": "FRA", "name": "France", "iso2": "FR"},
    "IDN": {"code": "IDN", "name": "Indonesia", "iso2": "ID"},
}

# ============================================================================
# HEALTH ORGANIZATIONS
# ============================================================================

ORGANIZATIONS = {
    "who": {
        "id": "who",
        "name": "World Health Organization",
        "acronym": "WHO",
        "wikidataId": "Q7817",
        "role": "Global health coordination",
        "headquarters": "Geneva, Switzerland",
        "website": "https://www.who.int"
    },
    "cdc": {
        "id": "cdc",
        "name": "Centers for Disease Control and Prevention",
        "acronym": "CDC",
        "wikidataId": "Q583725",
        "role": "US public health agency",
        "headquarters": "Atlanta, Georgia, USA",
        "website": "https://www.cdc.gov"
    },
    "ecdc": {
        "id": "ecdc",
        "name": "European Centre for Disease Prevention and Control",
        "acronym": "ECDC",
        "wikidataId": "Q902384",
        "role": "EU public health agency",
        "headquarters": "Stockholm, Sweden",
        "website": "https://www.ecdc.europa.eu"
    }
}

# ============================================================================
# COVID-19 VACCINES
# ============================================================================

VACCINES = {
    "pfizer": {
        "wikidataId": "Q98158256",
        "name": "Pfizer-BioNTech COVID-19 vaccine",
        "manufacturer": "Pfizer, BioNTech",
        "approvalDate": "2020-12-11"
    },
    "moderna": {
        "wikidataId": "Q98109286",
        "name": "Moderna COVID-19 vaccine",
        "manufacturer": "Moderna",
        "approvalDate": "2020-12-18"
    },
    "astrazeneca": {
        "wikidataId": "Q98244340",
        "name": "Oxford-AstraZeneca COVID-19 vaccine",
        "manufacturer": "AstraZeneca, Oxford University",
        "approvalDate": "2020-12-30"
    }
}


def get_all_diseases():
    """Get all 22 diseases"""
    return list(DISEASES.values())


def get_disease_by_id(disease_id: str):
    """Get disease by ID"""
    return DISEASES.get(disease_id)


def get_all_countries():
    """Get all sample countries"""
    return list(COUNTRIES.values())


def get_country_by_code(code: str):
    """Get country by ISO code"""
    return COUNTRIES.get(code)


def get_all_organizations():
    """Get all health organizations"""
    return list(ORGANIZATIONS.values())


def get_all_vaccines():
    """Get all vaccines"""
    return list(VACCINES.values())
