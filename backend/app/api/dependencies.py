"""Shared FastAPI dependencies."""

from functools import lru_cache

from app.services.github import GitHubAnalyzer
from app.services.llm import LLMService
from app.services.matching import Matcher


@lru_cache
def get_github_analyzer() -> GitHubAnalyzer:
    return GitHubAnalyzer()


@lru_cache
def get_llm_service() -> LLMService:
    return LLMService()


@lru_cache
def get_matcher() -> Matcher:
    return Matcher()
