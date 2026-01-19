#!/usr/bin/env python3
"""Build a small JSON feed for n8n from MyST Markdown front matter.

- Scans markdown files under ./content
- Reads YAML front matter (--- ... ---)
- Includes only items with status: published
- Generates url based on _config.yml sphinx.config.html_baseurl and file path

Output schema (array):
[
  {
    "title": "...",
    "date": "YYYY-MM-DD",
    "summary": "...",
    "tags": [...],
    "slug": "...",
    "source_path": "content/00_overview.md",
    "url": "https://.../content/00_overview.html"
  }
]
"""

from __future__ import annotations

import argparse
import json
import os
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

FRONT_MATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


@dataclass
class Item:
    title: str
    date_str: str
    summary: str
    tags: List[str]
    slug: str
    source_path: str
    url: str

    def sort_key(self):
        # Date descending; fallback to title
        return (self.date_str, self.title)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def parse_front_matter(md: str) -> Optional[Dict[str, Any]]:
    m = FRONT_MATTER_RE.match(md)
    if not m:
        return None
    raw = m.group(1)
    data = yaml.safe_load(raw) or {}
    if not isinstance(data, dict):
        return None
    return data


def load_baseurl(config_path: Path) -> str:
    cfg = yaml.safe_load(read_text(config_path)) or {}
    baseurl = (
        cfg.get("sphinx", {})
        .get("config", {})
        .get("html_baseurl", "")
    )
    if not baseurl:
        raise SystemExit(
            "html_baseurl is empty in _config.yml (sphinx.config.html_baseurl). "
            "Set it to your GitHub Pages URL."
        )
    return str(baseurl).rstrip("/")


def md_path_to_html_url(baseurl: str, md_path: Path) -> str:
    rel = md_path.with_suffix("").as_posix()  # e.g. content/00_overview
    return f"{baseurl}/{rel}.html"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--content", default="content", help="content directory")
    ap.add_argument("--config", default="_config.yml", help="Jupyter Book config")
    ap.add_argument(
        "--out",
        default="_build/html/social/latest.json",
        help="output JSON path",
    )
    args = ap.parse_args()

    baseurl = load_baseurl(Path(args.config))

    items: List[Item] = []
    content_dir = Path(args.content)

    for md_path in sorted(content_dir.rglob("*.md")):
        md = read_text(md_path)
        fm = parse_front_matter(md)
        if not fm:
            continue

        status = str(fm.get("status", "draft")).lower().strip()
        if status != "published":
            continue

        title = str(fm.get("title", md_path.stem))
        date_val = fm.get("date")
        if isinstance(date_val, (date,)):
            date_str = date_val.isoformat()
        else:
            date_str = str(date_val or "")
        summary = str(fm.get("summary", "")).strip()
        tags = fm.get("tags", [])
        if isinstance(tags, str):
            tags = [tags]
        tags = [str(t) for t in (tags or [])]
        slug = str(fm.get("slug", md_path.stem)).strip()

        url = md_path_to_html_url(baseurl, md_path)

        items.append(
            Item(
                title=title,
                date_str=date_str,
                summary=summary,
                tags=tags,
                slug=slug,
                source_path=md_path.as_posix(),
                url=url,
            )
        )

    # Sort newest first
    items.sort(key=lambda x: x.sort_key(), reverse=True)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        json.dump([i.__dict__ for i in items], f, ensure_ascii=False, indent=2)

    print(f"Wrote {len(items)} items to {out_path}")


if __name__ == "__main__":
    main()
