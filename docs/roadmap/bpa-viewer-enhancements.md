# BPA Viewer Enhancement Roadmap

Planned extensions for the Best Practice Analyzer Results Viewer tool to provide trend analysis, comparison capabilities, and portfolio-level insights.

---

## 1. Trend Analysis Dashboard ⭐⭐⭐

### Overview
Track BPA compliance metrics over time by analyzing historical TRX files. This enhancement transforms the viewer from a point-in-time snapshot into a longitudinal analysis tool showing how model quality evolves during development cycles.

### Key Features

#### 1.1 Temporal Data Grouping
- **Parse multiple TRX files per model**: Group by model name + timestamp
- **Time series construction**: Build arrays of `[{date, pass_rate, violations_by_rule, violations_by_severity}]`
- **Date extraction**: Parse timestamps from TRX filenames (e.g., `ModelName_20241122_143022.trx`)
- **Configurable time windows**: Last 7 days, 30 days, 90 days, all time

#### 1.2 Interactive Visualizations

**Pass Rate Trend Line Chart**
```javascript
// Chart.js line chart showing pass rate over time
{
  type: 'line',
  data: {
    labels: ['2024-11-15', '2024-11-16', '2024-11-17', ...],
    datasets: [{
      label: 'Pass Rate %',
      data: [78.5, 79.2, 81.0, ...],
      borderColor: '#27AE60',
      backgroundColor: 'rgba(39, 174, 96, 0.1)'
    }]
  }
}
```

**Violation Count Stacked Area Chart**
- Show severity breakdown over time (Info/Warning/Error stacked)
- Visualize whether violations are increasing or decreasing
- Color-coded by severity (yellow/orange/red)

**Rule Failure Heat Map**
- Rows: Individual BPA rules
- Columns: Time periods (days/weeks)
- Cell color intensity: Failure frequency (0-100%)
- Click cell to see which objects violated that rule on that date

#### 1.3 Delta Analysis ("What Changed?")

**New Violations vs Fixed Violations**
```python
def calculate_delta(previous_run, current_run):
    """
    Returns:
    {
        'new_violations': [{rule, objects, severity}],
        'fixed_violations': [{rule, objects, severity}],
        'regression_rules': [rules that changed from pass to fail],
        'improvement_rules': [rules that changed from fail to pass]
    }
    """
```

- Show badge: "🆕 5 New Violations" / "✅ 3 Fixed"
- Expandable sections showing exactly which objects/rules changed
- Timeline scrubber: Click any date to see delta from previous run

#### 1.4 Sprint Progress Tracking

**Use Case: Two-week sprint cycle**
```
Sprint Start (Nov 1): 72.3% pass rate, 23 violations
Sprint End (Nov 15):   81.5% pass rate, 15 violations
  
Progress: +9.2% pass rate, -8 violations ✅
  
Top Improvements:
  - [DAX Expressions] Fixed 5 DIVIDE by zero issues
  - [Formatting] Standardized 3 measure names
  
New Issues:
  - [Performance] 2 new unused columns detected
```

### Technical Implementation

#### File Structure Changes
```python
# visualize_bpa_results.py additions

def group_trx_by_model_and_time(trx_files):
    """Group TRX files by model name, sort chronologically"""
    model_timeline = defaultdict(list)
    for trx_file in trx_files:
        model_name = extract_model_name(trx_file)
        timestamp = extract_timestamp(trx_file)
        trx_data = parse_trx_file(trx_file)
        model_timeline[model_name].append({
            'timestamp': timestamp,
            'data': trx_data
        })
    return {k: sorted(v, key=lambda x: x['timestamp']) 
            for k, v in model_timeline.items()}

def calculate_violation_delta(prev_violations, curr_violations):
    """Compare two violation sets to find added/removed"""
    prev_set = {(v['rule'], v['object']) for v in prev_violations}
    curr_set = {(v['rule'], v['object']) for v in curr_violations}
    
    new = curr_set - prev_set
    fixed = prev_set - curr_set
    
    return {
        'new': list(new),
        'fixed': list(fixed),
        'net_change': len(new) - len(fixed)
    }

def generate_trend_html(model_timeline):
    """Generate HTML with Chart.js visualizations"""
    # Add Chart.js CDN script
    # Create canvas elements for charts
    # Embed timeline data as JSON
    # JavaScript to render charts on load
```

