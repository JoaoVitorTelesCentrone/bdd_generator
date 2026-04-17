"""
Tests for bist/bist_agent.py — core AI agent (user story → .feature file).

Cenários cobertos:
  - generate() cria o arquivo .feature no caminho especificado
  - generate() cria arquivo com nome automático quando output_path é None
  - AgentResult contém score_final, attempts, total_tokens, converged, duration_seconds
  - converged=True quando o loop convergiu
  - converged=False quando o loop não convergiu
  - Arquivo .feature não é criado quando bdd_text está vazio
  - Modelo "flash" instancia GeminiGenerator; "sonnet" instancia ClaudeGenerator
  - feature_path no resultado aponta para um arquivo que existe no disco
  - O conteúdo do arquivo salvo é igual ao bdd_text do resultado
"""
import sys, os, textwrap
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import pytest
from bist.bist_agent import BISTAgent, AgentResult


# ── helpers ───────────────────────────────────────────────────────────────────

SAMPLE_BDD = textwrap.dedent("""
    Feature: Login
      Scenario: Valid login
        Given I am on the login page
        When I fill "email" with "user@test.com"
        And I fill "password" with "secret"
        Then I should see "Dashboard"
""").strip()


def _mock_refinement_result(
    bdd_text: str = SAMPLE_BDD,
    score_final: float = 8.0,
    attempts: int = 2,
    total_tokens: int = 500,
    converged: bool = True,
) -> MagicMock:
    score = MagicMock()
    score.score_final = score_final
    result = MagicMock()
    result.bdd_text = bdd_text
    result.score = score
    result.attempts = attempts
    result.total_tokens = total_tokens
    result.converged = converged
    return result


def _make_agent(**kwargs) -> BISTAgent:
    defaults = dict(model="sonnet", threshold=7.0, max_attempts=3)
    defaults.update(kwargs)
    return BISTAgent(**defaults)


# ── feature file creation ─────────────────────────────────────────────────────

class TestFeatureFileCreation:
    """Cenário: generate() cria o arquivo .feature no caminho especificado"""

    def test_file_created_at_specified_path(self, tmp_path):
        agent = _make_agent()
        output = tmp_path / "login.feature"

        with patch.object(agent, "_build_loop") as mock_build:
            loop = MagicMock()
            loop.run.return_value = _mock_refinement_result()
            mock_build.return_value = loop
            result = agent.generate("Login story", output_path=str(output))

        assert output.exists()

    def test_file_content_matches_bdd_text(self, tmp_path):
        agent = _make_agent()
        output = tmp_path / "checkout.feature"

        with patch.object(agent, "_build_loop") as mock_build:
            loop = MagicMock()
            loop.run.return_value = _mock_refinement_result(bdd_text=SAMPLE_BDD)
            mock_build.return_value = loop
            result = agent.generate("Checkout story", output_path=str(output))

        assert output.read_text(encoding="utf-8") == SAMPLE_BDD

    def test_auto_named_file_created_in_default_dir(self, tmp_path):
        agent = _make_agent()

        with patch("bist.bist_agent.Path") as MockPath, \
             patch.object(agent, "_build_loop") as mock_build:

            # Don't mock Path globally — just test that the file is created
            pass

        # Use real Path but override output dir
        original_cwd = Path.cwd()
        os.chdir(tmp_path)
        try:
            with patch.object(agent, "_build_loop") as mock_build:
                loop = MagicMock()
                loop.run.return_value = _mock_refinement_result()
                mock_build.return_value = loop
                result = agent.generate("User story without path")
            assert Path(result.feature_path).exists()
        finally:
            os.chdir(original_cwd)

    def test_no_file_created_when_bdd_empty(self, tmp_path):
        agent = _make_agent()
        output = tmp_path / "empty.feature"

        with patch.object(agent, "_build_loop") as mock_build:
            loop = MagicMock()
            loop.run.return_value = _mock_refinement_result(bdd_text="")
            mock_build.return_value = loop
            result = agent.generate("Empty story", output_path=str(output))

        assert not output.exists()


# ── AgentResult fields ────────────────────────────────────────────────────────

class TestAgentResult:
    """Cenário: AgentResult contém todos os campos esperados"""

    def _generate(self, tmp_path, **refinement_kwargs):
        agent = _make_agent()
        output = tmp_path / "out.feature"
        with patch.object(agent, "_build_loop") as mock_build:
            loop = MagicMock()
            loop.run.return_value = _mock_refinement_result(**refinement_kwargs)
            mock_build.return_value = loop
            return agent.generate("User story", output_path=str(output))

    def test_result_is_agent_result_instance(self, tmp_path):
        result = self._generate(tmp_path)
        assert isinstance(result, AgentResult)

    def test_score_final_propagated(self, tmp_path):
        result = self._generate(tmp_path, score_final=9.1)
        assert result.score_final == 9.1

    def test_attempts_propagated(self, tmp_path):
        result = self._generate(tmp_path, attempts=4)
        assert result.attempts == 4

    def test_total_tokens_propagated(self, tmp_path):
        result = self._generate(tmp_path, total_tokens=1234)
        assert result.total_tokens == 1234

    def test_bdd_text_propagated(self, tmp_path):
        result = self._generate(tmp_path, bdd_text=SAMPLE_BDD)
        assert result.bdd_text == SAMPLE_BDD

    def test_converged_true(self, tmp_path):
        result = self._generate(tmp_path, converged=True)
        assert result.converged is True

    def test_converged_false(self, tmp_path):
        result = self._generate(tmp_path, converged=False)
        assert result.converged is False

    def test_duration_seconds_positive(self, tmp_path):
        result = self._generate(tmp_path)
        assert result.duration_seconds >= 0

    def test_feature_path_in_result(self, tmp_path):
        output = str(tmp_path / "my.feature")
        agent = _make_agent()
        with patch.object(agent, "_build_loop") as mock_build:
            loop = MagicMock()
            loop.run.return_value = _mock_refinement_result()
            mock_build.return_value = loop
            result = agent.generate("Story", output_path=output)
        assert result.feature_path == output


