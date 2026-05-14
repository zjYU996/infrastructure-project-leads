from .base import BaseCrawler, CrawlResult
from .generic import GenericCrawler
from .registry import get_crawler, register_crawler

__all__ = [
    "BaseCrawler",
    "CrawlResult",
    "GenericCrawler",
    "get_crawler",
    "register_crawler",
]
