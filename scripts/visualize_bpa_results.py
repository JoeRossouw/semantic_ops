"""
Generate interactive HTML visualization for BPA test results from TRX files

How to run:
  1. Place this script anywhere in your repo (root, scripts/, tools/, etc.)
  2. Open a terminal and run:
  
       python visualize_bpa_results.py                    # Scans current directory for .trx files
       python visualize_bpa_results.py --input ./results  # Scan specific folder

  Quick tip: Type "python " then drag this file into your terminal to paste the full path.

  Using VS Code with Copilot? Just ask:
       "Run the visualize_bpa_results.py script on my TRX files"

Requirements: Python 3.7+ (no external dependencies)
"""
import sys
import argparse
import re
import json
from pathlib import Path
from collections import defaultdict
import webbrowser
import xml.etree.ElementTree as ET
from datetime import datetime


def parse_trx_file(file_path):
    """Parse TRX file and extract test run metadata and results"""
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        # Define namespace
        ns = {'ns': 'http://microsoft.com/schemas/VisualStudio/TeamTest/2010'}
        
        # Extract test run info
        test_run = root.find('.//ns:TestRun', ns)
        run_name = test_run.get('name', '') if test_run else ''
        
        # Extract model name from run name or filename
        model_name = ''
        if run_name:
            # Extract from path like "C:\...\D&A - Inventory Insights.SemanticModel\definition"
            match = re.search(r'([^\\]+)\.SemanticModel', run_name)
            if match:
                model_name = match.group(1)
        
        if not model_name:
            # Fallback to filename pattern: 20251114_1705_BPA_Inventory_Insights.trx
            filename = Path(file_path).stem
            parts = filename.split('_BPA_')
            if len(parts) == 2:
                model_name = parts[1].replace('_', ' ')
        
        # Extract timestamps
        times = root.find('.//ns:Times', ns)
        start_time = times.get('start', '') if times is not None else ''
        finish_time = times.get('finish', '') if times is not None else ''
        
        # Extract result summary
        result_summary = root.find('.//ns:ResultSummary', ns)
        outcome = result_summary.get('outcome', 'Unknown') if result_summary is not None else 'Unknown'
        
        counters = root.find('.//ns:Counters', ns)
        stats = {
            'total': int(counters.get('total', 0)) if counters is not None else 0,
            'executed': int(counters.get('executed', 0)) if counters is not None else 0,
            'passed': int(counters.get('passed', 0)) if counters is not None else 0,
            'failed': int(counters.get('failed', 0)) if counters is not None else 0,
            'inconclusive': int(counters.get('inconclusive', 0)) if counters is not None else 0,
            'notExecuted': int(counters.get('notExecuted', 0)) if counters is not None else 0,
        }
        
        # Calculate pass rate
        pass_rate = (stats['passed'] / stats['total'] * 100) if stats['total'] > 0 else 0
        
        # Extract test definitions (rules)
        rules = {}
        for unit_test in root.findall('.//ns:UnitTest', ns):
            test_id = unit_test.get('id', '')
            test_name = unit_test.get('name', '')
            
            properties = {}
            for prop in unit_test.findall('.//ns:Property', ns):
                key_elem = prop.find('ns:Key', ns)
                value_elem = prop.find('ns:Value', ns)
                if key_elem is not None and value_elem is not None:
                    properties[key_elem.text] = value_elem.text
            
            rules[test_id] = {
                'id': test_id,
                'name': test_name,
                'description': properties.get('Description', ''),
                'severity': int(properties.get('Severity', 1)),
                'category': properties.get('Category', 'Unknown'),
                'rule_id': properties.get('RuleID', ''),
            }
        
        # Extract test results (violations)
        violations_by_rule = defaultdict(list)
        
        for result in root.findall('.//ns:UnitTestResult', ns):
            test_id = result.get('testId', '')
            outcome = result.get('outcome', '')
            
            if outcome == 'Failed':
                # Extract error message and stack trace (violation details)
                output = result.find('.//ns:Output', ns)
                if output is not None:
                    error_info = output.find('.//ns:ErrorInfo', ns)
                    if error_info is not None:
                        message_elem = error_info.find('ns:Message', ns)
                        stack_trace_elem = error_info.find('ns:StackTrace', ns)
                        
                        violation_count = ''
                        if message_elem is not None and message_elem.text:
                            violation_count = message_elem.text.strip()
                        
                        # Parse StackTrace to get individual violated objects
                        if stack_trace_elem is not None and stack_trace_elem.text:
                            stack_trace = stack_trace_elem.text.strip()
                            # Parse "Objects in violation:\n  Object1\n  Object2\n..."
                            if 'Objects in violation:' in stack_trace:
                                objects_text = stack_trace.split('Objects in violation:')[1].strip()
                                object_lines = [line.strip() for line in objects_text.split('\n') if line.strip()]
                                
                                for obj_line in object_lines:
                                    violations_by_rule[test_id].append({
                                        'object': obj_line,
                                        'message': violation_count
                                    })
        
        return {
            'model_name': model_name,
            'file_name': Path(file_path).name,
            'start_time': start_time,
            'finish_time': finish_time,
            'outcome': outcome,
            'stats': stats,
            'pass_rate': pass_rate,
            'rules': rules,
            'violations': violations_by_rule
        }
        
    except Exception as e:
        print(f"    ✗ Error parsing {Path(file_path).name}: {e}")
        return None


