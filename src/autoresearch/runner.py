from dataclasses import dataclass, field

from ..evaluators.scorer import BDDScorer
from ..generators.base import BaseLLMGenerator
from ..refinement.loop import RefinementLoop
from .config import ResearchConfig


@dataclass
class ExperimentResult:
    config: ResearchConfig
    avg_score: float
    scores: list = field(default_factory=list)
    total_tokens: int = 0
    n_approved: int = 0
    n_stories: int = 0


def run_experiment(
    stories: list[str],
    config: ResearchConfig,
    generator: BaseLLMGenerator,
) -> ExperimentResult:
    """Evaluates a ResearchConfig against a fixed set of stories and returns avg score."""
    scorer = BDDScorer(threshold=config.threshold, weights=config.as_weights())
    loop = RefinementLoop(
        generator=generator,
        scorer=scorer,
        max_attempts=config.max_attempts,
        logger=None,
        verbose=False,
    )

    scores = []
    total_tokens = 0
    n_approved = 0

    for story in stories:
        result = loop.run(story)
        scores.append(result.score.score_final)
        total_tokens += result.total_tokens
        if result.score.aprovado:
            n_approved += 1

    avg = round(sum(scores) / len(scores), 4) if scores else 0.0
    return ExperimentResult(
        config=config,
        avg_score=avg,
        scores=scores,
        total_tokens=total_tokens,
        n_approved=n_approved,
        n_stories=len(stories),
    )
