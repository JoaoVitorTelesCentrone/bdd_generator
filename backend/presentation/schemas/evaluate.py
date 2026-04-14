"""HTTP request/response schemas for POST /api/evaluate."""
from pydantic import BaseModel, Field
from backend.presentation.schemas.common import ScoreSchema


class EvaluateRequest(BaseModel):
    story: str    = Field(..., min_length=1)
    bdd_text: str = Field(..., min_length=1)
    threshold: float = Field(default=7.0, ge=0.0, le=10.0)


class EvaluateResponse(BaseModel):
    score: ScoreSchema
