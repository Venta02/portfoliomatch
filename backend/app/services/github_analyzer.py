"""Analyze GitHub user profile and extract skills from repositories."""

import re
from typing import List, Dict, Set
from github import Github, GithubException
from github.Repository import Repository

from app.core.config import settings
from app.core.logging import log
from app.models.schemas import RepoSummary, UserProfile


# Mapping of import patterns / dependency names to framework labels
FRAMEWORK_PATTERNS = {
    # Python ML/AI
    "torch": "PyTorch",
    "tensorflow": "TensorFlow",
    "keras": "Keras",
    "sklearn": "scikit-learn",
    "scikit-learn": "scikit-learn",
    "transformers": "Hugging Face Transformers",
    "huggingface": "Hugging Face",
    "langchain": "LangChain",
    "langgraph": "LangGraph",
    "llama-index": "LlamaIndex",
    "openai": "OpenAI API",
    "anthropic": "Anthropic API",
    "google-generativeai": "Google Gemini API",
    "chromadb": "ChromaDB",
    "qdrant": "Qdrant",
    "pinecone": "Pinecone",
    "weaviate": "Weaviate",
    "sentence-transformers": "sentence-transformers",
    # Computer vision
    "opencv": "OpenCV",
    "cv2": "OpenCV",
    "ultralytics": "YOLOv8",
    "yolov5": "YOLOv5",
    "mediapipe": "MediaPipe",
    "paddleocr": "PaddleOCR",
    "easyocr": "EasyOCR",
    "pytesseract": "Tesseract",
    # Backend
    "fastapi": "FastAPI",
    "flask": "Flask",
    "django": "Django",
    "starlette": "Starlette",
    "uvicorn": "Uvicorn",
    "celery": "Celery",
    # Frontend / JS
    "react": "React",
    "next": "Next.js",
    "vue": "Vue",
    "svelte": "Svelte",
    "tailwindcss": "Tailwind CSS",
    # Data
    "pandas": "pandas",
    "numpy": "NumPy",
    "polars": "Polars",
    "duckdb": "DuckDB",
    # Database
    "sqlalchemy": "SQLAlchemy",
    "psycopg2": "PostgreSQL",
    "redis": "Redis",
    "mongodb": "MongoDB",
    "pymongo": "MongoDB",
    # MLOps
    "mlflow": "MLflow",
    "wandb": "Weights & Biases",
    "dvc": "DVC",
    "prefect": "Prefect",
    "airflow": "Apache Airflow",
    # Mobile
    "flutter": "Flutter",
    # Other
    "streamlit": "Streamlit",
    "gradio": "Gradio",
    "chainlit": "Chainlit",
    "docker": "Docker",
    "kubernetes": "Kubernetes",
    "prometheus": "Prometheus",
    "grafana": "Grafana",
}

# Files that indicate dependencies
DEPENDENCY_FILES = [
    "requirements.txt",
    "requirements-dev.txt",
    "pyproject.toml",
    "setup.py",
    "Pipfile",
    "package.json",
    "go.mod",
    "Cargo.toml",
    "pom.xml",
    "build.gradle",
]


