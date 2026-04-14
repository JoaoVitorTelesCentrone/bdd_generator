"""Shared Pydantic schemas reused across multiple routers."""
from pydantic import BaseModel


class ScoreSchema(BaseModel):
    cobertura: float
    clareza: float
    estrutura: float
    executabilidade: float
    score_final: float
    aprovado: bool
    threshold: float
