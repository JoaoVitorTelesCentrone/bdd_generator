import time
from dataclasses import dataclass, field
from typing import Optional

from ..generators.base import BaseLLMGenerator
from ..evaluators.scorer import BDDScorer, ScoreResult
from ..utils.prompts import PromptTemplates
from ..utils.logger import AttemptLogger, AttemptRecord
from ..research.auto_researcher import AutoResearcher


@dataclass
class RefinementResult:
    bdd_text: str
    score: ScoreResult
    attempts: int
    total_input_tokens: int
    total_output_tokens: int
    total_duration_seconds: float
    converged: bool  # True if score >= threshold before max_attempts
    research_tokens: int = 0  # tokens used in auto-research phase

    @property
    def total_tokens(self) -> int:
        return self.total_input_tokens + self.total_output_tokens


class RefinementLoop:
    """
    Generates BDD, evaluates quality, and iteratively refines
    until the score meets the threshold or max_attempts is reached.

    When enable_research=True in run(), a preliminary LLM call analyzes
    the user story and extracts acceptance criteria, business rules and
    edge cases before the first generation attempt.
    """

    def __init__(
        self,
        generator: BaseLLMGenerator,
        scorer: BDDScorer,
        max_attempts: int = 5,
        logger: Optional[AttemptLogger] = None,
        verbose: bool = False,
        researcher: Optional[AutoResearcher] = None,
    ):
        self.generator = generator
        self.scorer = scorer
        self.max_attempts = max_attempts
        self.logger = logger
        self.verbose = verbose
        self.researcher = researcher

    def run(
        self,
        user_story: str,
        context: Optional[str] = None,
        enable_research: bool = False,
        until_converged: bool = False,
    ) -> RefinementResult:
        """
        Run the generate → evaluate → refine loop.

        Args:
            until_converged: When True, ignore max_attempts and keep refining
                             until score >= threshold. A hard ceiling of 50
                             attempts is enforced to prevent infinite loops.
        """
        total_input_tokens = 0
        total_output_tokens = 0
        total_duration = 0.0
        research_tokens = 0
        research_context: Optional[str] = None  # kept separate for the scorer

        best_bdd: str = ""
        best_score: Optional[ScoreResult] = None

        # ── Auto-Research Phase ──────────────────────────────────────────────
        if enable_research and self.researcher is not None:
            research = self.researcher.research(user_story)
            research_tokens = research.total_tokens
            if research.success and research.context:
                research_context = research.context
                # Merge with any manually supplied context for generation prompt
                if context:
                    context = f"{research.context}\n\n{context}"
                else:
                    context = research.context

        ceiling = 50 if until_converged else self.max_attempts
        attempt = 0
        while attempt < ceiling:
            attempt += 1
            limit_label = "∞" if until_converged else str(self.max_attempts)
            if self.verbose:
                print(f"\n  Tentativa {attempt}/{limit_label}...")

            # Build prompt
            if attempt == 1:
                prompt = PromptTemplates.generate_bdd(user_story, context)
            else:
                assert best_score is not None
                prompt = PromptTemplates.refine_bdd(
                    user_story=user_story,
                    previous_bdd=best_bdd,
                    score_summary=best_score.summary(),
                    weaknesses=best_score.weaknesses(),
                )

            # Generate
            t0 = time.time()
            result = self.generator.generate(prompt)
            duration = time.time() - t0

            if not result.success:
                if self.verbose:
                    print(f"  Erro na geração: {result.error}")
                break

            # Evaluate — pass research_context so coverage can check against LLM-extracted ACs
            score = self.scorer.score(user_story, result.bdd_text, research_context)

            total_input_tokens  += result.input_tokens
            total_output_tokens += result.output_tokens
            total_duration      += duration

            # Log attempt
            if self.logger:
                self.logger.log_attempt(
                    AttemptRecord(
                        attempt=attempt,
                        model=self.generator.get_model_name(),
                        user_story=user_story,
                        bdd_text=result.bdd_text,
                        score=score,
                        input_tokens=result.input_tokens,
                        output_tokens=result.output_tokens,
                        duration_seconds=duration,
                    )
                )

            # Keep best
            if best_score is None or score.score_final > best_score.score_final:
                best_bdd = result.bdd_text
                best_score = score

            if self.verbose:
                print(f"  Score: {score.score_final:.1f}/10 {'✓' if score.aprovado else '✗'}")

            if score.aprovado:
                return RefinementResult(
                    bdd_text=best_bdd,
                    score=best_score,
                    attempts=attempt,
                    total_input_tokens=total_input_tokens,
                    total_output_tokens=total_output_tokens,
                    total_duration_seconds=total_duration,
                    converged=True,
                    research_tokens=research_tokens,
                )

        # Return best result even if threshold not met
        return RefinementResult(
            bdd_text=best_bdd or "",
            score=best_score or self.scorer.score(user_story, ""),
            attempts=attempt,
            total_input_tokens=total_input_tokens,
            total_output_tokens=total_output_tokens,
            total_duration_seconds=total_duration,
            converged=False,
            research_tokens=research_tokens,
        )
