"""
Generate interactive HTML visualization for all Power BI Semantic Models

Scans the repository for .SemanticModel folders, parses TMDL relationship files,
and creates an interactive HTML viewer with relationship diagrams.

How to run:
  1. Place this script anywhere in your repo (root, scripts/, tools/, etc.)
  2. Open a terminal and run:
  
       python visualize_all_relationships.py              # Scans repo for .SemanticModel folders
       python visualize_all_relationships.py --no-browser # Skip opening browser

  Quick tip: Type "python " then drag this file into your terminal to paste the full path.

  Using VS Code with Copilot? Just ask:
       "Run the visualize_all_relationships.py script"

Requirements: Python 3.7+ (no external dependencies)
"""
import re
import json
import sys
import argparse
from pathlib import Path
from collections import defaultdict
import webbrowser


def parse_tmdl_relationships(file_path):
    """Parse relationships.tmdl file and extract relationship definitions"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"    ✗ Error reading file {file_path}: {e}")
        return []
    
    if not content.strip():
        return []
    
    relationships = []
    
    # Split by relationship blocks
    blocks = re.split(r'(?:^|\n)relationship\s+[\w-]+\n', content, flags=re.MULTILINE)
    rel_ids = re.findall(r'(?:^|\n)relationship\s+([\w-]+)\n', content, flags=re.MULTILINE)
    
    for i, block in enumerate(blocks[1:], 0):  # Skip first empty block
        rel = {'id': rel_ids[i] if i < len(rel_ids) else f'rel_{i}'}
        
        # Extract properties
        from_col_match = re.search(r'fromColumn:\s*(.+)', block)
        to_col_match = re.search(r'toColumn:\s*(.+)', block)
        from_card_match = re.search(r'fromCardinality:\s*(\w+)', block)
        to_card_match = re.search(r'toCardinality:\s*(\w+)', block)
        cross_filter_match = re.search(r'crossFilteringBehavior:\s*(\w+)', block)
        is_active_match = re.search(r'isActive:\s*(\w+)', block)
        
        if from_col_match and to_col_match:
            from_full = from_col_match.group(1).strip()
            to_full = to_col_match.group(1).strip()
            
            # Parse table.column format
            from_parts = from_full.split('.')
            to_parts = to_full.split('.')
            
            # Handle quoted table names
            from_table = from_parts[0].strip("'\"")
            from_column = '.'.join(from_parts[1:]).strip("'\"") if len(from_parts) > 1 else ''
            
            to_table = to_parts[0].strip("'\"")
            to_column = '.'.join(to_parts[1:]).strip("'\"") if len(to_parts) > 1 else ''
            
            rel['from_table'] = from_table
            rel['from_column'] = from_column
            rel['to_table'] = to_table
            rel['to_column'] = to_column
            rel['from_cardinality'] = from_card_match.group(1) if from_card_match else 'many'
            rel['to_cardinality'] = to_card_match.group(1) if to_card_match else 'one'
            rel['cross_filtering'] = cross_filter_match.group(1) if cross_filter_match else 'oneDirection'
            rel['is_active'] = is_active_match.group(1).lower() != 'false' if is_active_match else True
            
            relationships.append(rel)
    
    return relationships


def prepare_model_data(relationships, model_name):
    """Prepare visualization data for a model"""
    nodes = {}
    edges = []
    table_stats = defaultdict(lambda: {'incoming': 0, 'outgoing': 0})
    
    for rel in relationships:
        from_table = rel['from_table']
        to_table = rel['to_table']
        
        # Track statistics
        table_stats[from_table]['outgoing'] += 1
        table_stats[to_table]['incoming'] += 1
        
        # Add nodes if not exists
        if from_table not in nodes:
            nodes[from_table] = {'id': from_table, 'label': from_table, 'connections': []}
        if to_table not in nodes:
            nodes[to_table] = {'id': to_table, 'label': to_table, 'connections': []}
        
        # Track connections
        if to_table not in nodes[from_table]['connections']:
            nodes[from_table]['connections'].append(to_table)
        if from_table not in nodes[to_table]['connections']:
            nodes[to_table]['connections'].append(from_table)
        
        # Create edge
        # Note: In Power BI, filter direction flows FROM dimension (one-side) TO fact (many-side)
        # So we reverse the arrow direction from the TMDL definition
        cardinality = f"{rel['from_cardinality'][0].upper()}:{rel['to_cardinality'][0].upper()}"
        direction = '↔' if rel['cross_filtering'] == 'bothDirections' else '→'
        active_text = '' if rel['is_active'] else ' (inactive)'
        
        # Reverse arrow direction: filter flows from 'to' (dimension) to 'from' (fact)
        edge = {
            'from': to_table,
            'to': from_table,
            'label': f"{cardinality} {direction}{active_text}",
            'title': f"{to_table}.{rel['to_column']} → {from_table}.{rel['from_column']}",
            'arrows': 'to' if rel['cross_filtering'] != 'bothDirections' else 'to, from',
            'dashes': not rel['is_active'],
            'color': '#8E44AD' if rel['cross_filtering'] == 'bothDirections' else ('#999999' if not rel['is_active'] else '#2C3E50'),
            'width': 2.5 if rel['cross_filtering'] == 'bothDirections' else (1 if not rel['is_active'] else 2),
            'from_column': rel['to_column'],
            'to_column': rel['from_column'],
            'cardinality': cardinality,
            'cross_filtering': rel['cross_filtering'],
            'is_active': rel['is_active']
        }
        edges.append(edge)
    
    # Classify tables
    fact_tables = [t for t, stats in table_stats.items() if stats['outgoing'] > stats['incoming']]
    
    # Prepare nodes for vis.js
    vis_nodes = []
    for table_name, node_data in nodes.items():
        is_fact = table_name in fact_tables
        vis_node = {
            'id': table_name,
            'label': table_name,
            'title': f"{table_name}\n{'Fact Table' if is_fact else 'Dimension Table'}\nConnections: {len(node_data['connections'])}",
            'color': {
                'background': '#FF6B6B' if is_fact else '#4ECDC4',
                'border': '#C44545' if is_fact else '#3BA39F',
                'highlight': {
                    'background': '#FF8787' if is_fact else '#6FE8DE',
                    'border': '#A03333' if is_fact else '#2A7A77'
                }
            },
            'shape': 'box' if is_fact else 'ellipse',
            'font': {'size': 14, 'color': '#000000', 'bold': True},
            'connections': node_data['connections']
        }
        vis_nodes.append(vis_node)
    
    return {
        'nodes': vis_nodes,
        'edges': edges,
        'stats': {
            'tables': len(nodes),
            'relationships': len(relationships),
            'facts': len(fact_tables),
            'dimensions': len(nodes) - len(fact_tables)
        }
    }


def create_multi_model_html(models_data, output_path):
    """Create an interactive HTML with dropdown to select models"""
    
    # Create JavaScript object with all models data
    models_json = json.dumps(models_data)
    
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Power BI Semantic Models - Relationship Diagrams</title>
    <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
    <style type="text/css">
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f5f5f5;
        }}
        #header {{
            background-color: #2C3E50;
            color: white;
            padding: 15px 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        #header h1 {{
            margin: 0;
            font-size: 24px;
        }}
        #model-selector {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        #model-selector label {{
            font-size: 14px;
            font-weight: bold;
        }}
        #model-selector select {{
            padding: 8px 12px;
            font-size: 14px;
            border: none;
            border-radius: 4px;
            background-color: white;
            color: #2C3E50;
            cursor: pointer;
            min-width: 300px;
        }}
        #table-filter {{
            position: fixed;
            left: 20px;
            top: 140px;
            width: 280px;
            background: white;
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 15px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            max-height: calc(100vh - 160px);
            overflow-y: auto;
            display: none;
            z-index: 2000;
        }}
        #table-filter h3 {{
            margin-top: 0;
            color: #2C3E50;
            border-bottom: 2px solid #3498DB;
            padding-bottom: 10px;
            font-size: 16px;
        }}
        #table-filter .close-btn {{
            float: right;
            cursor: pointer;
            color: #999;
            font-size: 20px;
            font-weight: bold;
            line-height: 20px;
        }}
        #table-filter .close-btn:hover {{
            color: #333;
        }}
        #table-filter .filter-controls {{
            margin-bottom: 10px;
            display: flex;
            gap: 8px;
        }}
        #table-filter .filter-controls button {{
            padding: 6px 12px;
            font-size: 12px;
            border: 1px solid #ddd;
            border-radius: 4px;
            background-color: #f8f9fa;
            cursor: pointer;
            flex: 1;
        }}
        #table-filter .filter-controls button:hover {{
            background-color: #e9ecef;
        }}
        #table-filter .table-list {{
            max-height: calc(100vh - 260px);
            overflow-y: auto;
        }}
        #table-filter .table-item {{
            display: flex;
            align-items: center;
            padding: 6px;
            margin: 4px 0;
            cursor: pointer;
            border-radius: 4px;
            font-size: 13px;
        }}
        #table-filter .table-item:hover {{
            background-color: #f8f9fa;
        }}
        #table-filter .table-item input[type="checkbox"] {{
            margin-right: 8px;
            cursor: pointer;
        }}
        #table-filter .table-item.fact {{
            color: #C44545;
            font-weight: 500;
        }}
        #table-filter .table-item.dim {{
            color: #3BA39F;
        }}
        #toggle-filter-btn {{
            position: fixed;
            left: 20px;
            top: 140px;
            padding: 10px 15px;
            background-color: #3498DB;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 13px;
            font-weight: bold;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
            z-index: 1000;
        }}
        #toggle-filter-btn:hover {{
            background-color: #2980B9;
        }}
        #highlight-mode-toggle {{
            position: static;
            padding: 8px 12px;
            background-color: #9B59B6;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }}
        #highlight-mode-toggle:hover {{
            background-color: #8E44AD;
        }}
        #highlight-mode-toggle.directional {{
            background-color: #E67E22;
        }}
        #highlight-mode-toggle.directional:hover {{
            background-color: #D35400;
        }}
        #stats {{
            background-color: #34495E;
            color: white;
            padding: 8px 20px;
            display: flex;
            justify-content: center;
            gap: 40px;
            font-size: 13px;
        }}
        #mynetwork {{
            width: 100%;
            height: calc(100vh - 140px);
            border: 1px solid #ddd;
            background-color: white;
        }}
        #info-panel {{
            position: fixed;
            right: 20px;
            top: 140px;
            width: 320px;
            background: white;
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 15px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            max-height: calc(100vh - 160px);
            overflow-y: auto;
            display: none;
            z-index: 2000;
        }}
        #info-panel h3 {{
            margin-top: 0;
            color: #2C3E50;
            border-bottom: 2px solid #3498DB;
            padding-bottom: 10px;
        }}
        #info-panel .close-btn {{
            float: right;
            cursor: pointer;
            color: #999;
            font-size: 20px;
            font-weight: bold;
            line-height: 20px;
        }}
        #info-panel .close-btn:hover {{
            color: #333;
        }}
        .relationship-item {{
            margin: 10px 0;
            padding: 10px;
            background-color: #f8f9fa;
            border-left: 3px solid #3498DB;
            border-radius: 4px;
        }}
        .relationship-item.inactive {{
            border-left-color: #999;
            opacity: 0.7;
        }}
        .relationship-item strong {{
            color: #2C3E50;
        }}
        .relationship-item .detail {{
            font-size: 12px;
            color: #666;
            margin-top: 5px;
        }}
        .legend {{
            background-color: white;
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 10px 20px;
            margin: 10px 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            display: flex;
            align-items: center;
            gap: 25px;
            flex-wrap: wrap;
        }}
        .legend h3 {{
            margin: 0;
            color: #2C3E50;
            font-size: 16px;
        }}
        .legend-item {{
            display: flex;
            align-items: center;
            font-size: 13px;
        }}
        .legend-color {{
            width: 30px;
            height: 20px;
            margin-right: 10px;
            border: 1px solid #333;
            border-radius: 3px;
        }}
        .legend-color.fact {{
            background-color: #FF6B6B;
        }}
        .legend-color.dim {{
            background-color: #4ECDC4;
            border-radius: 50%;
        }}
        .legend-line {{
            width: 30px;
            height: 2px;
            margin-right: 10px;
        }}
        .legend-line.normal {{
            background-color: #2C3E50;
        }}
        .legend-line.bidirectional {{
            background-color: #8E44AD;
            height: 3px;
        }}
        .legend-line.inactive {{
            background-color: #999;
            border-top: 2px dashed #999;
            height: 0;
        }}
        .instructions {{
            background-color: #FFF3CD;
            border: 1px solid #FFE69C;
            border-radius: 8px;
            padding: 10px 20px;
            margin: 10px 20px;
            color: #856404;
            font-size: 13px;
        }}
        .instructions strong {{
            display: inline;
            margin-right: 8px;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div id="header">
        <h1>🔗 Power BI Semantic Models - Relationships</h1>
        <div id="model-selector">
            <label for="model-select">Select Model:</label>
            <select id="model-select" onchange="loadModel(this.value)">
                <option value="">-- Choose a model --</option>
            </select>
        </div>
    </div>
    <div id="stats">
        <div>📊 <strong id="stat-tables">0</strong> Tables</div>
        <div>🔗 <strong id="stat-relationships">0</strong> Relationships</div>
        <div>📦 <strong id="stat-facts">0</strong> Fact Tables</div>
        <div>🏷️ <strong id="stat-dimensions">0</strong> Dimension Tables</div>
    </div>
    
    <div class="instructions">
        <strong>💡 Interactive Controls:</strong>
        Select a model from the dropdown above. Click on any table to highlight its direct relationships. Connected tables remain colored while unrelated tables are greyed out. Click empty space to reset. Use mouse wheel to zoom, drag to pan.
    </div>
    
    <div class="legend">
        <h3>Legend</h3>
        <div class="legend-item">
            <div class="legend-color fact"></div>
            <span>Fact Table</span>
        </div>
        <div class="legend-item">
            <div class="legend-color dim"></div>
            <span>Dimension Table</span>
        </div>
        <div class="legend-item">
            <div class="legend-line normal"></div>
            <span>One-way</span>
        </div>
        <div class="legend-item">
            <div class="legend-line bidirectional"></div>
            <span>Bidirectional</span>
        </div>
        <div class="legend-item">
            <div class="legend-line inactive"></div>
            <span>Inactive</span>
        </div>
        <button id="highlight-mode-toggle" title="Click to toggle between highlighting all related tables or only tables filtered by selected table">
            Mode: All Relations
        </button>
    </div>
    
    <button id="toggle-filter-btn" onclick="toggleTableFilter()">📋 Filter Tables</button>
    
    <div id="table-filter">
        <span class="close-btn" onclick="toggleTableFilter()">×</span>
        <h3>Filter Tables</h3>
        <div class="filter-controls">
            <button onclick="selectAllTables()">Select All</button>
            <button onclick="deselectAllTables()">Deselect All</button>
        </div>
        <div class="table-list" id="table-list"></div>
    </div>
    
    <div id="mynetwork"></div>
    
    <div id="info-panel">
        <span class="close-btn" onclick="closeInfoPanel()">×</span>
        <h3 id="selected-table-name">Table Information</h3>
        <div id="relationships-list"></div>
    </div>

    <script type="text/javascript">
        // All models data
        const modelsData = {models_json};
        
        let network = null;
        let nodes = null;
        let edges = null;
        let currentModelData = null;
        let selectedNode = null;
        let visibleTables = new Set();
        let allNodesData = [];
        let allEdgesData = [];
        
        // Populate dropdown
        const select = document.getElementById('model-select');
        Object.keys(modelsData).sort().forEach(modelName => {{
            const option = document.createElement('option');
            option.value = modelName;
            option.textContent = modelName;
            select.appendChild(option);
        }});
        
        // Load first model by default
        if (Object.keys(modelsData).length > 0) {{
            const firstModel = Object.keys(modelsData).sort()[0];
            select.value = firstModel;
            loadModel(firstModel);
        }}
        
        // Highlight mode toggle
        let highlightDirectional = false;
        const toggleBtn = document.getElementById('highlight-mode-toggle');
        toggleBtn.addEventListener('click', () => {{
            highlightDirectional = !highlightDirectional;
            toggleBtn.textContent = highlightDirectional ? 'Mode: Filter Direction' : 'Mode: All Relations';
            toggleBtn.classList.toggle('directional', highlightDirectional);
            resetHighlight();
        }});
        
        function loadModel(modelName) {{
            if (!modelName || !modelsData[modelName]) return;
            
            currentModelData = modelsData[modelName];
            const data = currentModelData.data;
            
            // Store original data
            allNodesData = data.nodes;
            allEdgesData = data.edges;
            
            // Initialize all tables as visible
            visibleTables = new Set(allNodesData.map(n => n.id));
            
            // Update stats
            document.getElementById('stat-tables').textContent = currentModelData.stats.tables;
            document.getElementById('stat-relationships').textContent = currentModelData.stats.relationships;
            document.getElementById('stat-facts').textContent = currentModelData.stats.facts;
            document.getElementById('stat-dimensions').textContent = currentModelData.stats.dimensions;
            
            // Populate table filter list
            populateTableFilter();
            
            // Create or update network
            nodes = new vis.DataSet(data.nodes);
            edges = new vis.DataSet(data.edges);
            
            const container = document.getElementById('mynetwork');
            const networkData = {{ nodes: nodes, edges: edges }};
            
            const options = {{
                physics: {{
                    enabled: true,
                    solver: 'forceAtlas2Based',
                    forceAtlas2Based: {{
                        gravitationalConstant: -50,
                        centralGravity: 0.01,
                        springLength: 150,
                        springConstant: 0.08,
                        damping: 0.4,
                        avoidOverlap: 0.5
                    }},
                    stabilization: {{
                        enabled: true,
                        iterations: 200,
                        updateInterval: 25
                    }}
                }},
                interaction: {{
                    hover: true,
                    tooltipDelay: 100,
                    navigationButtons: true,
                    keyboard: true
                }},
                edges: {{
                    smooth: {{
                        type: 'continuous',
                        roundness: 0.5
                    }},
                    font: {{
                        size: 11,
                        align: 'middle'
                    }}
                }},
                nodes: {{
                    borderWidth: 2,
                    borderWidthSelected: 4
                }}
            }};
            
            if (network) {{
                network.destroy();
            }}
            
            network = new vis.Network(container, networkData, options);
            
            // Click on node
            network.on('click', function(params) {{
                if (params.nodes.length > 0) {{
                    const nodeId = params.nodes[0];
                    selectNode(nodeId);
                }} else {{
                    resetHighlight();
                }}
            }});
            
            closeInfoPanel();
        }}
        
        function selectNode(nodeId) {{
            selectedNode = nodeId;
            const nodeData = allNodesData.find(n => n.id === nodeId);
            
            if (!nodeData) return;
            
            // Only work with visible nodes
            const visibleNodesArray = allNodesData.filter(n => visibleTables.has(n.id));
            
            // Get connected nodes (only among visible ones)
            let connectedNodes;
            if (highlightDirectional) {{
                // Recursively find ALL tables that are filtered BY the selected table
                // Follow the arrow chain: if A filters B, and B filters C, then A transitively filters C
                // For bidirectional relationships (many-to-many), follow both directions
                connectedNodes = new Set();
                const toVisit = [nodeId];
                const visited = new Set([nodeId]);
                
                while (toVisit.length > 0) {{
                    const current = toVisit.shift();
                    allEdgesData.forEach(e => {{
                        // Follow outgoing edges: current table filters another table
                        if (e.from === current && visibleTables.has(e.to) && !visited.has(e.to)) {{
                            connectedNodes.add(e.to);
                            visited.add(e.to);
                            toVisit.push(e.to);
                        }}
                        // Follow incoming edges: another table filters current table
                        if (e.to === current && visibleTables.has(e.from) && !visited.has(e.from)) {{
                            connectedNodes.add(e.from);
                            visited.add(e.from);
                            toVisit.push(e.from);
                        }}
                    }});
                }}
            }} else {{
                // Original behavior: all connections
                connectedNodes = new Set(nodeData.connections.filter(c => visibleTables.has(c)));
            }}
            connectedNodes.add(nodeId);
            
            // Update node styles (only for visible nodes)
            visibleNodesArray.forEach(node => {{
                if (connectedNodes.has(node.id)) {{
                    nodes.update({{
                        id: node.id,
                        color: node.color,
                        opacity: 1
                    }});
                }} else {{
                    nodes.update({{
                        id: node.id,
                        color: {{
                            background: '#E0E0E0',
                            border: '#BDBDBD',
                            highlight: {{
                                background: '#E0E0E0',
                                border: '#BDBDBD'
                            }}
                        }},
                        opacity: 0.3
                    }});
                }}
            }});
            
            // Update edge styles (only for visible edges)
            const visibleEdgesArray = allEdgesData.filter(e => 
                visibleTables.has(e.from) && visibleTables.has(e.to)
            );
            
            const relatedEdges = allEdgesData.filter(e => 
                (e.from === nodeId || e.to === nodeId) && 
                visibleTables.has(e.from) && visibleTables.has(e.to)
            );
            
            const currentEdges = edges.get();
            visibleEdgesArray.forEach(edge => {{
                let isRelated;
                if (highlightDirectional) {{
                    // Highlight edges in the filter chain
                    // Both nodes must be in the connected set (either direct or transitive)
                    isRelated = connectedNodes.has(edge.from) && connectedNodes.has(edge.to);
                }} else {{
                    // Original behavior: both directions
                    isRelated = edge.from === nodeId || edge.to === nodeId;
                }}
                
                const edgeInGraph = currentEdges.find(e => 
                    e.from === edge.from && e.to === edge.to
                );
                if (edgeInGraph) {{
                    edges.update({{
                        id: edgeInGraph.id,
                        color: isRelated ? edge.color : '#E0E0E0',
                        width: isRelated ? edge.width : 1,
                        opacity: isRelated ? 1 : 0.2
                    }});
                }}
            }});
            
            // Show info panel (always show all relationships regardless of mode)
            showInfoPanel(nodeId, relatedEdges);
        }}
        
        function resetHighlight() {{
            selectedNode = null;
            
            // Only restore visible nodes
            const visibleNodesArray = allNodesData.filter(n => visibleTables.has(n.id));
            visibleNodesArray.forEach(node => {{
                nodes.update({{
                    id: node.id,
                    color: node.color,
                    opacity: 1
                }});
            }});
            
            // Only restore visible edges
            const visibleEdgesArray = allEdgesData.filter(e => 
                visibleTables.has(e.from) && visibleTables.has(e.to)
            );
            const currentEdges = edges.get();
            visibleEdgesArray.forEach(edge => {{
                const edgeInGraph = currentEdges.find(e => 
                    e.from === edge.from && e.to === edge.to
                );
                if (edgeInGraph) {{
                    edges.update({{
                        id: edgeInGraph.id,
                        color: edge.color,
                        width: edge.width,
                        opacity: 1
                    }});
                }}
            }});
            
            closeInfoPanel();
        }}
        
        function showInfoPanel(nodeId, relatedEdges) {{
            const panel = document.getElementById('info-panel');
            const tableName = document.getElementById('selected-table-name');
            const relationshipsList = document.getElementById('relationships-list');
            
            tableName.textContent = nodeId;
            
            let html = '<div style="margin-bottom: 15px; color: #666;">' + 
                       '<strong>' + relatedEdges.length + '</strong> direct relationship(s)</div>';
            
            relatedEdges.forEach(edge => {{
                const isOutgoing = edge.from === nodeId;
                const otherTable = isOutgoing ? edge.to : edge.from;
                const direction = edge.arrows === 'to, from' ? '↔' : (isOutgoing ? '→' : '←');
                const inactiveClass = edge.is_active ? '' : ' inactive';
                
                html += '<div class="relationship-item' + inactiveClass + '">';
                html += '<strong>' + direction + ' ' + otherTable + '</strong>';
                html += '<div class="detail">';
                html += 'Cardinality: ' + edge.cardinality + '<br>';
                html += (isOutgoing ? nodeId : otherTable) + '.' + edge.from_column + 
                       ' → ' + (isOutgoing ? otherTable : nodeId) + '.' + edge.to_column;
                if (!edge.is_active) {{
                    html += '<br><em>Inactive</em>';
                }}
                html += '</div></div>';
            }});
            
            relationshipsList.innerHTML = html;
            panel.style.display = 'block';
        }}
        
        function closeInfoPanel() {{
            document.getElementById('info-panel').style.display = 'none';
        }}
        
        function toggleTableFilter() {{
            const panel = document.getElementById('table-filter');
            const btn = document.getElementById('toggle-filter-btn');
            if (panel.style.display === 'none' || panel.style.display === '') {{
                panel.style.display = 'block';
                btn.style.display = 'none';
            }} else {{
                panel.style.display = 'none';
                btn.style.display = 'block';
            }}
        }}
        
        function populateTableFilter() {{
            const tableList = document.getElementById('table-list');
            if (!tableList) return;
            
            tableList.innerHTML = '';
            
            // Get fact tables
            const factTables = allNodesData.filter(n => n.shape === 'box').map(n => n.id);
            
            // Sort tables alphabetically
            const sortedTables = [...allNodesData].sort((a, b) => a.id.localeCompare(b.id));
            
            sortedTables.forEach(node => {{
                const isFact = factTables.includes(node.id);
                const div = document.createElement('div');
                div.className = 'table-item ' + (isFact ? 'fact' : 'dim');
                
                const checkbox = document.createElement('input');
                checkbox.type = 'checkbox';
                checkbox.id = 'table-' + node.id.replace(/[^a-zA-Z0-9]/g, '_');
                checkbox.checked = visibleTables.has(node.id);
                checkbox.setAttribute('data-table-id', node.id);
                
                const label = document.createElement('label');
                label.textContent = node.id;
                label.style.cursor = 'pointer';
                label.setAttribute('for', checkbox.id);
                
                div.appendChild(checkbox);
                div.appendChild(label);
                tableList.appendChild(div);
            }});
            
            // Add event listeners after all elements are created
            sortedTables.forEach(node => {{
                const checkboxId = 'table-' + node.id.replace(/[^a-zA-Z0-9]/g, '_');
                const checkbox = document.getElementById(checkboxId);
                console.log('Looking for checkbox:', checkboxId, 'Found:', checkbox);
                if (checkbox) {{
                    checkbox.addEventListener('change', function() {{
                        const tableId = this.getAttribute('data-table-id');
                        console.log('Checkbox changed for:', tableId);
                        toggleTable(tableId);
                    }});
                }} else {{
                    console.error('Checkbox not found for table:', node.id);
                }}
            }});
        }}
        
        function toggleTable(tableId) {{
            console.log('toggleTable called for:', tableId);
            if (visibleTables.has(tableId)) {{
                visibleTables.delete(tableId);
                console.log('Removed table:', tableId);
            }} else {{
                visibleTables.add(tableId);
                console.log('Added table:', tableId);
            }}
            updateVisibleTables();
        }}
        
        function selectAllTables() {{
            visibleTables = new Set(allNodesData.map(n => n.id));
            updateTableCheckboxes();
            updateVisibleTables();
        }}
        
        function deselectAllTables() {{
            visibleTables.clear();
            updateTableCheckboxes();
            updateVisibleTables();
        }}
        
        function updateTableCheckboxes() {{
            allNodesData.forEach(node => {{
                const checkbox = document.getElementById('table-' + node.id.replace(/[^a-zA-Z0-9]/g, '_'));
                if (checkbox) {{
                    checkbox.checked = visibleTables.has(node.id);
                }}
            }});
        }}
        
        function updateVisibleTables() {{
            if (!nodes || !edges) return;
            
            // Filter nodes
            const visibleNodes = allNodesData.filter(n => visibleTables.has(n.id));
            
            // Filter edges (only show if both tables are visible)
            const visibleEdges = allEdgesData.filter(e => 
                visibleTables.has(e.from) && visibleTables.has(e.to)
            );
            
            // Clear and update datasets
            try {{
                nodes.clear();
                edges.clear();
                
                if (visibleNodes.length > 0) {{
                    nodes.add(visibleNodes);
                }}
                if (visibleEdges.length > 0) {{
                    edges.add(visibleEdges);
                }}
                
                // Fit the network to show all visible nodes
                if (network && visibleNodes.length > 0) {{
                    network.fit({{
                        animation: {{
                            duration: 500,
                            easingFunction: 'easeInOutQuad'
                        }}
                    }});
                }}
            }} catch (e) {{
                console.error('Error updating visible tables:', e);
            }}
            
            // Update stats
            const factCount = visibleNodes.filter(n => n.shape === 'box').length;
            document.getElementById('stat-tables').textContent = visibleNodes.length;
            document.getElementById('stat-relationships').textContent = visibleEdges.length;
            document.getElementById('stat-facts').textContent = factCount;
            document.getElementById('stat-dimensions').textContent = visibleNodes.length - factCount;
            
            // Reset selection if selected node is no longer visible
            if (selectedNode && !visibleTables.has(selectedNode)) {{
                selectedNode = null;
                closeInfoPanel();
            }}
        }}
    </script>
</body>
</html>"""
    
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"✓ Multi-model interactive HTML saved to: {output_path}")
    except Exception as e:
        print(f"✗ Error writing HTML file: {e}")
        raise


