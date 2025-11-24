---
date: 2025-11-22
authors:
  - joe
categories:
  - Tools
  - Automation
  - Best Practices
tags:
  - BPA
  - Tabular Editor
  - Python
  - Quality Analysis
  - CI/CD
---

# Making Best Practice Analyzer Results Actually Readable

Tabular Editor's command-line interface lets you run Best Practice Analyzer checks on your Power BI semantic models without opening the GUI. You point it at your `.SemanticModel` folder, it analyzes your model against BPA rules, and outputs results in TRX format.

<!-- more -->

The problem? TRX files are XML test result files designed for Azure DevOps pipelines, not humans.

You get:
```xml
<UnitTestResult testId="abc-123" outcome="Failed">
  <Output>
    <ErrorInfo>
      <Message>2 violation(s) found</Message>
      <StackTrace>Objects in violation:
  Sales[Discount Percentage]
  Products[Markup]
      </StackTrace>
    </ErrorInfo>
  </Output>
</UnitTestResult>
```

That's a test framework artifact, not a usable quality report. You have to parse XML to understand what failed and why. If you run BPA on multiple models, you're opening individual files trying to piece together which models need attention.

## The Script

`visualize_bpa_results.py` scans your BPA output folder, parses all TRX files, and generates an interactive HTML viewer.

**What it does:**

1. **Scans for TRX files** - Finds all BPA results in your output directory
2. **Parses test metadata** - Extracts model name, rules, violations, severity levels, timestamps
3. **Groups by model** - Shows latest analysis per model by default, with toggle for full history
4. **Generates interactive HTML** - Self-contained viewer with dropdown to switch between models

**Key features:**

- **Multi-model dropdown** - Switch between different models' results instantly
- **Latest/All toggle** - Default shows only most recent analysis per model, button toggles to see full history
- **Category organization** - Rules grouped by category (DAX Expressions, Maintenance, Naming Conventions, Performance, etc.)
- **Color-coded severity** - Red (Error/Severity 1), Orange (Warning/Severity 2), Blue (Info/Severity 3)
- **Pass rate stats** - Overall pass percentage, passed/failed counts
- **Collapsible sections** - Click to expand categories, rules, violation lists
- **Filter controls** - Show All, Failed Only, Passed Only, Expand All, Collapse All
- **Violation details** - See exactly which tables/columns/measures failed each rule

[SCREENSHOT: Dropdown showing multiple models with pass rates and timestamps - "D&A - Inventory Insights - 87.5% (2025-11-14 17:05)"]

[SCREENSHOT: Stats bar showing color-coded pass rate (green/yellow/red based on %), passed/failed counts]

[SCREENSHOT: Category sections - blue headers for all-pass categories, red headers for categories with failures]

[SCREENSHOT: Expanded rule showing description, severity badge, violation list with specific objects]

[SCREENSHOT: Filter buttons and expand/collapse controls]

## How It Works

**Parsing TRX Files:**

The script walks through TRX XML structure to extract:
- Model name (from test run path or filename pattern)
- Rule definitions (test names, descriptions, severity, category)
- Violations (failed tests with objects listed in StackTrace)
- Statistics (total/passed/failed counts)

**Data Structure:**

Rules get grouped by category, then enriched with violation data:
```python
{
  'Performance': {
    'total': 15,
    'passed': 12,
    'failed': 3,
    'pass_rate': 80.0,
    'rules': [
      {
        'name': 'Avoid floating point data types',
        'severity': 2,
        'status': 'failed',
        'violations': [
          {'object': 'Sales[Discount Percentage]'},
          {'object': 'Products[Markup]'}
        ]
      },
      ...
    ]
  },
  ...
}
```

**Version Management:**

When multiple TRX files exist for the same model (timestamped runs), the script:
- Groups by model name
- Identifies latest analysis per model
- Shows latest by default in dropdown
- Provides toggle to show all analyses (compare historical results)

**Interactive HTML:**

Generated HTML is self-contained (no external dependencies) with JavaScript for:
- Model selection from dropdown
- Category expand/collapse
- Rule detail expand/collapse
- Violation list expand/collapse
- Filter application (all/failed/passed)
- Dynamic stats updates

## Get the Script

**Download:** [visualize_bpa_results.py](https://raw.githubusercontent.com/JoeRossouw/semantic_ops/main/tools/visualize_bpa_results.py)

**Full Documentation:** [BPA Results Viewer Tool](../../tools/bpa-viewer-guide.md) - Detailed setup and usage

[:material-open-in-new: Launch Interactive Demo](../../demos/bpa_results_viewer.html){ .md-button .md-button--primary target="_blank" }

## Usage

```bash
# Run BPA via Tabular Editor CLI (generates TRX files)
# (your existing BPA workflow)

# Generate viewer
python visualize_bpa_results.py
```

Script scans recursively from current directory for `*.trx` files, processes them all, outputs `bpa_results_viewer.html`, and opens in browser.

[SCREENSHOT: Terminal output showing script scanning, processing multiple TRX files, reporting rule counts and pass rates]

## Why This Matters

**Before:** You run BPA, get XML files, manually parse them or import to Azure DevOps to see results. To check multiple models, you open multiple files. To compare current vs previous run, you diff XML.

**After:** Run BPA, run the script, click through an interactive viewer. Dropdown shows all models. Toggle shows history. Filter shows only what you care about. Click to expand failure details.

This turns BPA from a CI/CD quality gate into a local development quality dashboard.

## The Technical Details

**TRX Format:**

Visual Studio Test Results format. Contains:
- `TestRun` - metadata about the run
- `UnitTest` elements - rule definitions with properties (Description, Severity, Category, RuleID)
- `UnitTestResult` elements - pass/fail outcomes
- `ErrorInfo` - violation messages and stack traces

The script maps test IDs between definitions and results to link rules with their violations.

**Model Name Extraction:**

TRX includes test run path like `C:\...\D&A - Inventory Insights.SemanticModel\definition`. Script extracts model name via regex. Fallback: filename pattern `YYYYMMDD_HHMM_BPA_ModelName.trx`.

**Violation Parsing:**

Failed test results include:
- `Message`: Violation count
- `StackTrace`: List of objects (tables, columns, measures)

Script splits stack trace by newlines to get individual violated objects.

**Self-Contained HTML:**

All CSS and JavaScript inline. vis.js-style interactive UI but no external dependencies. Result: single HTML file you can share with team, upload to wiki, or archive.

## What You Get

A quality dashboard showing:
- Which models need attention (low pass rates)
- Which categories have issues (Performance, DAX Expressions, etc.)
- Which specific rules failed
- Which exact objects violated each rule

Without opening XML, without CI/CD infrastructure, without external tools.

---

**Related:**
- [Relationship Visualizer Tool](../../tools/relationship-viewer-guide.md)
- Blog: [How I Built a Power BI Tool with AI](agentic-ai-pbip.md)

