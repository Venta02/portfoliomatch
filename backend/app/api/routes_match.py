"""Matching and gap analysis endpoints."""

from fastapi import APIRouter, Depends

from app.api.dependencies import get_llm_service, get_matcher
from app.models.schemas import (
    GapAnalysis, GapRequest, MatchRequest, MatchResponse,
)
from app.services.llm import LLMService
from app.services.matching import Matcher

router = APIRouter(prefix="/api", tags=["match"])


@router.post("/match", response_model=MatchResponse)
async def match_profile_to_jobs(
    req: MatchRequest,
    matcher: Matcher = Depends(get_matcher),
) -> MatchResponse:
    return matcher.match(req.profile, req.jobs)


@router.post("/gaps", response_model=GapAnalysis)
async def analyze_gaps(
    req: GapRequest,
    llm: LLMService = Depends(get_llm_service),
) -> GapAnalysis:
    return llm.analyze_gaps(req.profile, req.target_jobs)
