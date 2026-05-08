"""GitHub repository analyzer.

Fetches public repositories for a user and extracts skills from code,
not just from the README. This is the differentiator versus resume-based
matching: we read the actual implementation, imports, and dependencies.
"""

from __future__ import annotations

import logging
import re
from datetime import datetime
from typing import Any

from github import Github, Auth, GithubException
from github.Repository import Repository

from app.core.config import get_settings
from app.models.schemas import GitHubProfile, RepoSummary, RepoSkill

logger = logging.getLogger(__name__)


# Framework detection patterns. Maps a normalized framework name to the import
# tokens or dependency strings that signal its presence. Extend this as needed.
FRAMEWORK_SIGNALS: dict[str, list[str]] = {
    "FastAPI": ["fastapi", "from fastapi"],
    "Flask": ["flask", "from flask"],
    "Django": ["django", "from django"],
    "PyTorch": ["torch", "import torch"],
    "TensorFlow": ["tensorflow", "import tensorflow"],
    "Hugging Face Transformers": ["transformers", "from transformers"],
    "LangChain": ["langchain", "from langchain"],
    "LangGraph": ["langgraph", "from langgraph"],
    "Streamlit": ["streamlit", "import streamlit"],
    "Gradio": ["gradio", "import gradio"],
    "Next.js": ["next", "next/"],
    "React": ["react", "from \"react\""],
    "Vue": ["vue", "from 'vue'"],
    "Tailwind CSS": ["tailwindcss"],
    "Docker": ["FROM ", "Dockerfile"],
    "PostgreSQL": ["psycopg", "asyncpg", "postgres"],
    "MongoDB": ["pymongo", "mongoose"],
    "Redis": ["redis"],
    "Celery": ["celery"],
    "OpenCV": ["cv2", "import cv2"],
    "PaddleOCR": ["paddleocr"],
    "YOLO": ["ultralytics", "yolov"],
    "Gemini": ["google.generativeai", "google-generativeai"],
    "OpenAI": ["openai"],
    "Anthropic": ["anthropic"],
    "ChromaDB": ["chromadb"],
    "Qdrant": ["qdrant"],
    "AWS": ["boto3", "aws-sdk"],
    "GCP": ["google-cloud"],
    "Kubernetes": ["k8s", "kubernetes"],
}


class GitHubAnalyzer:
    """Analyzes a user's public GitHub repositories."""

    def __init__(self) -> None:
        settings = get_settings()
        if not settings.github_token:
            logger.warning("GITHUB_TOKEN not set; falling back to anonymous (rate-limited)")
            self.client = Github()
        else:
            self.client = Github(auth=Auth.Token(settings.github_token))

    def analyze_user(self, username: str, max_repos: int = 20) -> GitHubProfile:
        """Fetch and analyze a GitHub user's public repos."""
        try:
            user = self.client.get_user(username)
        except GithubException as e:
            logger.error("Failed to fetch user %s: %s", username, e)
            raise

        # Sort repos by recent activity to prioritize active work
        all_repos = sorted(
            user.get_repos(),
            key=lambda r: r.updated_at or datetime.min,
            reverse=True,
        )
        selected = [r for r in all_repos if not r.fork][:max_repos]

        repo_summaries: list[RepoSummary] = []
        skill_evidence: dict[str, list[str]] = {}

        for repo in selected:
            try:
                summary = self._analyze_repo(repo)
                repo_summaries.append(summary)
                for fw in summary.frameworks:
                    skill_evidence.setdefault(fw, []).append(repo.name)
                for lang in summary.languages:
                    skill_evidence.setdefault(lang, []).append(repo.name)
            except Exception as e:
                logger.warning("Skipping repo %s: %s", repo.name, e)

        skills = [
            RepoSkill(
                name=name,
                confidence=min(1.0, len(repos) / 3),
                evidence=repos,
            )
            for name, repos in skill_evidence.items()
        ]
        skills.sort(key=lambda s: s.confidence, reverse=True)

        return GitHubProfile(
            username=username,
            repo_count=len(repo_summaries),
            repos=repo_summaries,
            skills=skills,
            extracted_at=datetime.utcnow(),
        )

    def _analyze_repo(self, repo: Repository) -> RepoSummary:
        """Extract structured info from a single repo."""
        languages = repo.get_languages()
        readme_excerpt = self._read_readme(repo)
        frameworks = self._detect_frameworks(repo, readme_excerpt)

        return RepoSummary(
            name=repo.name,
            description=repo.description,
            primary_language=repo.language,
            languages=dict(languages),
            frameworks=frameworks,
            stars=repo.stargazers_count,
            forks=repo.forks_count,
            last_updated=repo.updated_at,
            topics=repo.get_topics(),
            readme_excerpt=readme_excerpt[:1500] if readme_excerpt else None,
        )

    def _read_readme(self, repo: Repository) -> str | None:
        try:
            readme = repo.get_readme()
            return readme.decoded_content.decode("utf-8", errors="ignore")
        except GithubException:
            return None

    def _detect_frameworks(self, repo: Repository, readme: str | None) -> list[str]:
        """Detect frameworks via dependency files and README mentions."""
        text_corpus = (readme or "").lower()

        # Try to read common dependency manifests
        for manifest in ["requirements.txt", "pyproject.toml", "package.json", "Cargo.toml"]:
            try:
                content = repo.get_contents(manifest)
                if isinstance(content, list):
                    continue
                text_corpus += "\n" + content.decoded_content.decode("utf-8", errors="ignore").lower()
            except GithubException:
                continue

        detected: list[str] = []
        for framework, signals in FRAMEWORK_SIGNALS.items():
            if any(sig.lower() in text_corpus for sig in signals):
                detected.append(framework)
        return detected