# ── model selection ───────────────────────────────────────────────────────────

class TestModelSelection:
    """Cenário: Modelo 'flash' instancia GeminiGenerator; 'sonnet' instancia ClaudeGenerator"""

    @pytest.mark.parametrize("model", ["flash", "pro", "flash-lite", "gemini-2.0-flash"])
    def test_gemini_models_use_gemini_generator(self, model, tmp_path):
        agent = _make_agent(model=model)
        root = Path(__file__).parent.parent.parent

        with patch("bist.bist_agent.GeminiGenerator") as MockGemini, \
             patch("bist.bist_agent.ClaudeGenerator") as MockClaude, \
             patch("bist.bist_agent.RefinementLoop") as MockLoop:

            mock_loop_instance = MagicMock()
            mock_loop_instance.run.return_value = _mock_refinement_result()
            MockLoop.return_value = mock_loop_instance

            MockGemini.return_value = MagicMock()
            MockClaude.return_value = MagicMock()

            agent.generate("story", output_path=str(tmp_path / "x.feature"))

            MockGemini.assert_called_once()
            MockClaude.assert_not_called()

    @pytest.mark.parametrize("model", ["sonnet", "opus", "haiku"])
    def test_claude_models_use_claude_generator(self, model, tmp_path):
        agent = _make_agent(model=model)

        with patch("bist.bist_agent.GeminiGenerator") as MockGemini, \
             patch("bist.bist_agent.ClaudeGenerator") as MockClaude, \
             patch("bist.bist_agent.RefinementLoop") as MockLoop:

            mock_loop_instance = MagicMock()
            mock_loop_instance.run.return_value = _mock_refinement_result()
            MockLoop.return_value = mock_loop_instance

            MockClaude.return_value = MagicMock()
            MockGemini.return_value = MagicMock()

            agent.generate("story", output_path=str(tmp_path / "x.feature"))

            MockClaude.assert_called_once()
            MockGemini.assert_not_called()


# ── loop configuration ────────────────────────────────────────────────────────

class TestLoopConfiguration:
    """Cenário: BISTAgent passa threshold e max_attempts corretos para o loop"""

    def test_threshold_passed_to_scorer(self, tmp_path):
        agent = _make_agent(threshold=8.5)

        with patch("bist.bist_agent.BDDScorer") as MockScorer, \
             patch("bist.bist_agent.ClaudeGenerator"), \
             patch("bist.bist_agent.RefinementLoop") as MockLoop:

            mock_loop_instance = MagicMock()
            mock_loop_instance.run.return_value = _mock_refinement_result()
            MockLoop.return_value = mock_loop_instance
            MockScorer.return_value = MagicMock()

            agent.generate("story", output_path=str(tmp_path / "x.feature"))
            MockScorer.assert_called_once_with(threshold=8.5)

    def test_max_attempts_passed_to_loop(self, tmp_path):
        agent = _make_agent(max_attempts=7)

        with patch("bist.bist_agent.ClaudeGenerator"), \
             patch("bist.bist_agent.BDDScorer"), \
             patch("bist.bist_agent.AttemptLogger"), \
             patch("bist.bist_agent.RefinementLoop") as MockLoop:

            mock_loop_instance = MagicMock()
            mock_loop_instance.run.return_value = _mock_refinement_result()
            MockLoop.return_value = mock_loop_instance

            agent.generate("story", output_path=str(tmp_path / "x.feature"))
            kwargs = MockLoop.call_args[1]
            assert kwargs.get("max_attempts") == 7

    def test_researcher_created_when_research_enabled(self, tmp_path):
        agent = _make_agent(enable_research=True)

        with patch("bist.bist_agent.ClaudeGenerator"), \
             patch("bist.bist_agent.BDDScorer"), \
             patch("bist.bist_agent.AttemptLogger"), \
             patch("bist.bist_agent.AutoResearcher") as MockResearcher, \
             patch("bist.bist_agent.RefinementLoop") as MockLoop:

            mock_loop_instance = MagicMock()
            mock_loop_instance.run.return_value = _mock_refinement_result()
            MockLoop.return_value = mock_loop_instance
            MockResearcher.return_value = MagicMock()

            agent.generate("story", output_path=str(tmp_path / "x.feature"))
            MockResearcher.assert_called_once()

    def test_researcher_not_created_when_research_disabled(self, tmp_path):
        agent = _make_agent(enable_research=False)

        with patch("bist.bist_agent.ClaudeGenerator"), \
             patch("bist.bist_agent.BDDScorer"), \
             patch("bist.bist_agent.AttemptLogger"), \
             patch("bist.bist_agent.AutoResearcher") as MockResearcher, \
             patch("bist.bist_agent.RefinementLoop") as MockLoop:

            mock_loop_instance = MagicMock()
            mock_loop_instance.run.return_value = _mock_refinement_result()
            MockLoop.return_value = mock_loop_instance

            agent.generate("story", output_path=str(tmp_path / "x.feature"))
            MockResearcher.assert_not_called()
