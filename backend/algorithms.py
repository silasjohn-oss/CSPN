"""
Manual algorithm implementations for Campus Navigation:
1. Dijkstra's Algorithm (Priority Queue / Min-Heap) - finds path minimizing physical distance (metres).
2. Breadth-First Search (FIFO Queue) - finds path minimizing edge count (hops/turns).
3. Performance comparison utility with timing benchmarks using time.perf_counter().

NO third-party graph algorithms used.
"""

from collections import deque
import heapq
import time
from typing import Any, Dict, List, Optional
from backend.graph import CampusGraph


def dijkstra(graph: CampusGraph, source: str, destination: str) -> Dict[str, Any]:
    """
    Dijkstra's Algorithm implemented manually using a binary min-heap (heapq).
    Optimizes for: Minimum total physical walking distance (metres).

    Time Complexity: O((V + E) log V) with adjacency list and binary heap.
    Space Complexity: O(V) for distances and predecessor lookup tables.

    Returns:
        Dict containing:
            - algorithm: "dijkstra"
            - found: bool
            - path: List[str] ordered building names
            - total_distance: float in metres
            - edge_count: int
            - visited_nodes: List[str] exploration sequence
            - description: Explanation of algorithm result
    """
    if not graph.has_node(source):
        raise ValueError(f"Source location '{source}' does not exist on campus.")
    if not graph.has_node(destination):
        raise ValueError(f"Destination location '{destination}' does not exist on campus.")

    # Edge Case: Source is destination
    if source == destination:
        return {
            "algorithm": "dijkstra",
            "found": True,
            "path": [source],
            "total_distance": 0.0,
            "edge_count": 0,
            "visited_nodes": [source],
            "description": "Source and destination are the exact same campus location.",
        }

    # Min-heap priority queue storing tuples: (distance_from_source, current_node)
    pq: List[tuple[float, str]] = []
    heapq.heappush(pq, (0.0, source))

    # Distance tracker initialized to infinity
    distances: Dict[str, float] = {node: float("inf") for node in graph.get_nodes()}
    distances[source] = 0.0

    # Predecessor mapping to reconstruct shortest path
    predecessors: Dict[str, Optional[str]] = {node: None for node in graph.get_nodes()}

    visited_nodes: List[str] = []
    settled: set[str] = set()

    while pq:
        current_dist, current_node = heapq.heappop(pq)

        if current_node in settled:
            continue
        settled.add(current_node)
        visited_nodes.append(current_node)

        # Early termination once target destination has been settled with optimal distance
        if current_node == destination:
            break

        for neighbor, weight in graph.get_neighbors(current_node):
            if neighbor in settled:
                continue

            new_dist = current_dist + weight
            if new_dist < distances[neighbor]:
                distances[neighbor] = new_dist
                predecessors[neighbor] = current_node
                heapq.heappush(pq, (new_dist, neighbor))

    # Check if destination was reached
    if distances[destination] == float("inf"):
        return {
            "algorithm": "dijkstra",
            "found": False,
            "path": [],
            "total_distance": float("inf"),
            "edge_count": 0,
            "visited_nodes": visited_nodes,
            "description": f"No accessible pathway exists from '{source}' to '{destination}'.",
        }

    # Reconstruct shortest path by backtracking predecessors
    path: List[str] = []
    curr: Optional[str] = destination
    while curr is not None:
        path.append(curr)
        curr = predecessors.get(curr)
    path.reverse()

    return {
        "algorithm": "dijkstra",
        "found": True,
        "path": path,
        "total_distance": round(distances[destination], 2),
        "edge_count": len(path) - 1,
        "visited_nodes": visited_nodes,
        "description": "Dijkstra's algorithm guarantees the route with the minimum cumulative walking distance (metres).",
    }