#### HTML Template Additions
```html
<!-- Trend Analysis Section -->
<div id="trend-section" style="display:none;">
    <div class="trend-controls">
        <button onclick="showTrendView('7d')">Last 7 Days</button>
        <button onclick="showTrendView('30d')">Last 30 Days</button>
        <button onclick="showTrendView('all')">All Time</button>
    </div>
    
    <div class="chart-row">
        <canvas id="passRateChart"></canvas>
        <canvas id="violationCountChart"></canvas>
    </div>
    
    <div class="chart-row">
        <canvas id="heatMapCanvas"></canvas>
    </div>
    
    <div id="delta-summary">
        <h3>Latest Changes</h3>
        <div class="delta-new">🆕 5 New Violations</div>
        <div class="delta-fixed">✅ 3 Fixed Violations</div>
    </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
```

#### CLI Flag
```bash
python visualize_bpa_results.py --input ./bpa_results --mode trend
```

### Data Requirements
- **Filename convention**: `{ModelName}_{YYYYMMDD}_{HHMMSS}.trx` (already implemented)
- **Minimum data points**: At least 2 TRX files per model (otherwise show "Insufficient data for trend analysis")
- **Storage**: No database needed, all trend data embedded in HTML

### Benefits
- **Sprint retrospectives**: Show concrete quality improvement metrics
- **Early warning system**: Detect pass rate regression before release
- **Developer motivation**: Visualize impact of quality improvements
- **Stakeholder reporting**: Executive dashboard showing compliance trajectory

---

## 2. Side-by-Side Diff View ⭐⭐⭐

### Overview
Compare two specific BPA runs to identify exactly what changed. Essential for code review, release validation, and understanding the impact of refactoring work.

### Key Features

#### 2.1 Comparison Selection UI
```
┌─────────────────────────────────────────┐
│  Compare BPA Results                    │
├─────────────────────────────────────────┤
│  Baseline:  [SalesModel_20241115] ▼     │
│  Current:   [SalesModel_20241122] ▼     │
│             [Compare] [Swap]            │
└─────────────────────────────────────────┘
```

**Selection Options:**
- Dropdown populated with all TRX files for selected model
- "Swap" button to reverse baseline/current
- Keyboard shortcut: Compare latest two runs automatically

#### 2.2 Three-Column Diff Layout

```
┌──────────────────┬──────────────────┬──────────────────┐
│  Baseline        │  Status          │  Current         │
│  (Nov 15)        │                  │  (Nov 22)        │
├──────────────────┼──────────────────┼──────────────────┤
│  78.5% pass rate │  ↗️ +3.0%        │  81.5% pass rate │
│  23 violations   │  ✅ -8           │  15 violations   │
├──────────────────┼──────────────────┼──────────────────┤
│                  │  ✅ FIXED (8)    │                  │
│  [Rule] Hidden   │  ───────────────→│  [PASSED]        │
│   foreign keys   │                  │                  │
│   • Table1.Col1  │                  │                  │
│   • Table2.Col2  │                  │                  │
├──────────────────┼──────────────────┼──────────────────┤
│  [PASSED]        │  🆕 NEW (5)      │  [Rule] Unused   │
│                  │  ←───────────────│   columns        │
│                  │                  │   • Table3.Col3  │
│                  │                  │   • Table4.Col4  │
├──────────────────┼──────────────────┼──────────────────┤
│  [Rule] DIVIDE   │  ⚠️ UNCHANGED    │  [Rule] DIVIDE   │
│   Severity 2     │  Severity ↑      │   Severity 3     │
│   • Measure1     │  +1 object       │   • Measure1     │
│                  │                  │   • Measure2     │
└──────────────────┴──────────────────┴──────────────────┘
```

#### 2.3 Diff Categories

**1. Fixed Violations (Green)**
- Rules that failed in baseline but pass in current
- Objects that were removed from violation lists
- Show count: "✅ 8 Fixed Violations"

**2. New Violations (Red)**
- Rules that passed in baseline but fail in current
- New objects added to existing violation lists
- Show count: "🆕 5 New Violations"

**3. Unchanged Violations (Gray)**
- Same rule, same objects, same severity
- Optional: Hide from view (checkbox filter)

