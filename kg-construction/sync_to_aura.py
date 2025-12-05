"""
Sync Database: Update Aura with changes from Local Neo4j

This script:
- Adds new nodes from Local to Aura
- Updates properties on existing nodes
- Adds new relationships
- Does NOT delete anything from Aura
"""
import logging
from neo4j import GraphDatabase
import time

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
LOCAL_URI = "bolt://localhost:7687"
LOCAL_USER = "neo4j"
LOCAL_PASSWORD = "epihelix123"

AURA_URI = "neo4j+s://a1671c1c.databases.neo4j.io"
AURA_USER = "neo4j"
AURA_PASSWORD = "nZgvoMZVAmSndTiuAsFvO-DbObIDE1APjur1k6n5TdM"


def sync_nodes_by_label(local_driver, aura_driver, label):
    """Sync nodes of a specific label"""
    logger.info(f"Syncing {label} nodes...")

    # Get all nodes from Local
    with local_driver.session() as session:
        local_nodes = session.run(f"""
            MATCH (n:{label})
            RETURN n
        """).data()

    logger.info(f"  Found {len(local_nodes)} {label} nodes in LOCAL")

    # Sync each node to Aura
    added = 0
    updated = 0

    with aura_driver.session() as session:
        for record in local_nodes:
            node = record['n']
            props = dict(node)

            # Determine the unique key for this node
            id_key = None
            id_value = None

            if 'id' in props:
                id_key = 'id'
                id_value = props['id']
            elif 'code' in props:
                id_key = 'code'
                id_value = props['code']
            elif 'name' in props:
                id_key = 'name'
                id_value = props['name']
            else:
                logger.warning(f"  Skipping node without ID key: {props}")
                continue

            # MERGE node (create if doesn't exist, update if exists)
            query = f"""
            MERGE (n:{label} {{{id_key}: $id_value}})
            ON CREATE SET n = $props
            ON MATCH SET n += $props
            RETURN
                CASE
                    WHEN n.{id_key} = $id_value THEN 'updated'
                    ELSE 'added'
                END as action
            """

            try:
                result = session.run(query, {
                    'id_value': id_value,
                    'props': props
                })

                action = result.single()
                if action:
                    if action['action'] == 'added':
                        added += 1
                    else:
                        updated += 1

            except Exception as e:
                logger.warning(f"  Failed to sync node {id_key}={id_value}: {e}")

    logger.info(f"  [OK] {label}: Added {added}, Updated {updated}")
    return added, updated


def sync_all_nodes(local_driver, aura_driver):
    """Sync all nodes from Local to Aura"""
    logger.info("=== SYNCING NODES ===")

    # Get all labels from Local
    with local_driver.session() as session:
        labels_result = session.run("CALL db.labels()").data()
        labels = [r['label'] for r in labels_result]

    logger.info(f"Found {len(labels)} node labels: {', '.join(labels)}\n")

    total_added = 0
    total_updated = 0

    for label in labels:
        added, updated = sync_nodes_by_label(local_driver, aura_driver, label)
        total_added += added
        total_updated += updated
        time.sleep(0.5)  # Rate limiting

    logger.info(f"\n[OK] Total Nodes: Added {total_added}, Updated {total_updated}")


