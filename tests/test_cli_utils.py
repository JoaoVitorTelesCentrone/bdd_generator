"""
TDD — CLI utility functions: _is_gemini, _make_generator, _load_dataset.

Gherkin mapeado:
  - "Modelos Gemini são reconhecidos corretamente"
  - "Modelos Claude são reconhecidos corretamente"
  - "Dataset CSV é carregado com colunas title, description e storypoints"
  - "Dataset aceita variações de nome de coluna (case-insensitive)"
"""
import sys, os, csv, tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from pathlib import Path
from unittest.mock import patch

from src.cli import _is_gemini, _load_dataset, _make_generator
from src.generators.gemini_generator import GeminiGenerator
from src.generators.claude_generator import ClaudeGenerator


# ─── _is_gemini ──────────────────────────────────────────────────────────────

class TestIsGemini:
    """
    Esquema do Cenário: Modelos Gemini são reconhecidos corretamente
    Esquema do Cenário: Modelos Claude são reconhecidos corretamente
    """

    @pytest.mark.parametrize("alias", [
        "flash", "pro", "flash-lite", "flash-1.5",
        "gemini-2.0-flash", "gemini-2.0-flash-lite",
        "gemini-1.5-pro", "gemini-1.5-flash",
    ])
    def test_gemini_aliases_return_true(self, alias):
        assert _is_gemini(alias) is True, f"'{alias}' deve ser Gemini"

    @pytest.mark.parametrize("alias", [
        "sonnet", "opus", "haiku",
    ])
    def test_claude_aliases_return_false(self, alias):
        assert _is_gemini(alias) is False, f"'{alias}' deve ser Claude"

    def test_unknown_model_not_starting_with_gemini_returns_false(self):
        assert _is_gemini("gpt-4") is False
        assert _is_gemini("llama3") is False

    def test_model_starting_with_gemini_returns_true(self):
        assert _is_gemini("gemini-experimental") is True


# ─── _make_generator ─────────────────────────────────────────────────────────

class TestMakeGenerator:
    """
    Cenário: _make_generator retorna instância correta por alias
    """

    @pytest.mark.parametrize("alias", ["flash", "pro", "flash-lite"])
    def test_gemini_alias_creates_gemini_generator(self, alias):
        gen = _make_generator(alias)
        assert isinstance(gen, GeminiGenerator), (
            f"'{alias}' deve criar GeminiGenerator, obtido {type(gen)}"
        )

    @pytest.mark.parametrize("alias", ["sonnet", "opus", "haiku"])
    def test_claude_alias_creates_claude_generator(self, alias):
        gen = _make_generator(alias)
        assert isinstance(gen, ClaudeGenerator), (
            f"'{alias}' deve criar ClaudeGenerator, obtido {type(gen)}"
        )

    def test_generator_has_get_model_name(self):
        gen = _make_generator("flash")
        assert hasattr(gen, "get_model_name")
        assert callable(gen.get_model_name)


# ─── _load_dataset ───────────────────────────────────────────────────────────

class TestLoadDataset:
    """
    Cenário: Dataset CSV é carregado com colunas title, description e storypoints
    Cenário: Dataset aceita variações de nome de coluna (case-insensitive)
    """

    def _write_csv(self, tmp_path, rows: list, fieldnames: list) -> Path:
        p = tmp_path / "dataset.csv"
        with open(p, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        return p

    def test_loads_title_description_storypoints(self, tmp_path):
        p = self._write_csv(tmp_path, [
            {"title": "Story A", "description": "Desc A", "storypoints": "3"},
        ], ["title", "description", "storypoints"])
        issues = _load_dataset(str(p))
        assert len(issues) == 1
        assert issues[0]["title"] == "Story A"
        assert issues[0]["description"] == "Desc A"
        assert issues[0]["storypoints"] == "3"

    def test_skips_rows_without_title(self, tmp_path):
        p = self._write_csv(tmp_path, [
            {"title": "Story A", "description": "Desc", "storypoints": "3"},
            {"title": "",        "description": "Sem título", "storypoints": "1"},
            {"title": "Story B", "description": "Desc B", "storypoints": "2"},
        ], ["title", "description", "storypoints"])
        issues = _load_dataset(str(p))
        assert len(issues) == 2
        assert all(i["title"] != "" for i in issues)

    def test_accepts_uppercase_title_column(self, tmp_path):
        p = self._write_csv(tmp_path, [
            {"Title": "Story X", "Description": "Desc X", "storypoints": "5"},
        ], ["Title", "Description", "storypoints"])
        issues = _load_dataset(str(p))
        assert len(issues) == 1
        assert issues[0]["title"] == "Story X"

    def test_accepts_uppercase_description_column(self, tmp_path):
        p = self._write_csv(tmp_path, [
            {"title": "Story Y", "Description": "Desc Upper", "storypoints": "2"},
        ], ["title", "Description", "storypoints"])
        issues = _load_dataset(str(p))
        assert issues[0]["description"] == "Desc Upper"

    def test_missing_description_defaults_to_empty_string(self, tmp_path):
        p = self._write_csv(tmp_path, [
            {"title": "Só título", "storypoints": "1"},
        ], ["title", "storypoints"])
        issues = _load_dataset(str(p))
        assert issues[0]["description"] == ""

    def test_missing_storypoints_defaults_to_na(self, tmp_path):
        p = self._write_csv(tmp_path, [
            {"title": "Story", "description": "Desc"},
        ], ["title", "description"])
        issues = _load_dataset(str(p))
        assert issues[0]["storypoints"] == "N/A"

    def test_multiple_rows_all_loaded(self, tmp_path):
        rows = [
            {"title": f"Story {i}", "description": f"Desc {i}", "storypoints": str(i)}
            for i in range(5)
        ]
        p = self._write_csv(tmp_path, rows, ["title", "description", "storypoints"])
        issues = _load_dataset(str(p))
        assert len(issues) == 5

    def test_file_not_found_raises_exit(self, tmp_path):
        import typer
        with pytest.raises((SystemExit, typer.Exit)):
            _load_dataset(str(tmp_path / "nao_existe.csv"))

    def test_real_neodataset_loads(self):
        """Verifica que o neodataset.csv real pode ser carregado."""
        neo = Path(__file__).parent.parent / "neodataset.csv"
        if not neo.exists():
            pytest.skip("neodataset.csv não encontrado")
        issues = _load_dataset(str(neo))
        assert len(issues) > 0
        assert all("title" in i for i in issues)

    def test_strips_whitespace_from_title(self, tmp_path):
        p = self._write_csv(tmp_path, [
            {"title": "  Story com espaços  ", "description": "", "storypoints": "1"},
        ], ["title", "description", "storypoints"])
        issues = _load_dataset(str(p))
        assert issues[0]["title"] == "Story com espaços"
