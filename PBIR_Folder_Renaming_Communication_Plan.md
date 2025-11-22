# PBIR Folder Renaming - Communication Plan

## 📋 Overview

**Problem**: PBIR uses GUID/random identifiers for page and visual folder names, making code reviews in GitHub/Azure DevOps impossible to understand.

**Solution**: PowerShell script that renames folders to human-readable format using metadata from JSON files.

**Target Audience**: Power BI developers using PBIP/PBIR format with source control and CI/CD.

---

## 🎯 Content Pieces

### 1. LinkedIn Post (Primary - Drive Traffic)

**Goal**: Quick hit to grab attention, drive to blog/repo

**Character Count**: ~1,000 characters (LinkedIn sweet spot)

**Draft**:

```
Microsoft just announced: PBIR becomes the default Power BI report format in January 2026.

Rui Romano says this enables "code-friendly file formats" for source control and CI/CD.

Great! Except...

Have you tried reviewing PBIR changes in GitHub? 🤔

BEFORE script:
MyReport.Report/                           # Report folder
└── definition/pages/
    ├── 50dd411cef39de30a198/               # Page folder (GUID)
    │   └── visuals/
    │       ├── 2402e6f6ec7ad97e9443/       # Visual folder (GUID)
    │       └── 33956a0230202bce8bc1/       # Visual folder (GUID)

What page? What visual? Who knows. 🤷‍♂️

AFTER script:
MyReport.Report/                           # Report folder
└── definition/pages/
    ├── Sales_Overview_50dd411cef39de30a198/  # Page folder (readable!)
    │   └── visuals/
    │       ├── clusteredBarChart_2402e6f6ec7ad97e9443/  # Visual folder (readable!)
    │       └── card_33956a0230202bce8bc1/               # Visual folder (readable!)

Now code reviews actually make sense.

The Reality Check:
PBIR unlocks professional workflows - version control, PRs, CI/CD pipelines.
But folder names are GUIDs. Your team's code reviews become guessing games.

"What changed in 50dd411cef39de30a198?"
"Let me open the file and check... oh, it's the sales page."

That's not a workflow. That's friction.

The Fix:
Python script that reads your metadata and prefixes folder names:
✅ Reads page.json and visual.json
✅ Transforms: 50dd411cef → Sales_Overview_50dd411cef
✅ Makes git diffs self-documenting
✅ Cross-platform (Windows, macOS, Linux)

PBIR is becoming mandatory. Microsoft is right - it enables professional development.
But only if your team can actually understand what changed.

Script + full write-up:
[Link to repo/blog]

PBIR is coming in January 2026.

#PowerBI #PBIR #DevOps #CICD #SourceControl #DataEngineering

Credit: Rui Romano's announcement: https://powerbi.microsoft.com/en-us/blog/pbir-will-become-the-default-power-bi-report-format-get-ready-for-the-transition/
```

**Posting Strategy**:
- Post between 8-10am or 12-2pm (weekday)
- Include 2-3 screenshots:
  1. Before/After folder structure comparison
  2. GitHub PR diff showing readable folder names
  3. Script execution in terminal
- Pin comment with link to full blog post

---

### 2. Blog Post (Repository - Full Technical Detail)

**Location**: `semantic_forge/blog_pbir_readable_folders.md`

**Structure**:

