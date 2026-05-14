from __future__ import annotations

import csv
from pathlib import Path
from urllib.parse import urlparse

from .models import Source


HEADER_ALIASES = {
    "website_name": {"website_name", "site", "source", "name", "网站名称", "来源网站"},
    "url": {"url", "link", "website", "网址", "链接"},
    "country": {"country", "region", "market", "国家", "地区"},
    "category": {"category", "type", "sector", "类别", "类型"},
}


def _canonical_headers(fieldnames: list[str] | None) -> dict[str, str]:
    headers = {}
    normalized = {field.strip(): field for field in fieldnames or []}
    lowered = {field.strip().lower(): field for field in fieldnames or []}

    for canonical, aliases in HEADER_ALIASES.items():
        for alias in aliases:
            if alias in normalized:
                headers[canonical] = normalized[alias]
                break
            if alias.lower() in lowered:
                headers[canonical] = lowered[alias.lower()]
                break
    return headers


def _fallback_name(url: str) -> str:
    parsed = urlparse(url)
    return parsed.netloc or url


def load_sources(path: str | Path) -> list[Source]:
    source_path = Path(path)
    if not source_path.exists():
        raise FileNotFoundError(f"sources file not found: {source_path}")

    with source_path.open("r", encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        headers = _canonical_headers(reader.fieldnames)
        if "url" not in headers:
            raise ValueError("sources.csv must include a URL column")

        sources: list[Source] = []
        for line_number, row in enumerate(reader, start=2):
            url = (row.get(headers["url"], "") or "").strip()
            if not url:
                continue

            name = (row.get(headers.get("website_name", ""), "") or "").strip()
            country = (row.get(headers.get("country", ""), "") or "").strip()
            category = (row.get(headers.get("category", ""), "") or "").strip()

            sources.append(
                Source(
                    name=name or _fallback_name(url),
                    url=url,
                    country=country or "Unknown",
                    category=category or "General",
                )
            )

    return sources