**4. Modified Violations (Orange)**
- Same rule still fails, but different objects
- Severity level changed (e.g., Warning → Error)
- Show object-level diff: "Added: [Measure2], Removed: [Measure3]"

**5. Status Changes (Purple)**
- Rule changed from pass→fail or fail→pass
- No object-level details (rule-level comparison)

#### 2.4 Summary Dashboard

```
╔══════════════════════════════════════════════════╗
║  Comparison Summary                              ║
║  Baseline: Nov 15, 2024 (78.5% pass rate)       ║
║  Current:  Nov 22, 2024 (81.5% pass rate)       ║
╠══════════════════════════════════════════════════╣
║  Overall Change:  ↗️ +3.0% pass rate             ║
║  Net Violations:  -8 (-34.8%)                    ║
║                                                  ║
║  ✅ Fixed:        8 violations                   ║
║  🆕 New:          5 violations                   ║
║  ⚠️ Modified:     2 violations                   ║
║  ⚪ Unchanged:    12 violations                  ║
║                                                  ║
║  Most Improved Category:  Formatting (-5)       ║
║  Most Regressed Category: Performance (+3)      ║
╚══════════════════════════════════════════════════╝
```

### Technical Implementation

#### Core Comparison Function
```python
def compare_trx_files(baseline_path, current_path):
    """
    Compare two TRX files and return structured diff
    
    Returns:
    {
        'summary': {
            'baseline_pass_rate': 78.5,
            'current_pass_rate': 81.5,
            'pass_rate_delta': +3.0,
            'baseline_violations': 23,
            'current_violations': 15,
            'violation_delta': -8
        },
        'fixed': [
            {
                'rule': '[Formatting] Hide foreign keys',
                'severity': 1,
                'objects': ['Table1.Col1', 'Table2.Col2']
            }
        ],
        'new': [
            {
                'rule': '[Performance] Unused columns',
                'severity': 2,
                'objects': ['Table3.Col3', 'Table4.Col4']
            }
        ],
        'modified': [
            {
                'rule': '[DAX] Avoid DIVIDE by zero',
                'baseline_severity': 2,
                'current_severity': 3,
                'objects_added': ['Measure2'],
                'objects_removed': [],
                'objects_unchanged': ['Measure1']
            }
        ],
        'unchanged': [
            # Same rule + same objects + same severity
        ]
    }
    """
    baseline_data = parse_trx_file(baseline_path)
    current_data = parse_trx_file(current_path)
    
    # Build violation dictionaries keyed by rule ID
    baseline_violations = {
        rule['id']: {
            'severity': rule['severity'],
            'objects': set(v['object'] for v in rule['violations'])
        }
        for rule in baseline_data['rules'] if rule['status'] == 'failed'
    }
    
    current_violations = {
        rule['id']: {
            'severity': rule['severity'],
            'objects': set(v['object'] for v in rule['violations'])
        }
        for rule in current_data['rules'] if rule['status'] == 'failed'
    }
    
    # Calculate diffs
    fixed = []
    new = []
    modified = []
    unchanged = []
    
    # Rules that were failing in baseline
    for rule_id, baseline_info in baseline_violations.items():
        if rule_id not in current_violations:
            # Rule now passes - FIXED
            fixed.append({
                'rule_id': rule_id,
                'severity': baseline_info['severity'],
                'objects': list(baseline_info['objects'])
            })
        else:
            # Rule still fails - check if modified
            current_info = current_violations[rule_id]
            
            objects_added = current_info['objects'] - baseline_info['objects']
            objects_removed = baseline_info['objects'] - current_info['objects']
            severity_changed = baseline_info['severity'] != current_info['severity']
            
            if objects_added or objects_removed or severity_changed:
                # MODIFIED
                modified.append({
                    'rule_id': rule_id,
                    'baseline_severity': baseline_info['severity'],
                    'current_severity': current_info['severity'],
                    'objects_added': list(objects_added),
                    'objects_removed': list(objects_removed),
                    'objects_unchanged': list(
                        baseline_info['objects'] & current_info['objects']
                    )
                })
            else:
                # UNCHANGED
                unchanged.append({
                    'rule_id': rule_id,
                    'severity': baseline_info['severity'],
                    'objects': list(baseline_info['objects'])
                })
    
    # Rules that are failing in current but weren't in baseline
    for rule_id, current_info in current_violations.items():
        if rule_id not in baseline_violations:
            # NEW violation
            new.append({
                'rule_id': rule_id,
                'severity': current_info['severity'],
                'objects': list(current_info['objects'])
            })
    
    return {
        'summary': calculate_summary_stats(baseline_data, current_data),
        'fixed': fixed,
        'new': new,
        'modified': modified,
        'unchanged': unchanged
    }
```