def extract_object_name(violation_msg):
    """Extract object name from violation message"""
    # Try to extract object name from common patterns
    # Pattern 1: "Object: TableName.ColumnName"
    match = re.search(r'Object:\s*(.+?)(?:\s+-|\s*$)', violation_msg)
    if match:
        return match.group(1).strip()
    
    # Pattern 2: Look for table[column] pattern
    match = re.search(r"'([^']+)'\['([^']+)'\]", violation_msg)
    if match:
        return f"{match.group(1)}.{match.group(2)}"
    
    # Pattern 3: Look for table.column pattern
    match = re.search(r'(\w+)\.(\w+)', violation_msg)
    if match:
        return f"{match.group(1)}.{match.group(2)}"
    
    # Return first 50 chars if no pattern matches
    return violation_msg[:50] + '...' if len(violation_msg) > 50 else violation_msg


def prepare_visualization_data(trx_data):
    """Prepare data structure for visualization"""
    rules = trx_data['rules']
    violations = trx_data['violations']
    
    # Group rules by category
    rules_by_category = defaultdict(list)
    for rule_id, rule in rules.items():
        category = rule['category']
        
        # Get violations for this rule
        rule_violations = violations.get(rule_id, [])
        
        rule_data = {
            'id': rule_id,
            'name': rule['name'],
            'description': rule['description'],
            'severity': rule['severity'],
            'rule_id': rule['rule_id'],
            'status': 'failed' if rule_violations else 'passed',
            'violation_count': len(rule_violations),
            'violations': rule_violations
        }
        
        rules_by_category[category].append(rule_data)
    
    # Calculate category statistics
    category_stats = {}
    for category, category_rules in rules_by_category.items():
        total = len(category_rules)
        passed = sum(1 for r in category_rules if r['status'] == 'passed')
        failed = total - passed
        pass_rate = (passed / total * 100) if total > 0 else 0
        
        category_stats[category] = {
            'total': total,
            'passed': passed,
            'failed': failed,
            'pass_rate': pass_rate,
            'rules': category_rules
        }
    
    return {
        'categories': category_stats,
        'stats': trx_data['stats'],
        'pass_rate': trx_data['pass_rate']
    }


