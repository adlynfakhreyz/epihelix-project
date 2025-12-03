"""
ETL Script: Load Vaccination Data into Neo4j
Dataset: 2- the-worlds-number-of-vaccinated-one-year-olds.csv

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


class VaccinationDataLoader:
    """Load vaccination data from CSV into Neo4j (raw data only)"""

    def __init__(self, conn):
        """
        Initialize loader

        Args:
            conn: Neo4jConnection instance
        """
        self.conn = conn
        self.batch_size = 500

        # Mapping: CSV column name -> (disease_id, vaccine_type)
        # This will be populated after reading the CSV
        self.vaccine_columns = {}

    def detect_vaccine_columns(self, df):
        """
        Detect vaccine columns from CSV dynamically

        Args:
            df: DataFrame with vaccination data
        """
        logger.info("Detecting vaccine columns...")

        # Common patterns in vaccination data CSVs
        exclude_cols = ['Entity', 'Code', 'Year']

        vaccine_cols = [col for col in df.columns if col not in exclude_cols]

        # Map vaccine columns to disease IDs
        # This mapping connects vaccines to the diseases they prevent
        vaccine_disease_mapping = {
            # Pattern matching for vaccine names
            'bcg': 'tuberculosis',
            'tuberculosis': 'tuberculosis',
            'dtp': 'diphtheria',  # Diphtheria-tetanus-pertussis
            'diphtheria': 'diphtheria',
            'pertussis': 'pertussis',
            'tetanus': 'tetanus',
            'polio': 'polio',
            'pol3': 'polio',
            'measles': 'measles',
            'mcv': 'measles',  # Measles-containing vaccine
            'hepb': 'hepatitis_b',
            'hepatitis': 'hepatitis_b',
            'hib': 'haemophilus_influenzae',
            'haemophilus': 'haemophilus_influenzae',
            'rotavirus': 'rotavirus',
            'pneumococcal': 'pneumonia',
            'pcv': 'pneumonia',  # Pneumococcal conjugate vaccine
            'rubella': 'rubella',
            'mumps': 'mumps',
            'yellow fever': 'yellow_fever',
            'japanese encephalitis': 'japanese_encephalitis',
            'cholera': 'cholera',
            'rabies': 'rabies',
            'typhoid': 'typhoid'
        }

        for col in vaccine_cols:
            col_lower = col.lower()

            # Try to match vaccine to disease
            disease_id = None
            for pattern, did in vaccine_disease_mapping.items():
                if pattern in col_lower:
                    disease_id = did
                    break

            if disease_id:
                self.vaccine_columns[col] = {
                    'disease_id': disease_id,
                    'vaccine_name': col,
                    'column_name': col
                }

        logger.info(f"✓ Detected {len(self.vaccine_columns)} vaccine columns")
        for col, info in self.vaccine_columns.items():
            logger.info(f"  - {col} → {info['disease_id']}")

    def ensure_diseases_exist(self):
        """
        Ensure all diseases referenced by vaccines exist in the graph
        Creates minimal disease nodes from CSV data (no external enrichment)
        """
        logger.info("Ensuring disease nodes exist...")

        # Simple name mapping for diseases (no external data)
        disease_name_mapping = {
            'tuberculosis': 'Tuberculosis',
            'diphtheria': 'Diphtheria',
            'pertussis': 'Pertussis (Whooping Cough)',
            'tetanus': 'Tetanus',
            'polio': 'Polio',
            'measles': 'Measles',
            'hepatitis_b': 'Hepatitis B',
            'haemophilus_influenzae': 'Haemophilus Influenzae',
            'rotavirus': 'Rotavirus',
            'pneumonia': 'Pneumonia',
            'rubella': 'Rubella',
            'mumps': 'Mumps',
            'yellow_fever': 'Yellow Fever',
            'japanese_encephalitis': 'Japanese Encephalitis',
            'cholera': 'Cholera',
            'rabies': 'Rabies',
            'typhoid': 'Typhoid'
        }

        # Get unique disease IDs from vaccine columns
        disease_ids = set(info['disease_id'] for info in self.vaccine_columns.values())

        for disease_id in disease_ids:
            # Check if disease already exists
            check_query = "MATCH (d:Disease {id: $disease_id}) RETURN count(d) as count"
            result = self.conn.execute_query(check_query, {'disease_id': disease_id})

            if result and result[0]['count'] > 0:
                logger.info(f"  ✓ Disease '{disease_id}' already exists, skipping")
                continue

            # Disease doesn't exist, create minimal node from CSV data
            logger.info(f"  Creating disease node for '{disease_id}'...")

            disease_name = disease_name_mapping.get(disease_id, disease_id.replace('_', ' ').title())

            # Create minimal disease node
            create_query = """
            MERGE (d:Disease {id: $disease_id})
            ON CREATE SET
                d.name = $name,
                d.vaccinePreventable = true,
                d.dataSource = 'HPD Dataset'
            """

            params = {
                'disease_id': disease_id,
                'name': disease_name
            }

            self.conn.execute_write(create_query, params)
            logger.info(f"  ✓ Created disease node for '{disease_id}'")

    def load_countries(self, df):
        """Create Country nodes (if they don't exist)"""
        logger.info("Loading countries...")

        countries = df[['Entity', 'Code']].drop_duplicates()
        countries = countries[countries['Code'].notna()]

        query = """
        UNWIND $countries AS country
        MERGE (c:Country {code: country.code})
        ON CREATE SET
            c.name = country.name
        """

        countries_data = [
            {'code': row['Code'], 'name': row['Entity']}
            for _, row in countries.iterrows()
        ]

        self.conn.execute_write(query, {'countries': countries_data})
        logger.info(f"✓ Loaded/verified {len(countries_data)} countries")

    def load_vaccination_records(self, df):
        """Load vaccination coverage data"""
        logger.info(f"Loading vaccination records from {len(df)} rows...")

        # Clean data
        df = df[df['Code'].notna()].copy()

        # Process each vaccine column
        for col_name, vaccine_info in self.vaccine_columns.items():
            disease_id = vaccine_info['disease_id']
            vaccine_name = vaccine_info['vaccine_name']

            if col_name not in df.columns:
                logger.warning(f"Column '{col_name}' not found, skipping...")
                continue

            # Filter rows with data for this vaccine
            vaccine_df = df[df[col_name].notna()].copy()
            if len(vaccine_df) == 0:
                logger.info(f"No data for {vaccine_name}, skipping...")
                continue

            logger.info(f"Loading {len(vaccine_df)} records for {vaccine_name}...")

            query = """
            UNWIND $records AS record
            MATCH (c:Country {code: record.country_code})
            MATCH (d:Disease {id: record.disease_id})

            MERGE (v:VaccinationRecord {id: record.id})
            ON CREATE SET
                v.year = record.year,
                v.vaccineName = record.vaccine_name,
                v.coveragePercent = record.coverage,
                v.vaccineType = record.vaccine_type
            ON MATCH SET
                v.coveragePercent = record.coverage

            MERGE (v)-[:ADMINISTERED_IN]->(c)
            MERGE (v)-[:PREVENTS]->(d)
            """

            # Process in batches
            total_batches = (len(vaccine_df) + self.batch_size - 1) // self.batch_size

            for i in tqdm(range(0, len(vaccine_df), self.batch_size),
                         total=total_batches,
                         desc=f"Loading {vaccine_name}"):
                batch = vaccine_df.iloc[i:i + self.batch_size]

                records_data = []
                for _, row in batch.iterrows():
                    record_id = f"vax_{disease_id}_{row['Code']}_{int(row['Year'])}"

                    records_data.append({
                        'id': record_id,
                        'country_code': row['Code'],
                        'disease_id': disease_id,
                        'year': int(row['Year']),
                        'vaccine_name': vaccine_name,
                        'vaccine_type': col_name,
                        'coverage': float(row[col_name])
                    })

                self.conn.execute_write(query, {'records': records_data})

            logger.info(f"✓ Loaded {len(vaccine_df)} records for {vaccine_name}")

    def load(self, csv_path):
        """
        Main load method

        Args:
            csv_path: Path to CSV file
        """
        logger.info(f"Loading vaccination data from {csv_path}")

        # Read CSV
        df = pd.read_csv(csv_path)
        logger.info(f"Read {len(df)} rows from CSV")
        logger.info(f"Columns: {list(df.columns)}\n")

        # Detect vaccine columns dynamically
        self.detect_vaccine_columns(df)

        # Ensure disease nodes exist
        self.ensure_diseases_exist()

        # Load data
        self.load_countries(df)
        self.load_vaccination_records(df)

        logger.info("✓ Vaccination data loading complete!")


if __name__ == "__main__":
    # Get data path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    kg_dir = os.path.dirname(script_dir)
    csv_path = os.path.join(kg_dir, 'data', 'raw', '2- the-worlds-number-of-vaccinated-one-year-olds.csv')

    # Check if file exists
    if not os.path.exists(csv_path):
        print(f"ERROR: CSV file not found at {csv_path}")
        print("Please ensure the file is in kg-construction/data/raw/")
        exit(1)

    # Connect to Neo4j
    conn = Neo4jConnection()
    if not conn.connect():
        exit(1)

    # Setup database
    conn.create_constraints()
    conn.create_indexes()

    # Load data (no enrichment, just raw CSV data)
    loader = VaccinationDataLoader(conn)
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

    # Show vaccination stats
    vax_query = "MATCH (v:VaccinationRecord) RETURN count(v) as count"
    vax_result = conn.execute_query(vax_query)
    if vax_result:
        print(f"Vaccination Records: {vax_result[0]['count']:,}")

    conn.close()