#### HTML Diff Viewer Template
```python
def generate_diff_html(diff_results, baseline_path, current_path):
    """Generate interactive diff viewer HTML"""
    
    html = f"""
    <div class="diff-viewer">
        <div class="diff-header">
            <div class="baseline-info">
                <h3>Baseline</h3>
                <p>{Path(baseline_path).name}</p>
                <p>Pass Rate: {diff_results['summary']['baseline_pass_rate']:.1f}%</p>
            </div>
            <div class="diff-summary">
                <h2>Δ {diff_results['summary']['pass_rate_delta']:+.1f}%</h2>
                <p>Net: {diff_results['summary']['violation_delta']:+d} violations</p>
            </div>
            <div class="current-info">
                <h3>Current</h3>
                <p>{Path(current_path).name}</p>
                <p>Pass Rate: {diff_results['summary']['current_pass_rate']:.1f}%</p>
            </div>
        </div>
        
        <div class="diff-filters">
            <label><input type="checkbox" checked onchange="toggleDiffCategory('fixed')"> 
                   ✅ Fixed ({len(diff_results['fixed'])})</label>
            <label><input type="checkbox" checked onchange="toggleDiffCategory('new')"> 
                   🆕 New ({len(diff_results['new'])})</label>
            <label><input type="checkbox" checked onchange="toggleDiffCategory('modified')"> 
                   ⚠️ Modified ({len(diff_results['modified'])})</label>
            <label><input type="checkbox" onchange="toggleDiffCategory('unchanged')"> 
                   ⚪ Unchanged ({len(diff_results['unchanged'])})</label>
        </div>
        
        <div class="diff-content">
            <!-- Fixed violations section -->
            <div class="diff-section fixed-section">
                <h3>✅ Fixed Violations ({len(diff_results['fixed'])})</h3>
                {render_fixed_violations(diff_results['fixed'])}
            </div>
            
            <!-- New violations section -->
            <div class="diff-section new-section">
                <h3>🆕 New Violations ({len(diff_results['new'])})</h3>
                {render_new_violations(diff_results['new'])}
            </div>
            
            <!-- Modified violations section -->
            <div class="diff-section modified-section">
                <h3>⚠️ Modified Violations ({len(diff_results['modified'])})</h3>
                {render_modified_violations(diff_results['modified'])}
            </div>
            
            <!-- Unchanged violations section (initially hidden) -->
            <div class="diff-section unchanged-section" style="display:none;">
                <h3>⚪ Unchanged Violations ({len(diff_results['unchanged'])})</h3>
                {render_unchanged_violations(diff_results['unchanged'])}
            </div>
        </div>
    </div>
    """
    return html
```

#### CLI Usage
```bash
# Compare two specific TRX files
python visualize_bpa_results.py --diff \
    --baseline ./bpa_results/Model_20241115_120000.trx \
    --current ./bpa_results/Model_20241122_120000.trx \
    --output diff_report.html

# Compare latest two runs for a model (auto-detect)
python visualize_bpa_results.py --diff --model "Sales Model" --input ./bpa_results
```

### Use Cases

#### Pull Request Reviews
```bash
# In CI/CD pipeline:
# 1. Run BPA on main branch → baseline.trx
# 2. Run BPA on PR branch → current.trx
# 3. Generate diff report
python visualize_bpa_results.py --diff \
    --baseline ./main_branch.trx \
    --current ./pr_branch.trx \
    --output pr_bpa_diff.html

# 4. Post diff summary as PR comment
# 5. Block merge if new violations exceed threshold
```

#### Release Validation
```bash
# Compare pre-release vs post-release
python visualize_bpa_results.py --diff \
    --baseline ./release-1.0_baseline.trx \
    --current ./release-1.1_candidate.trx
```