```markdown
# Making PBIR Code Reviews Actually Readable

## Microsoft Just Made PBIR Mandatory

On November 17, 2025, Rui Romano (Principal Program Manager at Microsoft) announced that **PBIR will become the default Power BI report format starting January 2026**.

From his blog post:

> "The Power BI Enhanced Report Format (PBIR) represents a major leap forward – empowering developers and teams to integrate source control, CI/CD, and collaborative development while enabling AI agents and scripts to programmatically create, edit, and manage Power BI reports in a fully supported way."

This is huge. After GA, PBIR becomes the *only* supported format. Every report will be text-based, version-controllable, and CI/CD-ready.

Microsoft is right: this enables professional development workflows for Power BI.

**But there's a problem nobody's talking about.**

## The Code Review Problem

PBIR is revolutionary - reports as text files, finally! Source control, CI/CD, pull requests, the works.

But have you actually tried reviewing PBIR changes in GitHub or Azure DevOps?

[Screenshot: GitHub PR with GUID folder names]

Your pull request shows changes to:
- `definition/pages/50dd411cef39de30a198/page.json`
- `definition/pages/50dd411cef39de30a198/visuals/2402e6f6ec7ad97e9443/visual.json`

**Which page is this? What visual changed?**

You have to open every file to find out.

That's not a code review workflow. That's friction.

## Why This Happens

PBIR saves report structure as folders and JSON files:

```
MyReport.Report/                           # Report folder (created by PBIP)
├── definition.pbir
├── semanticModelDiagramLayout.json
└── definition/
    ├── report.json
    └── pages/
        ├── pages.json
        ├── 50dd411cef39de30a198/           # Page folder (GUID - meaningless)
        │   ├── page.json                   # Contains displayName: "Sales Overview"
        │   └── visuals/
        │       ├── 2402e6f6ec7ad97e9443/   # Visual folder (GUID - meaningless)
        │       │   └── visual.json         # Contains visualType: "clusteredBarChart"
        │       └── 33956a0230202bce8bc1/   # Visual folder (GUID - meaningless)
        │           └── visual.json         # Contains visualType: "card"
        └── 8a889a93607ccc246a98/           # Another page folder (GUID)
```

The folder names are auto-generated GUIDs. They don't change when you rename pages/visuals in Power BI Desktop.

## The Solution

Rename the folders to match their actual content.

**Before:**
```
MyReport.Report/definition/pages/
└── 50dd411cef39de30a198/              # Page folder
    └── visuals/
        ├── 2402e6f6ec7ad97e9443/       # Visual folder
        └── 33956a0230202bce8bc1/       # Visual folder
```

**After:**
```
MyReport.Report/definition/pages/
└── Sales_Overview_50dd411cef39de30a198/     # Page folder (now readable!)
    └── visuals/
        ├── clusteredBarChart_2402e6f6ec7ad97e9443/  # Visual folder (now readable!)
        └── card_33956a0230202bce8bc1/               # Visual folder (now readable!)
```

Now your git diffs tell the story.

## The Script

[Link to rename_pbir_folders.py]

**What it does:**
1. Scans your `.Report` folder for page directories
2. Reads `page.json` files to extract `displayName` and `name`
3. Renames folders to `{displayName}_{name}` format
4. Recursively processes all visual folders within each page
5. Reads `visual.json` to extract `visualType` and `name`
6. Renames visual folders to `{visualType}_{name}` format

**How to use:**

```bash
# Interactive mode
python rename_pbir_folders.py

# Direct mode
python rename_pbir_folders.py "/path/to/MyReport.Report"
```

[Screenshot: Script execution with success messages]

## Impact on Code Reviews

### Before: Meaningless Diffs

[Screenshot: GitHub PR showing changes to GUIDs]

Reviewer sees:
- Modified: `definition/pages/50dd411cef39de30a198/page.json`
- Modified: `definition/pages/50dd411cef39de30a198/visuals/2402e6f6ec7ad97e9443/visual.json`

Reviewer thinks: "What is this? Let me dig into every file..."

### After: Self-Documenting Diffs

[Screenshot: GitHub PR showing changes to readable names]

Reviewer sees:
- Modified: `definition/pages/Sales_Overview_50dd411cef39de30a198/page.json`
- Modified: `definition/pages/Sales_Overview_50dd411cef39de30a198/visuals/clusteredBarChart_2402e6f6ec7ad97e9443/visual.json`

Reviewer thinks: "Oh, they changed the sales chart. Got it."

## When to Run This

**Recommended workflow:**
1. Save your `.pbip` project after making report changes
2. Run the renaming script before committing
3. Commit with clear folder names
4. Your team reviews readable diffs

**Automation option:**
Add as a pre-commit hook or CI/CD pipeline step:

```yaml
# Azure DevOps example
- task: UsePythonVersion@0
  inputs:
    versionSpec: '3.x'
- script: |
    python scripts/rename_pbir_folders.py "$(Build.SourcesDirectory)/reports/MyReport.Report"
  displayName: 'Rename PBIR folders to readable names'
