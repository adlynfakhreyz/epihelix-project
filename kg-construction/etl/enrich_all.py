"""
Master Enrichment Script for EpiHelix Knowledge Graph

REFACTORED: This script enriches the knowledge graph with external data sources.

Coordinates all external data enrichment from:
- Wikidata: Disease classifications, symptoms, treatments, country demographics
- DBpedia: Wikipedia abstracts, historical pandemics, additional context

⚠️  IMPORTANT: Run this AFTER loading raw data with load_all_data.py

Workflow:
1. python load_all_data.py  # Load raw CSV data
2. python enrich_all.py     # Enrich with external sources (this script)
"""
import logging
import time
from neo4j_connection import Neo4jConnection
from wikidata_enricher import WikidataEnricher
from dbpedia_enricher import DBpediaEnricher

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Run full enrichment pipeline"""
    logger.info("=" * 60)
    logger.info("EpiHelix Knowledge Graph - External Data Enrichment")
    logger.info("=" * 60)
    logger.info("")

    # Connect to Neo4j
    logger.info("Connecting to Neo4j...")
    conn = Neo4jConnection()
    if not conn.connect():
        logger.error("Failed to connect to Neo4j. Please ensure Neo4j is running.")
        exit(1)

    # Show database stats before enrichment
    logger.info("\n=== Database Statistics (Before Enrichment) ===")
    stats_before = conn.get_stats()
    for key, value in stats_before.items():
        logger.info(f"{key.capitalize()}: {value:,}")
    logger.info("")

    try:
        # Phase 1: Wikidata Enrichment
        logger.info("=" * 60)
        logger.info("PHASE 1: WIKIDATA ENRICHMENT")
        logger.info("=" * 60)
        logger.info("")

        wikidata_enricher = WikidataEnricher(conn)
        wikidata_enricher.enrich_all()

        logger.info("\n⏳ Waiting 5 seconds before DBpedia enrichment...")
        time.sleep(5)

        # Phase 2: DBpedia Enrichment (Optional - may fail if endpoint is down)
        logger.info("\n" + "=" * 60)
        logger.info("PHASE 2: DBPEDIA ENRICHMENT (Optional)")
        logger.info("=" * 60)
        logger.info("")

        try:
            dbpedia_enricher = DBpediaEnricher(conn)
            dbpedia_enricher.enrich_all()
        except Exception as e:
            logger.warning(f"⚠️  DBpedia enrichment failed (this is optional): {e}")
            logger.info("ℹ️  DBpedia endpoint may be down. Continuing without DBpedia enrichment.")
            logger.info("ℹ️  Wikidata enrichment alone is sufficient for project requirements.")

        # Show database stats after enrichment
        logger.info("\n" + "=" * 60)
        logger.info("=== Database Statistics (After Enrichment) ===")
        stats_after = conn.get_stats()
        for key, value in stats_after.items():
            change = value - stats_before.get(key, 0)
            change_str = f" (+{change:,})" if change > 0 else ""
            logger.info(f"{key.capitalize()}: {value:,}{change_str}")

        logger.info("\n" + "=" * 60)
        logger.info("✓ ENRICHMENT COMPLETE!")
        logger.info("=" * 60)
        logger.info("")
        logger.info("Your enriched knowledge graph now contains:")
        logger.info("✓ Raw HPD dataset (disease cases, deaths, vaccination coverage)")
        logger.info("✓ Disease metadata from Wikidata (symptoms, treatments, classifications)")
        logger.info("✓ Country demographics from Wikidata (population, GDP, coordinates, borders)")
        logger.info("✓ Health organizations (WHO, CDC, ECDC)")
        logger.info("  Wikipedia abstracts from DBpedia (if available)")
        logger.info("  Historical pandemic events from DBpedia (if available)")
        logger.info("")
        logger.info("Next steps:")
        logger.info("1. Query the knowledge graph: http://localhost:7474")
        logger.info("2. Build the FastAPI backend to expose the data")
        logger.info("3. Connect the frontend to display enriched information")
        logger.info("")
        logger.info("Example queries:")
        logger.info("  MATCH (d:Disease) RETURN d LIMIT 10")
        logger.info("  MATCH (c:Country)-[:OCCURRED_IN]-(o:Outbreak) RETURN c.name, count(o)")
        logger.info("")

    except KeyboardInterrupt:
        logger.warning("\n⚠️  Enrichment interrupted by user")
    except Exception as e:
        logger.error(f"\n❌ Enrichment failed: {e}", exc_info=True)
        exit(1)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