#### A/B Testing Model Changes
```bash
# Test two different approaches
python visualize_bpa_results.py --diff \
    --baseline ./original_design.trx \
    --current ./refactored_design.trx
```

### Benefits
- **Clear accountability**: See exactly what changed and who needs to fix it
- **Fast code reviews**: No need to manually compare violation lists
- **Regression prevention**: Immediately spot if changes broke previously passing rules
- **Decision support**: Compare quality impact of different implementation approaches

---

## 3. Multi-Model Aggregate Dashboard ⭐⭐

### Overview
Portfolio-level view showing compliance metrics across all models in a workspace, organization, or team. Helps managers and architects identify problematic models and track organizational quality trends.

### Key Features

#### 3.1 Portfolio Summary Table

```
╔════════════════════════════════════════════════════════════════════════════════╗
║  Model Portfolio Health Dashboard                              Last Updated: Nov 22, 2024 ║
╠════════════════════════════════════════════════════════════════════════════════╣
║  Models: 12  |  Avg Pass Rate: 76.3%  |  Total Violations: 187                ║
╚════════════════════════════════════════════════════════════════════════════════╝

┌──────────────────────────┬──────────┬────────────┬───────────┬────────────────────┬─────────┐
│ Model Name               │ Pass Rate│ Violations │ Trend     │ Worst Rule         │ Actions │
├──────────────────────────┼──────────┼────────────┼───────────┼────────────────────┼─────────┤
│ 🔴 Sales Analytics       │  57.6%   │     42     │ ↘️ -2.3%  │ Hidden foreign keys│ [View]  │
│ 🟠 Inventory Insights    │  78.0%   │     18     │ ↗️ +1.5%  │ Unused columns     │ [View]  │
│ 🟢 Finance Dashboard     │  91.2%   │      5     │ → 0.0%    │ Missing desc       │ [View]  │
│ 🟢 HR Metrics            │  88.5%   │      7     │ ↗️ +3.2%  │ Date formatting    │ [View]  │
│ 🟠 Logistics Tracker     │  74.6%   │     21     │ ↘️ -1.1%  │ Calc item names    │ [View]  │
│ 🔴 Customer 360          │  61.3%   │     35     │ ↘️ -5.2%  │ DIVIDE syntax      │ [View]  │
└──────────────────────────┴──────────┴────────────┴───────────┴────────────────────┴─────────┘

Sort by: [Pass Rate ↓] [Violations] [Trend] [Name]
Filter: [All] [Critical (<70%)] [Warning (70-85%)] [Good (>85%)]
```

**Health Indicators:**
- 🔴 Red: Pass rate < 70% (Critical)
- 🟠 Orange: Pass rate 70-85% (Needs attention)
- 🟢 Green: Pass rate > 85% (Healthy)

#### 3.2 Aggregate Metrics

**Top-Level KPIs:**
```
┌────────────────────────────────────────────────────────────┐
│  Organization Health Score: 76.3%                          │
│  ─────────────────────────────────────────────────────     │
│                                                             │
│  📊 Total Models:           12                              │
│  ✅ Healthy Models (>85%):   4  (33%)                       │
│  ⚠️ Warning Models (70-85%): 6  (50%)                       │
│  🚨 Critical Models (<70%):  2  (17%)                       │
│                                                             │
│  📈 Trending Up:            5 models                        │
│  📉 Trending Down:          3 models                        │
│  → Stable:                  4 models                        │
└────────────────────────────────────────────────────────────┘
```

**Most Common Violations Across Portfolio:**
```
┌────────────────────────────────────────────────────────────┐
│  Top 5 Rules Failing Across Models                         │
├────────────────────────────────────────────────────────────┤
│  1. [Formatting] Hide foreign keys       (8 models, 47 obj)│
│  2. [Performance] Unused columns         (6 models, 32 obj)│
│  3. [DAX] Avoid DIVIDE syntax            (5 models, 28 obj)│
│  4. [Formatting] Missing descriptions    (7 models, 24 obj)│
│  5. [Maintenance] Calc item naming       (4 models, 19 obj)│
└────────────────────────────────────────────────────────────┘
```

#### 3.3 Drill-Down Navigation