def create_multi_model_html(models_data, output_path):
    """Create an interactive HTML with dropdown to select BPA results"""
    
    # Create JavaScript object with all models data
    models_json = json.dumps(models_data)
    
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Power BI Semantic Models - BPA Results Viewer</title>
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
            min-width: 400px;
        }}
        #stats {{
            background-color: #34495E;
            color: white;
            padding: 12px 20px;
            display: flex;
            justify-content: center;
            gap: 40px;
            font-size: 13px;
        }}
        .stat-item {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .stat-item strong {{
            font-size: 18px;
        }}
        .pass-rate {{
            font-size: 20px;
            font-weight: bold;
        }}
        .pass-rate.good {{ color: #27AE60; }}
        .pass-rate.warning {{ color: #F39C12; }}
        .pass-rate.bad {{ color: #E74C3C; }}
        
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
        
        #content {{
            padding: 20px;
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        .category-section {{
            background: white;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        
        .category-header {{
            background-color: #3498DB;
            color: white;
            padding: 15px 20px;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
            user-select: none;
        }}
        
        .category-header:hover {{
            background-color: #2980B9;
        }}
        
        .category-header.failed {{
            background-color: #E74C3C;
        }}
        
        .category-header.failed:hover {{
            background-color: #C0392B;
        }}
        
        .category-title {{
            display: flex;
            align-items: center;
            gap: 12px;
            font-size: 16px;
            font-weight: bold;
        }}
        
        .category-stats {{
            display: flex;
            gap: 20px;
            font-size: 14px;
        }}
        
        .category-content {{
            display: none;
            padding: 20px;
        }}
        
        .category-content.expanded {{
            display: block;
        }}
        
        .rule-item {{
            border-left: 4px solid #3498DB;
            background-color: #f8f9fa;
            padding: 15px;
            margin-bottom: 12px;
            border-radius: 4px;
        }}
        
        .rule-item.failed {{
            border-left-color: #E74C3C;
            background-color: #FADBD8;
        }}
        
        .rule-item.passed {{
            border-left-color: #27AE60;
            background-color: #D5F4E6;
        }}
        
        .rule-header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 8px;
            cursor: pointer;
            user-select: none;
        }}
        
        .rule-header:hover {{
            opacity: 0.8;
        }}
        
        .rule-name {{
            font-weight: bold;
            color: #2C3E50;
            font-size: 14px;
            flex: 1;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        
        .rule-expand-icon {{
            font-size: 12px;
            transition: transform 0.3s;
            color: #666;
        }}
        
        .rule-expand-icon.expanded {{
            transform: rotate(180deg);
        }}
        
        .rule-status {{
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: bold;
            text-transform: uppercase;
        }}
        
        .rule-status.passed {{
            background-color: #27AE60;
            color: white;
        }}
        
        .rule-status.failed {{
            background-color: #E74C3C;
            color: white;
        }}
        
        .rule-description {{
            color: #666;
            font-size: 13px;
            line-height: 1.5;
            margin-top: 8px;
            padding: 10px;
            background-color: white;
            border-radius: 4px;
            display: none;
        }}
        
        .rule-description.expanded {{
            display: block;
        }}
        
        .violations-section {{
            margin-top: 12px;
            padding: 10px;
            background-color: white;
            border-radius: 4px;
            display: none;
        }}
        
        .violations-section.expanded {{
            display: block;
        }}
        
        .violations-header {{
            font-weight: bold;
            color: #E74C3C;
            margin-bottom: 8px;
            font-size: 13px;
            cursor: pointer;
            user-select: none;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        
        .violations-header:hover {{
            opacity: 0.8;
        }}
        
        .violations-expand-icon {{
            font-size: 12px;
            transition: transform 0.3s;
        }}
        
        .violations-expand-icon.expanded {{
            transform: rotate(180deg);
        }}
        
        .violations-list {{
            display: none;
        }}
        
        .violations-list.expanded {{
            display: block;
        }}
        
        .violation-item {{
            padding: 8px 12px;
            margin: 6px 0;
            background-color: #FFF5F5;
            border-left: 3px solid #E74C3C;
            border-radius: 3px;
            font-size: 12px;
            font-family: 'Consolas', 'Monaco', monospace;
        }}
        
        .violation-object {{
            color: #8E44AD;
            font-weight: bold;
        }}
        
        .violation-message {{
            color: #555;
            margin-top: 4px;
        }}
        
        .severity-badge {{
            display: inline-block;
            padding: 2px 8px;
            border-radius: 10px;
            font-size: 11px;
            font-weight: bold;
            margin-left: 8px;
        }}
        
        .severity-1 {{
            background-color: #F1C40F;
            color: #2C3E50;
        }}
        
        .severity-2 {{
            background-color: #F39C12;
            color: white;
        }}
        
        .severity-3 {{
            background-color: #E74C3C;
            color: white;
        }}
        
        .expand-icon {{
            transition: transform 0.3s;
        }}
        
        .expand-icon.expanded {{
            transform: rotate(180deg);
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
            width: 20px;
            height: 20px;
            margin-right: 8px;
            border-radius: 3px;
        }}
        
        .legend-color.passed {{
            background-color: #27AE60;
        }}
        
        .legend-color.failed {{
            background-color: #E74C3C;
        }}
        
        .legend-color.severity-1 {{
            background-color: #F1C40F;
        }}
        
        .legend-color.severity-2 {{
            background-color: #F39C12;
        }}
        
        .legend-color.severity-3 {{
            background-color: #E74C3C;
        }}
        
        .filter-controls {{
            background: white;
            padding: 15px 20px;
            margin: 10px 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            display: flex;
            gap: 15px;
            align-items: center;
        }}
        
        .filter-controls label {{
            font-weight: bold;
            color: #2C3E50;
        }}
        
        .filter-controls button {{
            padding: 8px 16px;
            border: 1px solid #ddd;
            border-radius: 4px;
            background-color: #f8f9fa;
            cursor: pointer;
            font-size: 13px;
        }}
        
        .filter-controls button:hover {{
            background-color: #e9ecef;
        }}
        
        .filter-controls button.active {{
            background-color: #3498DB;
            color: white;
            border-color: #3498DB;
        }}
        
        #version-toggle {{
            padding: 8px 16px;
            font-size: 13px;
            border: 2px solid white;
            border-radius: 4px;
            background-color: transparent;
            color: white;
            cursor: pointer;
            font-weight: bold;
            transition: all 0.3s;
        }}
        
        #version-toggle:hover {{
            background-color: rgba(255, 255, 255, 0.1);
        }}
        
        #version-toggle.active {{
            background-color: white;
            color: #2C3E50;
        }}
        
        .timestamp-info {{
            background: white;
            padding: 10px 20px;
            margin: 10px 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            font-size: 13px;
            color: #666;
        }}
    </style>
</head>
<body>
    <div id="header">
        <h1>🎯 Power BI Semantic Models - BPA Results</h1>
        <div id="model-selector">
            <label for="model-select">Select Analysis:</label>
            <select id="model-select" onchange="loadModel(this.value)">
                <option value="">-- Choose a result file --</option>
            </select>
            <button id="version-toggle" onclick="toggleVersionMode()" class="active">Latest Only</button>
        </div>
    </div>
    
    <div id="stats">
        <div class="stat-item">
            <span>Pass Rate:</span>
            <span class="pass-rate" id="pass-rate">0%</span>
        </div>
        <div class="stat-item">
            <span>✅</span>
            <strong id="stat-passed">0</strong>
            <span>Passed</span>
        </div>
        <div class="stat-item">
            <span>❌</span>
            <strong id="stat-failed">0</strong>
            <span>Failed</span>
        </div>
        <div class="stat-item">
            <span>📋</span>
            <strong id="stat-total">0</strong>
            <span>Total Rules</span>
        </div>
    </div>
    
    <div class="instructions">
        <strong>💡 How to use:</strong>
        Select a BPA analysis result from the dropdown above. Click on category headers to expand/collapse rule details. Failed rules show violation details with affected objects.
    </div>
    
    <div class="legend">
        <h3>Legend</h3>
        <div class="legend-item">
            <div class="legend-color passed"></div>
            <span>Passed</span>
        </div>
        <div class="legend-item">
            <div class="legend-color failed"></div>
            <span>Failed</span>
        </div>
        <div class="legend-item">
            <div class="legend-color severity-1"></div>
            <span>Info (Severity 1)</span>
        </div>
        <div class="legend-item">
            <div class="legend-color severity-2"></div>
            <span>Warning (Severity 2)</span>
        </div>
        <div class="legend-item">
            <div class="legend-color severity-3"></div>
            <span>Error (Severity 3)</span>
        </div>
    </div>
    
    <div class="filter-controls">
        <label>Show:</label>
        <button id="filter-all" class="active" onclick="filterRules('all')">All Rules</button>
        <button id="filter-failed" onclick="filterRules('failed')">Failed Only</button>
        <button onclick="expandAll()">Expand All</button>
        <button onclick="collapseAll()">Collapse All</button>
    </div>
    
    <div class="timestamp-info" id="timestamp-info"></div>
    
    <div id="content"></div>

    <script type="text/javascript">
        // All models data
        const modelsData = {models_json};
        let currentFilter = 'all';
        let showLatestOnly = true; // Default to latest only
        
        // Get latest analysis per model
        function getLatestAnalyses() {{
            const modelMap = new Map();
            
            // Group by model name and keep only the most recent
            Object.keys(modelsData).forEach(key => {{
                const model = modelsData[key];
                const modelName = model.model_name;
                
                if (!modelMap.has(modelName) || key > modelMap.get(modelName)) {{
                    modelMap.set(modelName, key);
                }}
            }});
            
            return Array.from(modelMap.values());
        }}
        
        // Populate dropdown
        function populateDropdown() {{
            const select = document.getElementById('model-select');
            select.innerHTML = ''; // Clear existing options
            
            // Get keys based on current mode
            let keysToShow;
            if (showLatestOnly) {{
                keysToShow = getLatestAnalyses();
            }} else {{
                keysToShow = Object.keys(modelsData);
            }}
            
            // Sort by filename (most recent first)
            keysToShow.sort().reverse();
            
            keysToShow.forEach(key => {{
                const model = modelsData[key];
                const option = document.createElement('option');
                option.value = key;
                
                // Format: "Model Name - Pass Rate% (YYYY-MM-DD HH:MM)"
                const passRate = model.data.pass_rate.toFixed(1);
                const timestamp = model.file_name.substring(0, 13).replace('_', ' ');
                option.textContent = `${{model.model_name}} - ${{passRate}}% (${{timestamp}})`;
                
                select.appendChild(option);
            }});
            
            // Load first model by default
            if (keysToShow.length > 0) {{
                const firstModel = keysToShow[0];
                select.value = firstModel;
                loadModel(firstModel);
            }}
        }}
        
        function toggleVersionMode() {{
            showLatestOnly = !showLatestOnly;
            const toggleBtn = document.getElementById('version-toggle');
            
            if (showLatestOnly) {{
                toggleBtn.textContent = 'Latest Only';
                toggleBtn.classList.add('active');
            }} else {{
                toggleBtn.textContent = 'All Analyses';
                toggleBtn.classList.remove('active');
            }}
            
            populateDropdown();
        }}
        
        // Initialize dropdown on load
        populateDropdown();
        
        function loadModel(modelKey) {{
            if (!modelKey || !modelsData[modelKey]) return;
            
            const model = modelsData[modelKey];
            const data = model.data;
            
            // Update stats
            const passRate = data.pass_rate;
            const passRateElem = document.getElementById('pass-rate');
            passRateElem.textContent = passRate.toFixed(1) + '%';
            passRateElem.className = 'pass-rate ' + getPassRateClass(passRate);
            
            document.getElementById('stat-passed').textContent = data.stats.passed;
            document.getElementById('stat-failed').textContent = data.stats.failed;
            document.getElementById('stat-total').textContent = data.stats.total;
            
            // Update timestamp info
            const timestampInfo = document.getElementById('timestamp-info');
            timestampInfo.innerHTML = `<strong>File:</strong> ${{model.file_name}} | <strong>Model:</strong> ${{model.model_name}}`;
            
            // Render categories and rules
            renderCategories(data.categories);
        }}
        
        function getPassRateClass(passRate) {{
            if (passRate >= 80) return 'good';
            if (passRate >= 60) return 'warning';
            return 'bad';
        }}
        
        function renderCategories(categories) {{
            const content = document.getElementById('content');
            content.innerHTML = '';
            
            // Sort categories by name
            const sortedCategories = Object.entries(categories).sort((a, b) => a[0].localeCompare(b[0]));
            
            sortedCategories.forEach(([categoryName, categoryData]) => {{
                const section = document.createElement('div');
                section.className = 'category-section';
                section.setAttribute('data-category', categoryName);
                
                const hasFailures = categoryData.failed > 0;
                
                const header = document.createElement('div');
                header.className = 'category-header' + (hasFailures ? ' failed' : '');
                header.onclick = () => toggleCategory(categoryName);
                
                header.innerHTML = `
                    <div class="category-title">
                        <span class="expand-icon">▼</span>
                        <span>${{categoryName}}</span>
                    </div>
                    <div class="category-stats">
                        <span>✅ ${{categoryData.passed}}</span>
                        <span>❌ ${{categoryData.failed}}</span>
                        <span>📊 ${{categoryData.pass_rate.toFixed(1)}}%</span>
                    </div>
                `;
                
                const contentDiv = document.createElement('div');
                contentDiv.className = 'category-content';
                contentDiv.id = 'category-' + categoryName.replace(/\\s+/g, '-');
                
                // Render rules
                categoryData.rules.forEach((rule, ruleIndex) => {{
                    const ruleDiv = document.createElement('div');
                    ruleDiv.className = 'rule-item ' + rule.status;
                    ruleDiv.setAttribute('data-status', rule.status);
                    const ruleId = `rule-${{categoryName.replace(/\\s+/g, '-')}}-${{ruleIndex}}`;
                    
                    const hasDetails = rule.description || rule.violations.length > 0;
                    const violationCount = rule.violations.length;
                    const violationBadge = violationCount > 0 ? ` <span style="font-size: 12px; color: #E74C3C; font-weight: bold;">(${{violationCount}} Violation${{violationCount > 1 ? 's' : ''}})</span>` : '';
                    
                    let html = `
                        <div class="rule-header" onclick="toggleRule('${{ruleId}}')">
                            <div class="rule-name">
                                ${{hasDetails ? '<span class="rule-expand-icon" id="icon-' + ruleId + '">▼</span>' : ''}}
                                ${{rule.name}}${{violationBadge}}
                                <span class="severity-badge severity-${{rule.severity}}">Severity ${{rule.severity}}</span>
                            </div>
                            <div class="rule-status ${{rule.status}}">${{rule.status}}</div>
                        </div>
                        <div class="rule-description" id="desc-${{ruleId}}">${{rule.description}}</div>
                    `;
                    
                    if (rule.violations.length > 0) {{
                        const objectCount = rule.violations.length;
                        html += `
                            <div class="violations-section" id="viol-${{ruleId}}">
                                <div class="violations-header" onclick="toggleViolationsList('${{ruleId}}')">
                                    <span class="violations-expand-icon" id="viol-icon-${{ruleId}}">▼</span>
                                    🚨 ${{objectCount}} Object${{objectCount > 1 ? 's' : ''}} in Violation
                                </div>
                                <div class="violations-list" id="viol-list-${{ruleId}}">
                        `;
                        
                        rule.violations.forEach(violation => {{
                            html += `
                                <div class="violation-item">
                                    <div class="violation-object">📌 ${{violation.object}}</div>
                                </div>
                            `;
                        }});
                        
                        html += '</div></div>';
                    }}
                    
                    ruleDiv.innerHTML = html;
                    contentDiv.appendChild(ruleDiv);
                }});
                
                section.appendChild(header);
                section.appendChild(contentDiv);
                content.appendChild(section);
            }});
            
            // Apply current filter
            applyFilter();
        }}
        
        function toggleCategory(categoryName) {{
            const contentId = 'category-' + categoryName.replace(/\\s+/g, '-');
            const content = document.getElementById(contentId);
            const section = content.parentElement;
            const icon = section.querySelector('.expand-icon');
            
            content.classList.toggle('expanded');
            icon.classList.toggle('expanded');
        }}
        
        function toggleRule(ruleId) {{
            const desc = document.getElementById('desc-' + ruleId);
            const viol = document.getElementById('viol-' + ruleId);
            const icon = document.getElementById('icon-' + ruleId);
            
            if (desc) {{
                desc.classList.toggle('expanded');
            }}
            if (viol) {{
                viol.classList.toggle('expanded');
            }}
            if (icon) {{
                icon.classList.toggle('expanded');
            }}
        }}
        
        function toggleViolationsList(ruleId) {{
            const list = document.getElementById('viol-list-' + ruleId);
            const icon = document.getElementById('viol-icon-' + ruleId);
            
            if (list) {{
                list.classList.toggle('expanded');
            }}
            if (icon) {{
                icon.classList.toggle('expanded');
            }}
        }}
        
        function expandAll() {{
            // Expand all categories
            document.querySelectorAll('.category-content').forEach(el => {{
                el.classList.add('expanded');
            }});
            document.querySelectorAll('.expand-icon').forEach(el => {{
                el.classList.add('expanded');
            }});
            // Expand all rule descriptions
            document.querySelectorAll('.rule-description').forEach(el => {{
                el.classList.add('expanded');
            }});
            document.querySelectorAll('.rule-expand-icon').forEach(el => {{
                el.textContent = '▲';
            }});
            // Expand all violation sections
            document.querySelectorAll('.violations-section').forEach(el => {{
                el.classList.add('expanded');
            }});
            // Expand all violation lists
            document.querySelectorAll('.violations-list').forEach(el => {{
                el.classList.add('expanded');
            }});
            document.querySelectorAll('.violations-expand-icon').forEach(el => {{
                el.textContent = '▲';
            }});
        }}
        
        function collapseAll() {{
            // Collapse all categories
            document.querySelectorAll('.category-content').forEach(el => {{
                el.classList.remove('expanded');
            }});
            document.querySelectorAll('.expand-icon').forEach(el => {{
                el.classList.remove('expanded');
            }});
            // Collapse all rule descriptions
            document.querySelectorAll('.rule-description').forEach(el => {{
                el.classList.remove('expanded');
            }});
            document.querySelectorAll('.rule-expand-icon').forEach(el => {{
                el.textContent = '▼';
            }});
            // Collapse all violation sections
            document.querySelectorAll('.violations-section').forEach(el => {{
                el.classList.remove('expanded');
            }});
            // Collapse all violation lists
            document.querySelectorAll('.violations-list').forEach(el => {{
                el.classList.remove('expanded');
            }});
            document.querySelectorAll('.violations-expand-icon').forEach(el => {{
                el.textContent = '▼';
            }});
        }}
        
        function filterRules(filter) {{
            currentFilter = filter;
            
            // Update button states
            document.getElementById('filter-all').classList.toggle('active', filter === 'all');
            document.getElementById('filter-failed').classList.toggle('active', filter === 'failed');
            
            applyFilter();
        }}
        
        function applyFilter() {{
            document.querySelectorAll('.rule-item').forEach(rule => {{
                const status = rule.getAttribute('data-status');
                
                if (currentFilter === 'all') {{
                    rule.style.display = '';
                }} else if (currentFilter === status) {{
                    rule.style.display = '';
                }} else {{
                    rule.style.display = 'none';
                }}
            }});
            
            // Hide empty categories
            document.querySelectorAll('.category-section').forEach(section => {{
                const visibleRules = Array.from(section.querySelectorAll('.rule-item')).filter(rule => {{
                    return rule.style.display !== 'none';
                }});
                section.style.display = visibleRules.length > 0 ? '' : 'none';
            }});
        }}
    </script>
</body>
</html>"""
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✓ Multi-model BPA viewer saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description='Generate interactive HTML viewer for Tabular Editor BPA results',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --input ./bpa_results --output bpa_viewer.html
  %(prog)s --input . --output report.html --no-browser
  %(prog)s  # Scans current directory, opens in browser
        """
    )
    parser.add_argument(
        '--input', '-i',
        type=Path,
        default=Path.cwd(),
        help='Path to directory containing TRX files (default: current directory, searches recursively)'
    )
    parser.add_argument(
        '--output', '-o',
        type=Path,
        default=None,
        help='Output HTML file path (default: bpa_results_viewer.html in input directory)'
    )
    parser.add_argument(
        '--no-browser',
        action='store_true',
        help='Do not open browser after generating HTML'
    )
    
    args = parser.parse_args()
    
    # Resolve input path
    input_path = args.input.resolve()
    if not input_path.exists():
        print(f"❌ Input path does not exist: {input_path}")
        return 1
    
    # Find TRX files recursively if input is a directory
    if input_path.is_dir():
        print(f"🔍 Scanning for BPA TRX files in: {input_path}")
        trx_files = list(input_path.rglob("*.trx"))
    elif input_path.is_file() and input_path.suffix == '.trx':
        trx_files = [input_path]
        input_path = input_path.parent
    else:
        print(f"❌ Invalid input: must be directory or .trx file")
        return 1
    
    if not trx_files:
        print(f"❌ No TRX files found in: {input_path}")
        print("   Run BPA analysis first to generate TRX files.")
        return 1
    
    print(f"Found {len(trx_files)} BPA result file(s)")
    
    models_data = {}
    
    for trx_file in sorted(trx_files, reverse=True):  # Most recent first
        print(f"  Processing: {trx_file.name}")
        
        try:
            trx_data = parse_trx_file(trx_file)
            
            if trx_data:
                viz_data = prepare_visualization_data(trx_data)
                
                # Use filename as unique key
                file_key = trx_file.stem
                
                models_data[file_key] = {
                    'model_name': trx_data['model_name'],
                    'file_name': trx_data['file_name'],
                    'data': viz_data
                }
                
                pass_rate = viz_data['pass_rate']
                print(f"    ✓ {viz_data['stats']['total']} rules, {pass_rate:.1f}% pass rate")
            else:
                print(f"    ⚠ Could not parse file")
        except Exception as e:
            print(f"    ✗ Error: {e}")
    
    if not models_data:
        print("No valid BPA results found.")
        return 1
    
    # Determine output path
    if args.output:
        output_html = args.output.resolve()
        output_html.parent.mkdir(parents=True, exist_ok=True)
    else:
        output_html = input_path / "bpa_results_viewer.html"
    
    print(f"\n🎨 Creating BPA results viewer...")
    create_multi_model_html(models_data, output_html)
    
    print(f"\n✅ Done! Viewer saved to: {output_html}")
    print(f"   BPA results available: {len(models_data)}")
    
    # Open in browser unless --no-browser specified
    if not args.no_browser:
        print(f"   Opening in browser...")
        webbrowser.open(output_html.as_uri())
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
