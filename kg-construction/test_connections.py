"""
Quick test to verify connections to both Local and Aura databases
"""
from neo4j import GraphDatabase
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# LOCAL Neo4j
LOCAL_URI = "bolt://localhost:7687"
LOCAL_USER = "neo4j"
LOCAL_PASSWORD = "epihelix123"

# AURA Neo4j
AURA_URI = "neo4j+s://a1671c1c.databases.neo4j.io"
AURA_USER = "neo4j"
AURA_PASSWORD = "nZgvoMZVAmSndTiuAsFvO-DbObIDE1APjur1k6n5TdM"

print("\n" + "="*60)
print("Testing Database Connections")
print("="*60)

# Test LOCAL
print("\n1. Testing LOCAL Neo4j...")
try:
    local_driver = GraphDatabase.driver(LOCAL_URI, auth=(LOCAL_USER, LOCAL_PASSWORD))
    local_driver.verify_connectivity()

    with local_driver.session() as session:
        result = session.run("MATCH (n) RETURN count(n) as count")
        node_count = result.single()['count']

        result = session.run("MATCH ()-[r]->() RETURN count(r) as count")
        rel_count = result.single()['count']

    print(f"   [OK] Connected to LOCAL: {LOCAL_URI}")
    print(f"   [OK] Nodes: {node_count:,}")
    print(f"   [OK] Relationships: {rel_count:,}")

    local_driver.close()
except Exception as e:
    print(f"   [FAIL] LOCAL connection failed: {e}")
    exit(1)

# Test AURA
print("\n2. Testing AURA Neo4j...")
try:
    aura_driver = GraphDatabase.driver(AURA_URI, auth=(AURA_USER, AURA_PASSWORD))
    aura_driver.verify_connectivity()

    with aura_driver.session() as session:
        result = session.run("MATCH (n) RETURN count(n) as count")
        node_count = result.single()['count']

        result = session.run("MATCH ()-[r]->() RETURN count(r) as count")
        rel_count = result.single()['count']

    print(f"   [OK] Connected to AURA: {AURA_URI}")
    print(f"   [OK] Nodes: {node_count:,}")
    print(f"   [OK] Relationships: {rel_count:,}")

    aura_driver.close()
except Exception as e:
    print(f"   [FAIL] AURA connection failed: {e}")
    exit(1)

print("\n" + "="*60)
print("[SUCCESS] All connections successful!")
print("="*60)
print("\nYou can now run: python migrate_local_to_aura.py")
print()
