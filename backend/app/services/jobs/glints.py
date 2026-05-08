"""Glints scraper.

Note: This is a starter implementation. Glints uses dynamic rendering for
some pages, so for production you may want Playwright or their public API
if available. For now this scrapes the public search results page.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime

import httpx
from bs4 import BeautifulSoup

from app.models.schemas import JobPosting
from app.services.jobs.base import JobScraper

logger = logging.getLogger(__name__)


class GlintsScraper(JobScraper):
    source_name = "glints"
    base_url = "https://glints.com"

    async def search(
        self,
        query: str,
        location: str | None = None,
        limit: int = 10,
    ) -> list[JobPosting]:
        """Search Glints. This is a starter; refine selectors as needed."""
        params = {"keyword": query}
        if location:
            params["country"] = location

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.get(
                    f"{self.base_url}/opportunities/jobs/explore",
                    params=params,
                    headers={
                        "User-Agent": (
                            "Mozilla/5.0 (compatible; PortfolioMatch/0.1; "
                            "+https://github.com/Venta02/portfoliomatch)"
                        )
                    },
                )
                resp.raise_for_status()
        except httpx.HTTPError as e:
            logger.error("Glints request failed: %s", e)
            return []

        soup = BeautifulSoup(resp.text, "lxml")
        # TODO: Glints renders job cards via JS in many cases. Update the selector
        # below to match the current DOM, or migrate this scraper to Playwright.
        cards = soup.select("[data-testid='job-card']")[:limit]

        postings: list[JobPosting] = []
        for card in cards:
            try:
                postings.append(self._parse_card(card))
            except Exception as e:
                logger.warning("Failed to parse Glints card: %s", e)

        return postings

    def _parse_card(self, card) -> JobPosting:
        """Parse a single job card element into a JobPosting."""
        title = card.select_one("h2, .job-title")
        company = card.select_one(".company-name")
        location = card.select_one(".location")
        link = card.select_one("a")

        return JobPosting(
            id=str(uuid.uuid4()),
            title=title.get_text(strip=True) if title else "Unknown",
            company=company.get_text(strip=True) if company else "Unknown",
            location=location.get_text(strip=True) if location else "",
            posted_at=None,
            url=f"{self.base_url}{link['href']}" if link and link.get("href") else "",
            description="",
            requirements=[],
            skills_required=[],
            experience_years=None,
            salary_range=None,
            source=self.source_name,
        )
