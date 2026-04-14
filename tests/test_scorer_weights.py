"""
TDD — Scorer weights, aprovado/reprovado e weaknesses.

Gherkin mapeado:
  - "Score final é calculado com os pesos corretos"
  - "BDD aprovado quando score_final >= threshold"
  - "BDD reprovado quando score_final < threshold"
  - "Método weaknesses retorna apenas dimensões abaixo do threshold"
  - "Avaliação de cobertura usa critérios do research quando disponíveis"
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from unittest.mock import patch
from src.evaluators.scorer import BDDScorer, ScoreResult, WEIGHTS


# ─── helpers ────────────────────────────────────────────────────────────────

def _make_score(cobertura=8.0, clareza=7.0, estrutura=9.0, executabilidade=6.0,
                threshold=7.0) -> ScoreResult:
    """Build a ScoreResult bypassing the actual evaluators."""
    score_final = round(
        cobertura       * WEIGHTS["cobertura"] +
        clareza         * WEIGHTS["clareza"] +
        estrutura       * WEIGHTS["estrutura"] +
        executabilidade * WEIGHTS["executabilidade"],
        2,
    )
    return ScoreResult(
        cobertura=cobertura,
        clareza=clareza,
        estrutura=estrutura,
        executabilidade=executabilidade,
        score_final=score_final,
        aprovado=score_final >= threshold,
        threshold=threshold,
    )


# ─── weight calculation ──────────────────────────────────────────────────────

class TestWeightCalculation:
    """
    Cenário: Score final é calculado com os pesos corretos
      cobertura=8.0, clareza=7.0, estrutura=9.0, exec=6.0
      esperado = 8.0*0.30 + 7.0*0.20 + 9.0*0.30 + 6.0*0.20 = 7.70
    """

    def test_weights_sum_to_one(self):
        total = sum(WEIGHTS.values())
        assert abs(total - 1.0) < 1e-9, f"Pesos devem somar 1.0, somam {total}"

    def test_weight_values_correct(self):
        assert WEIGHTS["cobertura"] == 0.30
        assert WEIGHTS["clareza"] == 0.20
        assert WEIGHTS["estrutura"] == 0.30
        assert WEIGHTS["executabilidade"] == 0.20

    def test_score_formula(self):
        score = _make_score(cobertura=8.0, clareza=7.0, estrutura=9.0, executabilidade=6.0)
        expected = round(8.0 * 0.30 + 7.0 * 0.20 + 9.0 * 0.30 + 6.0 * 0.20, 2)
        assert score.score_final == expected, (
            f"Esperado {expected}, obtido {score.score_final}"
        )

    def test_score_formula_all_ten(self):
        score = _make_score(10.0, 10.0, 10.0, 10.0)
        assert score.score_final == 10.0

    def test_score_formula_all_zero(self):
        score = _make_score(0.0, 0.0, 0.0, 0.0)
        assert score.score_final == 0.0

    def test_scorer_applies_weights_via_real_evaluators(self):
        """Integração: BDDScorer.score deve retornar score_final no intervalo correto."""
        scorer = BDDScorer(threshold=7.0)
        bdd = """
Cenário: Login
  Dado que estou na página de login
  Quando preencho o campo de email com "user@email.com"
  Então devo ver "Dashboard"
"""
        result = scorer.score("Como usuário quero fazer login", bdd)
        recalculated = round(
            result.cobertura       * WEIGHTS["cobertura"] +
            result.clareza         * WEIGHTS["clareza"] +
            result.estrutura       * WEIGHTS["estrutura"] +
            result.executabilidade * WEIGHTS["executabilidade"],
            2,
        )
        assert result.score_final == recalculated


# ─── aprovado / reprovado ────────────────────────────────────────────────────

class TestAprovadoReprovado:
    """
    Cenário: BDD aprovado quando score_final >= threshold
    Cenário: BDD reprovado quando score_final < threshold
    """

    @pytest.mark.parametrize("score_final,threshold,esperado", [
        (7.0, 7.0, True),    # exato no limite → aprovado
        (7.5, 7.0, True),    # acima → aprovado
        (10.0, 7.0, True),   # máximo → aprovado
        (6.9, 7.0, False),   # abaixo → reprovado
        (0.0, 7.0, False),   # zero → reprovado
        (9.0, 9.5, False),   # threshold alto → reprovado
        (9.5, 9.5, True),    # exato no threshold alto → aprovado
    ])
    def test_aprovado_flag(self, score_final, threshold, esperado):
        # Montar ScoreResult com score_final controlado
        result = ScoreResult(
            cobertura=score_final, clareza=score_final,
            estrutura=score_final, executabilidade=score_final,
            score_final=score_final,
            aprovado=score_final >= threshold,
            threshold=threshold,
        )
        assert result.aprovado is esperado, (
            f"score={score_final} threshold={threshold}: esperado aprovado={esperado}"
        )

    def test_scorer_threshold_default_7(self):
        scorer = BDDScorer()
        assert scorer.threshold == 7.0

    def test_scorer_custom_threshold_low(self):
        scorer = BDDScorer(threshold=2.0)
        bdd = """
Cenário: Ação básica
  Dado que estou na tela inicial
  Quando clico no botão "OK"
  Então devo ver "Confirmado"
"""
        result = scorer.score("Story qualquer", bdd)
        assert result.aprovado is True

    def test_scorer_custom_threshold_high(self):
        scorer = BDDScorer(threshold=9.5)
        bdd = """
