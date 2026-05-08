"""Match user profile to jobs using sentence embeddings."""

from typing import List, Set
import numpy as np
from sentence_transformers import SentenceTransformer

from app.core.config import settings
from app.core.logging import log
from app.models.schemas import (
    UserProfile,
    JobPosting,
    MatchResult,
)


class JobMatcher:
    """Embedding-based semantic matching of user profile to job postings.

    Match score combines:
    - Semantic similarity between profile summary and job description
    - Skill overlap ratio (matched required skills / total required skills)
    """

    def __init__(self):
        log.info(f"Loading embedding model: {settings.embedding_model}")
        self.model = SentenceTransformer(settings.embedding_model)
        log.info("Embedding model loaded")

    def match(
        self,
        profile: UserProfile,
        jobs: List[JobPosting],
        top_k: int = 10,
    ) -> List[MatchResult]:
        if not jobs:
            return []

        profile_text = self._build_profile_text(profile)
        profile_embedding = self.model.encode(profile_text, convert_to_numpy=True)

        job_texts = [self._build_job_text(j) for j in jobs]
        job_embeddings = self.model.encode(job_texts, convert_to_numpy=True)

        # Cosine similarity
        sims = self._cosine_similarity_batch(profile_embedding, job_embeddings)

        results: List[MatchResult] = []
        user_skills = self._normalize_skills(profile.aggregated_skills)

        for job, semantic_score in zip(jobs, sims):
            job_skills = self._normalize_skills(job.skills_required)
            matched = sorted(user_skills & job_skills)
            missing = sorted(job_skills - user_skills)

            if job_skills:
                skill_overlap = len(matched) / len(job_skills)
            else:
                skill_overlap = 0.5  # No skills listed, neutral

            # Weighted final score
            final_score = float(0.5 * semantic_score + 0.5 * skill_overlap)
            final_score = max(0.0, min(1.0, final_score))

            results.append(
                MatchResult(
                    job=job,
                    score=round(final_score, 3),
                    matched_skills=matched,
                    missing_skills=missing,
                )
            )

        # Sort descending by score
        results.sort(key=lambda r: r.score, reverse=True)
        return results[:top_k]

    def _build_profile_text(self, profile: UserProfile) -> str:
        """Aggregate profile into a single text for embedding."""
        parts = []
        if profile.bio:
            parts.append(profile.bio)
        if profile.skill_summary:
            parts.append(profile.skill_summary)
        if profile.aggregated_skills:
            parts.append("Skills: " + ", ".join(profile.aggregated_skills))

        # Add top repo descriptions for richer signal
        for repo in profile.repos[:5]:
            if repo.description:
                parts.append(f"{repo.name}: {repo.description}")

        return ". ".join(parts) if parts else profile.username

    def _build_job_text(self, job: JobPosting) -> str:
        parts = [job.title, job.description]
        if job.requirements:
            parts.append("Requirements: " + " ".join(job.requirements))
        if job.skills_required:
            parts.append("Skills: " + ", ".join(job.skills_required))
        return ". ".join(parts)

    def _normalize_skills(self, skills: List[str]) -> Set[str]:
        """Lowercase + simple alias normalization for skill comparison."""
        aliases = {
            "py": "python",
            "js": "javascript",
            "ts": "typescript",
            "tf": "tensorflow",
            "pt": "pytorch",
        }
        normalized = set()
        for s in skills:
            key = s.lower().strip()
            normalized.add(aliases.get(key, key))
        return normalized

    def _cosine_similarity_batch(
        self,
        query: np.ndarray,
        candidates: np.ndarray,
    ) -> np.ndarray:
        query_norm = query / (np.linalg.norm(query) + 1e-8)
        cand_norm = candidates / (np.linalg.norm(candidates, axis=1, keepdims=True) + 1e-8)
        return cand_norm @ query_norm


_matcher: JobMatcher = None


def get_matcher() -> JobMatcher:
    global _matcher
    if _matcher is None:
        _matcher = JobMatcher()
    return _matcher
