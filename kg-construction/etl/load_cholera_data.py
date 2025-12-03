"""
ETL Script: Load Cholera Deaths Data into Neo4j
Dataset: 5- number-of-reported-cholera-deaths.csv

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


class CholeraDataLoader:
    """Load cholera deaths data from CSV into Neo4j (raw data only)"""

    def __init__(self, conn):
        """
        Initialize loader

        Args:
            conn: Neo4jConnection instance
        """
        self.conn = conn
        self.batch_size = 500

    def load_countries(self, df):
        """Create Country nodes"""
        logger.info("Loading countries...")

        # Get unique countries
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

    def load_disease(self):
        """Create minimal Cholera Disease node from CSV data (no external enrichment)"""
        logger.info("Creating Cholera disease node from CSV data...")

        query = """
        MERGE (d:Disease {id: 'cholera'})
        ON CREATE SET
            d.name = 'Cholera',
            d.dataSource = 'HPD Dataset'
        ON MATCH SET
            d.name = 'Cholera'
        """

        self.conn.execute_write(query, {})
        logger.info(f"✓ Cholera disease node created from CSV data")

    def load_deaths(self, df):
        """Create or update Outbreak nodes with death data"""
        logger.info(f"Loading {len(df)} cholera death records...")

        # Clean data
        df = df[df['Code'].notna()].copy()
        df = df[df['Reported cholera deaths'].notna()].copy()

        query = """
        UNWIND $deaths AS death
        MATCH (c:Country {code: death.country_code})
        MATCH (d:Disease {id: 'cholera'})

        MERGE (o:Outbreak {id: death.id})
        ON CREATE SET
            o.year = death.year,
            o.deaths = death.deaths
        ON MATCH SET
            o.deaths = death.deaths

        MERGE (o)-[:OCCURRED_IN]->(c)
        MERGE (o)-[:CAUSED_BY]->(d)
        """

        # Process in batches
        total_batches = (len(df) + self.batch_size - 1) // self.batch_size

        for i in tqdm(range(0, len(df), self.batch_size), total=total_batches, desc="Loading cholera deaths"):
            batch = df.iloc[i:i + self.batch_size]

            deaths_data = []
            for _, row in batch.iterrows():
                outbreak_id = f"cholera_{row['Code']}_{int(row['Year'])}"

                deaths_data.append({
                    'id': outbreak_id,
                    'country_code': row['Code'],
                    'year': int(row['Year']),
                    'deaths': int(row['Reported cholera deaths'])
                })

            self.conn.execute_write(query, {'deaths': deaths_data})

        logger.info(f"✓ Loaded {len(df)} cholera death records")

    def load(self, csv_path):
        """
        Main load method

        Args:
            csv_path: Path to CSV file
        """
        logger.info(f"Loading Cholera data from {csv_path}")

        # Read CSV
        df = pd.read_csv(csv_path)
        logger.info(f"Read {len(df)} rows from CSV")

        # Load data
        self.load_countries(df)
        self.load_disease()
        self.load_deaths(df)

        logger.info("✓ Cholera data loading complete!")


if __name__ == "__main__":
    # Get data path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    kg_dir = os.path.dirname(script_dir)
    csv_path = os.path.join(kg_dir, 'data', 'raw', '5- number-of-reported-cholera-deaths.csv')

    # Connect to Neo4j
    conn = Neo4jConnection()
    if not conn.connect():
        exit(1)

    # Setup database
    conn.create_constraints()
    conn.create_indexes()

    # Load data (no enrichment, just raw CSV data)
    loader = CholeraDataLoader(conn)
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
