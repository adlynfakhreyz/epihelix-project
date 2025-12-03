"""
ETL Script: Load Infectious Disease Cases Data into Neo4j
Dataset: 1- the-number-of-cases-of-infectious-diseases.csv

REFACTORED: Loads ONLY raw CSV data without external enrichment.
Enrichment is handled separately by enrich_all.py workflow.
"""
import os
import pandas as pd
from tqdm import tqdm
from neo4j_connection import Neo4jConnection
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DiseaseCasesLoader:
    """Load disease cases data from CSV into Neo4j (raw data only)"""

    def __init__(self, conn):
        """
        Initialize loader

        Args:
            conn: Neo4jConnection instance
        """
        self.conn = conn
        self.batch_size = 500

        # Simple mapping: CSV column name -> (disease_id, disease_name)
        # Names are derived from CSV column text, no external enrichment
        self.disease_columns = {
            'Indicator:Number of cases of yaws reported': ('yaws', 'Yaws'),
            'Total (estimated) polio cases': ('polio', 'Polio'),
            'Reported cases of guinea worm disease in humans': ('guinea_worm', 'Guinea Worm Disease'),
            'Number of new cases of rabies, in both sexes aged all ages': ('rabies', 'Rabies'),
            'Number of new cases of malaria, in both sexes aged all ages': ('malaria', 'Malaria'),
            'Number of new cases of hiv/aids, in both sexes aged all ages': ('hiv_aids', 'HIV/AIDS'),
            'Number of new cases of tuberculosis, in both sexes aged all ages': ('tuberculosis', 'Tuberculosis'),
            'Number of reported smallpox cases': ('smallpox', 'Smallpox'),
            'Reported cholera cases': ('cholera', 'Cholera')
        }

    def load_countries(self, df):
        """Create Country nodes"""
        logger.info("Loading countries...")

        countries = df[['Entity', 'Code']].drop_duplicates()
        countries = countries[countries['Code'].notna()]

        query = """
        UNWIND $countries AS country
        MERGE (c:Country {code: country.code})
        ON CREATE SET
            c.name = country.name
        ON MATCH SET
            c.name = country.name
        """

        countries_data = [
            {'code': row['Code'], 'name': row['Entity']}
            for _, row in countries.iterrows()
        ]

        self.conn.execute_write(query, {'countries': countries_data})
        logger.info(f"✓ Loaded {len(countries_data)} countries")

    def load_diseases(self):
        """Create minimal Disease nodes from CSV data (no external enrichment)"""
        logger.info("Creating disease nodes from CSV data...")

        query = """
        UNWIND $diseases AS disease
        MERGE (d:Disease {id: disease.id})
        ON CREATE SET
            d.name = disease.name,
            d.eradicated = disease.eradicated,
            d.dataSource = 'HPD Dataset'
        ON MATCH SET
            d.name = disease.name
        """

        # Extract unique diseases from column mappings
        unique_diseases = {}
        for disease_id, disease_name in set(self.disease_columns.values()):
            unique_diseases[disease_id] = disease_name

        diseases_data = [
            {
                'id': disease_id,
                'name': disease_name,
                'eradicated': (disease_id == 'smallpox')  # Domain knowledge: smallpox eradicated in 1980
            }
            for disease_id, disease_name in unique_diseases.items()
        ]

        self.conn.execute_write(query, {'diseases': diseases_data})
        logger.info(f"✓ Created {len(diseases_data)} disease nodes from CSV data")

    def load_cases(self, df):
        """Load disease case data from CSV"""
        logger.info(f"Loading disease cases from {len(df)} rows...")

        # Clean data
        df = df[df['Code'].notna()].copy()

        # Process each disease column
        for col_name, (disease_id, disease_name) in self.disease_columns.items():
            if col_name not in df.columns:
                logger.warning(f"Column '{col_name}' not found, skipping...")
                continue

            # Filter rows with data for this disease
            disease_df = df[df[col_name].notna()].copy()
            if len(disease_df) == 0:
                logger.info(f"No data for {disease_name}, skipping...")
                continue

            logger.info(f"Loading {len(disease_df)} cases for {disease_name}...")

            query = """
            UNWIND $cases AS case
            MATCH (c:Country {code: case.country_code})
            MATCH (d:Disease {id: case.disease_id})

            MERGE (o:Outbreak {id: case.id})
            ON CREATE SET
                o.year = case.year,
                o.cases = case.cases
            ON MATCH SET
                o.cases = case.cases

            MERGE (o)-[:OCCURRED_IN]->(c)
            MERGE (o)-[:CAUSED_BY]->(d)
            """

            # Process in batches
            total_batches = (len(disease_df) + self.batch_size - 1) // self.batch_size

            for i in tqdm(range(0, len(disease_df), self.batch_size),
                         total=total_batches,
                         desc=f"Loading {disease_name}"):
                batch = disease_df.iloc[i:i + self.batch_size]

                cases_data = []
                for _, row in batch.iterrows():
                    outbreak_id = f"{disease_id}_{row['Code']}_{int(row['Year'])}"

                    cases_data.append({
                        'id': outbreak_id,
                        'country_code': row['Code'],
                        'disease_id': disease_id,
                        'year': int(row['Year']),
                        'cases': float(row[col_name])
                    })

                self.conn.execute_write(query, {'cases': cases_data})

            logger.info(f"✓ Loaded {len(disease_df)} records for {disease_name}")

    def load(self, csv_path):
        """
        Main load method

        Args:
            csv_path: Path to CSV file
        """
        logger.info(f"Loading disease cases data from {csv_path}")

        # Read CSV
        df = pd.read_csv(csv_path)
        logger.info(f"Read {len(df)} rows from CSV")

        # Load data
        self.load_countries(df)
        self.load_diseases()
        self.load_cases(df)

        logger.info("✓ Disease cases data loading complete!")


if __name__ == "__main__":
    # Get data path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    kg_dir = os.path.dirname(script_dir)
    csv_path = os.path.join(kg_dir, 'data', 'raw', '1- the-number-of-cases-of-infectious-diseases.csv')

    # Connect to Neo4j
    conn = Neo4jConnection()
    if not conn.connect():
        exit(1)

    # Setup database
    conn.create_constraints()
    conn.create_indexes()

    # Load data (no enrichment, just raw CSV data)
    loader = DiseaseCasesLoader(conn)
    loader.load(csv_path)

    logger.info("\n" + "=" * 60)
    logger.info("Data loading complete!")
    logger.info("To enrich with external data, run: python enrich_all.py")
    logger.info("=" * 60)

    # Show stats
    stats = conn.get_stats()
    print("\n=== Database Statistics ===")
    for key, value in stats.items():
        print(f"{key.capitalize()}: {value:,}")

    conn.close()
