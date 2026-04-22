import csv
import random
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Callable, Optional

from ..generators.base import BaseLLMGenerator
from .config import ResearchConfig
from .mutator import mutate
from .runner import ExperimentResult, run_experiment


@dataclass
class AutoresearchRun:
    best_config: ResearchConfig
    best_score: float
    baseline_score: float
    n_experiments: int
    n_accepted: int
    total_tokens: int
    duration_seconds: float
    log_path: Path
    best_config_path: Path


def run_autoresearch(
    stories: list[str],
    generator: BaseLLMGenerator,
    initial_config: Optional[ResearchConfig] = None,
    n_experiments: int = 30,
    run_dir: Path = Path("results/autoresearch"),
    seed: Optional[int] = None,
    on_experiment: Optional[Callable] = None,
) -> AutoresearchRun:
    """
    Hill-climbing optimizer: mutates scorer weights / threshold / max_attempts
    and accepts the change only when avg BDD score improves on the fixed story sample.

    Inspired by Karpathy's autoresearch — the key idea is a fixed evaluation budget
    (N stories) and a greedy acceptance rule, running autonomously without human input.

    Args:
        stories:        Fixed sample of user stories used as the evaluation budget.
        generator:      LLM backend (Gemini or Claude).
        initial_config: Starting configuration (defaults to current project weights).
        n_experiments:  Number of mutation→evaluate→accept/reject cycles.
        run_dir:        Directory for experiments.csv and best_config.json.
        seed:           RNG seed for reproducibility.
        on_experiment:  Optional callback(i, mutation_desc, config, result, accepted, is_best).
    """
    rng = random.Random(seed)
    run_dir.mkdir(parents=True, exist_ok=True)

    current_config = initial_config or ResearchConfig()

    baseline = run_experiment(stories, current_config, generator)
    current_score = baseline.avg_score
    best_config = current_config
    best_score = current_score
    total_tokens = baseline.total_tokens

    log_path = run_dir / "experiments.csv"
    best_config_path = run_dir / "best_config.json"
    best_config.save(best_config_path)

    _FIELDNAMES = [
        "experiment", "mutation",
        "cobertura", "clareza", "estrutura", "executabilidade",
        "threshold", "max_attempts",
        "avg_score", "n_approved", "total_tokens",
        "accepted", "is_best",
    ]

    n_accepted = 0
    start = time.time()

    with open(log_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=_FIELDNAMES)
        writer.writeheader()
        _write_row(writer, 0, "baseline", current_config, baseline, accepted=True, is_best=True)
        f.flush()

        if on_experiment:
            on_experiment(0, "baseline", current_config, baseline, True, True)

        for i in range(1, n_experiments + 1):
            candidate, mutation_desc = mutate(current_config, rng)
            result = run_experiment(stories, candidate, generator)
            total_tokens += result.total_tokens

            accepted = result.avg_score > current_score
            is_best = result.avg_score > best_score

            if accepted:
                current_config = candidate
                current_score = result.avg_score
                n_accepted += 1

            if is_best:
                best_config = candidate
                best_score = result.avg_score
                best_config.save(best_config_path)

            _write_row(writer, i, mutation_desc, candidate, result, accepted, is_best)
            f.flush()

            if on_experiment:
                on_experiment(i, mutation_desc, candidate, result, accepted, is_best)

    best_config.save(best_config_path)

    return AutoresearchRun(
        best_config=best_config,
        best_score=best_score,
        baseline_score=baseline.avg_score,
        n_experiments=n_experiments,
        n_accepted=n_accepted,
        total_tokens=total_tokens,
        duration_seconds=time.time() - start,
        log_path=log_path,
        best_config_path=best_config_path,
    )


def _write_row(
    writer: csv.DictWriter,
    i: int,
    mutation: str,
    config: ResearchConfig,
    result: ExperimentResult,
    accepted: bool,
    is_best: bool,
) -> None:
    d = asdict(config)
    writer.writerow({
        "experiment":      i,
        "mutation":        mutation,
        "cobertura":       d["cobertura"],
        "clareza":         d["clareza"],
        "estrutura":       d["estrutura"],
        "executabilidade": d["executabilidade"],
        "threshold":       d["threshold"],
        "max_attempts":    d["max_attempts"],
        "avg_score":       result.avg_score,
        "n_approved":      result.n_approved,
        "total_tokens":    result.total_tokens,
        "accepted":        accepted,
        "is_best":         is_best,
    })
