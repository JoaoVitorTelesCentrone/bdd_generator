"""
Application layer — EvaluateBDDUseCase.

Scores an existing BDD text against a user story.
No generation, no refinement — pure evaluation.
"""
from backend.domain.interfaces import IScorer
from backend.application.dtos import EvaluateInputDTO, EvaluateOutputDTO, ScoreDTO


class EvaluateBDDUseCase:
    """
    Scores a BDD text that was written externally (e.g., by a human or the CLI).

    Useful for CI pipelines or dashboard "evaluate only" mode.
    """

    def __init__(self, scorer: IScorer) -> None:
        self._scorer = scorer

    def execute(self, dto: EvaluateInputDTO) -> EvaluateOutputDTO:
        score = self._scorer.score(dto.story, dto.bdd_text)

        return EvaluateOutputDTO(
            score=ScoreDTO(
                cobertura=score.cobertura,
                clareza=score.clareza,
                estrutura=score.estrutura,
                executabilidade=score.executabilidade,
                score_final=score.score_final,
                aprovado=score.aprovado,
                threshold=score.threshold,
            )
        )
