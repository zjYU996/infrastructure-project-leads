from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Source:
    name: str
    url: str
    country: str
    category: str


@dataclass(frozen=True)
class Lead:
    date: str
    country: str
    project_name: str
    project_type: str
    owner: str
    contractor: str
    summary: str
    source_site: str
    original_url: str
    relevance_level: str
    follow_up: str


@dataclass(frozen=True)
class CrawlError:
    date: str
    country: str
    category: str
    source_site: str
    source_url: str
    error_reason: str
