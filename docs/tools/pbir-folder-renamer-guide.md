# PBIR Folder Renamer for Power BI Reports

Rename Power BI report page and visual folders from GUIDs to human-readable names based on their metadata.

[:material-download: Download Script](https://raw.githubusercontent.com/JoeRossouw/semantic_ops/main/scripts/rename_pbir_folders.py){ .md-button .md-button--primary }
[:fontawesome-brands-github: View on GitHub](https://github.com/JoeRossouw/semantic_ops/blob/main/scripts/rename_pbir_folders.py){ .md-button }

**Python 3.7+** - Cross-platform, no external dependencies required!

---

## The Problem

PBIR format saves reports with GUID-based folder names:

```
MyReport.Report/definition/pages/
└── 50dd411cef39de30a198/              # Page folder (meaningless GUID)
    └── visuals/
        └── 2402e6f6ec7ad97e9443/       # Visual folder (meaningless GUID)
```

Makes code reviews in GitHub/Azure DevOps impossible to understand.

## The Solution

Renames folders to readable format:

```
MyReport.Report/definition/pages/
└── Sales_Overview_50dd411cef39de30a198/        # Now you know it's the Sales Overview page!
    └── visuals/
        └── clusteredBarChart_2402e6f6ec7ad97e9443/  # Now you know it's a bar chart!
```

Now your git diffs and pull requests make sense.

---

## How to Run

### Step 1: Download the script

Save `rename_pbir_folders.py` anywhere in your repo (root folder, `scripts/`, `tools/`, wherever works for you).

### Step 2: Open a terminal

In VS Code: **Terminal → New Terminal** (or press `` Ctrl+` ``)

### Step 3: Run it

The command is `python` followed by the path to the script. How you write that path depends on where you saved the script.

**Option A: Drag and drop (easiest)**

1. Type `python ` in your terminal (with a space after)
2. Drag the script file from Explorer into the terminal
3. Press Enter

The terminal pastes the full path for you.

**Option B: Navigate to the script first**

```bash
cd path/to/folder/containing/script
python rename_pbir_folders.py
```

**Option C: Ask GitHub Copilot**

In VS Code with Copilot, just ask:

> *"Run the rename_pbir_folders.py script"*

Copilot will figure out the correct path and run it for you.

---

The script auto-detects all `.Report` folders in your repo. If it finds one report, it processes it automatically. If it finds multiple, you get a numbered list to choose from:

```
✓ Found 3 reports:

  [1] reports/Sales.Report
  [2] reports/Marketing.Report  
  [3] reports/Finance.Report

  [0] Process ALL reports

Select a report (0 for all, or 1-3):
```

Pick a number, or enter `0` to rename folders in all reports at once.

![Running the script and selecting a report](../assets/images/tools/pbir-renamer-select-report.png)

### Alternative: Specify a report directly

```bash
python rename_pbir_folders.py "path/to/MyReport.Report"
```

---

## What It Does

### 1. Pages: Renames to `{displayName}_{originalGUID}` format

**Example:**
```
50dd411cef39de30a198 → Sales_Overview_50dd411cef39de30a198
```

Reads `page.json` to extract `displayName` and prepends it to the existing folder name.

### 2. Visuals: Renames to `{visualType}_{originalGUID}` format

**Example:**
```
2402e6f6ec7ad97e9443 → clusteredBarChart_2402e6f6ec7ad97e9443
```

Reads `visual.json` to extract `visualType` and prepends it to the existing folder name.

---

## Requirements

- **Python**: 3.7 or higher
- **No external packages required** (uses only standard library)
- **Works on**: Windows, macOS, Linux

### Installing Python

**Windows:**
1. Download from [python.org/downloads](https://www.python.org/downloads/)
2. Run installer, check "Add Python to PATH"
3. Verify: Open Command Prompt, type `python --version`

**macOS:**
```bash
brew install python3
```
Or download from [python.org/downloads](https://www.python.org/downloads/)

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3
```

**Check if Python is already installed:**
```bash
python --version
# or
python3 --version
```

---

## Output Example

![Terminal output after running the script](../assets/images/tools/pbir-renamer-output.png)

```
=== Power BI Page & Visual Folder Renamer ===
Processing pages directory: C:\MyProject\MyReport.Report\definition\pages

✓ Page renamed: 50dd411cef39de30a198 → Sales_Overview_50dd411cef39de30a198
    ✓ Visual renamed: 2402e6f6ec7ad97e9443 → clusteredBarChart_2402e6f6ec7ad97e9443
    ✓ Visual renamed: 33956a0230202bce8bc1 → card_33956a0230202bce8bc1
✓ Page renamed: 8a889a93607ccc246a98 → Customer_Analysis_8a889a93607ccc246a98
    ✓ Visual renamed: 4c00c3e8380fe1740319 → tableEx_4c00c3e8380fe1740319

Summary:
  Total page folders: 2
  Pages successfully processed: 2
  Visual folders processed: 3
```

---

## Safety

✅ **This is cosmetic and safe:**
- Only renames folders, doesn't modify JSON content
- Power BI Desktop reads reports by JSON structure, not folder names
- Completely reversible (can always re-run with different names)

✅ **Edge cases handled:**
- Duplicate names (script warns and skips)
- Special characters in names (sanitized to file-system safe)
- Missing metadata (script warns and skips)
- Already-correct names (script skips silently)

---

## Troubleshooting

### "Pages directory not found"
- Ensure you're pointing to a `.Report` folder (not `.SemanticModel`)
- Check that `definition/pages/` exists within the folder
- Verify you're using PBIP format (not legacy `.pbix`)

### "Target folder already exists"
- Two pages/visuals have the same display name
- Manually rename one in Power BI Desktop first to make them unique

### "displayName cannot be sanitized"
- Display name contains only special characters
- Rename in Power BI Desktop to include alphanumeric characters

### Python "command not found" (macOS/Linux)
```bash
# Try python3 instead
python3 rename_pbir_folders.py
```

---

## Why This Matters

### Microsoft's PBIR Announcement
On November 17, 2025, Microsoft announced that **PBIR will become the default Power BI report format in January 2026**.

PBIR enables:
- ✅ Version control (Git)
- ✅ Code reviews (Pull Requests)
- ✅ CI/CD pipelines
- ✅ Automated testing
- ✅ Team collaboration

**But GUID folder names make code reviews impossible.**

Your pull request shows:
```
Modified: definition/pages/50dd411cef39de30a198/page.json
```

What page is that? Nobody knows without opening the file.

### With readable folder names:
```
Modified: definition/pages/Sales_Overview_50dd411cef39de30a198/page.json
```

Now reviewers instantly understand what changed.

---

## Related Resources

- **Microsoft's Announcement**: [PBIR will become the default Power BI Report Format](https://powerbi.microsoft.com/en-us/blog/pbir-will-become-the-default-power-bi-report-format-get-ready-for-the-transition/) (Rui Romano, November 17, 2025)
- **Microsoft PBIR Docs**: [Power BI Projects - Report Format](https://learn.microsoft.com/power-bi/developer/projects/projects-report)

---

## Contributing

Found a bug? Have a suggestion? Open an issue or submit a pull request!

---

## License

MIT - Use freely in your projects

---

## Get Ready for January 2026

PBIR is becoming mandatory. Start using readable folder names now, before your team is forced to deal with GUID-based code reviews.

