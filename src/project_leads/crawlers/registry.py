from __future__ import annotations

from collections.abc import Callable

import requests

from project_leads.models import Source

from .base import BaseCrawler
from .generic import GenericCrawler


CrawlerFactory = Callable[[requests.Session | None, int, int], BaseCrawler]
Matcher = Callable[[Source], bool]

_REGISTRY: list[tuple[Matcher, CrawlerFactory]] = []


def register_crawler(matcher: Matcher, factory: CrawlerFactory) -> None:
    _REGISTRY.append((matcher, factory))


def get_crawler(
    source: Source,
    session: requests.Session | None = None,
    timeout: int = 20,
    max_items: int = 50,
) -> BaseCrawler:
    for matcher, factory in _REGISTRY:
        if matcher(source):
            return factory(session, timeout, max_items)
    return GenericCrawler(session=session, timeout=timeout, max_items=max_items)