**Click model name → Opens detailed single-model view**
- Same view as current `visualize_bpa_results.py` output
- Breadcrumb: "← Back to Portfolio Dashboard"
- Context preserved: "Sales Analytics (57.6% pass rate, 42 violations)"

**Click rule name → Shows all models failing that rule**
```
Rule: [Formatting] Hide foreign keys
Failing in 8 models:

┌─────────────────────────┬────────────────────────────────┐
│ Model                   │ Affected Objects               │
├─────────────────────────┼────────────────────────────────┤
│ Sales Analytics         │ dim_product.product_key        │
│                         │ fact_sales.customer_key        │
│                         │ fact_sales.product_key         │
├─────────────────────────┼────────────────────────────────┤
│ Inventory Insights      │ dim_warehouse.warehouse_id     │
│                         │ fact_inventory.product_id      │
└─────────────────────────┴────────────────────────────────┘
```

#### 3.4 Team/Workspace Filtering

```
Filter by Workspace: [All ▼] [Sales ▼] [Finance ▼] [Operations ▼]
Filter by Owner:     [All ▼] [TeamA ▼] [TeamB ▼]
Filter by Tags:      [Production] [Development] [Legacy]
```

**Metadata source options:**
1. **Parse from TRX filename**: `{Workspace}_{ModelName}_{Timestamp}.trx`
2. **External metadata file**: `model_metadata.json`
   ```json
   {
     "SalesAnalytics": {
       "workspace": "Sales",
       "owner": "TeamA",
       "tags": ["production", "critical"]
     }
   }
   ```
3. **Power BI REST API**: Query workspace assignments (requires authentication)

#### 3.5 Export Capabilities

```bash
# Export portfolio summary to CSV
python visualize_bpa_results.py --portfolio \
    --input ./bpa_results \
    --export-csv portfolio_summary.csv

# CSV Format:
# Model,PassRate,Violations,Trend,WorstRule,Timestamp
# Sales Analytics,57.6,42,-2.3,Hide foreign keys,2024-11-22T14:30:22
```

### Technical Implementation

#### Portfolio Data Aggregation
```python
def generate_portfolio_view(trx_files):
    """
    Generate aggregate portfolio dashboard from multiple TRX files
    
    Args:
        trx_files: List of Path objects to TRX files
    
    Returns:
        {
            'summary': {
                'total_models': 12,
                'avg_pass_rate': 76.3,
                'total_violations': 187,
                'health_distribution': {
                    'healthy': 4,
                    'warning': 6,
                    'critical': 2
                }
            },
            'models': [
                {
                    'name': 'Sales Analytics',
                    'pass_rate': 57.6,
                    'violations': 42,
                    'trend': -2.3,  # percent change from previous run
                    'worst_rule': 'Hide foreign keys',
                    'health_status': 'critical',
                    'trx_file': 'path/to/trx'
                },
                ...
            ],
            'top_failing_rules': [
                {
                    'rule_name': '[Formatting] Hide foreign keys',
                    'models_affected': 8,
                    'total_objects': 47,
                    'models': ['Sales Analytics', 'Inventory', ...]
                },
                ...
            ]
        }
    """
    
    # Group TRX files by model name
    model_groups = defaultdict(list)
    for trx_file in trx_files:
        model_name = extract_model_name(trx_file)
        model_groups[model_name].append(trx_file)
    
    # For each model, use most recent TRX
    models_data = []
    for model_name, files in model_groups.items():
        latest_trx = max(files, key=lambda f: extract_timestamp(f))
        trx_data = parse_trx_file(latest_trx)
        
        # Calculate trend if multiple TRX files exist
        trend = 0.0
        if len(files) >= 2:
            previous_trx = sorted(files, key=lambda f: extract_timestamp(f))[-2]
            prev_data = parse_trx_file(previous_trx)
            trend = trx_data['pass_rate'] - prev_data['pass_rate']
        
        # Find worst failing rule
        worst_rule = None
        max_violations = 0
        for rule in trx_data['rules']:
            if rule['status'] == 'failed' and len(rule['violations']) > max_violations:
                max_violations = len(rule['violations'])
                worst_rule = rule['name']
        
        models_data.append({
            'name': model_name,
            'pass_rate': trx_data['pass_rate'],
            'violations': trx_data['stats']['failed'],
            'trend': trend,
            'worst_rule': worst_rule or 'N/A',
            'health_status': classify_health(trx_data['pass_rate']),
            'trx_file': str(latest_trx)
        })
    
    # Aggregate rule failures across models
    rule_failures = defaultdict(lambda: {'models': set(), 'objects': 0})
    for model_name, files in model_groups.items():
        latest_trx = max(files, key=lambda f: extract_timestamp(f))
        trx_data = parse_trx_file(latest_trx)
        
        for rule in trx_data['rules']:
            if rule['status'] == 'failed':
                rule_failures[rule['name']]['models'].add(model_name)
                rule_failures[rule['name']]['objects'] += len(rule['violations'])
    
    # Sort by number of models affected
    top_failing_rules = sorted(
        [
            {
                'rule_name': rule,
                'models_affected': len(data['models']),
                'total_objects': data['objects'],
                'models': list(data['models'])
            }
            for rule, data in rule_failures.items()
        ],
        key=lambda x: x['models_affected'],
        reverse=True
    )[:5]
    
    return {
        'summary': calculate_portfolio_summary(models_data),
        'models': sorted(models_data, key=lambda x: x['pass_rate']),
        'top_failing_rules': top_failing_rules
    }

def classify_health(pass_rate):
    """Classify model health based on pass rate"""
    if pass_rate >= 85:
        return 'healthy'
    elif pass_rate >= 70:
        return 'warning'
    else:
        return 'critical'
```