```

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
- ✅ **Version control** (Git) - Track every change to your reports
- ✅ **Code reviews** (PRs) - Collaborative development with proper approval workflows  
- ✅ **CI/CD pipelines** - Automated deployment and testing
- ✅ **AI integration** - Programmatic report creation and management
- ✅ **Team collaboration** - Multiple developers working on the same report

These are professional development workflows. Power BI needed this.

**But workflows are only useful if your team can actually understand what changed.**

GUID folder names break the code review workflow. This script fixes it.

## The Timeline

From Rui Romano's announcement:
- **January 2026**: PBIR becomes default format for all new reports
- **January 2026**: Existing reports auto-convert to PBIR when edited
- **2026 (GA)**: PBIR becomes the *only* supported format

You have a few months to get your team's PBIR workflow right.

Readable folder names aren't optional - they're essential for making code reviews actually work.

## Try It Yourself

1. Save one of your reports in `.pbip` format
2. Download the script: [link]
3. Run it on your `.Report` folder
4. Check the results
5. Make a change to your report
6. Look at the git diff

## Resources

- **Rui Romano's Announcement**: [PBIR will become the default Power BI Report Format](https://powerbi.microsoft.com/en-us/blog/pbir-will-become-the-default-power-bi-report-format-get-ready-for-the-transition/) (November 17, 2025)
- **This Script**: [rename_pbir_folders.py](./rename_pbir_folders.py)
- **Microsoft PBIR Docs**: [Power BI Projects - Report Format](https://learn.microsoft.com/power-bi/developer/projects/projects-report)

## Get Ready for January 2026

PBIR is coming. Microsoft is forcing the transition because text-based reports unlock professional workflows.

But those workflows only work if your team can understand what changed in a pull request.

Start using readable folder names now, before PBIR becomes mandatory.

---

**Tags**: #PowerBI #PBIR #PBIP #DevOps #SourceControl #CodeReview #CI/CD
```

---

### 3. README for Script (Repository)

**Location**: `semantic_forge/PBIR_Folder_Renamer_README.md`

**Content**:

```markdown
# PBIR Folder Renamer for Power BI Reports

Renames Power BI report page and visual folders from GUIDs to human-readable names based on their metadata.

## Problem

PBIR format saves reports with GUID-based folder names:
```
MyReport.Report/definition/pages/
└── 50dd411cef39de30a198/          # Page folder (meaningless GUID)
    └── visuals/
        └── 2402e6f6ec7ad97e9443/   # Visual folder (meaningless GUID)
```

Makes code reviews impossible to understand.

## Solution

Renames to readable format:
```
MyReport.Report/definition/pages/
└── Sales_Overview_50dd411cef39de30a198/        # Now you know it's the Sales Overview page!
    └── visuals/
        └── clusteredBarChart_2402e6f6ec7ad97e9443/  # Now you know it's a bar chart!
```

## Usage

### Interactive Mode
```bash
python rename_pbir_folders.py
```

### Direct Mode
```bash
python rename_pbir_folders.py "/path/to/MyReport.Report"
```

## Requirements

- Python 3.7 or higher
- No external dependencies (standard library only)
- Works on Windows, macOS, Linux

## What It Does

1. **Pages**: Renames folders to `{displayName}_{originalGUID}` format
   - Example: `50dd411cef39de30a198` → `Sales_Overview_50dd411cef39de30a198`

2. **Visuals**: Renames folders to `{visualType}_{originalGUID}` format
   - Example: `2402e6f6ec7ad97e9443` → `clusteredBarChart_2402e6f6ec7ad97e9443`

## Safety

- ✅ Only renames folders, doesn't modify JSON content
- ✅ Power BI Desktop reads reports by structure, not folder names
- ✅ Completely reversible
- ✅ Handles duplicates, special characters, missing metadata
- ✅ Dry-run mode available (shows what would change)

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

## Integration

### Pre-Commit Hook
```bash
#!/bin/bash
python3 ./scripts/rename_pbir_folders.py "./reports/MyReport.Report"
```

### Azure DevOps Pipeline
```yaml
- task: UsePythonVersion@0
  inputs:
    versionSpec: '3.x'
- script: |
    python scripts/rename_pbir_folders.py "$(Build.SourcesDirectory)/reports/MyReport.Report"
  displayName: 'Rename PBIR folders'
```

### GitHub Actions
```yaml
- name: Set up Python
  uses: actions/setup-python@v4
  with:
    python-version: '3.x'
