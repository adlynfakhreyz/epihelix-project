"""Generate embeddings for all entities in Neo4j and create vector index.

Run this in Kaggle with GPU to speed up embedding generation.

Requirements:
- sentence-transformers
- neo4j
- torch (for GPU acceleration)

Usage:
    python generate_embeddings.py

Environment variables needed:
- NEO4J_URI
- NEO4J_USER  
- NEO4J_PASSWORD
"""
import os
import torch
from neo4j import GraphDatabase
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
import logging
from kaggle_secrets import UserSecretsClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmbeddingGenerator:
    """Generate and store embeddings for Neo4j entities."""
    
    def __init__(
        self,
        neo4j_uri: str,
        neo4j_user: str,
        neo4j_password: str,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        batch_size: int = 32
    ):
        """Initialize generator.
        
        Args:
            neo4j_uri: Neo4j connection URI
            neo4j_user: Neo4j username
            neo4j_password: Neo4j password
            model_name: HuggingFace model for embeddings
            batch_size: Batch size for embedding generation
        """
        # Detect device (GPU if available)
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        logger.info(f"Using device: {self.device}")
        if self.device == 'cuda':
            print(f"GPU: {torch.cuda.get_device_name(0)}")
            logger.info(f"GPU: {torch.cuda.get_device_name(0)}")
            logger.info(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
        
        # Initialize model and move to GPU (double ensure)
        self.driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
        self.model = SentenceTransformer(model_name, device=self.device)
        self.model.to(self.device)  # Explicitly move model to device (belt + suspenders)
        self.batch_size = batch_size
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
        
        logger.info(f"Initialized with model: {model_name}")
        logger.info(f"Embedding dimension: {self.embedding_dim}")
        logger.info(f"Batch size: {batch_size}")
        logger.info(f"Model device: {next(self.model.parameters()).device}")  # Verify actual device
    
    def get_all_entities(self):
        """Fetch all entities with ALL properties from Neo4j."""
        query = """
        MATCH (n)
        WHERE n:Country OR n:Disease OR n:Outbreak OR n:VaccinationRecord 
           OR n:Organization OR n:Vaccine OR n:PandemicEvent
        RETURN 
            elementId(n) as id,
            labels(n)[0] as type,
            properties(n) as properties
        """
        
        with self.driver.session() as session:
            result = session.run(query)
            entities = [record.data() for record in result]
        
        logger.info(f"Found {len(entities)} entities")
        return entities
    
    def get_entity_with_neighbors(self, entity_id: str, max_neighbors: int = 5):
        """Fetch entity with its immediate neighbors for context-aware embeddings.
        
        Industry-standard Graph RAG approach:
        - Include 1-hop neighbors for relational context
        - Limit to top N most important neighbors
        - Include relationship types for semantic understanding
        
        Args:
            entity_id: Neo4j element ID
            max_neighbors: Maximum neighbors to include (default 5)
            
        Returns:
            dict with entity, neighbors, and relationships
        """
        query = f"""
        MATCH (n)
        WHERE elementId(n) = $entity_id
        
        // Get outgoing relationships
        OPTIONAL MATCH (n)-[r_out]->(neighbor_out)
        WHERE neighbor_out:Country OR neighbor_out:Disease OR neighbor_out:Outbreak 
           OR neighbor_out:Organization OR neighbor_out:Vaccine 
           OR neighbor_out:VaccinationRecord OR neighbor_out:PandemicEvent
        
        WITH n, collect({{
            type: type(r_out),
            direction: 'outgoing',
            neighbor: {{
                type: labels(neighbor_out)[0],
                name: COALESCE(neighbor_out.name, neighbor_out.label, neighbor_out.id),
                properties: properties(neighbor_out)
            }}
        }})[..{max_neighbors}] as outgoing
        
        // Get incoming relationships
        OPTIONAL MATCH (n)<-[r_in]-(neighbor_in)
        WHERE neighbor_in:Country OR neighbor_in:Disease OR neighbor_in:Outbreak 
           OR neighbor_in:Organization OR neighbor_in:Vaccine 
           OR neighbor_in:VaccinationRecord OR neighbor_in:PandemicEvent
        
        WITH n, outgoing, collect({{
            type: type(r_in),
            direction: 'incoming',
            neighbor: {{
                type: labels(neighbor_in)[0],
                name: COALESCE(neighbor_in.name, neighbor_in.label, neighbor_in.id),
                properties: properties(neighbor_in)
            }}
        }})[..{max_neighbors}] as incoming
        
        RETURN {{
            id: elementId(n),
            type: labels(n)[0],
            properties: properties(n),
            relationships: outgoing + incoming
        }} as result
        """
        
        with self.driver.session() as session:
            result = session.run(query, {"entity_id": entity_id})
            record = result.single()
            return record['result'] if record else None
    
    def create_text_representation(self, entity, include_neighbors: bool = True):
        """Create COMPREHENSIVE text representation for embedding.
        
        Industry-standard Graph RAG embedding approach:
        1. Include ALL entity properties (intrinsic features)
        2. Include neighbor context (structural/relational features)
        3. Include relationship types (semantic connections)
        
        This creates "context-aware" embeddings that understand:
        - What the entity is (its properties)
        - How it relates to other entities (its neighborhood)
        - The semantic meaning of relationships
        
        Args:
            entity: Entity dict with 'type' and 'properties'
            include_neighbors: Whether to fetch and include neighbor context
            
        Returns:
            Comprehensive text representation
        """
        parts = []
        entity_type = entity['type']
        props = entity.get('properties', {})
        
        # Helper to format arrays
        def format_array(arr):
            if isinstance(arr, list):
                return ', '.join(str(x) for x in arr if x)
            return str(arr) if arr else ''
        
        # Add type
        parts.append(f"Entity Type: {entity_type}")
        
        # ==== DISEASE - ALL PROPERTIES ====
        if entity_type == 'Disease':
            # Basic identifiers
            if props.get('id'):
                parts.append(f"ID: {props['id']}")
            if props.get('name'):
                parts.append(f"Name: {props['name']}")
            if props.get('fullName'):
                parts.append(f"Full Name: {props['fullName']}")
            
            # Medical classification codes
            if props.get('icd10'):
                parts.append(f"ICD-10 Code: {props['icd10']}")
            if props.get('mesh'):
                parts.append(f"MeSH Code: {props['mesh']}")
            
            # Disease category and type
            if props.get('category'):
                parts.append(f"Category: {props['category']}")
            if props.get('pathogen'):
                parts.append(f"Pathogen: {props['pathogen']}")
            if props.get('causativeAgent'):
                parts.append(f"Causative Agent: {props['causativeAgent']}")
            if props.get('medicalSpecialty'):
                parts.append(f"Medical Specialty: {props['medicalSpecialty']}")
            
            # Clinical information - ARRAYS
            if props.get('symptoms'):
                parts.append(f"Symptoms: {format_array(props['symptoms'])}")
            if props.get('treatments'):
                parts.append(f"Treatments: {format_array(props['treatments'])}")
            if props.get('drugs'):
                parts.append(f"Drugs: {format_array(props['drugs'])}")
            if props.get('possibleTreatments'):
                parts.append(f"Possible Treatments: {format_array(props['possibleTreatments'])}")
            if props.get('riskFactors'):
                parts.append(f"Risk Factors: {format_array(props['riskFactors'])}")
            if props.get('transmissionMethods'):
                parts.append(f"Transmission Methods: {format_array(props['transmissionMethods'])}")
            
            # Prevention and incubation
            if props.get('prevention'):
                parts.append(f"Prevention: {props['prevention']}")
            if props.get('incubationPeriod'):
                parts.append(f"Incubation Period: {props['incubationPeriod']}")
            
            # Descriptions
            if props.get('description'):
                parts.append(f"Description: {props['description'][:1000]}")
            if props.get('wikipediaAbstract'):
                parts.append(f"Wikipedia Abstract: {props['wikipediaAbstract'][:1000]}")
            if props.get('wikipediaUrl'):
                parts.append(f"Wikipedia URL: {props['wikipediaUrl']}")
            if props.get('dbpediaUri'):
                parts.append(f"DBpedia URI: {props['dbpediaUri']}")
            if props.get('thumbnailUrl'):
                parts.append(f"Image: {props['thumbnailUrl']}")
            
            # Status
            if props.get('eradicated'):
                parts.append(f"Eradicated: {props['eradicated']}")
            if props.get('pandemic'):
                parts.append(f"Pandemic: {props['pandemic']}")
            if props.get('dataSource'):
                parts.append(f"Data Source: {props['dataSource']}")
                
        # ==== COUNTRY - ALL PROPERTIES ====
        elif entity_type == 'Country':
            if props.get('name'):
                parts.append(f"Country Name: {props['name']}")
            if props.get('code'):
                parts.append(f"Country Code: {props['code']}")
            if props.get('iso2'):
                parts.append(f"ISO-2 Code: {props['iso2']}")
            
            # Geographic info
            if props.get('continent'):
                parts.append(f"Continent: {props['continent']}")
            if props.get('capital'):
                parts.append(f"Capital: {props['capital']}")
            if props.get('latitude') and props.get('longitude'):
                parts.append(f"Coordinates: {props['latitude']}, {props['longitude']}")
            if props.get('areaKm2'):
                parts.append(f"Area: {props['areaKm2']:,} km²")
            
            # Demographics
            if props.get('population'):
                parts.append(f"Population: {props['population']:,}")
            if props.get('officialLanguage'):
                parts.append(f"Official Language: {props['officialLanguage']}")
            
            # Economic
            if props.get('gdp'):
                parts.append(f"GDP: ${props['gdp']:,}")
            if props.get('lifeExpectancy'):
                parts.append(f"Life Expectancy: {props['lifeExpectancy']} years")
            
            # External links
            if props.get('wikipediaUrl'):
                parts.append(f"Wikipedia: {props['wikipediaUrl']}")
            if props.get('dbpediaUri'):
                parts.append(f"DBpedia: {props['dbpediaUri']}")
                
        # ==== OUTBREAK - ALL PROPERTIES ====
        elif entity_type == 'Outbreak':
            if props.get('id'):
                parts.append(f"Outbreak ID: {props['id']}")
            if props.get('year'):
                parts.append(f"Year: {props['year']}")
            if props.get('date'):
                parts.append(f"Date: {props['date']}")
            
            # Case statistics (comprehensive)
            if props.get('cases'):
                parts.append(f"Cases: {int(props['cases']):,}")
            if props.get('deaths'):
                parts.append(f"Deaths: {int(props['deaths']):,}")
            if props.get('confirmedDeaths'):
                parts.append(f"Confirmed Deaths: {int(props['confirmedDeaths']):,}")
            if props.get('excessDeaths'):
                parts.append(f"Excess Deaths: {props['excessDeaths']:,}")
            if props.get('confidenceIntervalTop'):
                parts.append(f"Confidence Interval Top: {props['confidenceIntervalTop']}")
            if props.get('confidenceIntervalBottom'):
                parts.append(f"Confidence Interval Bottom: {props['confidenceIntervalBottom']}")
            
            # Vaccination statistics (for VaccinationRecord outbreaks)
            if props.get('coverage'):
                parts.append(f"Vaccination Coverage: {props['coverage']}%")
            if props.get('totalVaccinated'):
                parts.append(f"Total Vaccinated: {props['totalVaccinated']:,}")
            
            # Links to disease/country
            if props.get('diseaseId'):
                parts.append(f"Disease: {props['diseaseId']}")
            if props.get('diseaseName'):
                parts.append(f"Disease Name: {props['diseaseName']}")
            if props.get('countryCode'):
                parts.append(f"Country: {props['countryCode']}")
            if props.get('countryName'):
                parts.append(f"Country Name: {props['countryName']}")
                
        # ==== ORGANIZATION - ALL PROPERTIES ====
        elif entity_type == 'Organization':
            if props.get('name'):
                parts.append(f"Organization: {props['name']}")
            if props.get('acronym'):
                parts.append(f"Acronym: {props['acronym']}")
            if props.get('role'):
                parts.append(f"Role: {props['role']}")
            if props.get('headquarters'):
                parts.append(f"Headquarters: {props['headquarters']}")
            if props.get('founded'):
                parts.append(f"Founded: {props['founded']}")
            if props.get('website'):
                parts.append(f"Website: {props['website']}")
                
        # ==== VACCINE - ALL PROPERTIES ====
        elif entity_type == 'Vaccine':
            if props.get('name'):
                parts.append(f"Vaccine Name: {props['name']}")
            if props.get('vaccineName'):
                parts.append(f"Vaccine: {props['vaccineName']}")
            if props.get('manufacturer'):
                parts.append(f"Manufacturer: {props['manufacturer']}")
            if props.get('vaccineType'):
                parts.append(f"Vaccine Type: {props['vaccineType']}")
            if props.get('approvalDate'):
                parts.append(f"Approval Date: {props['approvalDate']}")
            if props.get('description'):
                parts.append(f"Description: {props['description'][:500]}")
                
        # ==== VACCINATION RECORD - ALL PROPERTIES ====
        elif entity_type == 'VaccinationRecord':
            if props.get('id'):
                parts.append(f"Record ID: {props['id']}")
            if props.get('vaccineName'):
                parts.append(f"Vaccine: {props['vaccineName']}")
            if props.get('year'):
                parts.append(f"Year: {props['year']}")
            if props.get('coverage'):
                parts.append(f"Coverage: {props['coverage']}%")
            if props.get('totalVaccinated'):
                parts.append(f"Total Vaccinated: {props['totalVaccinated']:,}")
            if props.get('countryCode'):
                parts.append(f"Country: {props['countryCode']}")
                
        # ==== PANDEMIC EVENT - ALL PROPERTIES ====
        elif entity_type == 'PandemicEvent':
            if props.get('name'):
                parts.append(f"Event: {props['name']}")
            if props.get('abstract'):
                parts.append(f"Description: {props['abstract'][:1000]}")
            if props.get('startDate'):
                parts.append(f"Start Date: {props['startDate']}")
            if props.get('deathToll'):
                parts.append(f"Death Toll: {props['deathToll']}")
            if props.get('location'):
                parts.append(f"Location: {props['location']}")
        
        # ==== GRAPH CONTEXT (NEIGHBOR INFORMATION) ====
        # Industry-standard Graph RAG: Include 1-hop neighbors for relational context
        if include_neighbors and entity.get('id'):
            neighbor_data = self.get_entity_with_neighbors(entity['id'], max_neighbors=5)
            if neighbor_data and neighbor_data.get('relationships'):
                relationships = neighbor_data['relationships']
                
                # Group by relationship type
                rel_summary = {}
                for rel in relationships:
                    if rel and rel.get('type') and rel.get('neighbor'):
                        rel_type = rel['type']
                        neighbor = rel['neighbor']
                        direction = rel.get('direction', 'outgoing')
                        
                        if rel_type not in rel_summary:
                            rel_summary[rel_type] = []
                        
                        neighbor_desc = f"{neighbor.get('type', 'Entity')}: {neighbor.get('name', 'Unknown')}"
                        if direction == 'incoming':
                            neighbor_desc = f"← {neighbor_desc}"
                        else:
                            neighbor_desc = f"→ {neighbor_desc}"
                        
                        rel_summary[rel_type].append(neighbor_desc)
                
                # Add relationship context to embedding
                if rel_summary:
                    parts.append("RELATIONSHIPS:")
                    for rel_type, neighbors in rel_summary.items():
                        parts.append(f"{rel_type}: {', '.join(neighbors[:3])}")  # Max 3 per type
        
        # Join all parts with separator
        text = " | ".join(parts) if parts else "Unknown entity"
        return text
    
    def generate_embeddings(self, entities, include_graph_context: bool = True):
        """Generate embeddings for all entities using GPU if available.
        
        Args:
            entities: List of entity dictionaries
            include_graph_context: Whether to include neighbor relationships (Graph RAG)
        """
        logger.info("Generating embeddings...")
        logger.info(f"Processing {len(entities)} entities in batches of {self.batch_size}")
        logger.info(f"Graph context (neighbors): {'ENABLED' if include_graph_context else 'DISABLED'}")
        
        # Prepare texts with optional graph context
        texts = [self.create_text_representation(e, include_neighbors=include_graph_context) for e in entities]
        
        # Generate embeddings in batches with GPU acceleration
        embeddings = self.model.encode(
            texts,
            batch_size=self.batch_size,
            show_progress_bar=True,
            convert_to_numpy=True,
            device=self.device,  # Explicitly use GPU
            normalize_embeddings=True  # Normalize for cosine similarity
        )
        
        logger.info(f"✓ Generated {len(embeddings)} embeddings")
        return embeddings
    
    def store_embeddings(self, entities, embeddings):
        """Store embeddings back to Neo4j.
        
        OVERWRITES existing embeddings to ensure they're up-to-date with the latest schema.
        """
        logger.info("Storing embeddings in Neo4j (will overwrite existing)...")
        
        query = """
        MATCH (n)
        WHERE elementId(n) = $id
        SET n.embedding = $embedding
        """
        
        with self.driver.session() as session:
            for entity, embedding in tqdm(zip(entities, embeddings), total=len(entities), desc="Storing"):
                session.run(query, {
                    "id": entity['id'],
                    "embedding": embedding.tolist()
                })
        
        logger.info(f"✓ Stored {len(embeddings)} embeddings (overwrote any existing)")
    
    def create_vector_index(self):
        """Create vector index for similarity search."""
        logger.info("Creating vector index...")
        
        with self.driver.session() as session:
            # Check if index exists
            result = session.run("SHOW INDEXES")
            existing = [r['name'] for r in result]
            
            if 'entityEmbedding' in existing:
                logger.info("Vector index 'entityEmbedding' already exists, dropping...")
                session.run("DROP INDEX entityEmbedding IF EXISTS")
            
            # Create vector index for all entity types
            query = f"""
            CREATE VECTOR INDEX entityEmbedding IF NOT EXISTS
            FOR (n:Country)
            ON n.embedding
            OPTIONS {{
                indexConfig: {{
                    `vector.dimensions`: {self.embedding_dim},
                    `vector.similarity_function`: 'cosine'
                }}
            }}
            """
            
            try:
                session.run(query)
                logger.info("✓ Vector index 'entityEmbedding' created")
            except Exception as e:
                logger.warning(f"Note: {e}")
                logger.info("Trying alternative index creation method...")
                
                # Alternative: Create for specific label
                for label in ['Country', 'Disease', 'Outbreak', 'VaccinationRecord', 
                             'Organization', 'Vaccine', 'PandemicEvent']:
                    try:
                        query = f"""
                        CREATE VECTOR INDEX entityEmbedding_{label} IF NOT EXISTS
                        FOR (n:{label})
                        ON n.embedding
                        OPTIONS {{
                            indexConfig: {{
                                `vector.dimensions`: {self.embedding_dim},
                                `vector.similarity_function`: 'cosine'
                            }}
                        }}
                        """
                        session.run(query)
                        logger.info(f"✓ Created index for {label}")
                    except Exception as e2:
                        logger.error(f"Failed to create index for {label}: {e2}")
    
    def verify_setup(self):
        """Verify embeddings and index are working."""
        logger.info("\nVerifying setup...")
        
        with self.driver.session() as session:
            # Count nodes with embeddings
            result = session.run("""
                MATCH (n)
                WHERE n.embedding IS NOT NULL
                RETURN count(n) as count
            """)
            count = result.single()['count']
            logger.info(f"✓ {count} nodes have embeddings")
            
            # List indexes
            result = session.run("SHOW INDEXES")
            indexes = [r['name'] for r in result]
            logger.info(f"✓ Found indexes: {', '.join(indexes)}")
    
    def close(self):
        """Close Neo4j connection."""
        self.driver.close()
    
    def run(self):
        """Run the full embedding generation pipeline."""
        try:
            logger.info("=" * 60)
            logger.info("EpiHelix - Embedding Generation")
            logger.info("=" * 60)
            
            # Step 1: Fetch entities
            entities = self.get_all_entities()
            
            if not entities:
                logger.error("No entities found in Neo4j!")
                return
            
            # Step 2: Generate embeddings
            embeddings = self.generate_embeddings(entities)
            
            # Step 3: Store embeddings
            self.store_embeddings(entities, embeddings)
            
            # Step 4: Create vector index
            self.create_vector_index()
            
            # Step 5: Verify
            self.verify_setup()
            
            logger.info("\n" + "=" * 60)
            logger.info("✓ Embedding generation complete!")
            logger.info("=" * 60)
            logger.info("\nYour backend is now ready for semantic search.")
            
        except Exception as e:
            logger.error(f"Error: {e}", exc_info=True)
        finally:
            self.close()


def main():
    """Main entry point."""
    # Get credentials from environment
    user_secrets = UserSecretsClient()
    neo4j_user = "neo4j"
    neo4j_uri = user_secrets.get_secret("NEO4J_URI")
    neo4j_password = user_secrets.get_secret("NEO4J_PASSWORD")
    
    if not neo4j_password:
        logger.error("NEO4J_PASSWORD environment variable not set!")
        logger.info("\nSet it with:")
        logger.info("  export NEO4J_PASSWORD='your-password'")
        return
    
    # Initialize and run
    generator = EmbeddingGenerator(
        neo4j_uri=neo4j_uri,
        neo4j_user=neo4j_user,
        neo4j_password=neo4j_password,
        batch_size=256  # Larger batch size for GPU (Kaggle has 16GB GPU)
    )
    
    generator.run()


if __name__ == "__main__":
    main()