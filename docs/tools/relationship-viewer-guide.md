# Power BI Relationship Visualizer

Interactive HTML visualization tool for Power BI semantic model relationships from TMDL files.

[:material-download: Download Script](https://raw.githubusercontent.com/JoeRossouw/semantic_ops/main/scripts/visualize_all_relationships.py){ .md-button .md-button--primary }
[:fontawesome-brands-github: View on GitHub](https://github.com/JoeRossouw/semantic_ops/blob/main/scripts/visualize_all_relationships.py){ .md-button }

[:material-eye: **View Live Demo** →](../demos/relationships_viewer.html){ .md-button .md-button--primary target="_blank" }

---

## Live Demo

**[🔍 Open Interactive Demo](../demos/relationships_viewer.html){ target="_blank" }**

Try the interactive relationship visualizer with 6 sample Power BI models:

- **Switch between models** using the dropdown (Model_A through Model_F)
- **Click any table** to highlight its relationships (try both visualization modes)
- **Toggle modes** between "All Relations" (direct connections) and "Filter Direction" (transitive filter chains)
- **Filter tables** using the side panel to focus on specific areas of complex models
- **Interactive graph** - zoom with mouse wheel, drag to pan, physics-based auto-layout

The demo shows real model relationships (with anonymized data) from models ranging from simple (2-3 relationships) to complex (14 relationships). Perfect for seeing the tool in action before running it on your own models.

---

## Overview

This tool scans for Power BI semantic models in TMDL format, parses relationship definitions, and generates an interactive HTML diagram showing table relationships, cardinalities, and filter directions.

### Key Features

**🔍 Full Repository Visibility**
- **Automatic Discovery**: Recursively scans entire repo for all `.SemanticModel` folders, no manual configuration
- **Multi-Model Dropdown**: Single HTML file contains all models found; switch between them instantly
- **Zero Setup**: Just run the script and it finds everything

**🎯 Interactive Model Filtering**
- **Model Selector**: Dropdown menu to switch between different semantic models in your workspace
- **Table Filter Panel**: Click "📋 Filter Tables" button to show/hide specific tables from the visualization
- **Select All/Deselect All**: Quickly toggle entire sets of tables on/off
- **Fact/Dimension Classification**: Automatically identifies and color-codes table types based on relationship patterns
- **Visual Filtering**: Focus on specific portions of complex models without losing context

**🔗 Relationship Visualization Modes**
- **All Relations Mode** (default): Click any table to highlight all its direct relationships
  - Shows every table connected by at least one relationship
  - Great for understanding local connectivity
- **Filter Direction Mode**: Click any table to visualize the complete filter propagation chain
  - Follows arrows transitively. If Table A filters B, and B filters C, all three are highlighted
  - Handles bidirectional relationships (many-to-many) by following both directions
  - Perfect for understanding how selections flow through your model
- **Toggle Button**: Switch modes on the fly to analyze different aspects of model behavior

**📊 Smart Visual Design**
- **Fact Tables**: Red rectangles (tables with more outgoing than incoming relationships)
- **Dimension Tables**: Teal circles (tables with more incoming relationships)
- **One-Way Relationships**: Dark gray arrows showing standard filter direction
- **Bidirectional Relationships**: Purple arrows with wider lines (many-to-many)
- **Inactive Relationships**: Dashed gray lines
- **Hover Tooltips**: See cardinality, column mappings, and relationship status

**🎨 Production-Ready Output**
- **Self-Contained HTML**: Single file (500KB-2MB) with all data and interactivity embedded
- **Offline Capable**: No external dependencies except CDN-hosted vis.js library
- **Shareable**: Send to stakeholders, embed in documentation, store in wikis
- **CI/CD Friendly**: Generate relationship diagrams automatically in build pipelines
- **Interactive Physics**: Zoom with mouse wheel, pan by dragging, auto-layout optimization

## Prerequisites

- **Python**: 3.7 or higher
- **Dependencies**: None (uses Python standard library only)
- **Input Format**: Power BI semantic models in TMDL format (`.SemanticModel` folders)

## Installation

No installation required. Download the script using the button above, or:

```bash
curl -O https://raw.githubusercontent.com/JoeRossouw/semantic_ops/main/scripts/visualize_all_relationships.py
```

## Usage

### Basic Usage

**Just run it** - the script automatically scans your entire repository:

```bash
python visualize_all_relationships.py
```

This will:
1. Recursively search from the current directory for all `.SemanticModel` folders
2. Parse all `relationships.tmdl` files found
3. Generate `relationships_viewer.html` in the current directory
4. Automatically open the HTML file in your default browser

### Advanced Options

**Skip opening browser:**
```bash
python visualize_all_relationships.py --no-browser
```

**Search a specific directory only:**
```bash
python visualize_all_relationships.py --search-path ./my_models
```

**Combine options:**
```bash
python visualize_all_relationships.py \
  --search-path ./my_models \
  --no-browser
```

### Command-Line Options

| Option | Description | Default |
|--------|-------------|---------|-----|
| `--search-path <path>` | Limit search to specific directory | Scans entire repo recursively |
| `--no-browser` | Skip automatically opening HTML in browser | Opens browser |

## Expected Folder Structure

The script works with any folder structure containing Power BI semantic models in TMDL format:

```
your_project/
├── Sales.SemanticModel/
│   └── definition/
│       ├── relationships.tmdl    ← Parsed by this tool
│       ├── tables/
│       └── model.tmdl
├── Finance.SemanticModel/
│   └── definition/
│       └── relationships.tmdl    ← Parsed by this tool
└── my_models/
    └── Inventory.SemanticModel/
        └── definition/
            └── relationships.tmdl    ← Parsed by this tool
```

The script recursively searches for any `*.SemanticModel/definition/relationships.tmdl` files regardless of folder depth or naming conventions.

## Interactive Viewer Features

### Visualization Elements

- **Fact Tables**: Red rectangles (tables with more outgoing than incoming relationships)
- **Dimension Tables**: Teal circles (tables with more incoming than outgoing relationships)
- **One-Way Relationships**: Dark gray arrows (standard filter direction)
- **Bidirectional Relationships**: Purple arrows (both directions, wider line)
- **Inactive Relationships**: Dashed gray lines

### Interactive Controls

1. **Model Selector**: Dropdown menu to switch between different semantic models
2. **Table Filter**: Click "📋 Filter Tables" button to show/hide specific tables
3. **Highlight Mode Toggle**: Switch between:
   - **All Relations**: Shows all directly connected tables
   - **Filter Direction**: Shows transitive filter propagation chain
4. **Click Interactions**:
   - Click any table → Highlights related tables and relationships
   - Click empty space → Reset highlighting
   - Hover over elements → View tooltips with details
5. **Navigation**: Mouse wheel to zoom, click-drag to pan

### Statistics Panel

Displays real-time counts for the selected model:
- Total tables
- Total relationships
- Fact tables count
- Dimension tables count

## Output

The generated HTML file is **self-contained** (no external dependencies except CDN-hosted vis.js library) and includes:

- All relationship data embedded as JSON
- Full interactive visualization
- CSS styling
- JavaScript logic for interactivity

**File size**: Typically 500KB - 2MB depending on model complexity

## Troubleshooting

### No semantic models found

```
⚠️ No semantic models found with relationships.tmdl files
Expected structure: <ModelName>.SemanticModel/definition/relationships.tmdl
```

**Solution**: 
- Verify your models are in TMDL format (not `.bim` or legacy formats)
- Check that `relationships.tmdl` files exist in the `definition/` subfolder
- Use `--search-path` to specify the correct directory

### Empty visualization

If semantic models are found but no relationships appear, check that your `relationships.tmdl` files contain valid relationship definitions in TMDL format.

### Browser doesn't open

Use the `--no-browser` flag and manually open the output HTML file, or check that you have a default browser configured.

## CI/CD Integration

This tool works seamlessly in automated pipelines:

```yaml
# Example GitHub Actions workflow
- name: Generate Relationship Diagrams
  run: |
    python visualize_all_relationships.py \
      --search-path ./semantic_models \
      --no-browser

- name: Upload Artifact
  uses: actions/upload-artifact@v3
  with:
    name: relationship-diagrams
    path: ./relationships_viewer.html
```

## Technical Details

- **Parser**: Custom regex-based TMDL relationship parser
- **Visualization Library**: vis.js Network (loaded from CDN)
- **Graph Layout**: ForceAtlas2 physics simulation
- **Browser Compatibility**: Modern browsers (Chrome, Firefox, Edge, Safari)

