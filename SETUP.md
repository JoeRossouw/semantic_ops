# MkDocs Setup Guide

## Installation

```powershell
# Install MkDocs Material
pip install -r requirements.txt
```

## Local Development

```powershell
# Serve docs locally with live reload
mkdocs serve

# Opens at http://127.0.0.1:8000/
```

## Building Static Site

```powershell
# Generate static HTML in site/ folder
mkdocs build
```

## Deploying to GitHub Pages

### Automatic (Recommended)
Push to `main` branch - GitHub Actions will auto-deploy.

### Manual
```powershell
# Deploy to gh-pages branch
mkdocs gh-deploy
```

Site will be available at: `https://joerossouw.github.io/semantic_ops/`

## Content Organization

- **Blog posts**: Write in `docs/blog/` with LinkedIn sections
- **Tool docs**: Reference documentation in `docs/tools/`
- **Tutorials**: Step-by-step guides in `docs/tutorials/`
- **Guides**: How-to content in `docs/guides/`
- **Scripts**: Python tools in `scripts/` folder
- **Samples**: Model/report samples in `samples/` folder

## Adding New Content

1. Create `.md` file in appropriate `docs/` subfolder
2. Add entry to `nav:` section in `mkdocs.yml`
3. Test locally with `mkdocs serve`
4. Commit and push - auto-deploys via GitHub Actions

## MkDocs Material Features

- **Search**: Built-in full-text search
- **Dark mode**: Toggle in header
- **Code copy**: Click icon on code blocks
- **Navigation tabs**: Top-level sections
- **Mobile responsive**: Works on all devices
- **Mermaid diagrams**: Use `mermaid` code blocks
- **Admonitions**: Use `!!! note`, `!!! warning`, etc.

## Troubleshooting

### YAML errors in mkdocs.yml
The `!!python/name:` tags are MkDocs-specific and safe to ignore in IDE warnings.

### Links not working
Use relative paths: `[Link](../tools/bpa-viewer.md)` not absolute paths.

### Images not showing
Place images in `docs/images/` and reference: `![Alt](../images/pic.png)`
