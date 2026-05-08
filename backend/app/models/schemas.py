"""Pydantic models for API request/response."""

from typing import List, Optional, Dict
from pydantic import BaseModel, Field, HttpUrl


class AnalyzeRequest(BaseModel):
    github_username: str = Field(..., min_length=1, max_length=39)
    max_repos: int = Field(default=10, ge=1, le=30)


class RepoSummary(BaseModel):
    name: str
    description: Optional[str] = None
    languages: Dict[str, int] = Field(default_factory=dict)
    frameworks: List[str] = Field(default_factory=list)
    stars: int = 0
    topics: List[str] = Field(default_factory=list)
    url: str


class UserProfile(BaseModel):
    username: str
    name: Optional[str] = None
    bio: Optional[str] = None
    public_repos: int
    followers: int
    repos: List[RepoSummary] = Field(default_factory=list)
    aggregated_skills: List[str] = Field(default_factory=list)
    skill_summary: str = ""


class JobPosting(BaseModel):
    id: str
    title: str
    company: str
    location: str
    description: str
    requirements: List[str] = Field(default_factory=list)
    skills_required: List[str] = Field(default_factory=list)
    experience_years: Optional[int] = None
    salary_range: Optional[str] = None
    url: Optional[str] = None
    source: str = "manual"


class JobSearchRequest(BaseModel):
    role_keywords: List[str] = Field(default_factory=lambda: ["machine learning", "data scientist"])
    location: Optional[str] = None
    limit: int = Field(default=20, ge=1, le=100)


class MatchResult(BaseModel):
    job: JobPosting
    score: float = Field(..., ge=0.0, le=1.0)
    matched_skills: List[str] = Field(default_factory=list)
    missing_skills: List[str] = Field(default_factory=list)
    reasoning: Optional[str] = None


class MatchRequest(BaseModel):
    profile: UserProfile
    jobs: List[JobPosting]
    top_k: int = Field(default=10, ge=1, le=50)


class MatchResponse(BaseModel):
    matches: List[MatchResult]
    total_jobs_evaluated: int


class GapAnalysisRequest(BaseModel):
    profile: UserProfile
    target_jobs: List[JobPosting] = Field(..., max_length=5)


class ProjectSuggestion(BaseModel):
    name: str
    description: str
    skills_addressed: List[str]
    estimated_weeks: int
    difficulty: str = "medium"


class GapAnalysisResponse(BaseModel):
    common_missing_skills: List[str]
    skill_priority_ranking: List[str]
    suggested_projects: List[ProjectSuggestion]
    overall_assessment: str


class HealthResponse(BaseModel):
    status: str = "ok"
    github_available: bool
    gemini_available: bool
    embedding_model: str
