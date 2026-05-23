"""
Graph visualization and analysis utilities.
Provides methods for analyzing Neo4j graph structure and creating visualizations.
"""

import json
from typing import Dict, List, Any, Tuple
import networkx as nx
import plotly.graph_objects as go
from neo4j_utils import Neo4jConnector


class GraphAnalyzer:
    def __init__(self, connector: Neo4jConnector):
        self.connector = connector

    def get_subgraph(self, node_name: str, hops: int = 1) -> Dict[str, Any]:
        """Get a subgraph centered on a specific node with specified hops"""
        cypher = """
        MATCH p = (n {name: $name})-[*0..%d]-(m)
        RETURN DISTINCT
            collect(distinct n) as nodes,
            collect(distinct r) as relationships
        """ % (
            hops
        )

        try:
            results = self.connector.query(cypher, {"name": node_name})
            if results:
                return {
                    "nodes": results[0].get("nodes", []),
                    "relationships": results[0].get("relationships", []),
                }
        except Exception as e:
            print(f"Error getting subgraph: {e}")

        return {"nodes": [], "relationships": []}

    def get_connected_nodes(self, node_name: str) -> List[Dict[str, Any]]:
        """Get all directly connected nodes"""
        cypher = """
        MATCH (a {name: $name})-[r]-(b)
        RETURN DISTINCT b.name as name, labels(b) as labels, type(r) as relationship
        """
        return self.connector.query(cypher, {"name": node_name})

    def find_shortest_path(self, source: str, target: str) -> List[Dict[str, Any]]:
        """Find shortest path between two nodes"""
        cypher = """
        MATCH path = shortestPath((a {name: $source})-[*]-(b {name: $target}))
        RETURN
            [n in nodes(path) | n.name] as node_path,
            [r in relationships(path) | type(r)] as rel_types,
            length(path) as path_length
        """
        return self.connector.query(cypher, {"source": source, "target": target})

    def get_graph_density(self) -> float:
        """Calculate graph density"""
        cypher = """
        MATCH (n)
        WITH count(n) as nodes
        MATCH ()--()
        WITH nodes, count(*) as edges
        RETURN edges, nodes, edges / (nodes * (nodes - 1)) as density
        """
        try:
            results = self.connector.query(cypher)
            if results:
                return results[0].get("density", 0)
        except Exception as e:
            print(f"Error calculating density: {e}")
        return 0

    def get_node_degree(self, node_name: str) -> Dict[str, int]:
        """Get in-degree and out-degree of a node"""
        cypher = """
        MATCH (n {name: $name})
        OPTIONAL MATCH (n)-[out]->()
        WITH n, count(out) as out_degree
        OPTIONAL MATCH (()-[in]->(n))
        RETURN out_degree, count(in) as in_degree
        """
        results = self.connector.query(cypher, {"name": node_name})
        if results:
            return {
                "in_degree": results[0].get("in_degree", 0),
                "out_degree": results[0].get("out_degree", 0),
            }
        return {"in_degree": 0, "out_degree": 0}

    def create_plotly_network(self, node_name: str, hops: int = 1) -> go.Figure:
        """Create interactive Plotly network visualization"""
        cypher = f"""
        MATCH (center {{name: $name}})
        OPTIONAL MATCH (center)-[r*0..{hops}]-(neighbor)
        WITH center, collect(distinct neighbor) as neighbors, collect(distinct r) as rels
        WITH [center] + neighbors as all_nodes, rels
        UNWIND all_nodes as node
        OPTIONAL MATCH (node)-[rel]->(other)
        WHERE other in all_nodes
        RETURN
            collect(distinct node.name) as nodes,
            collect({{source: startNode(rel).name, target: endNode(rel).name, type: type(rel)}}) as edges
        """

        try:
            results = self.connector.query(cypher, {"name": node_name})

            if not results or not results[0]["nodes"]:
                return self._empty_figure()

            nodes = results[0]["nodes"]
            edges_data = [e for e in results[0]["edges"] if e["source"] and e["target"]]

            # Create networkx graph
            G = nx.DiGraph()
            G.add_nodes_from(nodes)

            edge_labels = {}
            for edge in edges_data:
                G.add_edge(edge["source"], edge["target"])
                edge_labels[(edge["source"], edge["target"])] = edge["type"]

            # Create layout
            pos = nx.spring_layout(G, k=2, iterations=50, seed=42)

            # Create edge traces
            edge_traces = []
            for edge in G.edges():
                x0, y0 = pos[edge[0]]
                x1, y1 = pos[edge[1]]

                edge_trace = go.Scatter(
                    x=[x0, x1, None],
                    y=[y0, y1, None],
                    mode="lines",
                    line=dict(width=1, color="#888"),
                    hoverinfo="text",
                    text=f"{edge[0]} → {edge[1]}",
                    showlegend=False,
                )
                edge_traces.append(edge_trace)

            # Create node trace
            node_x = []
            node_y = []
            node_labels = []
            node_colors = []

            for node in G.nodes():
                x, y = pos[node]
                node_x.append(x)
                node_y.append(y)
                node_labels.append(node)
                node_colors.append("red" if node == node_name else "lightblue")

            node_trace = go.Scatter(
                x=node_x,
                y=node_y,
                mode="markers+text",
                text=node_labels,
                textposition="top center",
                hoverinfo="text",
                marker=dict(
                    size=20,
                    color=node_colors,
                    line_width=2,
                ),
            )

            # Create figure
            fig = go.Figure(data=edge_traces + [node_trace])

            fig.update_layout(
                title=f"Knowledge Graph around '{node_name}'",
                showlegend=False,
                hovermode="closest",
                margin=dict(b=0, l=0, r=0, t=40),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            )

            return fig

        except Exception as e:
            print(f"Error creating visualization: {e}")
            return self._empty_figure()

    @staticmethod
    def _empty_figure() -> go.Figure:
        """Return empty figure for error cases"""
        fig = go.Figure()
        fig.add_annotation(text="No data found")
        return fig