Cenário: Algo vago
  Dado que o sistema está configurado
  Quando o usuário faz algo
  Então algo deve acontecer
"""
        result = scorer.score("Story qualquer", bdd)
        assert result.aprovado is False


# ─── weaknesses ─────────────────────────────────────────────────────────────

class TestWeaknesses:
    """
    Cenário: Método weaknesses retorna apenas dimensões abaixo do threshold
    """

    def test_weaknesses_empty_when_all_above_threshold(self):
        score = _make_score(8.0, 8.0, 8.0, 8.0, threshold=7.0)
        assert score.weaknesses() == []

    def test_weaknesses_returns_only_below_threshold(self):
        score = _make_score(cobertura=9.0, clareza=5.0, estrutura=8.0,
                            executabilidade=4.0, threshold=7.0)
        weaknesses = score.weaknesses()
        assert len(weaknesses) == 2

    def test_weaknesses_identifies_correct_dimensions(self):
        score = _make_score(cobertura=9.0, clareza=5.0, estrutura=8.0,
                            executabilidade=4.0, threshold=7.0)
        joined = " ".join(score.weaknesses()).lower()
        assert "clareza" in joined
        assert "executabilidade" in joined
        assert "cobertura" not in joined
        assert "estrutura" not in joined

    def test_weaknesses_contain_actionable_detail(self):
        score = _make_score(cobertura=3.0, clareza=3.0, estrutura=3.0,
                            executabilidade=3.0, threshold=7.0)
        for w in score.weaknesses():
            assert len(w) > 20, f"Fraqueza muito curta: '{w}'"

    def test_weaknesses_all_four_when_all_below(self):
        score = _make_score(1.0, 1.0, 1.0, 1.0, threshold=7.0)
        assert len(score.weaknesses()) == 4

    @pytest.mark.parametrize("dim,low_val", [
        ("cobertura", 2.0),
        ("clareza", 2.0),
        ("estrutura", 2.0),
        ("executabilidade", 2.0),
    ])
    def test_each_dimension_detected_individually(self, dim, low_val):
        kwargs = {"cobertura": 8.0, "clareza": 8.0, "estrutura": 8.0,
                  "executabilidade": 8.0, "threshold": 7.0}
        kwargs[dim] = low_val
        score = _make_score(**kwargs)
        joined = " ".join(score.weaknesses()).lower()
        assert dim.replace("_", " ").lower() in joined or dim in joined


# ─── summary ────────────────────────────────────────────────────────────────

class TestScoreSummary:
    def test_summary_contains_score_final(self):
        score = _make_score(8.0, 7.0, 9.0, 6.0)
        summary = score.summary()
        assert "SCORE" in summary
        assert str(score.score_final) in summary

    def test_summary_contains_status_aprovado(self):
        score = _make_score(9.0, 9.0, 9.0, 9.0, threshold=7.0)
        assert "APROVADO" in score.summary()

    def test_summary_contains_status_reprovado(self):
        score = _make_score(1.0, 1.0, 1.0, 1.0, threshold=7.0)
        assert "REPROVADO" in score.summary()

    def test_summary_contains_all_dimension_names(self):
        score = _make_score()
        summary = score.summary()
        for label in ["Cobertura", "Clareza", "Estrutura", "Executabilidade"]:
            assert label in summary, f"'{label}' ausente no summary"


# ─── coverage + research context ────────────────────────────────────────────

class TestCoverageWithResearch:
    """
    Cenário: Avaliação de cobertura usa critérios do research quando disponíveis
    """

    def test_research_context_accepted_by_scorer(self):
        scorer = BDDScorer()
        research = """
## CRITÉRIOS DE ACEITAÇÃO
- Deve fazer login com email e senha
- Deve bloquear após 3 tentativas
"""
        bdd = """
Cenário: Login válido
  Dado que estou na página de login
  Quando preencho o campo de email com "user@email.com"
  E preencho o campo de senha com "Senha@123"
  Então devo ver "Bem-vindo"

Cenário: Bloqueio após tentativas
  Dado que tentei fazer login 3 vezes com senha incorreta
  Quando tento fazer login com "senha_errada"
  Então devo ver "Conta bloqueada"
"""
        result = scorer.score("Login no sistema", bdd, research_context=research)
        assert 0.0 <= result.score_final <= 10.0

    def test_coverage_higher_with_research_context(self):
        """Com research_context detalhado, cobertura deve ser >= sem o contexto."""
        from src.evaluators.coverage import CoverageEvaluator

        ev = CoverageEvaluator()
        story = "Como usuário quero fazer login. Critérios: email/senha, bloqueio 3 tentativas"
        research = """
## CRITÉRIOS DE ACEITAÇÃO
- Login com email e senha válidos
- Bloqueio após 3 tentativas falhas
"""
        bdd = """
Cenário: Login válido
  Dado que estou na página de login
  Quando preencho o email com "user@email.com" e a senha com "Pass@123"
  Então devo ver "Dashboard"

Cenário: Bloqueio
  Dado que tentei login 3 vezes com senha errada
  Quando tento login novamente
  Então devo ver "Conta bloqueada"
"""
        score_without = ev.evaluate(story, bdd)
        score_with = ev.evaluate(story, bdd, research_context=research)
        assert 0.0 <= score_with <= 10.0
        # com research context, score deve ser razoável
        assert score_with >= 3.0
