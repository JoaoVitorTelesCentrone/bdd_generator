import csv
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field

from ..evaluators.scorer import ScoreResult


@dataclass
class AttemptRecord:
    attempt: int
    model: str
    user_story: str
    bdd_text: str
    score: ScoreResult
    input_tokens: int
    output_tokens: int
    duration_seconds: float
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def as_dict(self) -> dict:
        return {
            "timestamp":       self.timestamp,
            "attempt":         self.attempt,
            "model":           self.model,
            "user_story":      self.user_story[:200],
            "score_final":     self.score.score_final,
            "cobertura":       self.score.cobertura,
            "clareza":         self.score.clareza,
            "estrutura":       self.score.estrutura,
            "executabilidade": self.score.executabilidade,
            "aprovado":        self.score.aprovado,
            "input_tokens":    self.input_tokens,
            "output_tokens":   self.output_tokens,
            "total_tokens":    self.input_tokens + self.output_tokens,
            "duration_s":      round(self.duration_seconds, 2),
        }


class AttemptLogger:
    """Logs BDD generation attempts to CSV and optionally to stdout."""

    def __init__(
        self,
        log_dir: str = "results/experiments",
        verbose: bool = False,
        session_id: Optional[str] = None,
    ):
        self.verbose = verbose
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        ts = session_id or datetime.now().strftime("%Y%m%d_%H%M%S")
        self.csv_path = self.log_dir / f"session_{ts}.csv"
        self._csv_initialized = False

    # ------------------------------------------------------------------
    def log_attempt(self, record: AttemptRecord) -> None:
        self._write_csv(record)
        if self.verbose:
            self._print_attempt(record)

    def _write_csv(self, record: AttemptRecord) -> None:
        row = record.as_dict()
        file_exists = self.csv_path.exists()
        with open(self.csv_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(row.keys()))
            if not file_exists or not self._csv_initialized:
                writer.writeheader()
                self._csv_initialized = True
            writer.writerow(row)

    def _print_attempt(self, record: AttemptRecord) -> None:
        print(
            f"  Tentativa {record.attempt} | "
            f"Score: {record.score.score_final:.1f}/10 | "
            f"Tokens: {record.input_tokens + record.output_tokens} | "
            f"{record.duration_seconds:.1f}s",
            file=sys.stderr,
        )

    # ------------------------------------------------------------------
    def log_experiment_row(self, row: dict, csv_path: Optional[Path] = None) -> None:
        """Write a single experiment result row to a CSV file."""
        path = csv_path or (self.log_dir / "experiment_results.csv")
        file_exists = path.exists()
        with open(path, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(row.keys()))
            if not file_exists:
                writer.writeheader()
            writer.writerow(row)
