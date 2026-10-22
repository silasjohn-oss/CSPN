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
  HelpCircle,
  ExternalLink,
  ChevronDown,
  Sun,
  Moon
} from 'lucide-react';

const API_BASE = 'http://127.0.0.1:8000';

export default function App() {
  const [theme, setTheme] = useState(() => {
    return localStorage.getItem('theme') || 'dark';
  });

  const [locations, setLocations] = useState([]);
  const [edges, setEdges] = useState([]);
  const [source, setSource] = useState('Main Gate');
  const [destination, setDestination] = useState('Hostel');
  const [algorithm, setAlgorithm] = useState('dijkstra'); // 'dijkstra' | 'bfs' | 'compare'
  
  const [routeResult, setRouteResult] = useState(null);
  const [compareResult, setCompareResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [apiConnected, setApiConnected] = useState(false);
  
  const [hoveredNode, setHoveredNode] = useState(null);
  const [selectedNodeInfo, setSelectedNodeInfo] = useState(null);

  // Sync theme attribute on document root and persist in localStorage
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme((prev) => (prev === 'dark' ? 'light' : 'dark'));
  };

  // Fetch initial graph data from SQLite backend
  const fetchGraphData = async () => {
    try {
      setError(null);
      const [statusRes, locsRes, edgesRes] = await Promise.all([
        fetch(`${API_BASE}/`),
        fetch(`${API_BASE}/api/locations`),
        fetch(`${API_BASE}/api/edges`)
      ]);

      if (!statusRes.ok || !locsRes.ok || !edgesRes.ok) {
        throw new Error('Failed to retrieve graph data from backend server.');
      }

      const locsData = await locsRes.json();
      const edgesData = await edgesRes.json();

      setLocations(locsData.locations || []);
      setEdges(edgesData.edges || []);
      setApiConnected(true);
    } catch (err) {
      console.error('API connection error:', err);
      setApiConnected(false);
      setError('Backend server not connected. Ensure FastAPI is running on http://127.0.0.1:8000.');
    }
  };

  useEffect(() => {
    fetchGraphData();
  }, []);

  // Compute lookup map for location coordinates
  const locationMap = useMemo(() => {
    const map = {};
    locations.forEach(loc => {
      map[loc.name] = loc;
    });
    return map;
  }, [locations]);

  // Execute pathfinding or comparison
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
        if (!res.ok) {
          throw new Error(data.detail || 'Failed to compare algorithms.');
        }
        setCompareResult(data.comparison);
        setRouteResult(data.comparison.dijkstra);
      } else {
        const res = await fetch(
          `${API_BASE}/api/route?source=${encodeURIComponent(source)}&destination=${encodeURIComponent(destination)}&algorithm=${algoToUse}`
        );
        const data = await res.json();
        if (!res.ok) {
          throw new Error(data.detail || 'Failed to calculate shortest path.');
        }
        setRouteResult(data.result);
        setCompareResult(null);
      }
    } catch (err) {
      console.error('Route calculation error:', err);
      setError(err.message);
      setRouteResult(null);
      setCompareResult(null);
    } finally {
      setLoading(false);
    }
  };

  // Swap source and destination
  const handleSwap = () => {
    const temp = source;
    setSource(destination);
    setDestination(temp);
    setRouteResult(null);
    setCompareResult(null);
  };

  // Reset form
  const handleReset = () => {
    setSource('Main Gate');
    setDestination('Hostel');
    setAlgorithm('dijkstra');
    setRouteResult(null);
    setCompareResult(null);
    setError(null);
    setSelectedNodeInfo(null);
  };

  // Check if an edge is part of the active calculated route
  const isEdgeInRoute = (src, dst, path) => {
    if (!path || path.length < 2) return false;
    for (let i = 0; i < path.length - 1; i++) {
      if (
        (path[i] === src && path[i + 1] === dst) ||
        (path[i] === dst && path[i + 1] === src)
      ) {
        return true;
      }
    }
    return false;
  };

  // Node order in active path
  const getNodeOrderInRoute = (nodeName, path) => {
    if (!path) return -1;
    return path.indexOf(nodeName);
  };

  const activePath = routeResult?.path || [];

  return (
    <div className="app-container">
      {/* Top Banner */}
      <header className="top-header">
        <div className="header-left">
          <div className="logo-badge">
            <Compass className="icon-pulse text-indigo-400" size={28} />
          </div>
          <div>
            <div className="header-title-row">
              <h1>Campus Shortest Path Finder</h1>
            </div>
            <p className="header-subtitle">
              Interactive weighted graph navigation using manual Dijkstra and Breadth-First Search (BFS)
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
              <>
                <Sun size={17} className="theme-icon sun" />
                <span>Light Mode</span>
              </>
            ) : (
              <>
                <Moon size={17} className="theme-icon moon" />
                <span>Dark Mode</span>
              </>
            )}
          </button>
        </div>
      </header>

      {/* Main Grid Layout */}
      <main className="main-content">
        {/* Left Column: Navigation Controls & Metrics */}
        <section className="control-sidebar">
          {/* Navigation Form Card */}
          <div className="glass-card">
            <h2 className="card-title">
              <Navigation size={18} />
              <span>Route Configuration</span>
            </h2>

            {/* Source Selection */}
            <div className="form-group">
              <label htmlFor="source-select">
                <span className="dot-indicator green"></span>
                Starting Location
              </label>
              <div className="select-wrapper">
                <select
                  id="source-select"
                  value={source}
                  onChange={(e) => setSource(e.target.value)}
                  className="custom-select"
                >
                  {locations.map((loc) => (
                    <option key={loc.id} value={loc.name}>
                      {loc.name}
                    </option>
                  ))}
                </select>
                <ChevronDown size={16} className="select-chevron" />
              </div>
            </div>

            {/* Swap Button */}
            <div className="swap-row">
              <button
                type="button"
                onClick={handleSwap}
                className="btn-swap"
                title="Swap Start and Destination"
              >
                <ArrowLeftRight size={14} />
                <span>Swap</span>
              </button>
            </div>

            {/* Destination Selection */}
            <div className="form-group">
              <label htmlFor="destination-select">
                <span className="dot-indicator red"></span>
                Destination Location
              </label>
              <div className="select-wrapper">
                <select
                  id="destination-select"
                  value={destination}
                  onChange={(e) => setDestination(e.target.value)}
                  className="custom-select"
                >
                  {locations.map((loc) => (
                    <option key={loc.id} value={loc.name}>
                      {loc.name}
                    </option>
                  ))}
                </select>
                <ChevronDown size={16} className="select-chevron" />
              </div>
            </div>

            {/* Algorithm Selector */}
            <div className="form-group">
              <label>
                <Layers size={14} />
                Select Pathfinding Mode
              </label>
              <div className="algo-selector-tabs">
                <button
                  type="button"
                  className={`tab-btn ${algorithm === 'dijkstra' ? 'active' : ''}`}
                  onClick={() => {
                    setAlgorithm('dijkstra');
                    if (routeResult) handleFindRoute('dijkstra');
                  }}
                >
                  <strong>Dijkstra</strong>
                  <span>Min Distance</span>
                </button>
                <button
                  type="button"
                  className={`tab-btn ${algorithm === 'bfs' ? 'active' : ''}`}
                  onClick={() => {
                    setAlgorithm('bfs');
                    if (routeResult) handleFindRoute('bfs');
                  }}
                >
                  <strong>BFS</strong>
                  <span>Fewest Edges</span>
                </button>
                <button
                  type="button"
                  className={`tab-btn ${algorithm === 'compare' ? 'active' : ''}`}
                  onClick={() => {
                    setAlgorithm('compare');
                    if (routeResult) handleFindRoute('compare');
                  }}
                >
                  <strong>Compare</strong>
                  <span>Side-by-Side</span>
                </button>
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
                  <>
                    <Activity className="spin" size={16} />
                    <span>Calculating Route...</span>
                  </>
                ) : (
                  <>
                    <Compass size={16} />
                    <span>Find Shortest Path</span>
                  </>
                )}
              </button>

              <button
                id="reset-btn"
                className="btn-secondary"
                onClick={handleReset}
                title="Reset to default locations"
              >
                <RotateCcw size={16} />
                <span>Reset</span>
              </button>
            </div>

            {/* Algorithm Explanatory Banner */}
            <div className="algo-info-box">
              <div className="algo-info-header">
                <Info size={15} />
                <strong>
                  {algorithm === 'dijkstra'
                    ? "Dijkstra's Algorithm"
                    : algorithm === 'bfs'
                    ? "Breadth-First Search (BFS)"
                    : "Algorithm Comparison Mode"}
                </strong>
              </div>
              <p className="algo-info-text">
                {algorithm === 'dijkstra' && (
                  <>
                    Uses a <em>priority queue (min-heap)</em> to compute the absolute minimum cumulative walking distance (metres). Time: <code>O((V + E) log V)</code>.
                  </>
                )}
                {algorithm === 'bfs' && (
                  <>
                    Uses a <em>FIFO queue</em> to explore layer-by-layer, finding the path with the fewest turns/intersections (edges). It does <strong>not</strong> optimize for physical distance. Time: <code>O(V + E)</code>.
                  </>
                )}
                {algorithm === 'compare' && (
                  <>
                    Executes both algorithms concurrently on identical inputs. Averages 50 timing iterations in-memory to benchmark performance.
                  </>
                )}
              </p>
            </div>
          </div>

          {/* Error Message */}
          {error && (
            <div className="alert-box error">
              <AlertCircle size={18} />
              <div>
                <strong>Error:</strong> {error}
              </div>
            </div>
          )}

          {/* Route Metrics Card (Single Mode) */}
          {routeResult && algorithm !== 'compare' && (
            <div className="glass-card result-card">
              <div className="card-header-flex">
                <h3 className="card-subtitle">
                  <CheckCircle2 size={16} className="text-emerald-400" />
                  Route Navigation Results
                </h3>
                <span className="badge-pill uppercase">{routeResult.algorithm}</span>
              </div>

              {/* Metrics Row */}
              <div className="metrics-grid">
                <div className="metric-item">
                  <span className="metric-label">Total Distance</span>
                  <span className="metric-value highlight">{routeResult.total_distance} m</span>
                </div>
                <div className="metric-item">
                  <span className="metric-label">Pathways (Edges)</span>
                  <span className="metric-value">{routeResult.edge_count}</span>
                </div>
                <div className="metric-item">
                  <span className="metric-label">Execution Time</span>
                  <span className="metric-value text-amber-300">
                    {routeResult.execution_time_ms ? `${routeResult.execution_time_ms} ms` : '< 0.05 ms'}
                  </span>
                </div>
              </div>

              {/* Step by step path */}
              <div className="path-timeline">
                <span className="timeline-title">Turn-by-Turn Route:</span>
                <div className="path-nodes-list">
                  {routeResult.path.map((nodeName, idx) => (
                    <div key={idx} className="path-node-step">
                      <div className="node-badge">
                        <span className="step-num">{idx + 1}</span>
                      </div>
                      <span className="node-name">{nodeName}</span>
                      {idx < routeResult.path.length - 1 && (
                        <ArrowRight size={14} className="node-arrow" />
                      )}
                    </div>
                  ))}
                </div>
              </div>

              <div className="card-footer-note">
                <small>{routeResult.description}</small>
              </div>
            </div>
          )}

          {/* Side-by-Side Comparison Card */}
          {compareResult && (
            <div className="glass-card comparison-card">
              <div className="card-header-flex">
                <h3 className="card-subtitle">
                  <Activity size={16} className="text-indigo-400" />
                  Algorithm Performance Comparison
                </h3>
                <span className="badge-pill">50 Iterations</span>
              </div>

              {/* Side-by-Side Metrics Table */}
              <div className="comparison-table-wrapper">
                <table className="comparison-table">
                  <thead>
                    <tr>
                      <th>Metric</th>
                      <th>Dijkstra (Distance)</th>
                      <th>BFS (Edge Count)</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td>Total Distance</td>
                      <td className="highlight-green">{compareResult.dijkstra.total_distance} m</td>
                      <td className={compareResult.dijkstra.total_distance < compareResult.bfs.total_distance ? 'highlight-red' : ''}>
                        {compareResult.bfs.total_distance} m
                      </td>
                    </tr>
                    <tr>
                      <td>Pathways (Edges)</td>
                      <td>{compareResult.dijkstra.edge_count}</td>
                      <td className="highlight-green">{compareResult.bfs.edge_count}</td>
                    </tr>
                    <tr>
                      <td>Avg Execution Time</td>
                      <td>{compareResult.dijkstra.execution_time_ms} ms</td>
                      <td>{compareResult.bfs.execution_time_ms} ms</td>
                    </tr>
                    <tr>
                      <td>Route Order</td>
                      <td className="route-cell">{compareResult.dijkstra.path.join(' → ')}</td>
                      <td className="route-cell">{compareResult.bfs.path.join(' → ')}</td>
                    </tr>
                  </tbody>
                </table>
              </div>

              {/* Pedagogical Insight */}
              <div className="insight-box">
                <h4>Pedagogical Analysis</h4>
                <p>{compareResult.pedagogical_insight}</p>
                <small className="disclaimer-text">{compareResult.timing_disclaimer}</small>
              </div>
            </div>
          )}
        </section>

        {/* Right Column: Interactive Campus Graph Visualization */}
        <section className="visualization-container">
          <div className="glass-card map-card">
            <div className="map-header">
              <div>
                <h2 className="card-title">
                  <MapPin size={18} />
                  <span>Interactive Campus Graph Visualization</span>
                </h2>
                <p className="map-subtitle">
                  Nodes represent buildings; edges represent walkable pathways with distances in metres.
                </p>
              </div>

              <div className="legend-pills">
                <span className="legend-item"><span className="legend-dot start"></span> Start</span>
                <span className="legend-item"><span className="legend-dot end"></span> Destination</span>
                <span className="legend-item"><span className="legend-dot active"></span> Active Path</span>
                <span className="legend-item"><span className="legend-dot normal"></span> Campus Path</span>
              </div>
            </div>

            {/* SVG Graph Canvas */}
            <div className="svg-wrapper">
              <svg
                viewBox="0 0 850 560"
                className="campus-svg"
                preserveAspectRatio="xMidYMid meet"
              >
                <defs>
                  {/* Glowing Filter for Active Route */}
                  <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
                    <feGaussianBlur stdDeviation="3.5" result="blur" />
                    <feComposite in="SourceGraphic" in2="blur" operator="over" />
                  </filter>
                  {/* Soft Drop Shadow for Nodes */}
                  <filter id="nodeShadow" x="-10%" y="-10%" width="130%" height="130%">
                    <feDropShadow dx="0" dy="4" stdDeviation="4" floodOpacity="0.4" />
                  </filter>
                </defs>

                {/* Draw Background Campus Grid Lines */}
                <g className="grid-layer" opacity="0.15">
                  {[...Array(12)].map((_, i) => (
                    <line key={`gx-${i}`} x1={i * 80} y1="0" x2={i * 80} y2="560" stroke="#94a3b8" strokeDasharray="3,6" />
                  ))}
                  {[...Array(8)].map((_, i) => (
                    <line key={`gy-${i}`} x1="0" y1={i * 80} x2="850" y2={i * 80} stroke="#94a3b8" strokeDasharray="3,6" />
                  ))}
                </g>

                {/* Draw Graph Edges */}
                <g className="edges-layer">
                  {edges.map((edge) => {
                    const srcLoc = locationMap[edge.source];
                    const dstLoc = locationMap[edge.destination];
                    if (!srcLoc || !dstLoc) return null;

                    const inRoute = isEdgeInRoute(edge.source, edge.destination, activePath);
                    const midX = (srcLoc.x_coord + dstLoc.x_coord) / 2;
                    const midY = (srcLoc.y_coord + dstLoc.y_coord) / 2;

                    return (
                      <g key={edge.id} className={`edge-group ${inRoute ? 'active-edge' : ''}`}>
                        {/* Base Edge Line */}
                        <line
                          x1={srcLoc.x_coord}
                          y1={srcLoc.y_coord}
                          x2={dstLoc.x_coord}
                          y2={dstLoc.y_coord}
                          className={inRoute ? 'pathway-active' : 'pathway-base'}
                          filter={inRoute ? 'url(#glow)' : undefined}
                        />

                        {/* Animated overlay dash if in route */}
                        {inRoute && (
                          <line
                            x1={srcLoc.x_coord}
                            y1={srcLoc.y_coord}
                            x2={dstLoc.x_coord}
                            y2={dstLoc.y_coord}
                            className="pathway-animated"
                          />
                        )}

                        {/* Distance Badge on Edge */}
                        <g transform={`translate(${midX}, ${midY})`} className="edge-distance-badge">
                          <rect
                            x="-22"
                            y="-11"
                            width="44"
                            height="22"
                            rx="11"
                            className={inRoute ? 'badge-rect-active' : 'badge-rect-base'}
                          />
                          <text
                            x="0"
                            y="4"
                            textAnchor="middle"
                            className={inRoute ? 'badge-text-active' : 'badge-text-base'}
                          >
                            {Math.round(edge.distance_meters)}m
                          </text>
                        </g>
                      </g>
                    );
                  })}
                </g>

                {/* Draw Graph Nodes (Buildings) */}
                <g className="nodes-layer">
                  {locations.map((loc) => {
                    const isStart = loc.name === source;
                    const isEnd = loc.name === destination;
                    const orderInPath = getNodeOrderInRoute(loc.name, activePath);
                    const isInPath = orderInPath !== -1;
                    const isHovered = hoveredNode === loc.name;

                    let nodeClass = 'campus-node';
                    if (isStart) nodeClass += ' start-node';
                    else if (isEnd) nodeClass += ' end-node';
                    else if (isInPath) nodeClass += ' path-node';
                    if (isHovered) nodeClass += ' hovered-node';

                    return (
                      <g
                        key={loc.id}
                        transform={`translate(${loc.x_coord}, ${loc.y_coord})`}
                        className={nodeClass}
                        onMouseEnter={() => setHoveredNode(loc.name)}
                        onMouseLeave={() => setHoveredNode(null)}
                        onClick={() => setSelectedNodeInfo(loc)}
                        cursor="pointer"
                        filter="url(#nodeShadow)"
                      >
                        {/* Outer Glow Ring if in path */}
                        {isInPath && (
                          <circle r="34" className="pulse-ring" />
                        )}

                        {/* Main Building Node Circle */}
                        <circle
                          r="26"
                          className="node-circle"
                        />

                        {/* Order Step Number or Icon Indicator */}
                        {isInPath && (
                          <text
                            x="0"
                            y="5"
                            textAnchor="middle"
                            className="order-text"
                          >
                            {orderInPath + 1}
                          </text>
                        )}
                        {!isInPath && (
                          <circle r="5" className="node-center-dot" />
                        )}

                        {/* Building Name Label */}
                        <g transform="translate(0, 42)">
                          <rect
                            x="-65"
                            y="-12"
                            width="130"
                            height="24"
                            rx="12"
                            className="label-bg"
                          />
                          <text
                            x="0"
                            y="4"
                            textAnchor="middle"
                            className="building-label"
                          >
                            {loc.name}
                          </text>
                        </g>
                      </g>
                    );
                  })}
                </g>
              </svg>
            </div>

            {/* Quick Location Detail Modal / Drawer */}
            {selectedNodeInfo && (
              <div className="location-detail-panel">
                <div className="detail-header">
                  <div>
                    <h4 className="detail-title">{selectedNodeInfo.name}</h4>
                    <span className="detail-meta">Coordinates: ({selectedNodeInfo.x_coord}, {selectedNodeInfo.y_coord})</span>
                  </div>
                  <button
                    className="btn-close-detail"
                    onClick={() => setSelectedNodeInfo(null)}
                  >
                    ×
                  </button>
                </div>
                <p className="detail-desc">{selectedNodeInfo.description}</p>
                <div className="detail-actions">
                  <button
                    className="btn-set-start"
                    onClick={() => {
                      setSource(selectedNodeInfo.name);
                      setSelectedNodeInfo(null);
                    }}
                  >
                    Set as Starting Point
                  </button>
                  <button
                    className="btn-set-dest"
                    onClick={() => {
                      setDestination(selectedNodeInfo.name);
                      setSelectedNodeInfo(null);
                    }}
                  >
                    Set as Destination
                  </button>
                </div>
              </div>
            )}

            {/* Footer Disclaimer */}
            <div className="map-footer-disclaimer">
              <span className="notice-badge">Notice</span>
              <span>
                All pathways, distances, and building coordinates are illustrative sample data for university microproject demonstrations, not verified GPS surveyed coordinates.
              </span>
            </div>
          </div>
        </section>
      </main>

    </div>
  );
}
