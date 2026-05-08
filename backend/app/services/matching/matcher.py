"""Semantic matching between user profile and job postings.

Uses sentence-transformers to embed skill names and job descriptions, then
ranks jobs by cosine similarity plus a skill-overlap bonus.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import TYPE_CHECKING

import numpy as np

from app.core.config import get_settings
from app.models.schemas import (
    GitHubProfile, JobPosting, MatchResponse, MatchResult,
)

if TYPE_CHECKING:
    from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


class Matcher:
    """Embedding-based job matcher."""

    def __init__(self) -> None:
        # Lazy import so the module loads fast even on machines that don't
        # have torch installed yet (helps tests and dev iteration).
        from sentence_transformers import SentenceTransformer
        settings = get_settings()
        logger.info("Loading embedding model: %s", settings.embedding_model)
        self.model: SentenceTransformer = SentenceTransformer(settings.embedding_model)

    def match(self, profile: GitHubProfile, jobs: list[JobPosting]) -> MatchResponse:
        """Rank jobs by relevance to the user's profile."""
        profile_text = self._profile_to_text(profile)
        profile_emb = self.model.encode(profile_text, normalize_embeddings=True)

        results: list[MatchResult] = []
        user_skills = {s.name.lower() for s in profile.skills}

        for job in jobs:
            job_text = self._job_to_text(job)
            job_emb = self.model.encode(job_text, normalize_embeddings=True)

            cosine = float(np.dot(profile_emb, job_emb))

            job_skills = {s.lower() for s in job.skills_required}
            matched = sorted(user_skills & job_skills)
            missing = sorted(job_skills - user_skills)

            overlap_bonus = (
                len(matched) / max(len(job_skills), 1) if job_skills else 0
            )
            # Weighted: 60% semantic, 40% explicit overlap. Tune as needed.
            score = 0.6 * cosine + 0.4 * overlap_bonus

            results.append(MatchResult(
                job=job,
                score=max(0.0, min(1.0, score)),
                matched_skills=matched,
                missing_skills=missing,
                reasoning=None,
            ))

        results.sort(key=lambda r: r.score, reverse=True)
        return MatchResponse(matches=results, analyzed_at=datetime.utcnow())

    def _profile_to_text(self, profile: GitHubProfile) -> str:
        skills = ", ".join(s.name for s in profile.skills[:30])
        repos = " | ".join(
            f"{r.name}: {r.description or ''} ({', '.join(r.frameworks)})"
            for r in profile.repos[:15]
        )
        return f"Skills: {skills}\n\nProjects: {repos}"

    def _job_to_text(self, job: JobPosting) -> str:
        skills = ", ".join(job.skills_required)
        return f"{job.title} at {job.company}. Skills: {skills}\n\n{job.description[:2000]}"
