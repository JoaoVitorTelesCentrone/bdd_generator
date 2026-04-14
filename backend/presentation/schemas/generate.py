"""HTTP request/response schemas for POST /api/generate."""
from pydantic import BaseModel, Field
from backend.presentation.schemas.common import ScoreSchema


class GenerateRequest(BaseModel):
    story: str = Field(..., min_length=5, description="User story para gerar BDD")
    model: str = Field(
        default="flash",
        description="Modelo: flash | pro | flash-lite | sonnet | opus | haiku",
    )
    threshold: float     = Field(default=7.0, ge=0.0, le=10.0)
    max_attempts: int    = Field(default=5, ge=1, le=20)
    research: bool       = Field(default=False, description="Habilitar auto-research")
    until_converged: bool = Field(
        default=False,
        description="Refinar até atingir threshold (máx 50 tentativas)",
    )


class GenerateResponse(BaseModel):
    bdd_text: str
    score: ScoreSchema
    attempts: int
    total_tokens: int
    research_tokens: int
    converged: bool
    duration_seconds: float
