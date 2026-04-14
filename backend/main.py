"""
FastAPI application factory — BDD Generator API

Clean Architecture entry point.
This file only wires together the framework (FastAPI) with the
presentation layer (routers). No business logic lives here.

Run:
    python -m uvicorn backend.main:app --reload --port 8000
"""
import sys, os
# Ensure project root is on the path so src.* imports resolve
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.presentation.routers import health, models, generate, evaluate

app = FastAPI(
    title="BDD Generator API",
    description="Gerador de cenários BDD com auto-refinamento (Gemini / Claude)",
    version="2.0.0",
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", "http://127.0.0.1:3000",
        "http://localhost:3001", "http://127.0.0.1:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(health.router)
app.include_router(models.router)
app.include_router(generate.router)
app.include_router(evaluate.router)
