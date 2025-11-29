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

# PBIR Is Great, But Your Pull Requests Are Unreadable

On November 17, 2025, Microsoft [announced that PBIR becomes the default Power BI report format](https://powerbi.microsoft.com/en-us/blog/pbir-will-become-the-default-power-bi-report-format-get-ready-for-the-transition/) starting January 2026. Reports as text files, source control, CI/CD, pull requests. This is what we've been waiting for.

But have you actually tried reviewing PBIR changes in GitHub or Azure DevOps?

<!-- more -->

## The Announcement

From Rui Romano's blog post:

> "The Power BI Enhanced Report Format (PBIR) represents a major leap forward, empowering developers and teams to integrate source control, CI/CD, and collaborative development while enabling AI agents and scripts to programmatically create, edit, and manage Power BI reports in a fully supported way."

Microsoft is right. PBIR enables professional development workflows for Power BI. Text-based reports mean version control, code reviews, and CI/CD pipelines finally work properly.

But there's a practical problem that gets in the way.

## The Code Review Problem

Your pull request shows changes to:
- `definition/pages/50dd411cef39de30a198/page.json`
- `definition/pages/50dd411cef39de30a198/visuals/2402e6f6ec7ad97e9443/visual.json`

**Which page is this? What visual changed?**

You have to open every file to find out.

That's not a code review workflow. That's friction.

## Why This Happens

PBIR saves report structure as folders and JSON files:

![PBIR folders before renaming - GUIDs everywhere](../../assets/images/blog/pbir-folders-before.png)

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

![PBIR folders after renaming - readable names](../../assets/images/blog/pbir-folders-after.png)

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

![Readable diffs in pull requests](../../assets/images/blog/pbir-diff-readable.png)

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

Microsoft's vision for PBIR is spot-on. Version control, code reviews, CI/CD pipelines, AI integration, team collaboration. Power BI finally gets professional development workflows.

But workflows only matter if your team can understand what changed. GUID folder names get in the way. This script fixes that.


## Try It Yourself

1. Save one of your reports in `.pbip` format
2. Download the script: [rename_pbir_folders.py](https://raw.githubusercontent.com/JoeRossouw/semantic_ops/main/scripts/rename_pbir_folders.py)
3. Run it on your `.Report` folder
4. Check the results
5. Make a change to your report
6. Look at the git diff

---

**Resources:**

- [Microsoft Announcement: PBIR Becomes Default Format](https://powerbi.microsoft.com/en-us/blog/pbir-will-become-the-default-power-bi-report-format-get-ready-for-the-transition/) (Rui Romano, November 2025)
- [PBIR Folder Renamer Tool](../../tools/pbir-folder-renamer-guide.md)
- [Microsoft PBIR Documentation](https://learn.microsoft.com/power-bi/developer/projects/projects-report)

**Related:**

- [BPA Results Viewer](bpa-viewer-tool.md)
- [Building Tools with AI](agentic-ai-pbip.md)

