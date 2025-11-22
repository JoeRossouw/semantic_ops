
# Demo: Building a Power BI Relationship Viewer with Agentic AI

## Overview
This demo showcases how to build a production-ready interactive relationship viewer for Power BI semantic models using conversational AI prompts. What traditionally would take hours of coding is accomplished in minutes through iterative refinement.

## The Progressive Prompt Sequence

### Prompt 1: Initial Request
```
I need to visualize the relationships in my Power BI semantic models. 
I have TMDL format semantic models with relationships.tmdl files in my repo.

Can you create an interactive visualization showing how tables are connected?
Important: Arrow direction should show filter flow (dimension → fact), not the 
TMDL fromColumn/toColumn order.
```

**What happens:** AI creates a Python script that parses TMDL format and generates a network diagram.

---

### Prompt 2: Make it Interactive
```
This is great, but can we make it interactive HTML instead? 
I want to click on a table and see only its direct relationships, 
with unrelated tables greyed out.
```

**What happens:** AI rewrites to use vis.js for web-based interaction, adds click handlers and highlighting logic.

---

### Prompt 3: Polish the UI
```
Can you make the legend take up less space and display horizontally 
next to each other instead of stacked?
```

**What happens:** AI refactors CSS to create a compact, horizontal legend layout with responsive design.

---

### Prompt 4: Scale it Up
```
Can we add a dropdown to select any model in my repo? 
It should automatically find all .SemanticModel folders and parse their relationships.
```

**What happens:** AI adds recursive scanning to find all semantic models in the repo, builds a multi-model viewer with dropdown selection and dynamic loading.

---

### Prompt 5: Make it Portable
```
I want to share this script publicly. Make it portable:
- Remove any hardcoded paths or repo structure assumptions
- Add command-line arguments for search path and output location
- Make it scan from current directory by default
- Add --no-browser flag to skip auto-opening
- Include proper error handling and user-friendly messages
- Create a professional README
```

**What happens:** AI refactors with argparse, flexible path discovery, creates comprehensive documentation, and makes it work from any directory structure.

---

### Prompt 6: Add Table Filtering
```
Can we have a multi-select filter panel where I can select/unselect tables 
and they dynamically appear/disappear from the graph? Include Select All 
and Deselect All buttons. Make sure the panel has proper z-index so it appears 
above the graph canvas. When highlighting relationships by clicking a table, 
only work with currently visible tables (respect the filter).
```

**What happens:** AI adds a collapsible filter panel (left side) with checkboxes for each table, real-time graph updates as tables are toggled, and automatic stats recalculation. 

**Common issues to watch for:**
- If checkboxes aren't clickable → mention z-index layering issue
- If filtered tables reappear when clicking nodes → mention to respect visibleTables filter in selectNode/resetHighlight functions

---

## Single Comprehensive Prompt (For Time-Constrained Demos)

If you need to build the entire tool in one prompt, use this:

```
I need to create a portable, production-ready interactive HTML relationship viewer for Power BI semantic models.

Requirements:
1. Recursively scan for all relationships.tmdl files in *.SemanticModel/definition/ folders
2. Parse TMDL format to extract relationships (fromColumn, toColumn, cardinality, cross-filtering, isActive)
   IMPORTANT PARSING RULE: The regex pattern must match relationship blocks at the START of the file 
   (no preceding newline) or after a newline. Use (?:^|\n) not just \n to avoid skipping the first relationship.
   IMPORTANT: Arrow direction must show filter flow, not TMDL order. In Power BI, filters flow FROM 
   dimension (toColumn/one-side) TO fact (fromColumn/many-side). Reverse the edge direction accordingly.
3. Create an interactive HTML with:
   - Dropdown to select any semantic model found (alphabetically sorted)
   - Network graph visualization using vis.js showing tables as nodes and relationships as edges
   - Color coding: Red boxes for fact tables (many-side), cyan circles for dimension tables (one-side)
   - Click any table to highlight only its direct relationships (grey out unrelated tables/edges)
   - Click empty space to reset highlighting
   - Stats panel showing: total tables, relationships, fact tables, dimension tables
   - Horizontal compact legend showing: fact/dimension colors, one-way/bidirectional/inactive line styles
   - Info panel (right side) showing relationship details when table is clicked
   - Table filter panel (left side) with checkboxes to show/hide tables dynamically
   - Filter panel should have Select All/Deselect All buttons and proper z-index above canvas
   - When highlighting relationships, only consider currently visible (filtered) tables
   - Fast physics-based auto-layout (100 iterations max)
4. Make it portable:
   - Use argparse for CLI arguments: --search-path, --output, --no-browser
   - Default: scan from current directory, output to ./relationships_viewer.html
   - No hardcoded paths or folder structure assumptions
   - Works with any directory structure containing .SemanticModel folders
5. Include error handling and user-friendly messages
6. Create a professional README with usage examples

The script should be self-contained (Python stdlib only), create output directory if needed, and process all models automatically.
Important: In selectNode and resetHighlight functions, always check visibleTables Set to avoid showing filtered-out nodes.
```

**Result:** Complete portable tool ready for public sharing.

---

