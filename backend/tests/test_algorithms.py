"""
Comprehensive unit and integration test suite for Campus Shortest Path Finder:
- Dijkstra algorithm correctness (Main Gate -> Hostel = 540m)
- BFS algorithm correctness (Main Gate -> Hostel = 2 edges, 550m)
- Boundary cases: identical endpoints, unreachable nodes, invalid inputs
- Database initialization and duplicate-free re-seeding
- REST API endpoint verification with FastAPI TestClient
"""

import os
import tempfile
import pytest
from fastapi.testclient import TestClient

from backend.algorithms import bfs, compare_algorithms, dijkstra
from backend.database import (
    SAMPLE_EDGES,
    SAMPLE_LOCATIONS,
    get_all_edges,
    get_all_locations,
    init_db,
)
from backend.graph import CampusGraph, load_graph_from_db
from backend.main import app


@pytest.fixture
def sample_graph():
    """Build in-memory graph matching sample campus specifications."""
    g = CampusGraph()
    for loc in SAMPLE_LOCATIONS:
        g.add_node(loc["name"], loc["description"], loc["x_coord"], loc["y_coord"])
    for edge in SAMPLE_EDGES:
        g.add_edge(edge["source"], edge["destination"], edge["distance_meters"], bidirectional=True)
    return g


# ==============================================================================
# ALGORITHM UNIT TESTS
# ==============================================================================

def test_dijkstra_minimum_distance_main_gate_to_hostel(sample_graph):
    """
    Requirement 9: Dijkstra returns the expected minimum distance from Main Gate to Hostel: 540 metres.
    Path: Main Gate (120) -> Administration (100) -> Academic Block (140) -> Laboratory (180) -> Hostel = 540m.
    """
    res = dijkstra(sample_graph, "Main Gate", "Hostel")
    assert res["found"] is True
    assert res["total_distance"] == 540.0
    assert res["edge_count"] == 4
    assert res["path"] == ["Main Gate", "Administration", "Academic Block", "Laboratory", "Hostel"]
    assert res["path"][0] == "Main Gate"
    assert res["path"][-1] == "Hostel"


def test_bfs_route_and_edge_minimization(sample_graph):
    """
    Requirement 9: BFS finds a valid route using the fewest number of edges.
    Main Gate -> Library (250) -> Hostel (300) = 2 edges, 550m.
    Demonstrates BFS finds 2 edges (550m) whereas Dijkstra finds 4 edges (540m).
    """
    res = bfs(sample_graph, "Main Gate", "Hostel")
    assert res["found"] is True
    assert res["edge_count"] == 2
    assert res["total_distance"] == 550.0
    assert res["path"] == ["Main Gate", "Library", "Hostel"]
    assert res["path"][0] == "Main Gate"
    assert res["path"][-1] == "Hostel"


def test_identical_source_and_destination(sample_graph):
    """
    Requirement 9: Handle identical source and destination cleanly.
    """
    for algo in [dijkstra, bfs]:
        res = algo(sample_graph, "Academic Block", "Academic Block")
        assert res["found"] is True
        assert res["total_distance"] == 0.0
        assert res["edge_count"] == 0
        assert res["path"] == ["Academic Block"]


def test_invalid_locations_raise_error(sample_graph):
    """
    Requirement 9: Validate invalid source or destination inputs.
    """
    with pytest.raises(ValueError, match="Source location 'Clock Tower' does not exist"):
        dijkstra(sample_graph, "Clock Tower", "Hostel")

    with pytest.raises(ValueError, match="Destination location 'Swimming Pool' does not exist"):
        bfs(sample_graph, "Main Gate", "Swimming Pool")


def test_unreachable_destination(sample_graph):
    """
    Requirement 9: Handle disconnected / unreachable graph components.
    """
    # Add an isolated node with no incoming/outgoing edges
    sample_graph.add_node("Sports Complex")

    res_dijkstra = dijkstra(sample_graph, "Main Gate", "Sports Complex")
    assert res_dijkstra["found"] is False
    assert res_dijkstra["path"] == []
    assert res_dijkstra["total_distance"] == float("inf")

    res_bfs = bfs(sample_graph, "Main Gate", "Sports Complex")
    assert res_bfs["found"] is False
    assert res_bfs["path"] == []
    assert res_bfs["total_distance"] == float("inf")