- name: Rename PBIR folders
  run: |
    python scripts/rename_pbir_folders.py "./reports/MyReport.Report"
```

## Troubleshooting

**"Pages directory not found"**
- Ensure you're pointing to a `.Report` folder (not `.SemanticModel`)
- Check that `definition/pages/` exists

**"Target folder already exists"**
- Two pages/visuals have the same display name
- Manually rename one in Power BI Desktop first

**"displayName cannot be sanitized"**
- Display name contains only special characters
- Rename in Power BI Desktop to include alphanumeric characters

## Related

- [Blog Post: Making PBIR Code Reviews Readable](./blog_pbir_readable_folders.md)
- [Microsoft PBIR Documentation](https://learn.microsoft.com/power-bi/developer/projects/projects-report)

## License

MIT - Use freely in your projects
```

---

## 📸 Screenshot Requirements

### Must-Have Screenshots:

1. **Folder Structure Before/After** (side-by-side)
   - Left: GUID folder names in file explorer
   - Right: Readable folder names
   - Annotate with arrows showing transformation

2. **GitHub PR Diff - Before**
   - Pull request Files Changed view
   - Show multiple files with GUID paths
   - Highlight confusion: "What changed?"

3. **GitHub PR Diff - After**
   - Same PR structure but with readable names
   - Highlight clarity: "Oh, sales chart changed"

4. **Script Execution**
   - PowerShell terminal showing script running
   - Success messages with renamed folders
   - Summary statistics at end

5. **VS Code File Explorer**
   - Before: Collapsed folders with GUIDs
   - After: Expanded view showing readable structure

### Optional (Nice-to-Have):

6. **Azure DevOps PR Review**
   - Alternative to GitHub screenshots
   - Shows it works across platforms

7. **Power BI Desktop**
   - Report view showing "Sales Overview" page name
   - Link to corresponding folder name after script

---

## 📅 Publishing Schedule

### Week 1: Preparation
- [ ] Create all screenshots
- [ ] Finalize script with header update
- [ ] Write full blog post
- [ ] Write script README
- [ ] Test script on multiple report types

### Week 2: Launch
- [ ] **Monday**: Publish blog post to repo
- [ ] **Tuesday**: LinkedIn post (morning, 9am)
- [ ] **Wednesday**: Follow up in LinkedIn comments
- [ ] **Thursday**: Cross-post to relevant communities (Reddit r/PowerBI, Power BI Community forums)
- [ ] **Friday**: Gather feedback, update docs

### Ongoing:
- Monitor comments/issues
- Update script based on feedback
- Add to existing PBIP blog posts as reference

---

## 🎯 Success Metrics

**LinkedIn Post**:
- Target: 50+ reactions, 10+ comments
- Track: Click-through rate to repo

**Blog Post**:
- Target: 100+ views in first month
- Track: Time on page, scroll depth

**Script Adoption**:
- Target: 10+ stars on repo
- Track: Downloads, issues, feedback

---

## 💡 Key Messages to Emphasize

1. **"Microsoft just announced PBIR is becoming mandatory"** - Lead with Rui Romano's announcement, create urgency
2. **"PBIR enables professional workflows... but"** - Acknowledge Microsoft's vision while highlighting real friction  
3. **"Code reviews are broken with GUID folders"** - Make the pain point visceral with examples
4. **"Takes 10 seconds to fix"** - Emphasize simplicity and immediate value
5. **"January 2026 is coming"** - Deadline creates action (you have months to get this right)
6. **"Microsoft is right, but incomplete"** - Agree with the vision, provide the missing piece

---

## 🔗 Cross-Promotion Opportunities

**Link to**:
- Your existing PBIP/agentic AI blog post (related workflow)
- Relationship visualizer tool (both about making PBIR usable)
- Microsoft's PBIR announcement (context/validation)

**Mention in**:
- Future posts about CI/CD for Power BI
- Posts about team collaboration
- DevOps best practices content

---

## Next Steps

1. ✅ Update script header (DONE)
2. Create screenshots (prioritize GitHub PR before/after)
3. Write blog post using structure above
4. Draft LinkedIn post
5. Test script on 2-3 different report types
6. Publish and promote

Ready to move forward with any of these pieces?
