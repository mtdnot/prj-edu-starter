# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Jupyter Book project template for educational content about earthquake prediction science ("わかりやすい地震予知学"). It automates:
- Website building and deployment via GitHub Pages
- Social media feed generation (latest.json) for n8n automation
- X (Twitter) posts and YouTube script generation through n8n workflows

## Commands

### Build Jupyter Book locally
```bash
jupyter-book build .
```

### Generate social feed JSON
```bash
python tools/build_latest_json.py --out _build/html/social/latest.json
```

### Install dependencies
```bash
python -m pip install "jupyter-book<2" pyyaml
```

## Architecture

### Content Management
- Articles go in `content/` as MyST Markdown files
- Each article requires YAML front matter with: title, date, slug, summary, tags, status
- Only articles with `status: published` appear in the social feed
- Table of contents is managed in `_toc.yml`

### Deployment Pipeline
1. Push to main branch triggers GitHub Actions workflow
2. Workflow builds Jupyter Book and generates `social/latest.json`
3. Site deploys to GitHub Pages automatically
4. n8n monitors `latest.json` for new content and automates social posts

### Configuration
- `_config.yml`: Jupyter Book settings, requires updating:
  - `repository.url`: Your GitHub repository URL
  - `sphinx.config.html_baseurl`: Your GitHub Pages URL
- GitHub Pages must be enabled with GitHub Actions as source

## Important Notes
- This uses Jupyter Book v1 (Sphinx-based), not v2
- Language is set to Japanese (`language: "ja"`)
- The `tools/build_latest_json.py` script requires `html_baseurl` to be configured