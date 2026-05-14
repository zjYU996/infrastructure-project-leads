from __future__ import annotations

import re
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from project_leads.keywords import detect_project_type, follow_up_advice, relevance_level
from project_leads.models import CrawlError, Lead, Source
from project_leads.utils import clean_text, clip_text, first_non_empty

from .base import CrawlResult


OWNER_PATTERNS = (
    r"(?:Owner|Client|Employer|Buyer|Contracting authority|Procuring entity)\s*[:：-]\s*([^.;。\n]{2,100})",
    r"(?:业主|招标人|采购人|建设单位)\s*[:：-]\s*([^.;。\n]{2,100})",
)

CONTRACTOR_PATTERNS = (
    r"(?:Contractor|Supplier|Awarded to|Winner|Winning bidder)\s*[:：-]\s*([^.;。\n]{2,100})",
    r"(?:承包商|中标人|供应商|施工单位)\s*[:：-]\s*([^.;。\n]{2,100})",
)


class GenericCrawler:
    """Keyword-based crawler for public HTML listing pages."""

    def __init__(
        self,
        session: requests.Session | None = None,
        timeout: int = 20,
        max_items: int = 50,
    ) -> None:
        self.session = session or requests.Session()
        self.timeout = timeout
        self.max_items = max_items

    def crawl(self, source: Source, run_date: str) -> CrawlResult:
        try:
            response = self.session.get(
                source.url,
                timeout=self.timeout,
                headers={
                    "User-Agent": (
                        "Mozilla/5.0 (compatible; ProjectLeadCollector/0.1; "
                        "+https://github.com/)"
                    )
                },
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            return CrawlResult(
                leads=[],
                errors=[
                    CrawlError(
                        date=run_date,
                        country=source.country,
                        category=source.category,
                        source_site=source.name,
                        source_url=source.url,
                        error_reason=f"Request failed: {exc}",
                    )
                ],
            )

        content_type = response.headers.get("content-type", "")
        if "html" not in content_type and "xml" not in content_type and response.text.lstrip().startswith("<") is False:
            return CrawlResult(
                leads=[],
                errors=[
                    CrawlError(
                        date=run_date,
                        country=source.country,
                        category=source.category,
                        source_site=source.name,
                        source_url=source.url,
                        error_reason=f"Unsupported content type: {content_type or 'unknown'}",
                    )
                ],
            )

        soup = BeautifulSoup(response.text, "html.parser")
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()

        leads = self._extract_link_candidates(soup, source, run_date)
        return CrawlResult(leads=leads, errors=[])

    def _extract_link_candidates(self, soup: BeautifulSoup, source: Source, run_date: str) -> list[Lead]:
        leads: list[Lead] = []
        seen: set[str] = set()

        for anchor in soup.find_all("a", href=True):
            title = clean_text(anchor.get_text(" ", strip=True))
            parent_text = clean_text(anchor.parent.get_text(" ", strip=True) if anchor.parent else "")
            context = first_non_empty(parent_text, title)
            if len(title) < 3 and len(context) < 12:
                continue

            level, matches = relevance_level(f"{title} {context}")
            if level is None:
                continue

            original_url = urljoin(source.url, anchor["href"])
            dedupe_key = f"{original_url}|{title}".lower()
            if dedupe_key in seen:
                continue
            seen.add(dedupe_key)

            owner = self._extract_entity(context, OWNER_PATTERNS)
            contractor = self._extract_entity(context, CONTRACTOR_PATTERNS)
            project_name = clip_text(first_non_empty(title, context), 160)

            leads.append(
                Lead(
                    date=run_date,
                    country=source.country,
                    project_name=project_name,
                    project_type=detect_project_type(context, source.category),
                    owner=owner or "Unknown",
                    contractor=contractor or "Unknown",
                    summary=clip_text(context, 320),
                    source_site=source.name,
                    original_url=original_url,
                    relevance_level=level,
                    follow_up=follow_up_advice(level, matches, source.name),
                )
            )

            if len(leads) >= self.max_items:
                break

        return leads

    @staticmethod
    def _extract_entity(text: str, patterns: tuple[str, ...]) -> str:
        for pattern in patterns:
            match = re.search(pattern, text, flags=re.IGNORECASE)
            if match:
                return clip_text(match.group(1), 100)
        return ""
