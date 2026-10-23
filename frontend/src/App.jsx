import React, { useState, useEffect, useMemo } from 'react';
import {
  Navigation,
  Compass,
  MapPin,
  RotateCcw,
  Clock,
  ArrowRight,
  Layers,
  Activity,
  Info,
  CheckCircle2,
  AlertCircle,
  ArrowLeftRight,
  ChevronDown,
  Sun,
  Moon,
  Building2,
  Trees,
  Utensils,
  Car,
  HeartPulse,
  Dumbbell,
  FlaskConical,
  Cpu,
  Zap,
  Hammer,
  BookOpen,
  Users,
  Landmark
} from 'lucide-react';

const API_BASE = 'http://127.0.0.1:8000';

// Map each KITS node name to a lucide icon + category colour
const NODE_META = {
  'Main Gate':           { icon: Landmark,    color: '#f59e0b', zone: 'Entry' },
  'Parking Area':        { icon: Car,         color: '#94a3b8', zone: 'Entry' },
  'Admin Block':         { icon: Building2,   color: '#6366f1', zone: 'Administration' },
  'Emmanuel Auditorium': { icon: Users,       color: '#8b5cf6', zone: 'Auditorium' },
  'Elshaddai Auditorium':{ icon: Users,       color: '#8b5cf6', zone: 'Auditorium' },
  'CTC & Library':       { icon: BookOpen,    color: '#06b6d4', zone: 'Academic' },
  'Canteen':             { icon: Utensils,    color: '#f97316', zone: 'Amenity' },
  'Science & Humanities':{ icon: FlaskConical,color: '#10b981', zone: 'Academic' },
  'CSE Block':           { icon: Cpu,         color: '#3b82f6', zone: 'Academic' },
  'ECE & EEE Block':     { icon: Zap,         color: '#eab308', zone: 'Academic' },
  'Mech Block':          { icon: Hammer,      color: '#ef4444', zone: 'Academic' },
  'Civil Block':         { icon: Building2,   color: '#64748b', zone: 'Academic' },
  'Biotech & Health':    { icon: HeartPulse,  color: '#ec4899', zone: 'Academic' },
  'Aerospace & Robotics':{ icon: Compass,     color: '#06b6d4', zone: 'Academic' },
  'Edward George Hostel':{ icon: Users,       color: '#a78bfa', zone: 'North Gents' },
  'Angelina Hostel':     { icon: Users,       color: '#a78bfa', zone: 'North Gents' },
  'Hepzibah Hostel':     { icon: Users,       color: '#a78bfa', zone: 'North Gents' },
  'Campus Hospital':     { icon: HeartPulse,  color: '#f43f5e', zone: 'Medical' },
  'Bobraj Hostel':       { icon: Users,       color: '#7c3aed', zone: 'New Gents' },
  'Bethany Hostel':      { icon: Users,       color: '#7c3aed', zone: 'New Gents' },
  'Indoor Sports Center':{ icon: Dumbbell,    color: '#10b981', zone: 'Sports' },
  'Guest House & Bank':  { icon: Building2,   color: '#94a3b8', zone: 'Amenity' },
  'Sundararaj Hostel':   { icon: Users,       color: '#f43f5e', zone: 'Ladies Residence' },
  'Sports Ground':       { icon: Trees,       color: '#22c55e', zone: 'Sports' },
  'Agriculture Research':{ icon: Trees,       color: '#84cc16', zone: 'Research' },
  'Water Institute':     { icon: FlaskConical,color: '#38bdf8', zone: 'Research' },
};

