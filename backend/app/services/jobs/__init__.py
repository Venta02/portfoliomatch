from app.services.jobs.base import JobScraper
from app.services.jobs.glints import GlintsScraper

SCRAPERS: dict[str, type[JobScraper]] = {
    "glints": GlintsScraper,
}

__all__ = ["JobScraper", "GlintsScraper", "SCRAPERS"]
