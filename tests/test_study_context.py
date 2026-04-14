"""
TDD — BatchAnalyzer e load_study_context.

Gherkin mapeado:
  - "Study analisa resultados de batch e gera insights.json"
  - "Study carrega os top-N e bottom-N BDDs conforme configurado"
  - "load_study_context constrói string de contexto few-shot a partir do JSON"
  - "Study falha com mensagem de erro quando CSV não existe"
"""
import sys, os, json, csv
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from pathlib import Path
from unittest.mock import MagicMock

from src.generators.base import GenerationResult
from src.study.analyzer import BatchAnalyzer, StudyResult, load_study_context


# ─── helpers ────────────────────────────────────────────────────────────────

def _make_generator(insights_text="## 1. PADRÕES\nExemplo de insight.") -> MagicMock:
    gen = MagicMock()
    gen.generate.return_value = GenerationResult(
        success=True, bdd_text=insights_text, model="mock",
        input_tokens=100, output_tokens=200,
    )
    gen.get_model_name.return_value = "mock-model"
    return gen


def _write_batch_csv(tmp_path: Path, n_rows=5) -> tuple[Path, list[Path]]:
    """Creates a batch_results.csv with n_rows, each with a real feature file."""
    features_dir = tmp_path / "features"
    features_dir.mkdir()
    csv_path = tmp_path / "batch_results.csv"

    rows = []
    feature_paths = []
    for i in range(n_rows):
        score = 5.0 + i * 1.0  # 5.0, 6.0, 7.0, 8.0, 9.0
        feat = features_dir / f"{i+1:03d}_story_{i}.feature"
        feat.write_text(
            f"# Story: Story {i}\n\n"
            f"Cenário: Cenário {i}\n"
            f"  Dado que estou na tela {i}\n"
            f'  Quando clico no botão "OK {i}"\n'
            f'  Então devo ver "Resultado {i}"\n',
            encoding="utf-8",
        )
        feature_paths.append(feat)
        rows.append({
            "story_id": i + 1,
            "title": f"Story {i}",
            "model": "flash",
            "score_final": score,
            "cobertura": score,
            "clareza": score,
            "estrutura": score,
            "executabilidade": score,
            "tentativas": 2,
            "tokens_usados": 300,
            "tokens_research": 0,
            "tempo_segundos": 1.5,
            "aprovado": score >= 7.0,
            "convergiu": True,
            "feature_file": str(feat),
        })

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    return csv_path, feature_paths


# ─── BatchAnalyzer ───────────────────────────────────────────────────────────

class TestBatchAnalyzer:
    """
    Cenário: Study analisa resultados de batch e gera insights.json
    Cenário: Study carrega os top-N e bottom-N BDDs conforme configurado
    """

    def test_analyze_creates_insights_json(self, tmp_path):
        csv_path, _ = _write_batch_csv(tmp_path)
        output_path = tmp_path / "insights.json"
        analyzer = BatchAnalyzer(generator=_make_generator())
        result = analyzer.analyze(str(csv_path), str(output_path))
        assert output_path.exists()

    def test_insights_json_has_required_keys(self, tmp_path):
        csv_path, _ = _write_batch_csv(tmp_path)
        output_path = tmp_path / "insights.json"
        analyzer = BatchAnalyzer(generator=_make_generator())
        analyzer.analyze(str(csv_path), str(output_path))
        data = json.loads(output_path.read_text(encoding="utf-8"))
        for key in ["insights", "top_examples", "low_examples", "meta"]:
            assert key in data, f"Chave '{key}' ausente no insights.json"

    def test_top_n_respected(self, tmp_path):
        csv_path, _ = _write_batch_csv(tmp_path, n_rows=10)
        output_path = tmp_path / "insights.json"
        analyzer = BatchAnalyzer(generator=_make_generator())
        result = analyzer.analyze(str(csv_path), str(output_path), top_n=3)
        assert len(result.top_examples) <= 3

    def test_bottom_n_respected(self, tmp_path):
        csv_path, _ = _write_batch_csv(tmp_path, n_rows=10)
        output_path = tmp_path / "insights.json"
        analyzer = BatchAnalyzer(generator=_make_generator())
        result = analyzer.analyze(str(csv_path), str(output_path), top_n=5, bottom_n=2)
        assert len(result.low_examples) <= 2

    def test_top_examples_have_higher_score_than_bottom(self, tmp_path):
        csv_path, _ = _write_batch_csv(tmp_path, n_rows=8)
        output_path = tmp_path / "insights.json"
        analyzer = BatchAnalyzer(generator=_make_generator())
        result = analyzer.analyze(str(csv_path), str(output_path), top_n=2, bottom_n=2)
        if result.top_examples and result.low_examples:
            min_top = min(e["score"] for e in result.top_examples)
            max_low = max(e["score"] for e in result.low_examples)
            assert min_top >= max_low, (
                f"Top min score ({min_top}) deve ser >= bottom max score ({max_low})"
            )

    def test_insights_text_returned_in_result(self, tmp_path):
        csv_path, _ = _write_batch_csv(tmp_path)
        output_path = tmp_path / "insights.json"
        analyzer = BatchAnalyzer(generator=_make_generator("## 1. PADRÕES\nInsight real."))
        result = analyzer.analyze(str(csv_path), str(output_path))
        assert "PADRÕES" in result.insights or len(result.insights) > 0

    def test_tokens_tracked_in_result(self, tmp_path):
        csv_path, _ = _write_batch_csv(tmp_path)
        output_path = tmp_path / "insights.json"
        analyzer = BatchAnalyzer(generator=_make_generator())
        result = analyzer.analyze(str(csv_path), str(output_path))
        assert result.input_tokens > 0
        assert result.output_tokens > 0

    def test_duration_tracked(self, tmp_path):
        csv_path, _ = _write_batch_csv(tmp_path)
        output_path = tmp_path / "insights.json"
        analyzer = BatchAnalyzer(generator=_make_generator())
        result = analyzer.analyze(str(csv_path), str(output_path))
        assert result.duration_seconds >= 0.0

    def test_meta_contains_source_csv(self, tmp_path):
        csv_path, _ = _write_batch_csv(tmp_path)
        output_path = tmp_path / "insights.json"
        analyzer = BatchAnalyzer(generator=_make_generator())
        analyzer.analyze(str(csv_path), str(output_path))
        data = json.loads(output_path.read_text())
        assert "source_csv" in data["meta"]

    def test_examples_contain_bdd_text(self, tmp_path):
        csv_path, _ = _write_batch_csv(tmp_path, n_rows=5)
        output_path = tmp_path / "insights.json"
        analyzer = BatchAnalyzer(generator=_make_generator())
        result = analyzer.analyze(str(csv_path), str(output_path), top_n=2)
        for ex in result.top_examples:
            assert "bdd" in ex
            assert len(ex["bdd"]) > 0