def find_relationship_files(search_path: Path) -> list:
    """Recursively find all relationships.tmdl files under search_path"""
    print(f"🔍 Scanning for semantic models in: {search_path}")
    
    if not search_path.exists():
        print(f"❌ Error: Search path does not exist: {search_path}")
        return []
    
    relationship_files = list(search_path.glob("**/*.SemanticModel/definition/relationships.tmdl"))
    
    if not relationship_files:
        print(f"⚠️  No semantic models found with relationships.tmdl files")
        print(f"   Expected structure: <ModelName>.SemanticModel/definition/relationships.tmdl")
    
    return relationship_files


def main():
    parser = argparse.ArgumentParser(
        description='Generate interactive HTML visualization for Power BI Semantic Model relationships',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s
  %(prog)s --search-path ./my_models
  %(prog)s --no-browser
        """
    )
    
    parser.add_argument(
        '--search-path',
        type=Path,
        default=Path.cwd(),
        help='Root directory to search for .SemanticModel folders (default: scans entire repo from current directory)'
    )
    
    parser.add_argument(
        '--no-browser',
        action='store_true',
        help='Skip automatically opening the HTML file in browser'
    )
    
    args = parser.parse_args()
    
    # Find all relationships.tmdl files
    relationship_files = find_relationship_files(args.search_path)
    
    if not relationship_files:
        print("\n💡 No semantic models found in repository.")
        print("   Make sure your .SemanticModel folders contain definition/relationships.tmdl files.")
        print("   Or use --search-path to specify a different directory.")
        return 1
    
    print(f"Found {len(relationship_files)} semantic models")
    
    models_data = {}
    
    for rel_file in relationship_files:
        # Extract model name
        model_name = rel_file.parts[-3].replace('.SemanticModel', '')
        
        print(f"  Processing: {model_name}")
        
        try:
            relationships = parse_tmdl_relationships(rel_file)
            
            if relationships:
                model_data = prepare_model_data(relationships, model_name)
                models_data[model_name] = {
                    'data': model_data,
                    'stats': model_data['stats']
                }
                print(f"    ✓ {model_data['stats']['relationships']} relationships, {model_data['stats']['tables']} tables")
            else:
                print(f"    ⚠ No relationships found")
        except Exception as e:
            print(f"    ✗ Error: {e}")
    
    if not models_data:
        print("\n⚠️  No models with relationships found.")
        return 1
    
    # Set output path
    output_path = Path.cwd() / "relationships_viewer.html"
    
    print(f"\n🎨 Creating multi-model viewer...")
    create_multi_model_html(models_data, output_path)
    
    print(f"\n✅ Done! Visualization saved to: {output_path}")
    print(f"   Models available: {len(models_data)}")
    
    # Open in default browser unless --no-browser flag is set
    if not args.no_browser:
        print(f"   Opening in browser...")
        webbrowser.open(output_path.as_uri())
    else:
        print(f"   Open manually: {output_path}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
