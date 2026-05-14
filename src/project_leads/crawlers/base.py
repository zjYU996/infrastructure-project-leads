from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from project_leads.models import CrawlError, Lead, Source


@dataclass
class CrawlResult:
    leads: list[Lead]
    errors: list[CrawlError]


class BaseCrawler(Protocol):
    def crawl(self, source: Source, run_date: str) -> CrawlResult:
        ...
