"""
Initialize sample data in Neo4j for testing the context graph explorer.
This creates a sample knowledge graph following the POLE+O model.
"""

import os
from dotenv import load_dotenv
from neo4j_utils import Neo4jConnector

load_dotenv()


def create_sample_ontology_schema(connector: Neo4jConnector):
    """Create base ontology schema with POLE+O model"""
    cypher_queries = [
        # Create constraint for unique names
        "CREATE CONSTRAINT unique_node_name IF NOT EXISTS FOR (n) REQUIRE n.name IS UNIQUE",
        # Create indexes for better query performance
        "CREATE INDEX node_name_index IF NOT EXISTS FOR (n) ON (n.name)",
        "CREATE INDEX node_description_index IF NOT EXISTS FOR (n) ON (n.description)",
    ]

    for query in cypher_queries:
        try:
            connector.execute(query)
            print(f"✓ Executed: {query[:50]}...")
        except Exception as e:
            print(f"✗ Query failed: {e}")


def create_sample_nodes(connector: Neo4jConnector):
    """Create sample nodes across POLE+O categories"""

    # Person nodes
    persons = [
        {
            "name": "Alice Johnson",
            "description": "Software engineer working on AI systems",
            "domain": "technology",
        },
        {
            "name": "Bob Smith",
            "description": "Product manager at TechCorp",
            "domain": "technology",
        },
        {"name": "Carol Davis", "description": "Data scientist and researcher", "domain": "research"},
    ]

    # Organization nodes
    organizations = [
        {"name": "TechCorp", "description": "Leading technology company", "domain": "technology"},
        {"name": "AI Research Institute", "description": "Research organization focused on AI", "domain": "research"},
    ]

    # Location nodes
    locations = [
        {
            "name": "San Francisco",
            "description": "Major tech hub in California",
            "domain": "geography",
        },
        {"name": "Cambridge", "description": "University town in Massachusetts", "domain": "geography"},
    ]

    # Event nodes
    events = [
        {
            "name": "AI Conference 2024",
            "description": "Annual conference on artificial intelligence",
            "domain": "events",
        },
        {"name": "Tech Summit", "description": "Technology industry summit", "domain": "events"},
    ]

    # Object nodes
    objects = [
        {
            "name": "ContextGraph Framework",
            "description": "Knowledge graph framework for AI agents",
            "domain": "technology",
        },
    ]

    # Create Person nodes
    for person in persons:
        cypher = """
        CREATE (p:Person {
            name: $name,
            description: $description,
            domain: $domain
        })
        """
        try:
            connector.execute(cypher, person)
            print(f"✓ Created Person: {person['name']}")
        except Exception as e:
            print(f"✗ Failed to create Person {person['name']}: {e}")

    # Create Organization nodes
    for org in organizations:
        cypher = """
        CREATE (o:Organization {
            name: $name,
            description: $description,
            domain: $domain
        })
        """
        try:
            connector.execute(cypher, org)
            print(f"✓ Created Organization: {org['name']}")
        except Exception as e:
            print(f"✗ Failed to create Organization {org['name']}: {e}")

    # Create Location nodes
    for loc in locations:
        cypher = """
        CREATE (l:Location {
            name: $name,
            description: $description,
            domain: $domain
        })
        """
        try:
            connector.execute(cypher, loc)
            print(f"✓ Created Location: {loc['name']}")
        except Exception as e:
            print(f"✗ Failed to create Location {loc['name']}: {e}")

    # Create Event nodes
    for event in events:
        cypher = """
        CREATE (e:Event {
            name: $name,
            description: $description,
            domain: $domain
        })
        """
        try:
            connector.execute(cypher, event)
            print(f"✓ Created Event: {event['name']}")
        except Exception as e:
            print(f"✗ Failed to create Event {event['name']}: {e}")

    # Create Object nodes
    for obj in objects:
        cypher = """
        CREATE (obj:Object {
            name: $name,
            description: $description,
            domain: $domain
        })
        """
        try:
            connector.execute(cypher, obj)
            print(f"✓ Created Object: {obj['name']}")
        except Exception as e:
            print(f"✗ Failed to create Object {obj['name']}: {e}")


def create_sample_relationships(connector: Neo4jConnector):
    """Create relationships between nodes"""

    relationships = [
        {
            "source": "Alice Johnson",
            "target": "TechCorp",
            "type": "WORKS_AT",
            "description": "Alice works at TechCorp",
        },
        {
            "source": "Bob Smith",
            "target": "TechCorp",
            "type": "WORKS_AT",
            "description": "Bob works at TechCorp",
        },
        {
            "source": "Carol Davis",
            "target": "AI Research Institute",
            "type": "WORKS_AT",
            "description": "Carol works at AI Research Institute",
        },
        {
            "source": "Alice Johnson",
            "target": "San Francisco",
            "type": "LOCATED_IN",
            "description": "Alice is located in San Francisco",
        },
        {
            "source": "Carol Davis",
            "target": "Cambridge",
            "type": "LOCATED_IN",
            "description": "Carol is located in Cambridge",
        },
        {
            "source": "TechCorp",
            "target": "San Francisco",
            "type": "LOCATED_IN",
            "description": "TechCorp is located in San Francisco",
        },
        {
            "source": "Alice Johnson",
            "target": "AI Conference 2024",
            "type": "ATTENDING",
            "description": "Alice is attending AI Conference 2024",
        },
        {
            "source": "Carol Davis",
            "target": "AI Conference 2024",
            "type": "ATTENDING",
            "description": "Carol is attending AI Conference 2024",
        },
        {
            "source": "Alice Johnson",
            "target": "ContextGraph Framework",
            "type": "CREATED",
            "description": "Alice created ContextGraph Framework",
        },
        {
            "source": "Alice Johnson",
            "target": "Bob Smith",
            "type": "KNOWS",
            "description": "Alice knows Bob",
        },
    ]

    for rel in relationships:
        cypher = f"""
        MATCH (a {"{name: $source}"})
        MATCH (b {"{name: $target}"})
        CREATE (a)-[r:{rel['type']} {{description: $description}}]->(b)
        """
        try:
            connector.execute(cypher, {"source": rel["source"], "target": rel["target"], "description": rel["description"]})
            print(f"✓ Created relationship: {rel['source']} -[{rel['type']}]-> {rel['target']}")
        except Exception as e:
            print(f"✗ Failed to create relationship: {e}")


def main():
    print("🚀 Initializing Context Graph Sample Data\n")

    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "password")
    database = os.getenv("NEO4J_DATABASE", "neo4j")

    try:
        connector = Neo4jConnector(uri, user, password, database)
        print(f"✓ Connected to Neo4j at {uri} (database: {database})\n")

        print("📋 Creating schema and constraints...")
        create_sample_ontology_schema(connector)

        print("\n👥 Creating sample nodes...")
        create_sample_nodes(connector)

        print("\n🔗 Creating relationships...")
        create_sample_relationships(connector)

        print("\n📊 Retrieving graph statistics...")
        stats = connector.get_graph_stats()
        print(f"✓ Graph initialized successfully!")
        print(f"  Total nodes: {stats.get('nodes', 'N/A')}")
        print(f"  Total relationships: {stats.get('relationships', 'N/A')}")

        connector.close()

    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nMake sure Neo4j is running:")
        print("  docker run -p 7687:7687 -p 7474:7474 -e NEO4J_AUTH=neo4j/password neo4j:latest")


if __name__ == "__main__":
    main()