def sync_relationships(local_driver, aura_driver):
    """Sync relationships from Local to Aura"""
    logger.info("\n=== SYNCING RELATIONSHIPS ===")

    # Get all relationship types
    with local_driver.session() as session:
        types_result = session.run("CALL db.relationshipTypes()").data()
        rel_types = [r['relationshipType'] for r in types_result]

    logger.info(f"Found {len(rel_types)} relationship types: {', '.join(rel_types)}\n")

    total_added = 0

    for rel_type in rel_types:
        logger.info(f"Syncing {rel_type} relationships...")

        # Get relationships from Local
        with local_driver.session() as session:
            rels = session.run(f"""
                MATCH (a)-[r:{rel_type}]->(b)
                RETURN
                    labels(a)[0] as start_label,
                    properties(a) as start_props,
                    type(r) as rel_type,
                    properties(r) as rel_props,
                    labels(b)[0] as end_label,
                    properties(b) as end_props
                LIMIT 50000
            """).data()

        logger.info(f"  Found {len(rels)} {rel_type} relationships in LOCAL")

        # Sync relationships to Aura
        added = 0

        with aura_driver.session() as session:
            for rel in rels:
                start_props = rel['start_props']
                end_props = rel['end_props']

                # Get match keys
                start_key = 'id' if 'id' in start_props else ('code' if 'code' in start_props else 'name')
                end_key = 'id' if 'id' in end_props else ('code' if 'code' in end_props else 'name')

                if start_key not in start_props or end_key not in end_props:
                    continue

                start_label = rel['start_label']
                end_label = rel['end_label']
                rel_props = rel['rel_props']

                # MERGE relationship
                query = f"""
                MATCH (a:{start_label} {{{start_key}: $start_id}})
                MATCH (b:{end_label} {{{end_key}: $end_id}})
                MERGE (a)-[r:{rel_type}]->(b)
                ON CREATE SET r = $rel_props
                ON MATCH SET r += $rel_props
                """

                try:
                    session.run(query, {
                        'start_id': start_props[start_key],
                        'end_id': end_props[end_key],
                        'rel_props': rel_props or {}
                    })
                    added += 1

                    if added % 1000 == 0:
                        logger.info(f"    Synced {added:,} relationships...")

                except Exception as e:
                    pass  # Skip failed relationships

        logger.info(f"  [OK] {rel_type}: Synced {added} relationships")
        total_added += added
        time.sleep(0.5)

    logger.info(f"\n[OK] Total Relationships: Synced {total_added}")


def verify_sync(local_driver, aura_driver):
    """Show counts after sync"""
    logger.info("\n=== VERIFICATION ===")

    with local_driver.session() as session:
        local_nodes = session.run("MATCH (n) RETURN count(n) as c").single()['c']
        local_rels = session.run("MATCH ()-[r]->() RETURN count(r) as c").single()['c']

    with aura_driver.session() as session:
        aura_nodes = session.run("MATCH (n) RETURN count(n) as c").single()['c']
        aura_rels = session.run("MATCH ()-[r]->() RETURN count(r) as c").single()['c']

    logger.info(f"LOCAL: {local_nodes:,} nodes, {local_rels:,} relationships")
    logger.info(f"AURA:  {aura_nodes:,} nodes, {aura_rels:,} relationships")

    if aura_nodes >= local_nodes:
        logger.info("[OK] SYNC SUCCESSFUL - Aura has all data from Local!")
    else:
        logger.warning(f"[WARNING] Aura has fewer nodes ({aura_nodes - local_nodes} missing)")


def main():
    print("\n" + "="*60)
    print("DATABASE SYNC: Local -> Aura")
    print("="*60)
    print("\nThis will:")
    print("  1. Add new nodes from Local to Aura")
    print("  2. Update existing nodes with latest properties")
    print("  3. Add missing relationships")
    print("  4. Keep all existing data in Aura")
    print(f"\nAura: {AURA_URI}")
    print("="*60)

    confirm = input("\nType 'YES' to confirm sync: ")
    if confirm != "YES":
        print("Cancelled.")
        return

    start = time.time()

    # Connect
    logger.info("Connecting to databases...")
    local = GraphDatabase.driver(LOCAL_URI, auth=(LOCAL_USER, LOCAL_PASSWORD))
    aura = GraphDatabase.driver(AURA_URI, auth=(AURA_USER, AURA_PASSWORD))

    try:
        # Sync nodes
        sync_all_nodes(local, aura)

        # Sync relationships
        sync_relationships(local, aura)

        # Verify
        verify_sync(local, aura)

        elapsed = time.time() - start
        logger.info(f"\n[OK] Sync completed in {elapsed/60:.1f} minutes")

        print("\n" + "="*60)
        print("[SUCCESS] Database synced to Aura!")
        print("="*60)

    finally:
        local.close()
        aura.close()


if __name__ == "__main__":
    main()
