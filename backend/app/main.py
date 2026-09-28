"""
Main FastAPI application for GreenForge AI backend.
"""
import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.database import init_db
from app.api import health, analyze, benchmark, optimize, rag, copilot, ml, reports, settings_api, demo

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize application on startup."""
    logger.info("GreenForge AI backend starting...")
    await init_db()
    logger.info("Database initialized")
    # Pre-build RAG index
    from app.rag.rag_system import get_rag_system
    rag = get_rag_system()
    logger.info(f"RAG system ready with {len(rag.retriever.chunks)} chunks")
    yield
    logger.info("GreenForge AI backend shutting down")


app = FastAPI(
    title="GreenForge AI",
    description="Agentic AI for Sustainable Software & Machine Learning",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(health.router, prefix="/api")
app.include_router(analyze.router, prefix="/api")
app.include_router(benchmark.router, prefix="/api")
app.include_router(optimize.router, prefix="/api")
app.include_router(rag.router, prefix="/api")
app.include_router(copilot.router, prefix="/api")
app.include_router(ml.router, prefix="/api")
app.include_router(reports.router, prefix="/api")
app.include_router(settings_api.router, prefix="/api")
app.include_router(demo.router, prefix="/api")


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal error occurred. Check backend logs for details."}
    )
