"""
Graph data structure representation for Campus Shortest Path Finder.
Implements a weighted, undirected graph using an Adjacency List.
"""

from typing import Any, Dict, List, Optional, Tuple
from backend.database import get_all_edges, get_all_locations


class CampusGraph:
    """
    Weighted campus graph represented using an adjacency list.
    Supports nodes (campus buildings/landmarks) and weighted bidirectional edges (walkways).
    """

    def __init__(self) -> None:
        # Adjacency list: mapping node_name -> list of (neighbor_name, weight_in_meters)
        self.adj_list: Dict[str, List[Tuple[str, float]]] = {}
        # Node metadata: coordinates, descriptions
        self.node_info: Dict[str, Dict[str, Any]] = {}

    def add_node(self, name: str, description: str = "", x_coord: float = 0.0, y_coord: float = 0.0) -> None:
        """Add a location node if it does not already exist."""
        if name not in self.adj_list:
            self.adj_list[name] = []
            self.node_info[name] = {
                "name": name,
                "description": description,
                "x_coord": x_coord,
                "y_coord": y_coord,
            }

    def add_edge(self, source: str, destination: str, weight: float, bidirectional: bool = True) -> None:
        """
        Add a weighted edge between source and destination.
        Ensure both vertices exist in the graph.
        """
        if source not in self.adj_list:
            self.add_node(source)
        if destination not in self.adj_list:
            self.add_node(destination)

        # Avoid duplicate parallel edges in adjacency list
        if not any(neighbor == destination for neighbor, _ in self.adj_list[source]):
            self.adj_list[source].append((destination, float(weight)))

        if bidirectional:
            if not any(neighbor == source for neighbor, _ in self.adj_list[destination]):
                self.adj_list[destination].append((source, float(weight)))

    def has_node(self, name: str) -> bool:
        """Check whether a location exists in the graph."""
        return name in self.adj_list

    def get_nodes(self) -> List[str]:
        """Return list of all location names sorted alphabetically."""
        return sorted(list(self.adj_list.keys()))

    def get_neighbors(self, node: str) -> List[Tuple[str, float]]:
        """Return list of (neighbor_name, distance_meters) for a given node."""
        return self.adj_list.get(node, [])

    def get_edge_weight(self, u: str, v: str) -> Optional[float]:
        """Return physical distance in metres between u and v if edge exists."""
        for neighbor, weight in self.adj_list.get(u, []):
            if neighbor == v:
                return weight
        return None

    def get_node_info(self, name: str) -> Optional[Dict[str, Any]]:
        """Return metadata for a specific campus location."""
        return self.node_info.get(name)

    def calculate_path_distance(self, path: List[str]) -> float:
        """Calculate total walking distance for a given path sequence."""
        if not path or len(path) <= 1:
            return 0.0
        total = 0.0
        for i in range(len(path) - 1):
            weight = self.get_edge_weight(path[i], path[i + 1])
            if weight is None:
                raise ValueError(f"No direct edge between {path[i]} and {path[i + 1]}")
            total += weight
        return total


def load_graph_from_db(db_path: Optional[str] = None) -> CampusGraph:
    """
    Construct and return a populated CampusGraph from SQLite database.
    Decouples graph data structures from SQLite persistence.
    """
    graph = CampusGraph()

    # Load locations
    locations = get_all_locations(db_path)
    for loc in locations:
        graph.add_node(
            name=loc["name"],
            description=loc.get("description", ""),
            x_coord=loc.get("x_coord", 0.0),
            y_coord=loc.get("y_coord", 0.0),
        )

    # Load pathways
    edges = get_all_edges(db_path)
    for edge in edges:
        graph.add_edge(
            source=edge["source"],
            destination=edge["destination"],
            weight=edge["distance_meters"],
            bidirectional=bool(edge.get("bidirectional", 1)),
        )

    return graph
