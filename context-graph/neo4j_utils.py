import json
from typing import Optional, Dict, Any, List
from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable
import logging

logger = logging.getLogger(__name__)


class Neo4jConnector:
    def __init__(self, uri: str, user: str, password: str, database: str = "neo4j"):
        self.uri = uri
        self.user = user
        self.password = password
        self.database = database
        self._driver = None
        self._connect()

    def _connect(self):
        try:
            self._driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
            self._driver.verify_connectivity()
            logger.info("Connected to Neo4j database")
        except ServiceUnavailable:
            logger.error("Failed to connect to Neo4j. Ensure the database is running.")
            raise

    def query(self, cypher: str, parameters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        if parameters is None:
            parameters = {}

        with self._driver.session(database=self.database) as session:
            result = session.run(cypher, parameters)
            return [dict(record) for record in result]

    def execute(self, cypher: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if parameters is None:
            parameters = {}

        with self._driver.session(database=self.database) as session:
            result = session.run(cypher, parameters)
            summary = result.consume()
            return {
                "nodes_created": summary.counters.nodes_created,
                "nodes_deleted": summary.counters.nodes_deleted,
                "relationships_created": summary.counters.relationships_created,
                "relationships_deleted": summary.counters.relationships_deleted,
            }

    def get_node_by_name(self, name: str, label: Optional[str] = None) -> Optional[Dict[str, Any]]:
        if label:
            cypher = f"MATCH (n:{label}) WHERE n.name = $name RETURN n LIMIT 1"
        else:
            cypher = "MATCH (n) WHERE n.name = $name RETURN n LIMIT 1"

        results = self.query(cypher, {"name": name})
        return results[0] if results else None

    def get_relationships(self, node_name: str) -> List[Dict[str, Any]]:
        cypher = """
        MATCH (a {name: $name})-[r]->(b)
        RETURN a.name as source, type(r) as relationship, b.name as target
        UNION
        MATCH (a)-[r]->(b {name: $name})
        RETURN a.name as source, type(r) as relationship, b.name as target
        """
        return self.query(cypher, {"name": node_name})

    def search_nodes(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        cypher = """
        MATCH (n)
        WHERE n.name CONTAINS $query OR n.description CONTAINS $query
        RETURN labels(n) as labels, n.name as name, n.description as description
        LIMIT $limit
        """
        return self.query(cypher, {"query": query, "limit": limit})

    def get_graph_stats(self) -> Dict[str, Any]:
        try:
            nodes = self.query("MATCH (n) RETURN count(n) AS nodes")[0]["nodes"]
            relationships = self.query("MATCH ()-[r]->() RETURN count(r) AS relationships")[0]["relationships"]
            label_count = self.query(
                "MATCH (n) UNWIND labels(n) AS label RETURN count(DISTINCT label) AS label_count"
            )[0]["label_count"]
            return {
                "nodes": nodes,
                "relationships": relationships,
                "label_count": label_count,
            }
        except Exception as e:
            logger.error(f"Error getting graph stats: {e}")
            return {"nodes": 0, "relationships": 0, "label_count": 0}

    def close(self):
        if self._driver:
            self._driver.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
