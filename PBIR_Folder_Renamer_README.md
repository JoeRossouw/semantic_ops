# PBIR Folder Renamer for Power BI Reports

Rename Power BI report page and visual folders from GUIDs to human-readable names based on their metadata.

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

## Quick Start

**Any platform (Python 3.7+):**
```bash
python rename_pbir_folders.py
```

**macOS/Linux:**
```bash
python3 rename_pbir_folders.py
```

**Features:**
- ✅ Interactive mode (prompts for path)
- ✅ Direct mode (command-line argument)
- ✅ Colored output
- ✅ Cross-platform (Windows, macOS, Linux)
- ✅ No external dependencies

---

## Usage

### Interactive Mode (Recommended)

```bash
python rename_pbir_folders.py
```

The script will prompt you for the path to your `.Report` folder.

### Command-Line Mode

**Windows:**
```bash
python rename_pbir_folders.py "C:\path\to\MyReport.Report"
```

**macOS/Linux:**
```bash
python rename_pbir_folders.py "/path/to/MyReport.Report"
```

### Help

```bash
python rename_pbir_folders.py --help
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
- **Blog Post**: [Making PBIR Code Reviews Actually Readable](./blog_pbir_readable_folders.md) *(coming soon)*

---

## Contributing

Found a bug? Have a suggestion? Open an issue or submit a pull request!

---

## License

MIT - Use freely in your projects

---

## Get Ready for January 2026

PBIR is becoming mandatory. Start using readable folder names now, before your team is forced to deal with GUID-based code reviews.