# ─── load_study_context ──────────────────────────────────────────────────────

class TestLoadStudyContext:
    """
    Cenário: load_study_context constrói string de contexto few-shot a partir do JSON
    """

    def _write_insights_json(self, tmp_path, n_top=3) -> Path:
        p = tmp_path / "insights.json"
        top = [
            {
                "title": f"Story {i}",
                "score": 9.0 - i * 0.5,
                "cobertura": 9.0, "clareza": 8.5,
                "estrutura": 9.0, "executabilidade": 8.0,
                "bdd": f"# comentário\nFuncionalidade: F{i}\n  Cenário: C{i}\n    Dado que algo\n    Quando ação\n    Então resultado",
            }
            for i in range(n_top)
        ]
        data = {
            "insights": "## 1. PADRÕES\nUse verbos de ação.\n## 2. ANTI-PADRÕES\nEvite termos vagos.",
            "top_examples": top,
            "low_examples": [],
            "meta": {"source_csv": "batch.csv", "total_stories": 10,
                     "generated_at": "2026-01-01T00:00:00", "model": "flash"},
        }
        p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        return p

    def test_contains_guia_de_estilo(self, tmp_path):
        p = self._write_insights_json(tmp_path)
        ctx = load_study_context(str(p))
        assert "GUIA DE ESTILO" in ctx

    def test_contains_exemplos_de_referencia(self, tmp_path):
        p = self._write_insights_json(tmp_path, n_top=2)
        ctx = load_study_context(str(p))
        assert "EXEMPLOS DE REFERÊNCIA" in ctx

    def test_contains_insights_text(self, tmp_path):
        p = self._write_insights_json(tmp_path)
        ctx = load_study_context(str(p))
        assert "PADRÕES" in ctx

    def test_limits_to_max_examples_default_3(self, tmp_path):
        p = self._write_insights_json(tmp_path, n_top=10)
        ctx = load_study_context(str(p))
        # Deve conter no máximo 3 blocos "[Exemplo N |"
        import re
        matches = re.findall(r"\[Exemplo \d+", ctx)
        assert len(matches) <= 3

    def test_limits_to_custom_max_examples(self, tmp_path):
        p = self._write_insights_json(tmp_path, n_top=10)
        ctx = load_study_context(str(p), max_examples=2)
        import re
        matches = re.findall(r"\[Exemplo \d+", ctx)
        assert len(matches) <= 2

    def test_strips_comment_lines_from_examples(self, tmp_path):
        p = self._write_insights_json(tmp_path, n_top=1)
        ctx = load_study_context(str(p))
        # linhas de comentário (# ...) não devem aparecer no contexto
        assert "# comentário" not in ctx

    def test_returns_string_type(self, tmp_path):
        p = self._write_insights_json(tmp_path)
        ctx = load_study_context(str(p))
        assert isinstance(ctx, str)
        assert len(ctx) > 0

    def test_no_examples_when_top_empty(self, tmp_path):
        p = tmp_path / "empty_insights.json"
        data = {
            "insights": "Sem exemplos disponíveis.",
            "top_examples": [],
            "low_examples": [],
            "meta": {},
        }
        p.write_text(json.dumps(data), encoding="utf-8")
        ctx = load_study_context(str(p))
        assert "GUIA DE ESTILO" in ctx
        assert "EXEMPLOS DE REFERÊNCIA" not in ctx
