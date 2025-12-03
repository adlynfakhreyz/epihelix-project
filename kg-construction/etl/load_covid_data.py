"""
ETL Script: Load COVID-19 Excess Deaths Data into Neo4j
Dataset: 4- excess-deaths-cumulative-economist-single-entity.csv

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


class CovidDataLoader:
    """Load COVID-19 excess deaths data from CSV into Neo4j (raw data only)"""

    def __init__(self, conn):
        """
        Initialize loader

        Args:
            conn: Neo4jConnection instance
        """
        self.conn = conn
        self.batch_size = 1000

    def load_countries(self, df):
        """Create Country nodes"""
        logger.info("Loading countries...")

        # Get unique countries
        countries = df[['Entity', 'Code']].drop_duplicates()
        countries = countries[countries['Code'].notna()]  # Filter out null codes

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
        """Create minimal COVID-19 Disease node from CSV data (no external enrichment)"""
        logger.info("Creating COVID-19 disease node from CSV data...")

        query = """
        MERGE (d:Disease {id: 'covid19'})
        ON CREATE SET
            d.name = 'COVID-19',
            d.firstIdentified = date('2019-12-01'),
            d.pandemic = true,
            d.dataSource = 'HPD Dataset'
        ON MATCH SET
            d.name = 'COVID-19'
        """

        self.conn.execute_write(query, {})
        logger.info(f"✓ COVID-19 disease node created from CSV data")

    def load_outbreaks(self, df):
        """Create Outbreak nodes and relationships"""
        logger.info(f"Loading {len(df)} outbreak records...")

        # Clean data
        df = df[df['Code'].notna()].copy()
        df['Day'] = pd.to_datetime(df['Day'])

        # Sample data for performance (load every 7th day to reduce data volume)
        # You can remove this line to load all data
        df_sampled = df[df.index % 7 == 0].copy()

        logger.info(f"Loading {len(df_sampled)} sampled outbreak records (weekly)...")

        query = """
        UNWIND $outbreaks AS outbreak
        MATCH (c:Country {code: outbreak.country_code})
        MATCH (d:Disease {id: 'covid19'})

        CREATE (o:Outbreak {
            id: outbreak.id,
            date: date(outbreak.date),
            year: outbreak.year,
            excessDeaths: outbreak.excess_deaths,
            confirmedDeaths: outbreak.confirmed_deaths,
            confidenceIntervalTop: outbreak.ci_top,
            confidenceIntervalBottom: outbreak.ci_bottom
        })

        CREATE (o)-[:OCCURRED_IN]->(c)
        CREATE (o)-[:CAUSED_BY]->(d)
        """

        # Process in batches
        total_batches = (len(df_sampled) + self.batch_size - 1) // self.batch_size

        for i in tqdm(range(0, len(df_sampled), self.batch_size), total=total_batches, desc="Loading outbreaks"):
            batch = df_sampled.iloc[i:i + self.batch_size]

            outbreaks_data = []
            for _, row in batch.iterrows():
                outbreak_id = f"covid_{row['Code']}_{row['Day'].strftime('%Y%m%d')}"

                outbreaks_data.append({
                    'id': outbreak_id,
                    'country_code': row['Code'],
                    'date': row['Day'].strftime('%Y-%m-%d'),
                    'year': row['Day'].year,
                    'excess_deaths': float(row['cumulative_estimated_daily_excess_deaths']) if pd.notna(row['cumulative_estimated_daily_excess_deaths']) else None,
                    'confirmed_deaths': float(row['Total confirmed deaths due to COVID-19']) if pd.notna(row['Total confirmed deaths due to COVID-19']) else None,
                    'ci_top': float(row['cumulative_estimated_daily_excess_deaths_ci_95_top']) if pd.notna(row['cumulative_estimated_daily_excess_deaths_ci_95_top']) else None,
                    'ci_bottom': float(row['cumulative_estimated_daily_excess_deaths_ci_95_bot']) if pd.notna(row['cumulative_estimated_daily_excess_deaths_ci_95_bot']) else None
                })

            self.conn.execute_write(query, {'outbreaks': outbreaks_data})

        logger.info(f"✓ Loaded {len(df_sampled)} outbreak records")

    def load(self, csv_path):
        """
        Main load method

        Args:
            csv_path: Path to CSV file
        """
        logger.info(f"Loading COVID-19 data from {csv_path}")

        # Read CSV
        df = pd.read_csv(csv_path)
        logger.info(f"Read {len(df)} rows from CSV")

        # Load data (no enrichment)
        self.load_countries(df)
        self.load_disease()
        self.load_outbreaks(df)

        logger.info("✓ COVID-19 data loading complete!")


if __name__ == "__main__":
    # Get data path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    kg_dir = os.path.dirname(script_dir)
    csv_path = os.path.join(kg_dir, 'data', 'raw', '4- excess-deaths-cumulative-economist-single-entity.csv')

    # Connect to Neo4j
    conn = Neo4jConnection()
    if not conn.connect():
        exit(1)

    # Setup database
    conn.create_constraints()
    conn.create_indexes()

    # Load data (no enrichment, just raw CSV data)
    loader = CovidDataLoader(conn)
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
