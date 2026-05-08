"""Gemini-backed LLM service.

Used for:
1. Parsing free-form job descriptions into structured requirements.
2. Analyzing skill gaps and recommending concrete projects.
"""

from __future__ import annotations

import json
import logging

import google.generativeai as genai

from app.core.config import get_settings
from app.models.schemas import (
    GapAnalysis, GitHubProfile, JobPosting, JobRequirement, ProjectSuggestion,
)

logger = logging.getLogger(__name__)


class LLMService:
    def __init__(self) -> None:
        settings = get_settings()
        if not settings.gemini_api_key:
            self.model = None
            logger.warning("GEMINI_API_KEY not set; LLM features disabled")
            return
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel(settings.llm_model)

    @property
    def is_available(self) -> bool:
        return self.model is not None

    def parse_job_requirements(self, job: JobPosting) -> list[JobRequirement]:
        """Extract structured requirements from a free-form job description."""
        if not self.is_available:
            return []

        prompt = f"""Extract structured requirements from this job posting. Return JSON only.

Job title: {job.title}
Company: {job.company}
Description:
{job.description[:3000]}

Return a JSON array. Each item has these fields:
- name: short skill or requirement name (e.g. "Python", "FastAPI", "5 years experience")
- importance: one of "required", "preferred", "nice_to_have"
- raw: the original phrase from the description

Output JSON only, no explanation."""

        try:
            resp = self.model.generate_content(prompt)
            text = resp.text.strip()
            # Strip code fences if model wraps in ```json ... ```
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
            data = json.loads(text)
            return [JobRequirement(**item) for item in data]
        except Exception as e:
            logger.error("LLM job parse failed: %s", e)
            return []

    def analyze_gaps(
        self,
        profile: GitHubProfile,
        jobs: list[JobPosting],
    ) -> GapAnalysis:
        """Identify skill gaps and recommend projects."""
        if not self.is_available:
            return GapAnalysis(
                user_skills=[s.name for s in profile.skills],
                target_skills=[],
                gaps=[],
                project_suggestions=[],
            )

        user_skills = sorted({s.name for s in profile.skills})
        target_skills = sorted({
            req.name for job in jobs for req in job.requirements
            if req.importance == "required"
        })
        # Simple set diff is the obvious starting point; LLM enriches it
        # with project recommendations and reasoning the user wouldn't get
        # from a literal string subtraction.
        obvious_gaps = sorted(set(target_skills) - set(user_skills))

        prompt = f"""You are a career advisor for software engineers.

User's current skills (from GitHub analysis):
{user_skills}

Target skills required across applied jobs:
{target_skills}

Obvious gaps:
{obvious_gaps}

User's existing projects:
{[r.name for r in profile.repos[:10]]}

Suggest 3 concrete projects that would close the most important gaps. Each project should:
- Address 2-3 specific skills
- Be realistic in 2-4 weeks
- Be impressive on a portfolio
- Avoid duplicating what the user already has

Return JSON only with this shape:
{{
  "project_suggestions": [
    {{
      "title": "...",
      "description": "1-2 sentences",
      "skills_addressed": ["..."],
      "estimated_weeks": 3,
      "impact": "high"
    }}
  ]
}}"""

        try:
            resp = self.model.generate_content(prompt)
            text = resp.text.strip()
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
            data = json.loads(text)
            suggestions = [
                ProjectSuggestion(**item)
                for item in data.get("project_suggestions", [])
            ]
        except Exception as e:
            logger.error("LLM gap analysis failed: %s", e)
            suggestions = []

        return GapAnalysis(
            user_skills=user_skills,
            target_skills=target_skills,
            gaps=obvious_gaps,
            project_suggestions=suggestions,
        )
