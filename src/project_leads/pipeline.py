from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import requests

from .config import load_sources
from .crawlers import get_crawler
from .models import CrawlError, Lead
from .output import write_excel_report, write_markdown_report


@dataclass(frozen=True)
class RunSummary:
    run_date: str
    source_count: int
    lead_count: int
    error_count: int
    excel_path: Path
    markdown_path: Path


def run_collection(
    sources_path: str | Path = "sources.csv",
    output_dir: str | Path = "reports",
    timezone: str = "Asia/Shanghai",
    timeout: int = 20,
    max_items_per_source: int = 50,
) -> RunSummary:
    sources = load_sources(sources_path)
    run_date = datetime.now(ZoneInfo(timezone)).strftime("%Y-%m-%d")
    output_root = Path(output_dir)

    session = requests.Session()
    leads: list[Lead] = []
    errors: list[CrawlError] = []

    for source in sources:
        try:
            crawler = get_crawler(
                source,
                session=session,
                timeout=timeout,
                max_items=max_items_per_source,
            )
            result = crawler.crawl(source, run_date=run_date)
            leads.extend(result.leads)
            errors.extend(result.errors)
        except Exception as exc:
            errors.append(
                CrawlError(
                    date=run_date,
                    country=source.country,
                    category=source.category,
                    source_site=source.name,
                    source_url=source.url,
                    error_reason=f"Unhandled crawler error: {exc}",
                )
            )

    leads = _dedupe_leads(leads)
    excel_path = output_root / f"project_leads_{run_date}.xlsx"
    markdown_path = output_root / f"project_leads_{run_date}.md"

    write_excel_report(leads, errors, excel_path)
    write_markdown_report(leads, errors, markdown_path, run_date)

    return RunSummary(
        run_date=run_date,
        source_count=len(sources),
        lead_count=len(leads),
        error_count=len(errors),
        excel_path=excel_path,
        markdown_path=markdown_path,
    )


def _dedupe_leads(leads: list[Lead]) -> list[Lead]:
    unique: list[Lead] = []
    seen: set[str] = set()
    for lead in leads:
        key = f"{lead.original_url}|{lead.project_name}".lower()
        if key in seen:
            continue
        seen.add(key)
        unique.append(lead)
    return unique
