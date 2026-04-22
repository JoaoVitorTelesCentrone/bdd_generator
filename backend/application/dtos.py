"""
Application layer — Data Transfer Objects.

Pure dataclasses; zero FastAPI / Pydantic imports.
The presentation layer converts HTTP schemas → these DTOs,
and these DTOs → HTTP response schemas.
"""
from dataclasses import dataclass, field
from typing import Optional


# ── Generate ──────────────────────────────────────────────────────────────────

@dataclass
class GenerateInputDTO:
    story: str
    model: str              = "flash"
    threshold: float        = 7.0
    max_attempts: int       = 5
    research: bool          = False
    until_converged: bool   = False


@dataclass
class ScoreDTO:
    cobertura: float
    clareza: float
    estrutura: float
    executabilidade: float
    score_final: float
    aprovado: bool
    threshold: float


@dataclass
class GenerateOutputDTO:
    bdd_text: str
    score: ScoreDTO
    attempts: int
    total_tokens: int
    research_tokens: int
    converged: bool
    duration_seconds: float


# ── Unit Tests ────────────────────────────────────────────────────────────────

@dataclass
class UnitTestInputDTO:
    bdd_text: str
    language: str
    framework: str
    model: str = "flash"


@dataclass
class UnitTestOutputDTO:
    code: str
    language: str
    framework: str
    file_extension: str
    num_tests: int
    total_tokens: int
    duration_seconds: float


# ── Evaluate ──────────────────────────────────────────────────────────────────

@dataclass
class EvaluateInputDTO:
    story: str
    bdd_text: str
    threshold: float = 7.0


@dataclass
class EvaluateOutputDTO:
    score: ScoreDTO
