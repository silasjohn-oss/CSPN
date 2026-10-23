"""
Database module for Campus Shortest Path Finder.
Handles SQLite database connection, table creation, and initial data seeding.
Seeded with real Karunya Institute of Technology and Sciences (KITS) campus data.
"""

import os
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

# Default database path: data/campus.db in project root
DEFAULT_DB_DIR = Path(__file__).resolve().parent.parent / "data"
DEFAULT_DB_PATH = DEFAULT_DB_DIR / "campus.db"

# ---------------------------------------------------------------------------
# KITS Campus Locations
# Coordinates are illustrative 2D positions scaled to fit the SVG canvas
# (viewBox 0 0 1150 720). Layout mirrors actual campus zone topology:
#   East  → Main Gate & Ladies Residence
#   Center → Admin, Auditoriums, Library/CTC, Canteen
#   Center-Left → Academic Ring (CSE, ECE/EEE, Mech, Civil, Biotech …)
#   North → North Gents Hostels & Hospital
#   Northwest → New Gents Hostels & Sports Center
#   South → Sports Grounds, Agriculture, Water Institute
# ---------------------------------------------------------------------------
SAMPLE_LOCATIONS = [
    # ── Zone 1: Central Administration & Entry Core ──────────────────────
    {
        "name": "Main Gate",
        "description": "Primary east-facing campus entrance on Siruvani Road with security checkpoint and visitor registration. The starting point for all campus navigation.",
        "x_coord": 1060.0,
        "y_coord": 360.0,
    },
    {
        "name": "Parking Area",
        "description": "Multi-bay parking plaza adjacent to the Main Gate, serving visitors, faculty, and administration vehicles.",
        "x_coord": 980.0,
        "y_coord": 240.0,
    },
    {
        "name": "Admin Block",
        "description": "Administrative headquarters of KITS — houses the Chancellor's office, Registrar, Finance, and student-services facilities. Central hub of the campus ring road.",
        "x_coord": 820.0,
        "y_coord": 290.0,
    },
    {
        "name": "Emmanuel Auditorium",
        "description": "High-capacity multi-tier indoor auditorium used for convocations, seminars, and large institutional events.",
        "x_coord": 730.0,
        "y_coord": 185.0,
    },
    {
        "name": "Elshaddai Auditorium",
        "description": "Open-air mega-assembly arena accommodating mass gatherings, cultural festivals, and outdoor ceremonies.",
        "x_coord": 820.0,
        "y_coord": 145.0,
    },
    {
        "name": "CTC & Library",
        "description": "Central Computer Technology Center and Main Library — two-wing integrated facility with 10 Gbps fiber hub, SAN storage, digital media centre, and quiet study halls.",
        "x_coord": 660.0,
        "y_coord": 310.0,
    },
    {
        "name": "Canteen",
        "description": "Central student dining facility serving breakfast, lunch, and dinner. A key social gathering point at the heart of campus.",
        "x_coord": 720.0,
        "y_coord": 410.0,
    },
    # ── Zone 2: Academic Ring ─────────────────────────────────────────────
    {
        "name": "Science & Humanities",
        "description": "21,012 sq m block housing Applied Physics, Applied Chemistry, Nanotechnology, and Language Labs alongside humanities classrooms.",
        "x_coord": 510.0,
        "y_coord": 245.0,
    },
    {
        "name": "CSE Block",
        "description": "Computer Science & Data Science Tower — Data Science, Cyber Security, AI & ML research hubs, and Software Engineering stations.",
        "x_coord": 390.0,
        "y_coord": 165.0,
    },
    {
        "name": "ECE & EEE Block",
        "description": "Electronics & Electrical building with large industrial lab wings: VLSI, 5G Wireless Communications, Electrical Machines, Power Electronics, and Electric Drives labs.",
        "x_coord": 285.0,
        "y_coord": 250.0,
    },
    {
        "name": "Mech Block",
        "description": "Mechanical Engineering block adjacent to central workshops — CAD/CAM, Thermal Engineering plant, and Manufacturing Automation floor.",
        "x_coord": 265.0,
        "y_coord": 370.0,
    },
    {
        "name": "Civil Block",
        "description": "Civil Engineering complex with high-clearance structural engineering, geology, and environmental testing labs.",
        "x_coord": 365.0,
        "y_coord": 460.0,
    },
    {
        "name": "Biotech & Health",
        "description": "Biotechnology & Applied Health Sciences block — negative-pressure cleanrooms, animal tissue culture labs, and microbiology facilities.",
        "x_coord": 490.0,
        "y_coord": 510.0,
    },
    {
        "name": "Aerospace & Robotics",
        "description": "High-roof hangar-layout wing housing drone/UAV labs, aviation systems, and mobile robotics platform labs.",
        "x_coord": 210.0,
        "y_coord": 165.0,
    },
    # ── Zone 3: North Gents Residence ─────────────────────────────────────
    {
        "name": "Edward George Hostel",
        "description": "North Gents residential block with 4-seater first-year student accommodation. Part of the northern sector residential campus.",
        "x_coord": 355.0,
        "y_coord": 80.0,
    },
    {
        "name": "Angelina Hostel",
        "description": "North Gents high-density structural wing with multi-occupancy rooms for male students.",
        "x_coord": 510.0,
        "y_coord": 80.0,
    },
    {
        "name": "Hepzibah Hostel",
        "description": "Dedicated multi-story male residential block in the North Gents sector of KITS campus.",
        "x_coord": 660.0,
        "y_coord": 80.0,
    },
    {
        "name": "Campus Hospital",
        "description": "Campus Rural Hospital & Dispensary with 24x7 care, external medical vehicle access lanes, and emergency services for the KITS community.",
        "x_coord": 190.0,
        "y_coord": 85.0,
    },
    # ── Zone 4: New Gents Residence ───────────────────────────────────────
    {
        "name": "Bobraj Hostel",
        "description": "SGBOBRAJ Residence — massive structural block surrounding internal courtyard gardens, with 4-seater and 6-seater room layouts.",
        "x_coord": 105.0,
        "y_coord": 300.0,
    },
    {
        "name": "Bethany Hostel",
        "description": "Dedicated PG, international student, and single-occupancy room layouts in the New Gents northwest sector.",
        "x_coord": 105.0,
        "y_coord": 445.0,
    },
    {
        "name": "Indoor Sports Center",
        "description": "Indoor Sports & Fitness Center — central geometric focal point between Bobraj and Bethany blocks, featuring courts, gym, and recreation facilities.",
        "x_coord": 195.0,
        "y_coord": 370.0,
    },
    {
        "name": "Guest House & Bank",
        "description": "Guest House, Commercial Bank Centre, and ATM plazas serving the New Gents residential campus and external visitors.",
        "x_coord": 105.0,
        "y_coord": 560.0,
    },
    # ── Zone 5: Ladies Residence ──────────────────────────────────────────
    {
        "name": "Sundararaj Hostel",
        "description": "Sundararaj Girls Residence — high-security courtyard system on the eastern campus edge. Houses girls gymnasium, reading rooms, basketball courts, and dedicated kitchen-dining complex.",
        "x_coord": 900.0,
        "y_coord": 490.0,
    },
    # ── Zone 6: Sports Arena ──────────────────────────────────────────────
    {
        "name": "Sports Ground",
        "description": "Outdoor sports complex with athletics track, football ground, cricket nets, hockey field, basketball & volleyball courts, and kabaddi courts.",
        "x_coord": 565.0,
        "y_coord": 590.0,
    },
    # ── Zone 7: Agriculture, Water & Utilities ────────────────────────────
    {
        "name": "Agriculture Research",
        "description": "Precision Agriculture Research Lands — open test beds, automated greenhouses, and soil testing hubs at the southern campus periphery.",
        "x_coord": 380.0,
        "y_coord": 650.0,
    },
    {
        "name": "Water Institute",
        "description": "Water Research Institute with desalination trial loops, wastewater recycling infrastructure, and physical wetland testing sites.",
        "x_coord": 570.0,
        "y_coord": 665.0,
    },
]

