"""
Domain layer — pure protocols (interfaces).

These abstractions define what the application layer needs.
No concrete dependencies, no framework imports.
"""
from typing import Optional, Protocol, runtime_checkable


# ── Generator ─────────────────────────────────────────────────────────────────

@runtime_checkable
class IGenerationResult(Protocol):
    success: bool
    bdd_text: str
    model: str
    input_tokens: int
    output_tokens: int
    error: Optional[str]

    @property
    def total_tokens(self) -> int: ...


@runtime_checkable
class IGenerator(Protocol):
    def generate(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
    ) -> IGenerationResult: ...

    def get_model_name(self) -> str: ...


# ── Scorer ────────────────────────────────────────────────────────────────────

@runtime_checkable
class IScoreResult(Protocol):
    cobertura: float
    clareza: float
    estrutura: float
    executabilidade: float
    score_final: float
    aprovado: bool
    threshold: float

    def summary(self) -> str: ...
    def weaknesses(self) -> list[str]: ...


@runtime_checkable
class IScorer(Protocol):
    threshold: float

    def score(
        self,
        user_story: str,
        bdd_text: str,
        research_context: Optional[str] = None,
    ) -> IScoreResult: ...


# ── Researcher ────────────────────────────────────────────────────────────────

@runtime_checkable
class IResearchResult(Protocol):
    success: bool
    context: Optional[str]
    total_tokens: int


@runtime_checkable
class IResearcher(Protocol):
    def research(self, user_story: str) -> IResearchResult: ...


# ── Refinement loop ───────────────────────────────────────────────────────────

@runtime_checkable
class IRefinementResult(Protocol):
    bdd_text: str
    score: IScoreResult
    attempts: int
    total_tokens: int
    research_tokens: int
    converged: bool
    total_duration_seconds: float
