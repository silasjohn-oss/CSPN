"""
FastAPI application for Campus Shortest Path Finder.
Provides RESTful endpoints for querying campus graph data, calculating shortest paths,
and running algorithm performance comparisons.
"""

from contextlib import asynccontextmanager
import time
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.algorithms import benchmark_algorithm, bfs, compare_algorithms, dijkstra
from backend.database import get_all_edges, get_all_locations, init_db
from backend.graph import CampusGraph, load_graph_from_db


# Global graph instance in memory
campus_graph: Optional[CampusGraph] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager: Runs on startup and shutdown.
    Ensures SQLite tables exist, seeds sample data, and loads graph into memory.
    """
    global campus_graph
    # 1. Initialize SQLite database & seed if needed
    init_db()
    # 2. Build in-memory graph from database
    campus_graph = load_graph_from_db()
    yield
    # Cleanup on shutdown (if required)


app = FastAPI(
    title="Campus Shortest Path Finder API",
    description="REST API providing graph pathfinding using manual Dijkstra and BFS algorithms.",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS for local frontend development (Vite default: 5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "*",  # Allow all for seamless local development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_active_graph() -> CampusGraph:
    """Helper to ensure graph is ready in memory."""
    global campus_graph
    if campus_graph is None:
        init_db()
        campus_graph = load_graph_from_db()
    return campus_graph


@app.get("/", tags=["Status"])
def get_root_status() -> Dict[str, Any]:
    """Root health and status endpoint."""
    graph = get_active_graph()
    return {
        "status": "online",
        "service": "Campus Shortest Path Finder API",
        "version": "1.0.0",
        "locations_count": len(graph.get_nodes()),
        "notice": "All campus pathway distances are illustrative sample data for academic demonstration.",
    }


@app.get("/api/locations", tags=["Campus Data"])
def list_locations() -> Dict[str, Any]:
    """
    Return all campus locations with coordinates and descriptions from SQLite.
    Used by frontend for dropdown menus and map nodes.
    """
    locations = get_all_locations()
    return {
        "status": "success",
        "count": len(locations),
        "locations": locations,
    }


@app.get("/api/edges", tags=["Campus Data"])
def list_edges() -> Dict[str, Any]:
    """
    Return all campus pathways, distances (metres), and bidirectional status.
    Used by frontend for drawing the graph network.
    """
    edges = get_all_edges()
    return {
        "status": "success",
        "count": len(edges),
        "edges": edges,
    }


@app.get("/api/route", tags=["Navigation"])
def calculate_route(
    source: str = Query(..., description="Starting campus location name"),
    destination: str = Query(..., description="Target campus destination name"),
    algorithm: str = Query("dijkstra", description="Pathfinding algorithm: 'dijkstra' or 'bfs'"),
) -> Dict[str, Any]:
    """
    Find navigation route between source and destination using Dijkstra or BFS.
    """
    graph = get_active_graph()
    algo = algorithm.strip().lower()

    # Input validation
    if not graph.has_node(source):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown source location: '{source}'. Please select a valid campus building.",
        )
    if not graph.has_node(destination):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown destination location: '{destination}'. Please select a valid campus building.",
        )

    if algo == "dijkstra":
        target_fn = dijkstra
    elif algo == "bfs":
        target_fn = bfs
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported algorithm '{algorithm}'. Must be 'dijkstra' or 'bfs'.",
        )

    # Execute algorithm
    try:
        result = target_fn(graph, source, destination)
        # Measure in-memory execution time (ms)
        exec_time_ms = benchmark_algorithm(target_fn, graph, source, destination, iterations=50)
        result["execution_time_ms"] = exec_time_ms
        return {
            "status": "success",
            "source": source,
            "destination": destination,
            "algorithm": algo,
            "result": result,
        }
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Pathfinding calculation error: {str(exc)}",
        )


@app.get("/api/compare", tags=["Performance Analysis"])
def compare_route_algorithms(
    source: str = Query(..., description="Starting campus location name"),
    destination: str = Query(..., description="Target campus destination name"),
    iterations: int = Query(50, description="Benchmark timing iterations", ge=10, le=1000),
) -> Dict[str, Any]:
    """
    Compare Dijkstra and BFS side-by-side for the identical route.
    Returns physical distance, edge count, and averaged timing benchmarks.
    """
    graph = get_active_graph()

    if not graph.has_node(source):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown source location: '{source}'.",
        )
    if not graph.has_node(destination):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown destination location: '{destination}'.",
        )

    try:
        comparison = compare_algorithms(graph, source, destination, iterations=iterations)
        return {
            "status": "success",
            "comparison": comparison,
        }
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Comparison calculation error: {str(exc)}",
        )
