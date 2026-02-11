"""FastAPI application entry point for the SEAM Assessment Chatbot."""

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.config import settings
from backend.database import init_db
from backend.routers import auth, interview, dashboard

# ── Logging ───────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


# ── App Lifespan ──────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    logger.info("🚀 Starting SEAM Assessment Chatbot...")
    await init_db()
    logger.info("✅ Database initialized.")
    yield
    logger.info("👋 Shutting down.")


# ── FastAPI App ───────────────────────────────────────────────────────

app = FastAPI(
    title=settings.app_title,
    description="AI-Augmented SEAM Organizational Diagnosis Chatbot",
    version="1.0.0",
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────

app.include_router(auth.router)
app.include_router(interview.router)
app.include_router(dashboard.router)

# ── Static Files (Frontend) ──────────────────────────────────────────

frontend_dir = Path(__file__).resolve().parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")


# ── Health Check ──────────────────────────────────────────────────────

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "service": settings.app_title,
        "version": "1.0.0",
    }