#### HTML Portfolio Template
```python
def generate_portfolio_html(portfolio_data):
    """Generate interactive portfolio dashboard HTML"""
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>BPA Portfolio Dashboard</title>
        <style>
            .portfolio-header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                border-radius: 8px;
                margin-bottom: 20px;
            }}
            
            .kpi-grid {{
                display: grid;
                grid-template-columns: repeat(4, 1fr);
                gap: 20px;
                margin-bottom: 30px;
            }}
            
            .kpi-card {{
                background: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            
            .model-table {{
                width: 100%;
                border-collapse: collapse;
                background: white;
                border-radius: 8px;
                overflow: hidden;
            }}
            
            .model-table th {{
                background-color: #3498DB;
                color: white;
                padding: 12px;
                text-align: left;
            }}
            
            .model-table td {{
                padding: 12px;
                border-bottom: 1px solid #eee;
            }}
            
            .health-critical {{ color: #E74C3C; }}
            .health-warning {{ color: #F39C12; }}
            .health-healthy {{ color: #27AE60; }}
            
            .trend-up {{ color: #27AE60; }}
            .trend-down {{ color: #E74C3C; }}
            .trend-neutral {{ color: #95a5a6; }}
        </style>
    </head>
    <body>
        <div class="portfolio-header">
            <h1>🎯 BPA Portfolio Dashboard</h1>
            <p>Organization Health Score: {portfolio_data['summary']['avg_pass_rate']:.1f}%</p>
        </div>
        
        <div class="kpi-grid">
            <div class="kpi-card">
                <h3>Total Models</h3>
                <h1>{portfolio_data['summary']['total_models']}</h1>
            </div>
            <div class="kpi-card">
                <h3>Avg Pass Rate</h3>
                <h1>{portfolio_data['summary']['avg_pass_rate']:.1f}%</h1>
            </div>
            <div class="kpi-card">
                <h3>Total Violations</h3>
                <h1>{portfolio_data['summary']['total_violations']}</h1>
            </div>
            <div class="kpi-card">
                <h3>Critical Models</h3>
                <h1>{portfolio_data['summary']['health_distribution']['critical']}</h1>
            </div>
        </div>
        
        <table class="model-table">
            <thead>
                <tr>
                    <th>Model Name</th>
                    <th>Pass Rate</th>
                    <th>Violations</th>
                    <th>Trend</th>
                    <th>Worst Rule</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
    """
    
    for model in portfolio_data['models']:
        health_icon = {'critical': '🔴', 'warning': '🟠', 'healthy': '🟢'}[model['health_status']]
        health_class = f"health-{model['health_status']}"
        
        trend_icon = '↗️' if model['trend'] > 0 else ('↘️' if model['trend'] < 0 else '→')
        trend_class = 'trend-up' if model['trend'] > 0 else ('trend-down' if model['trend'] < 0 else 'trend-neutral')
        
        html += f"""
                <tr>
                    <td>{health_icon} {model['name']}</td>
                    <td class="{health_class}">{model['pass_rate']:.1f}%</td>
                    <td>{model['violations']}</td>
                    <td class="{trend_class}">{trend_icon} {model['trend']:+.1f}%</td>
                    <td>{model['worst_rule']}</td>
                    <td><a href="#" onclick="loadModelDetail('{model['name']}')">View</a></td>
                </tr>
        """
    
    html += """
            </tbody>
        </table>
        
        <div class="top-rules-section">
            <h2>🚨 Top Failing Rules Across Portfolio</h2>
    """
    
    for rule in portfolio_data['top_failing_rules']:
        html += f"""
            <div class="rule-card">
                <h3>{rule['rule_name']}</h3>
                <p>Affecting {rule['models_affected']} models ({rule['total_objects']} objects)</p>
                <p><small>Models: {', '.join(rule['models'][:5])}{'...' if len(rule['models']) > 5 else ''}</small></p>
            </div>
        """
    
    html += """
        </div>
    </body>
    </html>
    """
    
    return html
```

