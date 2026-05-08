"""Base scraper interface for job sources.

Each source implements a Scraper subclass. The interface is intentionally
small to keep individual sources easy to add and replace when their HTML
inevitably changes.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from app.models.schemas import JobPosting


class JobScraper(ABC):
    """Abstract base for any job board scraper."""

    source_name: str = "unknown"

    @abstractmethod
    async def search(
        self,
        query: str,
        location: str | None = None,
        limit: int = 10,
    ) -> list[JobPosting]:
        """Search for jobs matching the query and return parsed postings."""
        ...
