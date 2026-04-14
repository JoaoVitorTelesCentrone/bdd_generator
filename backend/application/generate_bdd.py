"""
Application layer — GenerateBDDUseCase.

Orchestrates: research → generate → evaluate → refine loop.
Depends only on domain interfaces; no framework, no I/O.
"""
from typing import Optional

from backend.domain.interfaces import IGenerator, IScorer, IResearcher
from backend.application.dtos import GenerateInputDTO, GenerateOutputDTO, ScoreDTO

# Infrastructure imports are deferred to avoid circular deps — the use case
# receives concrete implementations via dependency injection at runtime.
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.refinement.loop import RefinementLoop
from src.research.auto_researcher import AutoResearcher


class GenerateBDDUseCase:
    """
    Executes the full BDD generation pipeline for a single user story.

    Dependencies are injected, making the use case independently testable
    without hitting any LLM API.
    """

    def __init__(
        self,
        generator: IGenerator,
        scorer: IScorer,
    ) -> None:
        self._generator = generator
        self._scorer = scorer

    def execute(self, dto: GenerateInputDTO) -> GenerateOutputDTO:
        researcher: Optional[AutoResearcher] = None
        if dto.research:
            # AutoResearcher satisfies IResearcher; pass the same generator
            researcher = AutoResearcher(generator=self._generator)  # type: ignore[arg-type]

        loop = RefinementLoop(
            generator=self._generator,   # type: ignore[arg-type]
            scorer=self._scorer,         # type: ignore[arg-type]
            max_attempts=dto.max_attempts,
            researcher=researcher,
        )

        result = loop.run(
            dto.story,
            enable_research=dto.research,
            until_converged=dto.until_converged,
        )

        return GenerateOutputDTO(
            bdd_text=result.bdd_text,
            score=ScoreDTO(
                cobertura=result.score.cobertura,
                clareza=result.score.clareza,
                estrutura=result.score.estrutura,
                executabilidade=result.score.executabilidade,
                score_final=result.score.score_final,
                aprovado=result.score.aprovado,
                threshold=result.score.threshold,
            ),
            attempts=result.attempts,
            total_tokens=result.total_tokens,
            research_tokens=result.research_tokens,
            converged=result.converged,
            duration_seconds=round(result.total_duration_seconds, 2),
        )
