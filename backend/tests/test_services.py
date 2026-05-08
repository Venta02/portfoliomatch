"""Smoke tests for backend services."""

import pytest
from app.services.matcher import get_matcher
from app.services.job_scraper import get_job_scraper
from app.models.schemas import UserProfile, RepoSummary


def test_load_jobs():
    scraper = get_job_scraper()
    jobs = scraper.get_all_jobs()
    assert len(jobs) >= 10
    assert all(j.title for j in jobs)


def test_search_jobs():
    scraper = get_job_scraper()
    jobs = scraper.search(["computer vision"], limit=5)
    assert all("vision" in (j.title + j.description).lower() for j in jobs)


def test_match_basic():
    matcher = get_matcher()
    scraper = get_job_scraper()

    profile = UserProfile(
        username="testuser",
        public_repos=5,
        followers=10,
        bio="Computer vision engineer building OCR and document AI",
        aggregated_skills=["Python", "PyTorch", "OpenCV", "FastAPI"],
        skill_summary="CV engineer with PyTorch experience",
        repos=[
            RepoSummary(
                name="my-ocr",
                description="OCR pipeline with PaddleOCR and Gemini fallback",
                languages={"Python": 10000},
                frameworks=["PyTorch", "PaddleOCR", "FastAPI"],
                stars=5,
                topics=["ocr", "computer-vision"],
                url="https://github.com/test/my-ocr",
            )
        ],
    )
    jobs = scraper.get_all_jobs()
    matches = matcher.match(profile, jobs, top_k=5)

    assert len(matches) <= 5
    assert all(0.0 <= m.score <= 1.0 for m in matches)
    # Top match should mention vision or OCR
    top = matches[0].job
    text = (top.title + top.description).lower()
    assert any(k in text for k in ["vision", "ocr", "ml", "ai"])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
