"""
Main ETL Runner: Load all datasets into Neo4j Knowledge Graph

REFACTORED: Loads ONLY raw CSV data without external enrichment.
After loading, run enrich_all.py to add external data from Wikidata/DBpedia.
"""
import os
import sys
from neo4j_connection import Neo4jConnection
from load_disease_cases import DiseaseCasesLoader
from load_cholera_data import CholeraDataLoader
from load_covid_data import CovidDataLoader
from load_vaccination_data import VaccinationDataLoader
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main(clear_db=False):
    """
    Load all datasets into Neo4j (raw data only, no enrichment)

    Args:
        clear_db: If True, clear database before loading
    """
    # Get paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    kg_dir = os.path.dirname(script_dir)
    data_dir = os.path.join(kg_dir, 'data', 'raw')

    datasets = {
        'disease_cases': os.path.join(data_dir, '1- the-number-of-cases-of-infectious-diseases.csv'),
        'vaccination_data': os.path.join(data_dir, '2- the-worlds-number-of-vaccinated-one-year-olds.csv'),
        'covid_excess_deaths': os.path.join(data_dir, '4- excess-deaths-cumulative-economist-single-entity.csv'),
        'cholera_deaths': os.path.join(data_dir, '5- number-of-reported-cholera-deaths.csv'),
    }

    # Check if files exist
    missing_files = [name for name, path in datasets.items() if not os.path.exists(path)]
    if missing_files:
        logger.error(f"Missing files: {', '.join(missing_files)}")
        logger.error("Please ensure all CSV files are in the kg-construction/data/raw/ directory")
        return False

    # Connect to Neo4j
    logger.info("=" * 60)
    logger.info("EpiHelix Knowledge Graph ETL Pipeline")
    logger.info("=" * 60)

    conn = Neo4jConnection()
    if not conn.connect():
        logger.error("Failed to connect to Neo4j. Please ensure Neo4j is running.")
        logger.error("Run: cd infrastructure && docker-compose up -d")
        return False

    try:
        # Clear database if requested
        if clear_db:
            logger.warning("Clearing existing database...")
            response = input("Are you sure you want to clear the database? (yes/no): ")
            if response.lower() == 'yes':
                conn.clear_database()
            else:
                logger.info("Skipping database clear")

        # Setup database constraints and indexes
        logger.info("\n" + "=" * 60)
        logger.info("Setting up database schema...")
        logger.info("=" * 60)
        conn.create_constraints()
        conn.create_indexes()

        # Load datasets (raw data only, no enrichment)
        logger.info("\n" + "=" * 60)
        logger.info("Loading Dataset 1: Infectious Disease Cases (HPD)")
        logger.info("=" * 60)
        loader1 = DiseaseCasesLoader(conn)
        loader1.load(datasets['disease_cases'])

        logger.info("\n" + "=" * 60)
        logger.info("Loading Dataset 2: Vaccination Coverage Data (HPD)")
        logger.info("=" * 60)
        loader2 = VaccinationDataLoader(conn)
        loader2.load(datasets['vaccination_data'])

        logger.info("\n" + "=" * 60)
        logger.info("Loading Dataset 3: COVID-19 Excess Deaths")
        logger.info("=" * 60)
        loader3 = CovidDataLoader(conn)
        loader3.load(datasets['covid_excess_deaths'])

        logger.info("\n" + "=" * 60)
        logger.info("Loading Dataset 4: Cholera Deaths")
        logger.info("=" * 60)
        loader4 = CholeraDataLoader(conn)
        loader4.load(datasets['cholera_deaths'])

        # Show final statistics
        logger.info("\n" + "=" * 60)
        logger.info("RAW DATA LOADING COMPLETE - Database Statistics")
        logger.info("=" * 60)
        stats = conn.get_stats()
        for key, value in stats.items():
            logger.info(f"  {key.capitalize()}: {value:,}")

        logger.info("\n" + "=" * 60)
        logger.info("✓ Raw data successfully loaded into Knowledge Graph!")
        logger.info("=" * 60)
        logger.info(f"\nNext steps:")
        logger.info(f"1. Run enrichment: python enrich_all.py")
        logger.info(f"2. Access Neo4j Browser: http://localhost:7474")
        logger.info(f"3. Credentials: neo4j / epihelix123")

        return True

    except Exception as e:
        logger.error(f"Error during ETL: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        conn.close()


if __name__ == "__main__":
    # Check for --clear flag
    clear_db = '--clear' in sys.argv

    if clear_db:
        print("⚠️  Running with --clear flag: Database will be cleared before loading")

    success = main(clear_db=clear_db)
    sys.exit(0 if success else 1)
