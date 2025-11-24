# Tools

Python automation scripts for Power BI development, quality analysis, and CI/CD workflows.

## Available Tools

### [BPA Results Viewer](bpa-viewer-guide.md)
Interactive HTML dashboard for Tabular Editor Best Practice Analyzer results.

**Use case**: Visualize BPA compliance across multiple semantic models, track violations by severity, and filter by category.

**Key features**:
- Multi-model dropdown selector
- Severity and category filtering
- Expandable violation details
- Self-contained HTML output

---

### [Relationship Visualizer](relationship-viewer-guide.md)
Network diagram generator for Power BI semantic model relationships.

**Use case**: Understand table relationships, filter propagation, and model complexity at a glance.

**Key features**:
- Interactive graph with click-to-highlight
- Fact/dimension classification
- Filter direction visualization
- Multi-model support

---

### [PBIR Folder Renamer](pbir-folder-renamer-guide.md)
Rename Power BI report page and visual folders from GUIDs to human-readable names.

**Use case**: Make code reviews and git diffs understandable by converting meaningless GUIDs to descriptive names.

**Key features**:
- Automatic page name extraction
- Visual type identification
- Safe, reversible operation
- Cross-platform support

---

## Installation

All tools use Python standard library, no external dependencies required (except MkDocs for this documentation site).

```powershell
# Clone the repo
git clone https://github.com/JoeRossouw/semantic_ops.git
cd semantic_ops

# Tools are in the scripts/ folder
python scripts/visualize_bpa_results.py --help
python scripts/visualize_all_relationships.py --help
python scripts/rename_pbir_folders.py --help
```

---

## Requirements

- **Python**: 3.7 or higher
- **Input formats**: 
  - TMDL (`.SemanticModel` folders) for relationship viewer
  - TRX files for BPA viewer
  - PBIR (`.Report` folders) for folder renamer

---

## Quick Examples

```powershell
# Generate BPA compliance dashboard
python scripts/visualize_bpa_results.py --input ./bpa_results

# Visualize model relationships
python scripts/visualize_all_relationships.py --search-path ./models

# Rename PBIR folders
python scripts/rename_pbir_folders.py "path/to/Report.Report"
```

