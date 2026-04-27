"""
FastAPI application factory — BDD Generator API

Clean Architecture entry point.
This file only wires together the framework (FastAPI) with the
presentation layer (routers). No business logic lives here.

Run:
    python -m uvicorn backend.main:app --reload --port 8000
"""
import sys, os, logging
# Ensure project root is on the path so src.* imports resolve
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

_logger = logging.getLogger(__name__)

_ENV_CHECKS = {
    "GROQ_API_KEY":       "Groq / Llama / DeepSeek (grátis)",
    "GEMINI_API_KEY":     "Gemini (flash / pro / flash-lite)",
    "ANTHROPIC_API_KEY":  "Claude (sonnet / opus / haiku)",
}

def _validate_env() -> None:
    missing = [k for k, label in _ENV_CHECKS.items() if not os.getenv(k)]
    for k in missing:
        _logger.warning("⚠  %s não configurada — modelos %s indisponíveis", k, _ENV_CHECKS[k])
    configured = [k for k in _ENV_CHECKS if os.getenv(k)]
    if configured:
        _logger.info("✓ Chaves configuradas: %s", ", ".join(configured))
    if not configured:
        _logger.warning("Configure as chaves no arquivo .env na raiz do projeto")

from backend.presentation.routers import health, models, generate, evaluate
from backend.presentation.routers import bist_router
from backend.presentation.routers import tenants_router
from backend.presentation.routers import stories_router
from backend.presentation.routers import autoresearch_router
from backend.presentation.routers import unit_tests_router

_validate_env()

app = FastAPI(
    title="BDD Generator API",
    description="Gerador de cenários BDD com auto-refinamento (Gemini / Claude)",
    version="3.0.0",
)

# ── CORS ──────────────────────────────────────────────────────────────────────
_cors_origins = [
    "http://localhost:3000", "http://127.0.0.1:3000",
    "http://localhost:3001", "http://127.0.0.1:3001",
]
if _frontend_url := os.getenv("FRONTEND_URL"):
    _cors_origins.append(_frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(health.router)
app.include_router(models.router)
app.include_router(generate.router)
app.include_router(evaluate.router)
app.include_router(bist_router.router)
app.include_router(tenants_router.router)
app.include_router(stories_router.router)
app.include_router(autoresearch_router.router)
app.include_router(unit_tests_router.router)