# ---------------------------------------------------------------------------
# KITS Campus Edges (walking pathways, distances in metres)
# ---------------------------------------------------------------------------
SAMPLE_EDGES = [
    # ── Entry Core connections ─────────────────────────────────────────────
    {"source": "Main Gate",          "destination": "Parking Area",        "distance_meters": 140.0},
    {"source": "Main Gate",          "destination": "Admin Block",          "distance_meters": 320.0},
    {"source": "Main Gate",          "destination": "Sundararaj Hostel",    "distance_meters": 260.0},
    {"source": "Parking Area",       "destination": "Admin Block",          "distance_meters": 200.0},
    {"source": "Admin Block",        "destination": "Emmanuel Auditorium",  "distance_meters": 180.0},
    {"source": "Admin Block",        "destination": "Elshaddai Auditorium", "distance_meters": 200.0},
    {"source": "Admin Block",        "destination": "CTC & Library",        "distance_meters": 210.0},
    {"source": "Admin Block",        "destination": "Canteen",              "distance_meters": 200.0},
    {"source": "Emmanuel Auditorium","destination": "Elshaddai Auditorium", "distance_meters": 140.0},
    {"source": "Emmanuel Auditorium","destination": "CTC & Library",        "distance_meters": 240.0},
    {"source": "CTC & Library",      "destination": "Canteen",              "distance_meters": 130.0},
    {"source": "CTC & Library",      "destination": "Science & Humanities", "distance_meters": 210.0},
    {"source": "CTC & Library",      "destination": "Hepzibah Hostel",      "distance_meters": 290.0},
    {"source": "Canteen",            "destination": "Science & Humanities", "distance_meters": 180.0},
    {"source": "Canteen",            "destination": "Sundararaj Hostel",    "distance_meters": 290.0},
    {"source": "Canteen",            "destination": "Sports Ground",        "distance_meters": 290.0},
    # ── Academic Ring connections ──────────────────────────────────────────
    {"source": "Science & Humanities","destination": "CSE Block",           "distance_meters": 195.0},
    {"source": "Science & Humanities","destination": "ECE & EEE Block",     "distance_meters": 235.0},
    {"source": "CSE Block",           "destination": "ECE & EEE Block",     "distance_meters": 185.0},
    {"source": "CSE Block",           "destination": "Aerospace & Robotics","distance_meters": 260.0},
    {"source": "CSE Block",           "destination": "Edward George Hostel","distance_meters": 310.0},
    {"source": "ECE & EEE Block",     "destination": "Mech Block",          "distance_meters": 205.0},
    {"source": "ECE & EEE Block",     "destination": "Aerospace & Robotics","distance_meters": 185.0},
    {"source": "Mech Block",          "destination": "Civil Block",         "distance_meters": 200.0},
    {"source": "Mech Block",          "destination": "Indoor Sports Center","distance_meters": 225.0},
    {"source": "Mech Block",          "destination": "Bobraj Hostel",       "distance_meters": 280.0},
    {"source": "Civil Block",         "destination": "Biotech & Health",    "distance_meters": 185.0},
    {"source": "Civil Block",         "destination": "Sports Ground",       "distance_meters": 240.0},
    {"source": "Biotech & Health",    "destination": "Sports Ground",       "distance_meters": 200.0},
    {"source": "Biotech & Health",    "destination": "Canteen",             "distance_meters": 310.0},
    # ── North Gents connections ────────────────────────────────────────────
    {"source": "Aerospace & Robotics","destination": "Campus Hospital",     "distance_meters": 195.0},
    {"source": "Aerospace & Robotics","destination": "Bobraj Hostel",       "distance_meters": 205.0},
    {"source": "Campus Hospital",     "destination": "Edward George Hostel","distance_meters": 310.0},
    {"source": "Edward George Hostel","destination": "Angelina Hostel",     "distance_meters": 255.0},
    {"source": "Angelina Hostel",     "destination": "Hepzibah Hostel",     "distance_meters": 255.0},
    # ── New Gents connections ──────────────────────────────────────────────
    {"source": "Bobraj Hostel",       "destination": "Indoor Sports Center","distance_meters": 205.0},
    {"source": "Bobraj Hostel",       "destination": "Bethany Hostel",      "distance_meters": 255.0},
    {"source": "Indoor Sports Center","destination": "Bethany Hostel",      "distance_meters": 195.0},
    {"source": "Bethany Hostel",      "destination": "Guest House & Bank",  "distance_meters": 245.0},
    {"source": "Indoor Sports Center","destination": "Mech Block",          "distance_meters": 225.0},
    # ── Ladies Residence connections ───────────────────────────────────────
    {"source": "Sundararaj Hostel",   "destination": "Sports Ground",       "distance_meters": 195.0},
    {"source": "Sundararaj Hostel",   "destination": "Admin Block",         "distance_meters": 360.0},
    # ── Southern Utilities connections ────────────────────────────────────
    {"source": "Sports Ground",       "destination": "Agriculture Research", "distance_meters": 295.0},
    {"source": "Sports Ground",       "destination": "Water Institute",      "distance_meters": 240.0},
    {"source": "Agriculture Research","destination": "Water Institute",      "distance_meters": 295.0},
    {"source": "Guest House & Bank",  "destination": "Sports Ground",       "distance_meters": 320.0},
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
    Initialize SQLite database schema and seed with KITS campus locations and edges.
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