#### CLI Usage
```bash
# Generate portfolio dashboard
python visualize_bpa_results.py --portfolio \
    --input ./bpa_results \
    --output portfolio_dashboard.html

# Filter by workspace (requires metadata)
python visualize_bpa_results.py --portfolio \
    --input ./bpa_results \
    --workspace "Sales" \
    --output sales_portfolio.html

# Export to CSV for Excel analysis
python visualize_bpa_results.py --portfolio \
    --input ./bpa_results \
    --export-csv models_summary.csv
```

### Use Cases

#### Executive Reporting
- Monthly compliance report showing organizational progress
- Identify which teams/workspaces need quality improvement support
- Track compliance trends at portfolio level

#### Architecture Governance
- Identify models that don't meet organizational standards
- Prioritize technical debt remediation efforts
- Enforce minimum pass rate thresholds for production models

#### Team Benchmarking
- Compare quality metrics across teams
- Highlight best practices from high-performing models
- Create friendly competition to improve overall quality

### Benefits
- **Bird's eye view**: See entire model portfolio health at a glance
- **Identify outliers**: Quickly spot models needing attention
- **Resource allocation**: Prioritize quality improvement efforts
- **Trend visibility**: Track if org is improving or regressing overall
- **Pattern recognition**: Identify systemic issues affecting multiple models

---

## Implementation Priority

### Phase 1: Trend Analysis (2-3 days)
- Core value: Historical context for compliance metrics
- Minimal UI changes needed
- Leverages existing TRX parsing
- Immediate value for sprint retrospectives

### Phase 2: Diff View (2-3 days)
- Critical for code review workflow
- Enables CI/CD quality gates
- High developer demand
- Natural extension of existing comparison logic

### Phase 3: Portfolio Dashboard (3-4 days)
- Requires more UI work (tables, sorting, filtering)
- Metadata management complexity
- Value grows with # of models
- Best for orgs with 10+ models

---

## Technical Considerations

### Dependencies
- **Chart.js**: CDN-hosted, no install needed (trend analysis)
- **No external databases**: All data embedded in HTML
- **Backward compatible**: Existing single-model viewer unchanged

### File Size Impact
- Trend analysis: +50-100KB (chart library + time series data)
- Diff view: Minimal (+10-20KB for comparison logic)
- Portfolio dashboard: +100-200KB (all models summary data)

### Browser Compatibility
- Modern browsers (Chrome, Firefox, Edge, Safari)
- Responsive design (desktop primary, mobile secondary)
- Offline-capable (no server dependencies)

### Testing Strategy
- Unit tests for comparison/aggregation logic
- Sample TRX files covering edge cases (empty results, missing fields)
- Visual regression tests for HTML rendering
- Performance testing with 50+ TRX files

---

## Future Enhancements (Beyond Scope)

- **Real-time monitoring**: WebSocket connection to refresh live
- **Email alerts**: Notify on pass rate drops
- **JIRA integration**: Auto-create tickets for new violations
- **Machine learning**: Predict future compliance trends
- **Custom rule sets**: Define org-specific BPA rules
- **Baseline management**: Accept certain violations as technical debt