def test_compare_algorithms_output(sample_graph):
    """
    Requirement 8: Verify side-by-side comparison produces expected trade-offs and timing metrics.
    """
    comp = compare_algorithms(sample_graph, "Main Gate", "Hostel", iterations=10)
    assert comp["source"] == "Main Gate"
    assert comp["destination"] == "Hostel"
    assert comp["dijkstra"]["total_distance"] == 540.0
    assert comp["bfs"]["total_distance"] == 550.0
    assert comp["distance_difference_meters"] == 10.0
    assert comp["edge_difference"] == -2  # BFS has 2 edges, Dijkstra has 4 (-2)
    assert "execution_time_ms" in comp["dijkstra"]
    assert "execution_time_ms" in comp["bfs"]
    assert comp["dijkstra"]["execution_time_ms"] >= 0.0


# ==============================================================================
# DATABASE INITIALIZATION & DUPLICATION TESTS
# ==============================================================================

def test_database_init_and_no_duplicates():
    """
    Requirement 6 & 9: Database initialization and duplicate-free re-seeding.
    """
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        temp_db_path = tmp.name
    # Close immediately on Windows so other processes can access
    tmp.close()

    try:
        # First initialization
        init_db(temp_db_path)
        locs_first = get_all_locations(temp_db_path)
        edges_first = get_all_edges(temp_db_path)

        assert len(locs_first) == len(SAMPLE_LOCATIONS)
        assert len(edges_first) == len(SAMPLE_EDGES)

        # Second initialization (simulating multiple backend restarts)
        init_db(temp_db_path)
        locs_second = get_all_locations(temp_db_path)
        edges_second = get_all_edges(temp_db_path)

        # Ensure no duplicates were added
        assert len(locs_second) == len(SAMPLE_LOCATIONS)
        assert len(edges_second) == len(SAMPLE_EDGES)

        # Load graph from test DB
        graph = load_graph_from_db(temp_db_path)
        assert len(graph.get_nodes()) == len(SAMPLE_LOCATIONS)
    finally:
        if os.path.exists(temp_db_path):
            try:
                os.remove(temp_db_path)
            except OSError:
                pass


# ==============================================================================
# FASTAPI API INTEGRATION TESTS
# ==============================================================================

@pytest.fixture(scope="module")
def api_client():
    """FastAPI TestClient with lifespan triggered."""
    with TestClient(app) as client:
        yield client


def test_api_status_endpoint(api_client):
    """GET / -> Check status online and metadata."""
    response = api_client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert data["locations_count"] == 6


def test_api_locations_endpoint(api_client):
    """GET /api/locations -> Returns list of campus locations."""
    response = api_client.get("/api/locations")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["count"] == 6
    names = [loc["name"] for loc in data["locations"]]
    assert "Main Gate" in names
    assert "Hostel" in names


def test_api_edges_endpoint(api_client):
    """GET /api/edges -> Returns pathways with distances."""
    response = api_client.get("/api/edges")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["count"] == 8


def test_api_dijkstra_route(api_client):
    """GET /api/route with algorithm=dijkstra."""
    response = api_client.get("/api/route?source=Main%20Gate&destination=Hostel&algorithm=dijkstra")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["result"]["total_distance"] == 540.0
    assert data["result"]["edge_count"] == 4
    assert data["result"]["path"] == ["Main Gate", "Administration", "Academic Block", "Laboratory", "Hostel"]


def test_api_bfs_route(api_client):
    """GET /api/route with algorithm=bfs."""
    response = api_client.get("/api/route?source=Main%20Gate&destination=Hostel&algorithm=bfs")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["result"]["total_distance"] == 550.0
    assert data["result"]["edge_count"] == 2
    assert data["result"]["path"] == ["Main Gate", "Library", "Hostel"]


def test_api_invalid_location_400(api_client):
    """GET /api/route with unknown location returns 400 Bad Request."""
    response = api_client.get("/api/route?source=UnknownPlace&destination=Hostel&algorithm=dijkstra")
    assert response.status_code == 400
    assert "Unknown source location" in response.json()["detail"]


def test_api_invalid_algorithm_400(api_client):
    """GET /api/route with invalid algorithm parameter returns 400 Bad Request."""
    response = api_client.get("/api/route?source=Main%20Gate&destination=Hostel&algorithm=floyd_warshall")
    assert response.status_code == 400
    assert "Unsupported algorithm" in response.json()["detail"]


def test_api_compare_endpoint(api_client):
    """GET /api/compare returns side-by-side comparison metrics."""
    response = api_client.get("/api/compare?source=Main%20Gate&destination=Hostel&iterations=20")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    comp = data["comparison"]
    assert comp["dijkstra"]["total_distance"] == 540.0
    assert comp["bfs"]["total_distance"] == 550.0
    assert comp["distance_difference_meters"] == 10.0