class GitHubAnalyzer:
    """Fetches GitHub profile and extracts skills from real code."""

    def __init__(self):
        if not settings.github_available:
            log.warning("GITHUB_TOKEN not set, using unauthenticated client (rate limits apply)")
            self.client = Github()
        else:
            self.client = Github(settings.github_token)

    def analyze_user(self, username: str, max_repos: int = 10) -> UserProfile:
        """Main entry: fetch user, top repos, extract skills."""
        log.info(f"Analyzing GitHub user: {username}")

        try:
            user = self.client.get_user(username)
        except GithubException as e:
            log.error(f"Failed to fetch user {username}: {e}")
            raise ValueError(f"GitHub user '{username}' not found or inaccessible")

        # Get top N repos by stars (or recently updated)
        repos = sorted(
            user.get_repos(),
            key=lambda r: (r.stargazers_count, r.pushed_at),
            reverse=True,
        )[:max_repos]

        repo_summaries: List[RepoSummary] = []
        all_frameworks: Set[str] = set()
        all_languages: Set[str] = set()

        for repo in repos:
            if repo.fork:
                continue
            try:
                summary = self._analyze_repo(repo)
                repo_summaries.append(summary)
                all_frameworks.update(summary.frameworks)
                all_languages.update(summary.languages.keys())
            except Exception as e:
                log.warning(f"Skipped repo {repo.name}: {e}")

        skills = sorted(all_languages | all_frameworks)
        skill_summary = self._build_skill_summary(repo_summaries, skills)

        return UserProfile(
            username=user.login,
            name=user.name,
            bio=user.bio,
            public_repos=user.public_repos,
            followers=user.followers,
            repos=repo_summaries,
            aggregated_skills=skills,
            skill_summary=skill_summary,
        )

    def _analyze_repo(self, repo: Repository) -> RepoSummary:
        """Extract languages, frameworks, topics from a single repo."""
        languages = repo.get_languages()
        frameworks = self._detect_frameworks(repo)

        return RepoSummary(
            name=repo.name,
            description=repo.description,
            languages=languages,
            frameworks=frameworks,
            stars=repo.stargazers_count,
            topics=repo.get_topics(),
            url=repo.html_url,
        )

    def _detect_frameworks(self, repo: Repository) -> List[str]:
        """Detect frameworks by reading dependency files."""
        detected: Set[str] = set()

        for filename in DEPENDENCY_FILES:
            try:
                content_file = repo.get_contents(filename)
                content = content_file.decoded_content.decode("utf-8", errors="ignore").lower()
                detected.update(self._scan_content_for_frameworks(content))
            except GithubException:
                # File not found, skip
                continue
            except Exception as e:
                log.debug(f"Could not read {filename} in {repo.name}: {e}")

        return sorted(detected)

    def _scan_content_for_frameworks(self, content: str) -> Set[str]:
        """Match known framework patterns in dependency file content."""
        detected: Set[str] = set()
        for pattern, label in FRAMEWORK_PATTERNS.items():
            # Match pattern as word boundary or import statement
            if re.search(rf"\b{re.escape(pattern)}\b", content):
                detected.add(label)
        return detected

    def _build_skill_summary(self, repos: List[RepoSummary], skills: List[str]) -> str:
        """Build a one-paragraph natural language summary of skills."""
        if not repos:
            return ""

        top_langs = self._top_languages(repos)
        framework_list = ", ".join(skills[:15]) if skills else "general programming"
        repo_count = len(repos)
        ml_repo_count = sum(
            1 for r in repos
            if any(f in r.frameworks for f in ["PyTorch", "TensorFlow", "Hugging Face Transformers"])
        )
        ai_repo_count = sum(
            1 for r in repos
            if any("Gemini" in f or "OpenAI" in f or "Anthropic" in f or "LangChain" in f for f in r.frameworks)
        )

        parts = [
            f"Engineer with {repo_count} active repositories.",
            f"Primary languages: {', '.join(top_langs[:3])}.",
        ]
        if ml_repo_count > 0:
            parts.append(f"Built {ml_repo_count} ML projects using deep learning frameworks.")
        if ai_repo_count > 0:
            parts.append(f"Shipped {ai_repo_count} LLM-powered applications.")
        parts.append(f"Working knowledge of: {framework_list}.")

        return " ".join(parts)

    def _top_languages(self, repos: List[RepoSummary]) -> List[str]:
        """Aggregate language byte counts across repos."""
        totals: Dict[str, int] = {}
        for repo in repos:
            for lang, bytes_count in repo.languages.items():
                totals[lang] = totals.get(lang, 0) + bytes_count
        return sorted(totals, key=totals.get, reverse=True)


# Singleton instance
_analyzer: GitHubAnalyzer = None


def get_github_analyzer() -> GitHubAnalyzer:
    global _analyzer
    if _analyzer is None:
        _analyzer = GitHubAnalyzer()
    return _analyzer
