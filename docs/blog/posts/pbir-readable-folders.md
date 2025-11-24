---
date: 2025-11-22
authors:
  - joe
categories:
  - Tools
  - DevOps
  - Best Practices
tags:
  - PBIR
  - PBIP
  - Source Control
  - Code Review
  - CI/CD
  - GitHub
  - Azure DevOps
---

# Making PBIR Code Reviews Actually Readable

Microsoft just announced PBIR becomes the default Power BI report format in January 2026. This enables professional development workflows with source control, CI/CD, and pull requests.

But there's a problem nobody's talking about: PBIR uses GUID folder names, making code reviews impossible to understand.

<!-- more -->

## Microsoft Just Made PBIR Mandatory

On November 17, 2025, Rui Romano (Principal Program Manager at Microsoft) announced that **PBIR will become the default Power BI report format starting January 2026**.

From his blog post:

> "The Power BI Enhanced Report Format (PBIR) represents a major leap forward, empowering developers and teams to integrate source control, CI/CD, and collaborative development while enabling AI agents and scripts to programmatically create, edit, and manage Power BI reports in a fully supported way."

This is huge. After GA, PBIR becomes the only supported format. Every report will be text-based, version-controllable, and CI/CD-ready.

Microsoft is right: this enables professional development workflows for Power BI.

**But there's a problem nobody's talking about.**

## The Code Review Problem

PBIR is revolutionary. Reports as text files, finally! Source control, CI/CD, pull requests, the works.

But have you actually tried reviewing PBIR changes in GitHub or Azure DevOps?

Your pull request shows changes to:
- `definition/pages/50dd411cef39de30a198/page.json`
- `definition/pages/50dd411cef39de30a198/visuals/2402e6f6ec7ad97e9443/visual.json`

**Which page is this? What visual changed?**

You have to open every file to find out.

That's not a code review workflow. That's friction.

## Why This Happens

PBIR saves report structure as folders and JSON files:

```
MyReport.Report/
└── definition/
    └── pages/
        ├── 50dd411cef39de30a198/           # Page folder (GUID)
        │   ├── page.json                   # Contains displayName: "Sales Overview"
        │   └── visuals/
        │       ├── 2402e6f6ec7ad97e9443/   # Visual folder (GUID)
        │       │   └── visual.json         # Contains visualType: "clusteredBarChart"
        │       └── 33956a0230202bce8bc1/
        │           └── visual.json
        └── 8a889a93607ccc246a98/
```

The folder names are auto-generated GUIDs. They don't change when you rename pages or visuals in Power BI Desktop.

## The Solution

Rename the folders to match their actual content.

**Before:**
```
MyReport.Report/definition/pages/
└── 50dd411cef39de30a198/
    └── visuals/
        ├── 2402e6f6ec7ad97e9443/
        └── 33956a0230202bce8bc1/
```

**After:**
```
MyReport.Report/definition/pages/
└── Sales_Overview_50dd411cef39de30a198/
    └── visuals/
        ├── clusteredBarChart_2402e6f6ec7ad97e9443/
        └── card_33956a0230202bce8bc1/
```

Now your git diffs tell the story.

## Get the Script

**Download:** [rename_pbir_folders.py](https://raw.githubusercontent.com/JoeRossouw/semantic_ops/main/scripts/rename_pbir_folders.py)

Or see the [full documentation page](../../tools/pbir-folder-renamer-guide.md) for detailed setup instructions.

## How It Works

**What the script does:**
1. Scans your `.Report` folder for page directories
2. Reads `page.json` files to extract `displayName` and `name`
3. Renames folders to `{displayName}_{name}` format
4. Recursively processes all visual folders within each page
5. Reads `visual.json` to extract `visualType` and `name`
6. Renames visual folders to `{visualType}_{name}` format

**Usage:**

```bash
# Interactive mode
python rename_pbir_folders.py

# Direct mode
python rename_pbir_folders.py "/path/to/MyReport.Report"
```

## Impact on Code Reviews

**Before (Meaningless Diffs):**

Reviewer sees:
- Modified: `definition/pages/50dd411cef39de30a198/page.json`
- Modified: `definition/pages/50dd411cef39de30a198/visuals/2402e6f6ec7ad97e9443/visual.json`

Reviewer thinks: "What is this? Let me dig into every file..."

**After (Self-Documenting Diffs):**

Reviewer sees:
- Modified: `definition/pages/Sales_Overview_50dd411cef39de30a198/page.json`
- Modified: `definition/pages/Sales_Overview_50dd411cef39de30a198/visuals/clusteredBarChart_2402e6f6ec7ad97e9443/visual.json`

Reviewer thinks: "Oh, they changed the sales chart. Got it."

## When to Run This

**Recommended workflow:**
1. Save your `.pbip` project after making report changes
2. Run the renaming script before committing
3. Commit with clear folder names

**Automation:**

You can integrate this into your CI/CD pipeline to run automatically on PR merge, pre-commit hooks, or scheduled workflows. The script works in any automation environment that supports Python.

## Important Notes

**This is cosmetic and safe:**
- Only renames folders, doesn't modify JSON content
- Power BI Desktop reads reports by JSON structure, not folder names
- Completely reversible (can always re-run with different names)

**Edge cases handled:**
- Duplicate names (script warns and skips)
- Special characters in names (sanitized to file-system safe)
- Missing metadata (script warns and skips)
- Already-correct names (script skips silently)

## The Bigger Picture

Microsoft's vision for PBIR is spot-on:
- Version control (Git): Track every change to your reports
- Code reviews (PRs): Collaborative development with proper approval workflows
- CI/CD pipelines: Automated deployment and testing
- AI integration: Programmatic report creation and management
- Team collaboration: Multiple developers working on the same report

These are professional development workflows. Power BI needed this.

**But workflows are only useful if your team can actually understand what changed.**

GUID folder names break the code review workflow. This script fixes it.


## Try It Yourself

1. Save one of your reports in `.pbip` format
2. Download the script: [rename_pbir_folders.py](https://raw.githubusercontent.com/JoeRossouw/semantic_ops/main/scripts/rename_pbir_folders.py)
3. Run it on your `.Report` folder
4. Check the results
5. Make a change to your report
6. Look at the git diff

---

**Resources:**
- [Rui Romano's Announcement](https://powerbi.microsoft.com/en-us/blog/pbir-will-become-the-default-power-bi-report-format-get-ready-for-the-transition/) (November 17, 2025)
- [PBIR Folder Renamer Tool](../../tools/pbir-folder-renamer-guide.md)
- [Microsoft PBIR Documentation](https://learn.microsoft.com/power-bi/developer/projects/projects-report)

**Related:**
- [BPA Results Viewer](bpa-viewer-tool.md)
- [Building Tools with AI](agentic-ai-pbip.md)

