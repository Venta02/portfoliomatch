"""GitHub profile analysis endpoints."""

from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_github_analyzer
from app.models.schemas import AnalyzeGitHubRequest, GitHubProfile
from app.services.github import GitHubAnalyzer

router = APIRouter(prefix="/api/analyze", tags=["analyze"])


@router.post("/github", response_model=GitHubProfile)
async def analyze_github(
    req: AnalyzeGitHubRequest,
    analyzer: GitHubAnalyzer = Depends(get_github_analyzer),
) -> GitHubProfile:
    try:
        return analyzer.analyze_user(req.username, max_repos=req.max_repos)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
