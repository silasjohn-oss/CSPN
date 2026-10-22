"""
Database module for Campus Shortest Path Finder.
Handles SQLite database connection, table creation, and initial data seeding.
"""

import os
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

# Default database path: data/campus.db in project root
DEFAULT_DB_DIR = Path(__file__).resolve().parent.parent / "data"
DEFAULT_DB_PATH = DEFAULT_DB_DIR / "campus.db"

# Sample campus locations with illustrative coordinates for 2D visualization
SAMPLE_LOCATIONS = [
    {
        "name": "Main Gate",
        "description": "Primary campus entrance with security checkpoint and visitor registration.",
        "x_coord": 80.0,
        "y_coord": 300.0,
    },
    {
        "name": "Administration",
        "description": "Administrative headquarters, admissions office, and student services.",
        "x_coord": 280.0,
        "y_coord": 140.0,
    },
    {
        "name": "Library",
        "description": "Central academic library, digital media centre, and quiet study halls.",
        "x_coord": 310.0,
        "y_coord": 450.0,
    },
    {
        "name": "Academic Block",
        "description": "Multi-storey lecture halls, faculty suites, and departmental seminar rooms.",
        "x_coord": 520.0,
        "y_coord": 210.0,
    },
    {
        "name": "Laboratory",
        "description": "Specialized computer science, electronics, and scientific research laboratories.",
        "x_coord": 750.0,
        "y_coord": 210.0,
    },
    {
        "name": "Hostel",
        "description": "Student residential complex, cafeteria, and student recreation centre.",
        "x_coord": 730.0,
        "y_coord": 470.0,
    },
]

# Illustrative walking distances in metres (bidirectional)
# Note: These are sample measurements for academic microproject demonstration.
SAMPLE_EDGES = [
    {"source": "Main Gate", "destination": "Administration", "distance_meters": 120.0},
    {"source": "Main Gate", "destination": "Library", "distance_meters": 250.0},
    {"source": "Administration", "destination": "Academic Block", "distance_meters": 100.0},
    {"source": "Administration", "destination": "Library", "distance_meters": 160.0},
    {"source": "Library", "destination": "Academic Block", "distance_meters": 90.0},
    {"source": "Library", "destination": "Hostel", "distance_meters": 300.0},
    {"source": "Academic Block", "destination": "Laboratory", "distance_meters": 140.0},
    {"source": "Laboratory", "destination": "Hostel", "distance_meters": 180.0},
]


def get_db_path(custom_path: Optional[str] = None) -> Path:
    """Return resolved Path to the SQLite database file."""
    if custom_path:
        return Path(custom_path)
    return DEFAULT_DB_PATH


def get_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    """
    Establish and return a connection to the SQLite database.
    Configures Row factory to return dict-like rows.
    """
    path = get_db_path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    # Enable foreign keys
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db(db_path: Optional[str] = None) -> None:
    """
    Initialize SQLite database schema and seed with default campus locations and edges.
    Guarantees no duplicate records are inserted on repeated startups.
    """
    path = get_db_path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    conn = get_connection(db_path)
    try:
        with conn:
            cursor = conn.cursor()

            # Create locations table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS locations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    description TEXT,
                    x_coord REAL DEFAULT 0.0,
                    y_coord REAL DEFAULT 0.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # Create edges table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS edges (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source TEXT NOT NULL,
                    destination TEXT NOT NULL,
                    distance_meters REAL NOT NULL,
                    bidirectional INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(source, destination)
                );
            """)

            # Seed locations if table is empty
            cursor.execute("SELECT COUNT(*) AS count FROM locations;")
            location_count = cursor.fetchone()["count"]

            if location_count == 0:
                for loc in SAMPLE_LOCATIONS:
                    cursor.execute("""
                        INSERT OR IGNORE INTO locations (name, description, x_coord, y_coord)
                        VALUES (?, ?, ?, ?);
                    """, (loc["name"], loc["description"], loc["x_coord"], loc["y_coord"]))

            # Seed edges if table is empty
            cursor.execute("SELECT COUNT(*) AS count FROM edges;")
            edge_count = cursor.fetchone()["count"]

            if edge_count == 0:
                for edge in SAMPLE_EDGES:
                    cursor.execute("""
                        INSERT OR IGNORE INTO edges (source, destination, distance_meters, bidirectional)
                        VALUES (?, ?, ?, 1);
                    """, (edge["source"], edge["destination"], edge["distance_meters"]))
    finally:
        conn.close()


def get_all_locations(db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieve all campus locations from SQLite."""
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, description, x_coord, y_coord FROM locations ORDER BY name ASC;")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def get_all_edges(db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieve all campus pathways and distances from SQLite."""
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, source, destination, distance_meters, bidirectional FROM edges ORDER BY id ASC;")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()
