"""Core BIST agent: user story → BDD → .feature file via src/ modules."""

import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

# Ensure src/ is importable regardless of where bist is invoked from
_ROOT = Path(__file__).parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src.generators.claude_generator import ClaudeGenerator
from src.generators.gemini_generator import GeminiGenerator
from src.evaluators.scorer import BDDScorer
from src.refinement.loop import RefinementLoop
from src.utils.logger import AttemptLogger
from src.research.auto_researcher import AutoResearcher


@dataclass
class AgentResult:
    feature_path: str
    bdd_text: str
    score_final: float
    attempts: int
    total_tokens: int
    converged: bool
    duration_seconds: float


_GEMINI_ALIASES = {
    "flash", "flash-lite", "pro", "flash-1.5",
    "gemini-2.0-flash", "gemini-2.0-flash-lite",
    "gemini-1.5-pro", "gemini-1.5-flash",
}


def _is_gemini(model: str) -> bool:
    return model in _GEMINI_ALIASES or model.startswith("gemini")


class BISTAgent:
    """
    Wraps src/generators + src/refinement to produce a quality-gated
    .feature file from a plain-text user story.
    """

    def __init__(
        self,
        model: str = "sonnet",
        threshold: float = 7.0,
        max_attempts: int = 5,
        verbose: bool = False,
        enable_research: bool = False,
        until_converged: bool = False,
    ):
        self.model = model
        self.threshold = threshold
        self.max_attempts = max_attempts
        self.verbose = verbose
        self.enable_research = enable_research
        self.until_converged = until_converged
        self._loop = None

    def _build_loop(self, log_dir: str = "bist_output"):
        generator = (
            GeminiGenerator(model=self.model)
            if _is_gemini(self.model)
            else ClaudeGenerator(model=self.model)
        )
        scorer = BDDScorer(threshold=self.threshold)
        logger = AttemptLogger(log_dir=log_dir, verbose=self.verbose)
        researcher = (
            AutoResearcher(generator=generator, verbose=self.verbose)
            if self.enable_research
            else None
        )
        return RefinementLoop(
            generator=generator,
            scorer=scorer,
            max_attempts=self.max_attempts,
            logger=logger,
            verbose=self.verbose,
            researcher=researcher,
        )

    def generate(self, user_story: str, output_path: Optional[str] = None) -> AgentResult:
        """
        Generate a .feature file from a user story.

        Runs the refinement loop until quality threshold is met (or attempts
        exhausted), then persists the best result to *output_path* (or an
        auto-named file under bist_output/features/).
        """
        t0 = time.time()

        if output_path:
            feature_path = Path(output_path)
            feature_path.parent.mkdir(parents=True, exist_ok=True)
            log_dir = str(feature_path.parent)
        else:
            out_dir = Path("bist_output/features")
            out_dir.mkdir(parents=True, exist_ok=True)
            safe = "".join(c if c.isalnum() or c in "_- " else "_" for c in user_story[:40])
            safe = safe.strip().replace(" ", "_")
            ts = time.strftime("%Y%m%d_%H%M%S")
            feature_path = out_dir / f"{safe}_{ts}.feature"
            log_dir = "bist_output"

        loop = self._build_loop(log_dir=log_dir)
        result = loop.run(
            user_story,
            enable_research=self.enable_research,
            until_converged=self.until_converged,
        )

        if result.bdd_text:
            feature_path.write_text(result.bdd_text, encoding="utf-8")

        return AgentResult(
            feature_path=str(feature_path),
            bdd_text=result.bdd_text,
            score_final=result.score.score_final,
            attempts=result.attempts,
            total_tokens=result.total_tokens,
            converged=result.converged,
            duration_seconds=time.time() - t0,
        )
