"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import log
from app.api.routes import router


app = FastAPI(
    title="PortfolioMatch API",
    description="AI job matcher based on actual GitHub code analysis",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")


@app.on_event("startup")
async def startup():
    log.info("PortfolioMatch API starting")
    log.info(f"GitHub available: {settings.github_available}")
    log.info(f"Gemini available: {settings.gemini_available}")
    log.info(f"Embedding model: {settings.embedding_model}")


@app.get("/")
async def root():
    return {
        "name": "PortfolioMatch",
        "version": "0.1.0",
        "docs": "/docs",
    }