def bfs(graph: CampusGraph, source: str, destination: str) -> Dict[str, Any]:
    """
    Breadth-First Search (BFS) algorithm implemented manually using a FIFO queue (deque).
    Optimizes for: Fewest number of pathways/edges (hops/intersections).

    Time Complexity: O(V + E) with adjacency list.
    Space Complexity: O(V) for queue and visited set.

    Note:
        BFS explores layer-by-layer uniformly. In a weighted graph, minimizing edge count
        does NOT guarantee minimum physical walking distance.

    Returns:
        Dict containing:
            - algorithm: "bfs"
            - found: bool
            - path: List[str] ordered building names
            - total_distance: float in metres
            - edge_count: int
            - visited_nodes: List[str] exploration sequence
            - description: Explanation of algorithm result
    """
    if not graph.has_node(source):
        raise ValueError(f"Source location '{source}' does not exist on campus.")
    if not graph.has_node(destination):
        raise ValueError(f"Destination location '{destination}' does not exist on campus.")

    # Edge Case: Source is destination
    if source == destination:
        return {
            "algorithm": "bfs",
            "found": True,
            "path": [source],
            "total_distance": 0.0,
            "edge_count": 0,
            "visited_nodes": [source],
            "description": "Source and destination are the exact same campus location.",
        }

    # Standard FIFO Queue for BFS
    queue: deque[str] = deque([source])
    visited: set[str] = {source}
    predecessors: Dict[str, Optional[str]] = {source: None}
    visited_nodes: List[str] = []

    destination_found = False

    while queue:
        current_node = queue.popleft()
        visited_nodes.append(current_node)

        if current_node == destination:
            destination_found = True
            break

        for neighbor, _ in graph.get_neighbors(current_node):
            if neighbor not in visited:
                visited.add(neighbor)
                predecessors[neighbor] = current_node
                queue.append(neighbor)

    if not destination_found:
        return {
            "algorithm": "bfs",
            "found": False,
            "path": [],
            "total_distance": float("inf"),
            "edge_count": 0,
            "visited_nodes": visited_nodes,
            "description": f"No accessible pathway exists from '{source}' to '{destination}'.",
        }

    # Reconstruct path by backtracking
    path: List[str] = []
    curr: Optional[str] = destination
    while curr is not None:
        path.append(curr)
        curr = predecessors.get(curr)
    path.reverse()

    # Calculate actual physical distance of the BFS route
    total_distance = graph.calculate_path_distance(path)

    return {
        "algorithm": "bfs",
        "found": True,
        "path": path,
        "total_distance": round(total_distance, 2),
        "edge_count": len(path) - 1,
        "visited_nodes": visited_nodes,
        "description": "BFS explores layer-by-layer to find the route with the fewest connections (edges), ignoring edge weights.",
    }


def benchmark_algorithm(func, graph: CampusGraph, source: str, destination: str, iterations: int = 50) -> float:
    """
    Measure algorithm-only execution time using time.perf_counter().
    Averages over multiple runs to eliminate CPU scheduling noise.
    Excludes database access, graph construction, and network I/O.
    Returns average execution time in milliseconds.
    """
    # Warm up run
    func(graph, source, destination)

    start = time.perf_counter()
    for _ in range(iterations):
        func(graph, source, destination)
    end = time.perf_counter()

    avg_seconds = (end - start) / iterations
    return round(avg_seconds * 1000.0, 4)  # Convert to milliseconds


def compare_algorithms(graph: CampusGraph, source: str, destination: str, iterations: int = 50) -> Dict[str, Any]:
    """
    Execute both Dijkstra and BFS on identical inputs and compare outcomes:
    - Route taken
    - Total physical distance
    - Edge count
    - Average execution time (ms)
    - Educational analysis comparing edge-optimal vs distance-optimal tradeoffs
    """
    # Run algorithms for path results
    dijkstra_result = dijkstra(graph, source, destination)
    bfs_result = bfs(graph, source, destination)

    # Benchmark algorithm-only execution times
    dijkstra_time_ms = benchmark_algorithm(dijkstra, graph, source, destination, iterations)
    bfs_time_ms = benchmark_algorithm(bfs, graph, source, destination, iterations)

    dijkstra_result["execution_time_ms"] = dijkstra_time_ms
    bfs_result["execution_time_ms"] = bfs_time_ms

    # Construct analytical comparison commentary
    distance_diff = round(bfs_result["total_distance"] - dijkstra_result["total_distance"], 2)
    edge_diff = bfs_result["edge_count"] - dijkstra_result["edge_count"]

    if distance_diff > 0:
        pedagogical_insight = (
            f"Dijkstra found a route that is {distance_diff}m shorter than BFS. "
            f"Although BFS used {abs(edge_diff)} fewer pathway(s), each pathway was physically longer. "
            "This highlights why unweighted BFS is insufficient for physical navigation."
        )
    elif distance_diff == 0 and edge_diff == 0:
        pedagogical_insight = "Both algorithms identified identical paths in terms of distance and edge count."
    else:
        pedagogical_insight = "Both algorithms produced valid routes under their respective objective functions."

    return {
        "source": source,
        "destination": destination,
        "iterations": iterations,
        "dijkstra": dijkstra_result,
        "bfs": bfs_result,
        "distance_difference_meters": distance_diff,
        "edge_difference": edge_diff,
        "pedagogical_insight": pedagogical_insight,
        "timing_disclaimer": "Execution times are measured in-memory using time.perf_counter() averaged over multiple runs. Very short microsecond measurements naturally fluctuate with operating system thread scheduling.",
    }
