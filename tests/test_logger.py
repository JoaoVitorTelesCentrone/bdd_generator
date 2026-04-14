"""
TDD — AttemptLogger: CSV creation, row logging and token tracking.

Gherkin mapeado:
  - "AttemptLogger registra todas as tentativas em CSV"
  - "Tokens de geração são rastreados corretamente no resultado"
"""
import sys, os, csv, tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from pathlib import Path

from src.utils.logger import AttemptLogger, AttemptRecord
from src.evaluators.scorer import ScoreResult


# ─── helpers ────────────────────────────────────────────────────────────────

def _score(score_final=7.5, threshold=7.0) -> ScoreResult:
    return ScoreResult(
        cobertura=score_final, clareza=score_final,
        estrutura=score_final, executabilidade=score_final,
        score_final=score_final,
        aprovado=score_final >= threshold,
        threshold=threshold,
    )


def _record(attempt=1, model="flash", score_val=7.5, input_tokens=100, output_tokens=50) -> AttemptRecord:
    return AttemptRecord(
        attempt=attempt,
        model=model,
        user_story="Story de teste",
        bdd_text="Cenário: Teste\n  Dado que...",
        score=_score(score_val),
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        duration_seconds=1.2,
    )


# ─── CSV creation ────────────────────────────────────────────────────────────

class TestAttemptLoggerCSVCreation:
    """
    Cenário: AttemptLogger registra todas as tentativas em CSV
    """

    def test_csv_file_created_after_first_log(self, tmp_path):
        logger = AttemptLogger(log_dir=str(tmp_path), session_id="test01")
        logger.log_attempt(_record())
        assert logger.csv_path.exists()

    def test_csv_has_header_row(self, tmp_path):
        logger = AttemptLogger(log_dir=str(tmp_path), session_id="test02")
        logger.log_attempt(_record())
        with open(logger.csv_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
        assert fieldnames is not None
        assert "attempt" in fieldnames
        assert "model" in fieldnames
        assert "score_final" in fieldnames

    def test_csv_has_one_data_row_per_attempt(self, tmp_path):
        logger = AttemptLogger(log_dir=str(tmp_path), session_id="test03")
        logger.log_attempt(_record(attempt=1))
        logger.log_attempt(_record(attempt=2))
        logger.log_attempt(_record(attempt=3))
        with open(logger.csv_path, encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        assert len(rows) == 3

    def test_csv_row_contains_correct_attempt_number(self, tmp_path):
        logger = AttemptLogger(log_dir=str(tmp_path), session_id="test04")
        logger.log_attempt(_record(attempt=2))
        with open(logger.csv_path, encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        assert rows[0]["attempt"] == "2"

    def test_csv_row_contains_model_name(self, tmp_path):
        logger = AttemptLogger(log_dir=str(tmp_path), session_id="test05")
        logger.log_attempt(_record(model="sonnet"))
        with open(logger.csv_path, encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        assert rows[0]["model"] == "sonnet"

    def test_csv_row_contains_score(self, tmp_path):
        logger = AttemptLogger(log_dir=str(tmp_path), session_id="test06")
        logger.log_attempt(_record(score_val=8.5))
        with open(logger.csv_path, encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        assert float(rows[0]["score_final"]) == pytest.approx(8.5)

    def test_log_dir_created_if_not_exists(self, tmp_path):
        new_dir = tmp_path / "deep" / "nested" / "dir"
        logger = AttemptLogger(log_dir=str(new_dir), session_id="test07")
        logger.log_attempt(_record())
        assert new_dir.exists()
        assert logger.csv_path.exists()


# ─── token columns in CSV ────────────────────────────────────────────────────

class TestAttemptLoggerTokens:
    """
    Cenário: Tokens de geração são rastreados corretamente no resultado
    """

    def test_csv_has_input_and_output_token_columns(self, tmp_path):
        logger = AttemptLogger(log_dir=str(tmp_path), session_id="tok01")
        logger.log_attempt(_record(input_tokens=150, output_tokens=75))
        with open(logger.csv_path, encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        assert "input_tokens" in rows[0]
        assert "output_tokens" in rows[0]

    def test_csv_has_total_tokens_column(self, tmp_path):
        logger = AttemptLogger(log_dir=str(tmp_path), session_id="tok02")
        logger.log_attempt(_record(input_tokens=100, output_tokens=50))
        with open(logger.csv_path, encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        assert "total_tokens" in rows[0]
        assert int(rows[0]["total_tokens"]) == 150

    def test_total_tokens_equals_sum_of_parts(self, tmp_path):
        logger = AttemptLogger(log_dir=str(tmp_path), session_id="tok03")
        logger.log_attempt(_record(input_tokens=200, output_tokens=80))
        with open(logger.csv_path, encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        total = int(rows[0]["total_tokens"])
        inp = int(rows[0]["input_tokens"])
        out = int(rows[0]["output_tokens"])
        assert total == inp + out


# ─── AttemptRecord.as_dict ───────────────────────────────────────────────────

class TestAttemptRecordAsDict:
    def test_as_dict_contains_required_keys(self):
        rec = _record()
        d = rec.as_dict()
        for key in ["attempt", "model", "score_final", "cobertura", "clareza",
                    "estrutura", "executabilidade", "input_tokens", "output_tokens",
                    "total_tokens", "duration_s", "aprovado"]:
            assert key in d, f"Chave '{key}' ausente em as_dict()"

    def test_total_tokens_computed_correctly(self):
        rec = _record(input_tokens=120, output_tokens=60)
        d = rec.as_dict()
        assert d["total_tokens"] == 180

    def test_user_story_truncated_to_200_chars(self):
        rec = AttemptRecord(
            attempt=1, model="m",
            user_story="x" * 500,
            bdd_text="bdd",
            score=_score(),
            input_tokens=10, output_tokens=5,
            duration_seconds=0.1,
        )
        d = rec.as_dict()
        assert len(d["user_story"]) <= 200