export default function App() {
  const [theme, setTheme] = useState(() => localStorage.getItem('theme') || 'dark');
  const [locations, setLocations] = useState([]);
  const [edges, setEdges] = useState([]);
  const [source, setSource] = useState('Main Gate');
  const [destination, setDestination] = useState('Canteen');
  const [algorithm, setAlgorithm] = useState('dijkstra');

  const [routeResult, setRouteResult] = useState(null);
  const [compareResult, setCompareResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [apiConnected, setApiConnected] = useState(false);

  const [hoveredNode, setHoveredNode] = useState(null);
  const [selectedNodeInfo, setSelectedNodeInfo] = useState(null);
  const [routeKey, setRouteKey] = useState(0); // forces re-animation on new route

  // Sync theme
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
  }, [theme]);

  const toggleTheme = () => setTheme(prev => prev === 'dark' ? 'light' : 'dark');

  // Fetch graph data
  const fetchGraphData = async () => {
    try {
      setError(null);
      const [statusRes, locsRes, edgesRes] = await Promise.all([
        fetch(`${API_BASE}/`),
        fetch(`${API_BASE}/api/locations`),
        fetch(`${API_BASE}/api/edges`),
      ]);

      if (!statusRes.ok || !locsRes.ok || !edgesRes.ok) {
        throw new Error('Failed to retrieve graph data from backend server.');
      }

      const locsData  = await locsRes.json();
      const edgesData = await edgesRes.json();
      setLocations(locsData.locations  || []);
      setEdges(edgesData.edges || []);
      setApiConnected(true);
    } catch (err) {
      console.error('API connection error:', err);
      setApiConnected(false);
      setError('Backend server not connected. Ensure FastAPI is running on http://127.0.0.1:8000.');
    }
  };

  useEffect(() => { fetchGraphData(); }, []);

  // Coordinate lookup
  const locationMap = useMemo(() => {
    const map = {};
    locations.forEach(loc => { map[loc.name] = loc; });
    return map;
  }, [locations]);

  // Pathfinding
  const handleFindRoute = async (algoToUse = algorithm) => {
    if (!source || !destination) {
      setError('Please select both a source and destination location.');
      return;
    }
    setLoading(true);
    setError(null);

    try {
      if (algoToUse === 'compare') {
        const res = await fetch(
          `${API_BASE}/api/compare?source=${encodeURIComponent(source)}&destination=${encodeURIComponent(destination)}&iterations=50`
        );
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || 'Failed to compare algorithms.');
        setCompareResult(data.comparison);
        setRouteResult(data.comparison.dijkstra);
      } else {
        const res = await fetch(
          `${API_BASE}/api/route?source=${encodeURIComponent(source)}&destination=${encodeURIComponent(destination)}&algorithm=${algoToUse}`
        );
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || 'Failed to calculate shortest path.');
        setRouteResult(data.result);
        setCompareResult(null);
      }
      setRouteKey(k => k + 1); // trigger re-animation
    } catch (err) {
      console.error('Route calculation error:', err);
      setError(err.message);
      setRouteResult(null);
      setCompareResult(null);
    } finally {
      setLoading(false);
    }
  };

  const handleSwap = () => {
    const temp = source;
    setSource(destination);
    setDestination(temp);
    setRouteResult(null);
    setCompareResult(null);
  };

  const handleReset = () => {
    setSource('Main Gate');
    setDestination('Canteen');
    setAlgorithm('dijkstra');
    setRouteResult(null);
    setCompareResult(null);
    setError(null);
    setSelectedNodeInfo(null);
  };

  const isEdgeInRoute = (src, dst, path) => {
    if (!path || path.length < 2) return false;
    for (let i = 0; i < path.length - 1; i++) {
      if (
        (path[i] === src && path[i + 1] === dst) ||
        (path[i] === dst && path[i + 1] === src)
      ) return true;
    }
    return false;
  };

  const getNodeOrderInRoute = (nodeName, path) => {
    if (!path) return -1;
    return path.indexOf(nodeName);
  };

  const activePath = routeResult?.path || [];

  // Node radius — slightly smaller for the dense KITS graph
  const NODE_R = 18;

  return (
    <div className="app-container">

      {/* ── Header ─────────────────────────────────────────────────────── */}
      <header className="top-header">
        <div className="header-left">
          <div className="logo-badge">
            <Compass className="icon-pulse text-indigo-400" size={26} />
          </div>
          <div>
            <div className="header-title-row">
              <h1>KITS Campus Navigator</h1>
              <span className="campus-tag">KITS · Coimbatore</span>
            </div>
            <p className="header-subtitle">
              Karunya Institute of Technology &amp; Sciences — Dijkstra &amp; BFS shortest-path visualiser
            </p>
          </div>
        </div>

        <div className="header-right">
          <button
            className="theme-toggle-btn"
            onClick={toggleTheme}
            title={theme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
            aria-label="Toggle Theme"
          >
            {theme === 'dark' ? (
              <><Sun size={16} className="theme-icon sun" /><span>Light Mode</span></>
            ) : (
              <><Moon size={16} className="theme-icon moon" /><span>Dark Mode</span></>
            )}
          </button>
        </div>
      </header>

      {/* ── Main Grid ──────────────────────────────────────────────────── */}
      <main className="main-content">

        {/* Left: Controls */}
        <section className="control-sidebar">
          <div className="glass-card">
            <h2 className="card-title">
              <Navigation size={17} />
              <span>Route Configuration</span>
            </h2>

            {/* Source */}
            <div className="form-group">
              <label htmlFor="source-select">
                <span className="dot-indicator green" />
                Starting Location
              </label>
              <div className="select-wrapper">
                <select
                  id="source-select"
                  value={source}
                  onChange={e => setSource(e.target.value)}
                  className="custom-select"
                >
                  {locations.map(loc => (
                    <option key={loc.id} value={loc.name}>{loc.name}</option>
                  ))}
                </select>
                <ChevronDown size={15} className="select-chevron" />
              </div>
            </div>

            {/* Swap */}
            <div className="swap-row">
              <button type="button" onClick={handleSwap} className="btn-swap" title="Swap Start ↔ Destination">
                <ArrowLeftRight size={13} />
                <span>Swap</span>
              </button>
            </div>

            {/* Destination */}
            <div className="form-group">
              <label htmlFor="destination-select">
                <span className="dot-indicator red" />
                Destination Location
              </label>
              <div className="select-wrapper">
                <select
                  id="destination-select"
                  value={destination}
                  onChange={e => setDestination(e.target.value)}
                  className="custom-select"
                >
                  {locations.map(loc => (
                    <option key={loc.id} value={loc.name}>{loc.name}</option>
                  ))}
                </select>
                <ChevronDown size={15} className="select-chevron" />
              </div>
            </div>

            {/* Algorithm Tabs */}
            <div className="form-group">
              <label>
                <Layers size={13} />
                Pathfinding Mode
              </label>
              <div className="algo-selector-tabs">
                {[
                  { id: 'dijkstra', label: 'Dijkstra', sub: 'Min Distance' },
                  { id: 'bfs',      label: 'BFS',      sub: 'Fewest Edges' },
                  { id: 'compare',  label: 'Compare',  sub: 'Side-by-Side' },
                ].map(({ id, label, sub }) => (
                  <button
                    key={id}
                    type="button"
                    className={`tab-btn ${algorithm === id ? 'active' : ''}`}
                    onClick={() => {
                      setAlgorithm(id);
                      if (routeResult) handleFindRoute(id);
                    }}
                  >
                    <strong>{label}</strong>
                    <span>{sub}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Action Buttons */}
            <div className="button-group">
              <button
                id="find-path-btn"
                className="btn-primary"
                onClick={() => handleFindRoute(algorithm)}
                disabled={loading}
              >
                {loading ? (
                  <><Activity className="spin" size={15} /><span>Calculating…</span></>
                ) : (
                  <><Compass size={15} /><span>Find Shortest Path</span></>
                )}
              </button>
              <button id="reset-btn" className="btn-secondary" onClick={handleReset} title="Reset">
                <RotateCcw size={15} /><span>Reset</span>
              </button>
            </div>

            {/* Algorithm Info */}
            <div className="algo-info-box">
              <div className="algo-info-header">
                <Info size={14} />
                <strong>
                  {algorithm === 'dijkstra' ? "Dijkstra's Algorithm"
                  : algorithm === 'bfs'     ? 'Breadth-First Search (BFS)'
                  :                           'Algorithm Comparison Mode'}
                </strong>
              </div>
              <p className="algo-info-text">
                {algorithm === 'dijkstra' && (
                  <>Uses a <em>priority queue (min-heap)</em> to compute the absolute minimum cumulative walking distance. Time: <code>O((V+E) log V)</code>.</>
                )}
                {algorithm === 'bfs' && (
                  <>Uses a <em>FIFO queue</em> to explore layer-by-layer, finding the path with the fewest junctions. Does <strong>not</strong> optimise for distance. Time: <code>O(V+E)</code>.</>
                )}
                {algorithm === 'compare' && (
                  <>Executes both algorithms concurrently on identical inputs and averages 50 timing iterations in-memory to benchmark performance.</>
                )}
              </p>
            </div>
          </div>

          {/* Error */}
          {error && (
            <div className="alert-box error">
              <AlertCircle size={17} />
              <div><strong>Error:</strong> {error}</div>
            </div>
          )}

          {/* Single Route Result */}
          {routeResult && algorithm !== 'compare' && (
            <div className="glass-card result-card" key={`result-${routeKey}`}>
              <div className="card-header-flex">
                <h3 className="card-subtitle">
                  <CheckCircle2 size={15} className="text-emerald-400" />
                  Route Results
                </h3>
                <span className="badge-pill uppercase">{routeResult.algorithm}</span>
              </div>

              <div className="metrics-grid">
                <div className="metric-item">
                  <span className="metric-label">Distance</span>
                  <span className="metric-value highlight">{routeResult.total_distance} m</span>
                </div>
                <div className="metric-item">
                  <span className="metric-label">Edges</span>
                  <span className="metric-value">{routeResult.edge_count}</span>
                </div>
                <div className="metric-item">
                  <span className="metric-label">Time</span>
                  <span className="metric-value text-amber-300">
                    {routeResult.execution_time_ms ? `${routeResult.execution_time_ms} ms` : '< 0.05 ms'}
                  </span>
                </div>
              </div>

              <div className="path-timeline">
                <span className="timeline-title">Turn-by-Turn Route:</span>
                <div className="path-nodes-list">
                  {routeResult.path.map((nodeName, idx) => (
                    <div key={idx} className="path-node-step" style={{ animationDelay: `${idx * 55}ms` }}>
                      <div className="node-badge"><span className="step-num">{idx + 1}</span></div>
                      <span className="node-name">{nodeName}</span>
                      {idx < routeResult.path.length - 1 && <ArrowRight size={13} className="node-arrow" />}
                    </div>
                  ))}
                </div>
              </div>

              <div className="card-footer-note">
                <small>{routeResult.description}</small>
              </div>
            </div>
          )}

          {/* Comparison Result */}
          {compareResult && (
            <div className="glass-card comparison-card" key={`compare-${routeKey}`}>
              <div className="card-header-flex">
                <h3 className="card-subtitle">
                  <Activity size={15} className="text-indigo-400" />
                  Algorithm Comparison
                </h3>
                <span className="badge-pill">50 Iterations</span>
              </div>

              <div className="comparison-table-wrapper">
                <table className="comparison-table">
                  <thead>
                    <tr>
                      <th>Metric</th>
                      <th>Dijkstra</th>
                      <th>BFS</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td>Distance</td>
                      <td className="highlight-green">{compareResult.dijkstra.total_distance} m</td>
                      <td className={compareResult.dijkstra.total_distance < compareResult.bfs.total_distance ? 'highlight-red' : ''}>
                        {compareResult.bfs.total_distance} m
                      </td>
                    </tr>
                    <tr>
                      <td>Edges</td>
                      <td>{compareResult.dijkstra.edge_count}</td>
                      <td className="highlight-green">{compareResult.bfs.edge_count}</td>
                    </tr>
                    <tr>
                      <td>Avg Time</td>
                      <td>{compareResult.dijkstra.execution_time_ms} ms</td>
                      <td>{compareResult.bfs.execution_time_ms} ms</td>
                    </tr>
                    <tr>
                      <td>Route</td>
                      <td className="route-cell">{compareResult.dijkstra.path.join(' → ')}</td>
                      <td className="route-cell">{compareResult.bfs.path.join(' → ')}</td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <div className="insight-box">
                <h4>Pedagogical Analysis</h4>
                <p>{compareResult.pedagogical_insight}</p>
                <small className="disclaimer-text">{compareResult.timing_disclaimer}</small>
              </div>
            </div>
          )}
        </section>

        {/* Right: Interactive SVG Map */}
        <section className="visualization-container">
          <div className="glass-card map-card">
            <div className="map-header">
              <div>
                <h2 className="card-title">
                  <MapPin size={17} />
                  <span>KITS Campus Map</span>
                </h2>
                <p className="map-subtitle">
                  26 nodes · 46 pathways · Karunya Nagar, Coimbatore — click any building to inspect it.
                </p>
              </div>

              <div className="legend-pills">
                <span className="legend-item"><span className="legend-dot start" />Start</span>
                <span className="legend-item"><span className="legend-dot end" />Destination</span>
                <span className="legend-item"><span className="legend-dot active" />Active Path</span>
                <span className="legend-item"><span className="legend-dot normal" />Campus Path</span>
              </div>
            </div>

            {/* SVG Canvas — viewBox spans KITS coordinate space */}
            <div className="svg-wrapper">
              <svg
                viewBox="0 0 1150 720"
                className="campus-svg"
                preserveAspectRatio="xMidYMid meet"
              >
                <defs>
                  {/* Glow filter for active route */}
                  <filter id="glow" x="-25%" y="-25%" width="150%" height="150%">
                    <feGaussianBlur stdDeviation="4" result="blur" />
                    <feComposite in="SourceGraphic" in2="blur" operator="over" />
                  </filter>
                  {/* Node shadow */}
                  <filter id="nodeShadow" x="-15%" y="-15%" width="130%" height="130%">
                    <feDropShadow dx="0" dy="3" stdDeviation="4" floodOpacity="0.45" />
                  </filter>
                  {/* Active node glow */}
                  <filter id="activeGlow" x="-30%" y="-30%" width="160%" height="160%">
                    <feGaussianBlur stdDeviation="5" result="blur" />
                    <feMerge>
                      <feMergeNode in="blur" />
                      <feMergeNode in="SourceGraphic" />
                    </feMerge>
                  </filter>

                  {/* Gradient for active edge */}
                  <linearGradient id="activeEdgeGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                    <stop offset="0%"   stopColor="#6366f1" />
                    <stop offset="100%" stopColor="#06b6d4" />
                  </linearGradient>
                </defs>

                {/* Background Campus Grid */}
                <g className="grid-layer" opacity="0.12">
                  {[...Array(15)].map((_, i) => (
                    <line key={`gx-${i}`} x1={i * 80} y1="0" x2={i * 80} y2="720"
                      stroke="var(--svg-grid)" strokeDasharray="2,7" strokeWidth="1" />
                  ))}
                  {[...Array(10)].map((_, i) => (
                    <line key={`gy-${i}`} x1="0" y1={i * 80} x2="1150" y2={i * 80}
                      stroke="var(--svg-grid)" strokeDasharray="2,7" strokeWidth="1" />
                  ))}
                </g>

                {/* Zone labels (decorative background text) */}
                <g opacity="0.55">
                  <text x="58"  y="22"  className="zone-label-text">New Gents</text>
                  <text x="160" y="22"  className="zone-label-text">North Gents</text>
                  <text x="580" y="22"  className="zone-label-text">North Residence</text>
                  <text x="910" y="22"  className="zone-label-text">Parking / Entry</text>
                  <text x="200" y="710" className="zone-label-text">Academic Ring</text>
                  <text x="500" y="710" className="zone-label-text">Sports &amp; Agriculture</text>
                  <text x="880" y="710" className="zone-label-text">Ladies Residence</text>
                </g>

                {/* ── Edges ──────────────────────────────────────────── */}
                <g className="edges-layer">
                  {edges.map(edge => {
                    const srcLoc = locationMap[edge.source];
                    const dstLoc = locationMap[edge.destination];
                    if (!srcLoc || !dstLoc) return null;

                    const inRoute = isEdgeInRoute(edge.source, edge.destination, activePath);
                    const midX = (srcLoc.x_coord + dstLoc.x_coord) / 2;
                    const midY = (srcLoc.y_coord + dstLoc.y_coord) / 2;

                    return (
                      <g key={edge.id} className={`edge-group ${inRoute ? 'active-edge' : ''}`}>
                        {/* Base line */}
                        <line
                          x1={srcLoc.x_coord} y1={srcLoc.y_coord}
                          x2={dstLoc.x_coord} y2={dstLoc.y_coord}
                          className={inRoute ? 'pathway-active' : 'pathway-base'}
                          stroke={inRoute ? 'url(#activeEdgeGrad)' : undefined}
                          filter={inRoute ? 'url(#glow)' : undefined}
                          key={`base-${edge.id}-${routeKey}`}
                        />

                        {/* Animated dash overlay when in route */}
                        {inRoute && (
                          <line
                            x1={srcLoc.x_coord} y1={srcLoc.y_coord}
                            x2={dstLoc.x_coord} y2={dstLoc.y_coord}
                            className="pathway-animated"
                          />
                        )}

                        {/* Distance badge */}
                        <g transform={`translate(${midX},${midY})`} className="edge-distance-badge">
                          <rect
                            x="-20" y="-9" width="40" height="18" rx="9"
                            className={inRoute ? 'badge-rect-active' : 'badge-rect-base'}
                          />
                          <text x="0" y="4" textAnchor="middle"
                            className={inRoute ? 'badge-text-active' : 'badge-text-base'}
                          >
                            {Math.round(edge.distance_meters)}m
                          </text>
                        </g>
                      </g>
                    );
                  })}
                </g>

                {/* ── Nodes ──────────────────────────────────────────── */}
                <g className="nodes-layer">
                  {locations.map(loc => {
                    const isStart   = loc.name === source;
                    const isEnd     = loc.name === destination;
                    const orderInPath = getNodeOrderInRoute(loc.name, activePath);
                    const isInPath  = orderInPath !== -1;
                    const isHovered = hoveredNode === loc.name;
                    const meta      = NODE_META[loc.name] || {};
                    const dotColor  = isStart ? '#10b981' : isEnd ? '#f43f5e' : isInPath ? '#6366f1' : (meta.color || '#94a3b8');

                    let nodeClass = 'campus-node';
                    if (isStart)       nodeClass += ' start-node';
                    else if (isEnd)    nodeClass += ' end-node';
                    else if (isInPath) nodeClass += ' path-node';
                    if (isHovered)     nodeClass += ' hovered-node';

                    return (
                      <g
                        key={loc.id}
                        transform={`translate(${loc.x_coord},${loc.y_coord})`}
                        className={nodeClass}
                        onMouseEnter={() => setHoveredNode(loc.name)}
                        onMouseLeave={() => setHoveredNode(null)}
                        onClick={() => setSelectedNodeInfo(loc)}
                        cursor="pointer"
                        filter={isInPath || isStart || isEnd ? 'url(#activeGlow)' : 'url(#nodeShadow)'}
                      >
                        {/* Outer pulse ring */}
                        <circle r={NODE_R + 10} className="pulse-ring" />

                        {/* Colour accent ring */}
                        <circle
                          r={NODE_R + 3}
                          fill="none"
                          stroke={dotColor}
                          strokeWidth={isInPath || isStart || isEnd ? 2 : 1}
                          opacity={isHovered ? 0.8 : isInPath || isStart || isEnd ? 0.55 : 0.22}
                          style={{ transition: 'opacity 0.25s ease, stroke-width 0.25s ease' }}
                        />

                        {/* Main circle */}
                        <circle r={NODE_R} className="node-circle" />

                        {/* Step number or centre dot */}
                        {isInPath ? (
                          <text x="0" y="5" textAnchor="middle" className="order-text">
                            {orderInPath + 1}
                          </text>
                        ) : (
                          <circle r="4" className="node-center-dot" />
                        )}

                        {/* Building name label */}
                        <g transform="translate(0,32)">
                          <rect
                            x="-52" y="-10" width="104" height="20" rx="10"
                            className="label-bg"
                          />
                          <text x="0" y="4" textAnchor="middle" className="building-label">
                            {loc.name}
                          </text>
                        </g>
                      </g>
                    );
                  })}
                </g>
              </svg>
            </div>

            {/* Node Detail Panel */}
            {selectedNodeInfo && (() => {
              const meta = NODE_META[selectedNodeInfo.name] || {};
              const Icon = meta.icon || Building2;
              return (
                <div className="location-detail-panel">
                  <div className="detail-header">
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                      <div style={{
                        width: 36, height: 36, borderRadius: 10,
                        background: `${meta.color || '#6366f1'}22`,
                        border: `1px solid ${meta.color || '#6366f1'}55`,
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                        flexShrink: 0,
                      }}>
                        <Icon size={18} style={{ color: meta.color || '#6366f1' }} />
                      </div>
                      <div>
                        <h4 className="detail-title">{selectedNodeInfo.name}</h4>
                        <span className="detail-meta">
                          x: {selectedNodeInfo.x_coord} · y: {selectedNodeInfo.y_coord}
                        </span>
                      </div>
                    </div>
                    <button className="btn-close-detail" onClick={() => setSelectedNodeInfo(null)}>×</button>
                  </div>

                  {meta.zone && <span className="detail-zone">{meta.zone}</span>}

                  <p className="detail-desc">{selectedNodeInfo.description}</p>

                  <div className="detail-actions">
                    <button className="btn-set-start" onClick={() => { setSource(selectedNodeInfo.name); setSelectedNodeInfo(null); }}>
                      Set as Start
                    </button>
                    <button className="btn-set-dest" onClick={() => { setDestination(selectedNodeInfo.name); setSelectedNodeInfo(null); }}>
                      Set as Destination
                    </button>
                  </div>
                </div>
              );
            })()}

            <div className="map-footer-disclaimer">
              <span className="notice-badge">Notice</span>
              <span>
                Campus layout is illustrative 2-D representation of Karunya Institute of Technology &amp; Sciences (KITS),
                Coimbatore. Distances and coordinates are approximate and not GPS-surveyed.
              </span>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}
