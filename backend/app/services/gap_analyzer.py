"""Analyze skill gaps and suggest concrete projects using Gemini."""

import json
from typing import List
import google.generativeai as genai

from app.core.config import settings
from app.core.logging import log
from app.models.schemas import (
    UserProfile,
    JobPosting,
    GapAnalysisResponse,
    ProjectSuggestion,
)


SYSTEM_PROMPT = """You are an expert career coach for ML/AI engineers. \
Given a user's actual skills (from their GitHub) and target job requirements, \
identify concrete skill gaps and suggest realistic projects to close them.

Be honest, specific, and actionable. Avoid generic advice. Focus on what is \
genuinely missing, not what they already have.

Output strict JSON with this schema:
{
  "common_missing_skills": ["skill1", "skill2"],
  "skill_priority_ranking": ["highest priority skill first"],
  "suggested_projects": [
    {
      "name": "Specific project name",
      "description": "1-2 sentence description",
      "skills_addressed": ["skill1", "skill2"],
      "estimated_weeks": 3,
      "difficulty": "easy|medium|hard"
    }
  ],
  "overall_assessment": "2-3 sentence honest summary"
}

Suggest 3 projects max. Each should be buildable in 2-5 weeks by a single engineer.
"""


class GapAnalyzer:
    """Identifies skill gaps and suggests projects using LLM reasoning."""

    def __init__(self):
        if not settings.gemini_available:
            log.warning("GEMINI_API_KEY not set, gap analysis will return placeholder")
            self.model = None
            return

        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel(
            model_name=settings.gemini_model,
            system_instruction=SYSTEM_PROMPT,
            generation_config=genai.GenerationConfig(
                temperature=0.3,
                response_mime_type="application/json",
            ),
        )
        log.info(f"Gemini model initialized: {settings.gemini_model}")

    def analyze(
        self,
        profile: UserProfile,
        target_jobs: List[JobPosting],
    ) -> GapAnalysisResponse:
        if not self.model:
            return self._placeholder_response(profile, target_jobs)

        prompt = self._build_prompt(profile, target_jobs)

        try:
            response = self.model.generate_content(prompt)
            data = json.loads(response.text)
            return GapAnalysisResponse(
                common_missing_skills=data.get("common_missing_skills", []),
                skill_priority_ranking=data.get("skill_priority_ranking", []),
                suggested_projects=[
                    ProjectSuggestion(**p) for p in data.get("suggested_projects", [])
                ],
                overall_assessment=data.get("overall_assessment", ""),
            )
        except json.JSONDecodeError as e:
            log.error(f"Failed to parse Gemini response: {e}")
            return self._placeholder_response(profile, target_jobs)
        except Exception as e:
            log.error(f"Gemini call failed: {e}")
            return self._placeholder_response(profile, target_jobs)

    def _build_prompt(
        self,
        profile: UserProfile,
        target_jobs: List[JobPosting],
    ) -> str:
        user_skills = ", ".join(profile.aggregated_skills)
        skill_summary = profile.skill_summary or "No summary available"

        jobs_text = []
        for i, job in enumerate(target_jobs, 1):
            jobs_text.append(
                f"\nJob {i}: {job.title} at {job.company}\n"
                f"Required skills: {', '.join(job.skills_required)}\n"
                f"Description: {job.description[:300]}"
            )

        return f"""USER PROFILE:
Username: {profile.username}
Skills present: {user_skills}
Summary: {skill_summary}

TARGET JOBS:
{''.join(jobs_text)}

Analyze the gap between this user's skills and the target jobs. \
Identify the most critical missing skills, rank them by priority, \
and suggest 3 concrete projects to close the gaps.

Respond with valid JSON only."""

    def _placeholder_response(
        self,
        profile: UserProfile,
        target_jobs: List[JobPosting],
    ) -> GapAnalysisResponse:
        """Fallback when Gemini unavailable: rule-based gap analysis."""
        user_skills_lower = {s.lower() for s in profile.aggregated_skills}
        all_required = []
        for job in target_jobs:
            all_required.extend(s.lower() for s in job.skills_required)

        from collections import Counter
        skill_counts = Counter(all_required)
        missing = [
            (skill, count) for skill, count in skill_counts.most_common()
            if skill not in user_skills_lower
        ]

        common_missing = [skill for skill, _ in missing[:8]]
        priority = [skill for skill, _ in missing[:5]]

        suggested = [
            ProjectSuggestion(
                name="Skill Gap Builder",
                description=(
                    f"Build a project covering: {', '.join(priority[:3])}. "
                    "Configure GEMINI_API_KEY for personalized suggestions."
                ),
                skills_addressed=priority[:3],
                estimated_weeks=3,
                difficulty="medium",
            )
        ]

        return GapAnalysisResponse(
            common_missing_skills=common_missing,
            skill_priority_ranking=priority,
            suggested_projects=suggested,
            overall_assessment=(
                f"Rule-based analysis: {len(common_missing)} skills missing across "
                f"{len(target_jobs)} target jobs. Configure Gemini for richer analysis."
            ),
        )


_gap_analyzer: GapAnalyzer = None


def get_gap_analyzer() -> GapAnalyzer:
    global _gap_analyzer
    if _gap_analyzer is None:
        _gap_analyzer = GapAnalyzer()
    return _gap_analyzer
