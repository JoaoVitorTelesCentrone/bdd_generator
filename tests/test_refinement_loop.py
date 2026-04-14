"""
TDD — RefinementLoop behavior.

Gherkin mapeado:
  - "Primeira tentativa usa prompt de geração inicial"
  - "Tentativas subsequentes usam prompt de refinamento com fraquezas"
  - "Loop preserva o melhor BDD entre tentativas"
  - "Geração com --until-converged respeita o teto de 50 tentativas"
  - "Geração com --until-converged converge antes do teto"
  - "Tokens de geração são rastreados corretamente no resultado"
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from unittest.mock import MagicMock, call, patch

from src.generators.base import GenerationResult
from src.evaluators.scorer import BDDScorer, ScoreResult
from src.refinement.loop import RefinementLoop, RefinementResult


# ─── helpers ────────────────────────────────────────────────────────────────

BDD_TEMPLATE = """
Funcionalidade: Login
  Cenário: {label}
    Dado que estou na página de login
    Quando preencho o campo de email com "user@email.com"
    Então devo ver "Dashboard"
"""


def _gen_result(bdd_label="ok", input_tokens=100, output_tokens=50) -> GenerationResult:
    return GenerationResult(
        success=True,
        bdd_text=BDD_TEMPLATE.format(label=bdd_label),
        model="mock",
        input_tokens=input_tokens,
        output_tokens=output_tokens,
    )


def _score_result(score_final: float, threshold: float = 7.0) -> ScoreResult:
    return ScoreResult(
        cobertura=score_final,
        clareza=score_final,
        estrutura=score_final,
        executabilidade=score_final,
        score_final=score_final,
        aprovado=score_final >= threshold,
        threshold=threshold,
    )


def _make_loop(
    gen_results: list,
    score_results: list,
    max_attempts: int = 5,
    threshold: float = 7.0,
    verbose: bool = False,
    researcher=None,
) -> RefinementLoop:
    generator = MagicMock()
    generator.generate.side_effect = gen_results
    generator.get_model_name.return_value = "mock-model"

    scorer = MagicMock(spec=BDDScorer)
    scorer.threshold = threshold
    scorer.score.side_effect = score_results

    return RefinementLoop(
        generator=generator,
        scorer=scorer,
        max_attempts=max_attempts,
        logger=None,
        verbose=verbose,
        researcher=researcher,
    )


# ─── prompt selection ────────────────────────────────────────────────────────

class TestPromptSelection:
    """
    Cenário: Primeira tentativa usa prompt de geração inicial
    Cenário: Tentativas subsequentes usam prompt de refinamento com fraquezas
    """

    def test_first_attempt_uses_generate_prompt(self):
        loop = _make_loop(
            gen_results=[_gen_result()],
            score_results=[_score_result(8.0)],  # aprovado na 1ª tentativa
            max_attempts=1,
        )
        with patch("src.refinement.loop.PromptTemplates.generate_bdd") as mock_gen, \
             patch("src.refinement.loop.PromptTemplates.refine_bdd") as mock_ref:
            mock_gen.return_value = "generate_prompt"
            loop.generator.generate.side_effect = [_gen_result()]
            loop.scorer.score.side_effect = [_score_result(8.0)]
            loop.run("Login com email e senha")
            mock_gen.assert_called_once()
            mock_ref.assert_not_called()

    def test_second_attempt_uses_refine_prompt(self):
        loop = _make_loop(
            gen_results=[_gen_result("attempt1"), _gen_result("attempt2")],
            score_results=[_score_result(5.0), _score_result(8.0)],
            max_attempts=2,
        )
        with patch("src.refinement.loop.PromptTemplates.generate_bdd") as mock_gen, \
             patch("src.refinement.loop.PromptTemplates.refine_bdd") as mock_ref:
            mock_gen.return_value = "generate_prompt"
            mock_ref.return_value = "refine_prompt"
            loop.generator.generate.side_effect = [_gen_result("attempt1"), _gen_result("attempt2")]
            loop.scorer.score.side_effect = [_score_result(5.0), _score_result(8.0)]
            loop.run("Cadastro de usuário")
            mock_gen.assert_called_once()
            mock_ref.assert_called_once()

    def test_refine_prompt_receives_weaknesses(self):
        low_score = _score_result(4.0)
        loop = _make_loop(
            gen_results=[_gen_result(), _gen_result()],
            score_results=[low_score, _score_result(8.0)],
            max_attempts=2,
        )
        with patch("src.refinement.loop.PromptTemplates.generate_bdd", return_value="gp"), \
             patch("src.refinement.loop.PromptTemplates.refine_bdd") as mock_ref:
            mock_ref.return_value = "rp"
            loop.generator.generate.side_effect = [_gen_result(), _gen_result()]
            loop.scorer.score.side_effect = [low_score, _score_result(8.0)]
            loop.run("Story")
            _, kwargs = mock_ref.call_args
            assert "weaknesses" in kwargs or len(mock_ref.call_args[0]) >= 4


# ─── best BDD preservation ───────────────────────────────────────────────────

class TestBestBDDPreservation:
    """
    Cenário: Loop preserva o melhor BDD entre tentativas
      scores: 6.5, 7.2, 6.8 → retorna BDD da tentativa com 7.2
    """

    def test_returns_bdd_with_highest_score(self):
        bdd_a = _gen_result("attempt-A", input_tokens=10, output_tokens=5)
        bdd_b = _gen_result("attempt-B", input_tokens=10, output_tokens=5)
        bdd_c = _gen_result("attempt-C", input_tokens=10, output_tokens=5)

        loop = _make_loop(
            gen_results=[bdd_a, bdd_b, bdd_c],
            score_results=[_score_result(6.5), _score_result(7.2), _score_result(6.8)],
            max_attempts=3,
            threshold=8.0,  # nenhum vai aprovar
        )
        result = loop.run("Story sem aprovação")
        assert "attempt-B" in result.bdd_text, (
            "Deveria retornar o BDD da tentativa com score 7.2 (attempt-B)"
        )

    def test_converged_false_when_threshold_never_reached(self):
        loop = _make_loop(
            gen_results=[_gen_result(), _gen_result(), _gen_result()],
            score_results=[_score_result(5.0), _score_result(6.0), _score_result(6.5)],
            max_attempts=3,
            threshold=8.0,
        )
        result = loop.run("Story")
        assert result.converged is False

    def test_converged_true_on_first_approval(self):
        loop = _make_loop(
            gen_results=[_gen_result(), _gen_result()],
            score_results=[_score_result(8.0), _score_result(9.0)],
            max_attempts=5,
            threshold=7.0,
        )
        result = loop.run("Story")
        assert result.converged is True
        assert result.attempts == 1  # parou na 1ª tentativa aprovada

    def test_returns_non_empty_bdd_even_on_failure(self):
        loop = _make_loop(
            gen_results=[_gen_result("fallback")],
            score_results=[_score_result(3.0)],
            max_attempts=1,
            threshold=8.0,
        )
        result = loop.run("Story")
        assert result.bdd_text != ""


# ─── until_converged ceiling ─────────────────────────────────────────────────

class TestUntilConverged:
    """
    Cenário: Geração com --until-converged respeita o teto de 50 tentativas
    """

    def test_until_converged_ceiling_50(self):
        # Nunca aprova — deve parar em 50
        gen_results = [_gen_result(f"a{i}") for i in range(55)]
        score_results = [_score_result(3.0) for _ in range(55)]

        loop = _make_loop(gen_results=gen_results, score_results=score_results,
                          max_attempts=5, threshold=7.0)
        result = loop.run("Story que nunca converge", until_converged=True)
        assert result.attempts == 50
        assert result.converged is False

    def test_until_converged_stops_early_on_approval(self):
        # Aprova na tentativa 3
        gen_results = [_gen_result(f"a{i}") for i in range(10)]
        score_results = [_score_result(4.0), _score_result(5.0), _score_result(8.0)]

        loop = _make_loop(gen_results=gen_results, score_results=score_results,
                          max_attempts=5, threshold=7.0)
        result = loop.run("Story que converge cedo", until_converged=True)
        assert result.attempts == 3
        assert result.converged is True

    def test_max_attempts_respected_without_until_converged(self):
        gen_results = [_gen_result(f"a{i}") for i in range(10)]
        score_results = [_score_result(3.0) for _ in range(10)]

        loop = _make_loop(gen_results=gen_results, score_results=score_results,
                          max_attempts=3, threshold=7.0)
        result = loop.run("Story")
        assert result.attempts == 3


# ─── token tracking ──────────────────────────────────────────────────────────

class TestTokenTracking:
    """
    Cenário: Tokens de geração são rastreados corretamente no resultado
    """

    def test_total_tokens_sum_of_all_attempts(self):
        gen1 = GenerationResult(success=True, bdd_text="BDD1", model="m",
                                input_tokens=100, output_tokens=50)
        gen2 = GenerationResult(success=True, bdd_text="BDD2", model="m",
                                input_tokens=120, output_tokens=60)

        loop = _make_loop(
            gen_results=[gen1, gen2],
            score_results=[_score_result(5.0), _score_result(8.0)],
            max_attempts=2,
        )
        result = loop.run("Story")
        assert result.total_input_tokens == 100 + 120
        assert result.total_output_tokens == 50 + 60
        assert result.total_tokens == 330

    def test_total_tokens_property(self):
        r = RefinementResult(
            bdd_text="x",
            score=_score_result(8.0),
            attempts=2,
            total_input_tokens=200,
            total_output_tokens=100,
            total_duration_seconds=1.5,
            converged=True,
        )
        assert r.total_tokens == 300

    def test_research_tokens_zero_without_researcher(self):
        loop = _make_loop(
            gen_results=[_gen_result()],
            score_results=[_score_result(8.0)],
            max_attempts=1,
        )
        result = loop.run("Story")
        assert result.research_tokens == 0

    def test_research_tokens_tracked_with_researcher(self):
        researcher = MagicMock()
        from src.research.auto_researcher import ResearchResult
        researcher.research.return_value = ResearchResult(
            context="## CRITÉRIOS DE ACEITAÇÃO\n- AC1",
            input_tokens=80,
            output_tokens=40,
            duration_seconds=0.5,
            success=True,
        )
        loop = _make_loop(
            gen_results=[_gen_result()],
            score_results=[_score_result(8.0)],
            max_attempts=1,
            researcher=researcher,
        )
        result = loop.run("Story", enable_research=True)
        assert result.research_tokens == 120  # 80 + 40


# ─── generation failure handling ─────────────────────────────────────────────

class TestGenerationFailure:
    def test_loop_breaks_on_generation_error(self):
        failed = GenerationResult(success=False, error="API Error", model="m")
        # O loop chama scorer.score("", ...) como fallback quando best_score is None
        fallback_score = _score_result(0.0)
        loop = _make_loop(
            gen_results=[failed],
            score_results=[fallback_score],
            max_attempts=3,
        )
        result = loop.run("Story")
        assert result.attempts == 1
        assert result.bdd_text == ""

    def test_result_has_score_even_on_empty_bdd(self):
        """Quando todos os attempts falham, score é calculado sobre string vazia."""
        failed = GenerationResult(success=False, error="err", model="m")
        scorer = BDDScorer(threshold=7.0)
        generator = MagicMock()
        generator.generate.return_value = failed
        generator.get_model_name.return_value = "mock"
        loop = RefinementLoop(generator=generator, scorer=scorer, max_attempts=1)
        result = loop.run("Story")
        assert result.score is not None
        assert 0.0 <= result.score.score_final <= 10.0
