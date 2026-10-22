# Shortest Path Finder for Campus Navigation Using Graph Algorithms

An academic full-stack college microproject demonstrating graph data structures and pathfinding algorithms for campus navigation. This project compares **Dijkstra's Algorithm** (shortest physical walking distance) with **Breadth-First Search (BFS)** (fewest edge crossings / turns) on a weighted graph, backed by a FastAPI REST backend, SQLite database, and an interactive React + Vite frontend.

> **Notice:** All campus pathways, distances, and building coordinates used in this project are illustrative sample measurements designed for academic demonstrations and algorithm visualization.

---

## Table of Contents
1. [Project Objective](#1-project-objective)
2. [Problem Statement](#2-problem-statement)
3. [Key Features](#3-key-features)
4. [Technology Stack](#4-technology-stack)
5. [Folder Structure](#5-folder-structure)
6. [Campus Graph Representation](#6-campus-graph-representation)
7. [Algorithm Explanations & Complexity](#7-algorithm-explanations--complexity)
8. [Database Schema](#8-database-schema)
9. [REST API Endpoints & Examples](#9-rest-api-endpoints--examples)
10. [Setup & Installation Instructions (Windows PowerShell)](#10-setup--installation-instructions-windows-powershell)
11. [Running Backend and Frontend](#11-running-backend-and-frontend)
12. [Running Automated Tests](#12-running-automated-tests)
13. [Sample Expected Output](#13-sample-expected-output)
14. [Performance Analysis](#14-performance-analysis)
15. [Course Outcome (CO) Mapping](#15-course-outcome-co-mapping)
16. [Limitations & Future Enhancements](#16-limitations--future-enhancements)

---

## 1. Project Objective
To model a university campus as a weighted, undirected graph and evaluate the trade-offs between unweighted layer-by-layer traversal (Breadth-First Search) and greedy priority-queue-driven traversal (Dijkstra's Algorithm) for navigating between campus buildings.

---

## 2. Problem Statement
Navigating a large academic campus poses different optimization problems depending on user criteria:
1. **Distance Minimization:** Pedestrians wish to walk the least total distance (metres), requiring edge-weighted pathfinding.
2. **Turn / Complexity Minimization:** Visitors unfamiliar with campus may prefer the simplest route with the fewest corridor transitions or pathway intersections (edges), irrespective of physical walking length.

Standard unweighted graph algorithms such as Breadth-First Search (BFS) treat each pathway as equal cost (1 hop), which frequently yields suboptimal physical walking distances. This project solves, visualizes, and contrasts both techniques from first principles.

---

## 3. Key Features
- **Manual Algorithm Implementation:** Pure Python implementations of Dijkstra's Algorithm (with `heapq`) and BFS (with `collections.deque`) without third-party pathfinding libraries (no NetworkX).
- **Interactive SVG Campus Map:** Dynamic visual graph displaying buildings as nodes and pathways as edges, complete with distance labels, route highlighting, and pulse animations.
- **Side-by-Side Algorithm Comparison:** Direct benchmarking showing route path, physical distance, edge count, and averaged in-memory execution time (ms).
- **SQLite Persistence:** Automatic database creation and duplicate-free data seeding on initial backend launch.
- **RESTful FastAPI Service:** Clean endpoints with CORS middleware, rigorous query validation, and descriptive HTTP error responses.
- **Educational Course Outcome Viewer:** Integrated modal mapping project concepts to ABET / NBA Data Structures and Algorithms outcomes.

---

## 4. Technology Stack

| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **Frontend** | React 18, Vite, JavaScript, CSS3 | Single-page responsive UI and interactive SVG graph canvas |
| **Backend** | Python 3.12+, FastAPI, Uvicorn | REST API, algorithm execution, and performance benchmarking |
| **Database** | SQLite (`sqlite3`) | Persistent storage of campus locations and weighted pathways |
| **Testing** | Pytest, FastAPI TestClient (`httpx`) | Unit testing of algorithms, database idempotency, and API endpoints |
| **Data Structures** | Adjacency List, Min-Heap (`heapq`), FIFO Queue (`deque`), Hash Maps | Efficient in-memory graph representation and traversal |

---

## 5. Folder Structure

```text
campus-shortest-path/
├── backend/
│   ├── main.py                  # FastAPI application routes & CORS configuration
│   ├── graph.py                 # CampusGraph class (Adjacency List) & DB loader
│   ├── algorithms.py            # Manual Dijkstra, BFS, and benchmark functions
│   ├── database.py              # SQLite connection, schema creation, & idempotent seeding
│   ├── requirements.txt         # Python dependencies
│   └── tests/
│       └── test_algorithms.py   # Pytest suite (algorithms, database, API)
├── frontend/
│   ├── src/
│   │   ├── App.jsx              # Main React dashboard & SVG visualization
│   │   ├── App.css              # Custom design system with glassmorphism & dark theme
│   │   └── main.jsx             # React entry point
│   ├── index.html               # HTML document with Google Fonts (Outfit, Plus Jakarta)
│   ├── package.json             # Frontend dependencies & scripts
│   └── vite.config.js           # Vite development server configuration
├── data/
│   └── campus.db                # SQLite database file (created automatically)
├── README.md                    # Project documentation & course outcome mapping
└── .gitignore                   # Version control exclusions
```

---

## 6. Campus Graph Representation

The campus is modeled as a **weighted, undirected graph** $G = (V, E)$, represented in Python as an **Adjacency List** using a hash table (`dict`):

$$\text{adj\_list}[u] = [(v_1, w_1), (v_2, w_2), \dots]$$

### Illustrative Graph Data:

```
                  Administration (120m) ──── 100m ──── Academic Block
                  /          \                            /       \
              120m            160m                     90m         140m
              /                  \                     /             \
      [Main Gate] ──────── 250m ──────── [Library]                [Laboratory]
                                            \                         /
                                            300m                   180m
                                              \                     /
                                                ──── [Hostel] ─────
```

### Edge Weights (Sample Distances in Metres):
- **Main Gate ↔ Administration:** 120 m
- **Main Gate ↔ Library:** 250 m
- **Administration ↔ Academic Block:** 100 m
- **Administration ↔ Library:** 160 m
- **Library ↔ Academic Block:** 90 m
- **Library ↔ Hostel:** 300 m
- **Academic Block ↔ Laboratory:** 140 m
- **Laboratory ↔ Hostel:** 180 m

---

## 7. Algorithm Explanations & Complexity

### A. Dijkstra's Algorithm (Weighted Shortest Path)
- **Objective:** Find the route that minimizes the cumulative physical walking distance (metres).
- **Data Structures:** 
  - Binary Min-Heap (`heapq`): Stores `(tentative_distance, node)` pairs, allowing $O(\log V)$ extraction of the minimum-distance unvisited vertex.
  - Distances Dictionary (`dict`): Tracks the current shortest known distance from the source vertex.
  - Predecessor Dictionary (`dict`): Stores the back-pointer for each node to reconstruct the path.
- **Time Complexity:** $O((V + E) \log V)$ using an adjacency list and binary heap.
- **Space Complexity:** $O(V)$ for the heap, distance map, and predecessor map.
- **Main Gate → Hostel Result:**
  - Route: `Main Gate → Administration → Academic Block → Laboratory → Hostel`
  - Total Distance: **540 metres** (4 edges)

### B. Breadth-First Search (BFS) (Unweighted Fewest-Hop Path)
- **Objective:** Find the route containing the fewest number of edges (hops / intersections).
- **Data Structures:**
  - FIFO Queue (`collections.deque`): Explores vertices level-by-level in order of distance in edges.
  - Visited Set (`set`): Tracks settled nodes to prevent infinite cycling in cyclic graphs.
  - Predecessor Dictionary (`dict`): Stores back-pointers.
- **Time Complexity:** $O(V + E)$ using an adjacency list.
- **Space Complexity:** $O(V)$ for the queue and visited set.
- **Main Gate → Hostel Result:**
  - Route: `Main Gate → Library → Hostel`
  - Total Distance: **550 metres** (2 edges)

### Educational Comparison:
Notice that BFS discovers a 2-edge route (`Main Gate → Library → Hostel`) whose distance is **550m**, whereas Dijkstra discovers a 4-edge route (`Main Gate → Administration → Academic Block → Laboratory → Hostel`) whose distance is **540m** (10m shorter!). This illustrates that **BFS optimizes for fewest edges, not lowest cumulative edge weight**.

---

## 8. Database Schema

Stored in `data/campus.db` via SQLite:

### Table: `locations`
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique location identifier |
| `name` | TEXT | UNIQUE NOT NULL | Campus building name |
| `description` | TEXT | | Brief functional description |
| `x_coord` | REAL | DEFAULT 0.0 | SVG 2D X-coordinate for visualization |
| `y_coord` | REAL | DEFAULT 0.0 | SVG 2D Y-coordinate for visualization |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Record creation timestamp |

### Table: `edges`
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique pathway identifier |
| `source` | TEXT | NOT NULL | Starting building name |
| `destination` | TEXT | NOT NULL | Ending building name |
| `distance_meters` | REAL | NOT NULL | Physical distance in metres |
| `bidirectional` | INTEGER | DEFAULT 1 | 1 = walkable both directions |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Record creation timestamp |

*Seeding is idempotent (`INSERT OR IGNORE` and row count checks) to guarantee no duplicate records are generated upon multiple server restarts.*

---

## 9. REST API Endpoints & Examples

Base URL: `http://127.0.0.1:8000`

### 1. `GET /`
Returns service status, version, and location count.
```bash
curl -X GET "http://127.0.0.1:8000/"
```
**Response:**
```json
{
  "status": "online",
  "service": "Campus Shortest Path Finder API",
  "version": "1.0.0",
  "locations_count": 6,
  "notice": "All campus pathway distances are illustrative sample data for academic demonstration."
}
```

### 2. `GET /api/locations`
Returns all registered campus buildings with coordinates.
```bash
curl -X GET "http://127.0.0.1:8000/api/locations"
```

### 3. `GET /api/edges`
Returns all walkable pathways with distances.
```bash
curl -X GET "http://127.0.0.1:8000/api/edges"
```

### 4. `GET /api/route`
Computes the route between two locations using either `dijkstra` or `bfs`.
```bash
curl -X GET "http://127.0.0.1:8000/api/route?source=Main%20Gate&destination=Hostel&algorithm=dijkstra"
```
**Response:**
```json
{
  "status": "success",
  "source": "Main Gate",
  "destination": "Hostel",
  "algorithm": "dijkstra",
  "result": {
    "algorithm": "dijkstra",
    "found": true,
    "path": ["Main Gate", "Administration", "Academic Block", "Laboratory", "Hostel"],
    "total_distance": 540.0,
    "edge_count": 4,
    "visited_nodes": ["Main Gate", "Administration", "Library", "Academic Block", "Laboratory", "Hostel"],
    "description": "Dijkstra's algorithm guarantees the route with the minimum cumulative walking distance (metres).",
    "execution_time_ms": 0.045
  }
}
```

### 5. `GET /api/compare`
Executes both algorithms concurrently and reports comparative metrics.
```bash
curl -X GET "http://127.0.0.1:8000/api/compare?source=Main%20Gate&destination=Hostel&iterations=50"
```

---

## 10. Setup & Installation Instructions (Windows PowerShell)

### Prerequisites:
- Python 3.10+ (Check with `python --version`)
- Node.js v18+ and npm (Check with `node --version` and `npm --version`)

### Step 1: Open Windows PowerShell in the project directory
```powershell
# Open terminal in project root
Set-Location "C:\Users\<USERNAME>\Desktop\CSPN"
```

### Step 2: Install Backend Dependencies
```powershell
python -m pip install -r backend/requirements.txt
```

### Step 3: Install Frontend Dependencies
```powershell
npm --prefix frontend install
```

---

## 11. Running Backend and Frontend

### Terminal 1: Start the FastAPI Backend
```powershell
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```
- API Docs (Swagger UI): [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- API Health Status: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

### Terminal 2: Start the React Frontend
```powershell
npm --prefix frontend run dev
```
- Frontend Application URL: [http://localhost:5173](http://localhost:5173)

---

## 12. Running Automated Tests

A comprehensive 15-test automated test suite is provided in `backend/tests/test_algorithms.py`.

Run tests with verbose output:
```powershell
python -m pytest backend/tests/test_algorithms.py -v
```

### Test Suite Coverage:
- `test_dijkstra_minimum_distance_main_gate_to_hostel`: Verifies exact minimum distance of 540.0m.
- `test_bfs_route_and_edge_minimization`: Verifies BFS finds 2-edge route (550.0m).
- `test_identical_source_and_destination`: Tests identical endpoint handling (distance: 0m, 0 edges).
- `test_invalid_locations_raise_error`: Tests rejection of unknown campus buildings.
- `test_unreachable_destination`: Verifies disconnected graph handling.
- `test_compare_algorithms_output`: Verifies side-by-side comparison structure and timing metrics.
- `test_database_init_and_no_duplicates`: Validates SQLite idempotent creation across repeated startups.
- `test_api_*`: Validates all FastAPI endpoints (`/`, `/api/locations`, `/api/edges`, `/api/route`, `/api/compare`, and 400 error handlers).

---

## 13. Sample Expected Output

When running Dijkstra from **Main Gate** to **Hostel**:
```text
Algorithm: Dijkstra's Algorithm
Total Distance: 540.0 m
Edge Count: 4
Turn-by-turn Route:
  1. Main Gate
  2. Administration (120 m)
  3. Academic Block (100 m)
  4. Laboratory (140 m)
  5. Hostel (180 m)
Execution Time: ~0.04 ms
```

When running BFS from **Main Gate** to **Hostel**:
```text
Algorithm: Breadth-First Search (BFS)
Total Distance: 550.0 m
Edge Count: 2
Turn-by-turn Route:
  1. Main Gate
  2. Library (250 m)
  3. Hostel (300 m)
Execution Time: ~0.03 ms
```

---

## 14. Performance Analysis

Algorithm execution time is measured in-memory using Python's high-resolution timer `time.perf_counter()`. 

- **Methodology:** The backend executes the pathfinding function over 50 iterations and calculates the arithmetic mean in milliseconds.
- **Isolation:** Measurements exclude database disk I/O, graph construction overhead, JSON serialization, and network latency.
- **Caveat on Sub-Millisecond Timing:** For small campus graphs ($V=6, E=8$), execution times fall in the microsecond range (typically 0.02 ms to 0.08 ms). Microscopic measurements fluctuate with operating system thread scheduling, CPU frequency scaling, and background processes. A single timing snapshot is not a statistically rigorous benchmark; repeated averages provide a fair comparative indicator.

---

## 15. Course Outcome (CO) Mapping

This project directly aligns with Data Structures and Algorithms (DSA) engineering course outcomes:

### CO1: Develop efficient solutions using stack and/or queue data structures.
- **Relevance:** BFS employs a **FIFO queue** (`collections.deque`) to explore graph levels in sequential depth order. Vertices at depth $d$ are completely dequeued and evaluated before vertices at depth $d+1$ are processed, ensuring the path with the fewest edges is discovered.

### CO2: Evaluate suitability of data structures for efficient storage and retrieval.
- **Relevance:** 
  - **Adjacency List vs. Adjacency Matrix:** Storing $V=6$ buildings with $E=8$ pathways requires $O(V + E)$ space in an adjacency list rather than $O(V^2)$ in an adjacency matrix.
  - **Binary Heap (`heapq`):** Enables $O(\log V)$ priority queue extraction of the minimum distance vertex in Dijkstra's algorithm, vastly outperforming an unsorted array ($O(V)$ per extraction).
  - **Hash Maps (`dict`):** Provide $O(1)$ average-time vertex coordinate and metadata lookups.

### CO3: Evaluate performance of searching and sorting algorithms for engineering problems.
- **Relevance & Honest Scope:** The project incorporates in-memory timing analysis (`time.perf_counter()`) to compare the computational trade-offs of unweighted searching (BFS) versus greedy weighted searching (Dijkstra). 
- *Academic Note:* While this project demonstrates searching trade-offs, graph pathfinding alone does not evaluate sorting algorithms; therefore, CO3 is partially demonstrated through search analysis.

### CO5: Evaluate graph data structures and traversal techniques for engineering problems.
- **Relevance:** Directly models a real-world civil engineering / navigation scenario as a weighted undirected graph. Compares and contrasts two fundamental graph traversal paradigms: uniform unweighted exploration (BFS) versus greedy optimal shortest-path relaxation (Dijkstra).

---

## 16. Limitations & Future Enhancements
- **Static Graph Topology:** Current edge weights represent static walking distances; real-world enhancements could incorporate dynamic crowd density, staircases vs. ramps, or accessible wheelchair routes.
- **Multi-Floor Vertical Navigation:** The present model is 2-dimensional. Extension to 3D graphs would allow modeling multi-level buildings with elevators and stairwells.
- **Heuristic Search (A* Algorithm):** Adding an A* pathfinder using Euclidean distance heuristics $(\sqrt{(x_1-x_2)^2 + (y_1-y_2)^2})$ would further illustrate directional pruning.
