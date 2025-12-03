"""
Test DBpedia SPARQL Endpoint Connectivity

Quick script to check if DBpedia is accessible before running enrichment.
"""
from SPARQLWrapper import SPARQLWrapper, JSON
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_dbpedia_connection():
    """Test if DBpedia SPARQL endpoint is accessible"""
    logger.info("Testing DBpedia SPARQL endpoint connectivity...")
    logger.info("Endpoint: https://dbpedia.org/sparql")

    try:
        endpoint = SPARQLWrapper("https://dbpedia.org/sparql")
        endpoint.setReturnFormat(JSON)
        endpoint.setTimeout(15)  # 15 second timeout
        endpoint.addCustomHttpHeader("User-Agent", "EpiHelix/1.0 (Connection Test)")

        # Simple test query
        test_query = """
        SELECT ?label
        WHERE {
          <http://dbpedia.org/resource/Cholera> rdfs:label ?label .
          FILTER(LANG(?label) = "en")
        }
        LIMIT 1
        """

        logger.info("Sending test query...")
        endpoint.setQuery(test_query)
        results = endpoint.query().convert()

        if results and results['results']['bindings']:
            label = results['results']['bindings'][0]['label']['value']
            logger.info(f"✓ SUCCESS! DBpedia is accessible.")
            logger.info(f"  Test result: {label}")
            return True
        else:
            logger.warning("⚠️  DBpedia responded but returned no data.")
            return False

    except Exception as e:
        logger.error(f"❌ FAILED! Cannot connect to DBpedia.")
        logger.error(f"  Error: {e}")
        logger.info("")
        logger.info("Possible reasons:")
        logger.info("  1. DBpedia public endpoint is down (common)")
        logger.info("  2. Your network/firewall is blocking access")
        logger.info("  3. Temporary network issues")
        logger.info("")
        logger.info("Solutions:")
        logger.info("  • Run enrichment anyway - DBpedia is optional")
        logger.info("  • Use Wikidata-only enrichment (sufficient for project)")
        logger.info("  • Try again later when DBpedia is back up")
        logger.info("  • Skip DBpedia enrichment entirely")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("DBpedia SPARQL Endpoint Connectivity Test")
    print("=" * 60)
    print()

    success = test_dbpedia_connection()

    print()
    print("=" * 60)
    if success:
        print("✓ You can proceed with full enrichment (Wikidata + DBpedia)")
        print("  Run: python enrich_all.py")
    else:
        print("⚠️  DBpedia is not accessible")
        print("ℹ️  You can still run enrichment - DBpedia is now optional")
        print("  Run: python enrich_all.py")
        print("  (Will complete successfully with Wikidata enrichment only)")
    print("=" * 60)
