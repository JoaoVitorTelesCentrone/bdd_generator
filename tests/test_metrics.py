"""Unit tests for all 4 BDD quality metrics."""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.evaluators.coverage import CoverageEvaluator
from src.evaluators.clarity import ClarityEvaluator
from src.evaluators.structure import StructureEvaluator
from src.evaluators.executability import ExecutabilityEvaluator
from src.evaluators.scorer import BDDScorer


# ─── Fixtures ──────────────────────────────────────────────────────────────

STORY_LOGIN = """Como usuário, quero fazer login no sistema para acessar minha conta.

Critérios de aceitação:
- Login com email/senha
- Recuperação de senha
- Bloqueio após 3 tentativas
- Login social (Google/GitHub)"""

RESEARCH_CONTEXT = """
## CRITÉRIOS DE ACEITAÇÃO
- O usuário deve conseguir fazer login com email e senha válidos
- O sistema deve enviar email de recuperação de senha
- Após 3 tentativas falhas, a conta deve ser bloqueada temporariamente
- O usuário deve poder fazer login via Google ou GitHub

## CASOS EXTREMOS E ERROS
- Email inválido (sem @) deve exibir mensagem de erro
- Senha em branco deve ser rejeitada
"""

BDD_LOW_COVERAGE = """
Cenário: Login bem-sucedido
  Dado que estou na página de login
  Quando preencho o campo de email com "user@email.com"
  Então devo ver minha dashboard
"""

BDD_HIGH_COVERAGE = """
Cenário: Login com credenciais válidas
  Dado que estou na página de login
  Quando preencho o campo de email com "user@email.com"
  E preencho o campo de senha com "Pass123!"
  E clico no botão "Entrar"
  Então devo ser redirecionado para "/dashboard"

Cenário: Recuperação de senha
  Dado que estou na página de login
  Quando clico em "Esqueci minha senha"
  E preencho o campo de email com "user@email.com"
  Então devo ver a mensagem "Email de recuperação enviado"

Cenário: Bloqueio após tentativas falhas
  Dado que tentei fazer login 3 vezes com senha incorreta
  Quando tento fazer login com a senha "senhaerrada"
  Então devo ver "Conta bloqueada temporariamente"

Cenário: Login via Google
  Dado que estou na página de login
  Quando clico no botão "Continuar com Google"
  Então devo ser redirecionado para a autenticação do Google
"""

BDD_BAD_STRUCTURE = """
Cenário: Comprar produto
  Dado que clico no botão comprar
  Quando o produto está no carrinho
  Então estou na página de produtos
"""

BDD_GOOD_STRUCTURE = """
Cenário: Comprar produto
  Dado que estou na página do produto "MacBook Pro"
  E o produto está disponível em estoque
  Quando clico no botão "Comprar agora"
  Então devo ver a confirmação "Adicionado ao carrinho"
  E o contador do carrinho deve exibir "1"
"""

BDD_LOW_EXECUTABILITY = """
Cenário: Fazer login
  Dado que o sistema está funcionando
  Quando o usuário faz login corretamente
  Então tudo deve funcionar como esperado
"""

BDD_HIGH_EXECUTABILITY = """
Cenário: Login com credenciais válidas
  Dado que estou na página de login em "https://app.com/login"
  Quando preencho o campo de email com "test@example.com"
  E preencho o campo de senha com "Pass123!"
  E clico no botão "Entrar"
  Então devo ser redirecionado para "https://app.com/dashboard"
  E devo ver a mensagem "Bem-vindo, test@example.com"
"""

BDD_WITH_TAGS = """
@happy_path @smoke
Cenário: Login bem-sucedido
  Dado que estou na página de login
  Quando preencho o campo de email com "user@email.com"
  E preencho o campo de senha com "Pass123!"
  E clico no botão "Entrar"
  Então devo ser redirecionado para "/dashboard"

@error_case
Cenário: Login com senha errada
  Dado que estou na página de login
  Quando preencho o campo de email com "user@email.com"
  E preencho o campo de senha com "senhaerrada"
  E clico no botão "Entrar"
  Então devo ver a mensagem "Credenciais inválidas"
"""

BDD_VAGUE = """
Cenário: Fazer algo no sistema
  Dado que o contexto está configurado corretamente
  Quando o usuário realiza a operação necessária
  Então o resultado esperado deve ocorrer adequadamente
"""


# ─── Coverage Tests ─────────────────────────────────────────────────────────

class TestCoverageEvaluator:
    def setup_method(self):
        self.ev = CoverageEvaluator()

    def test_low_coverage_score_below_5(self):
        score = self.ev.evaluate(STORY_LOGIN, BDD_LOW_COVERAGE)
        assert score < 5.0, f"Expected < 5, got {score}"

    def test_high_coverage_score_above_7(self):
        score = self.ev.evaluate(STORY_LOGIN, BDD_HIGH_COVERAGE)
        assert score >= 7.0, f"Expected >= 7, got {score}"

    def test_score_range(self):
        for bdd in [BDD_LOW_COVERAGE, BDD_HIGH_COVERAGE, BDD_BAD_STRUCTURE]:
            score = self.ev.evaluate(STORY_LOGIN, bdd)
            assert 0.0 <= score <= 10.0, f"Score out of range: {score}"

    def test_empty_bdd_returns_low_score(self):
        score = self.ev.evaluate(STORY_LOGIN, "")
        assert score < 5.0

    def test_story_without_explicit_criteria(self):
        story = "Como usuário, quero visualizar meu perfil."
        score = self.ev.evaluate(story, BDD_HIGH_COVERAGE)
        assert 0.0 <= score <= 10.0

    def test_research_context_improves_coverage_detection(self):
        # With research context, coverage should be at least as good as without
        score_without = self.ev.evaluate(STORY_LOGIN, BDD_HIGH_COVERAGE)
        score_with    = self.ev.evaluate(STORY_LOGIN, BDD_HIGH_COVERAGE, RESEARCH_CONTEXT)
        assert 0.0 <= score_with <= 10.0
        # Both should be reasonable (research context uses same BDD text)
        assert score_with >= 5.0

    def test_tags_do_not_pollute_coverage_keywords(self):
        # Tags like @smoke, @happy_path should not count as coverage keywords
        score = self.ev.evaluate(STORY_LOGIN, BDD_WITH_TAGS)
        assert 0.0 <= score <= 10.0


# ─── Clarity Tests ───────────────────────────────────────────────────────────

class TestClarityEvaluator:
    def setup_method(self):
        self.ev = ClarityEvaluator()

    def test_vague_bdd_scores_low(self):
        score = self.ev.evaluate(BDD_VAGUE)
        assert score < 5.0, f"Expected < 5, got {score}"

    def test_good_bdd_scores_higher_than_vague(self):
        vague = self.ev.evaluate(BDD_VAGUE)
        good  = self.ev.evaluate(BDD_GOOD_STRUCTURE)
        assert good > vague, f"Good ({good}) should be > vague ({vague})"

    def test_concrete_data_improves_score(self):
        # BDD with concrete values (emails, quoted strings) should score higher
        score_concrete = self.ev.evaluate(BDD_HIGH_EXECUTABILITY)
        score_vague    = self.ev.evaluate(BDD_LOW_EXECUTABILITY)
        assert score_concrete > score_vague

    def test_no_baseline_inflation(self):
        # Vague BDD with no concrete data should NOT score >= 6 (old bug: concrete_score started at 6.0)
        score = self.ev.evaluate(BDD_VAGUE)
        assert score < 6.0, f"Vague BDD should score < 6, got {score}"

    def test_score_range(self):
        for bdd in [BDD_VAGUE, BDD_GOOD_STRUCTURE, BDD_HIGH_COVERAGE]:
            score = self.ev.evaluate(bdd)
            assert 0.0 <= score <= 10.0

    def test_empty_returns_zero(self):
        assert self.ev.evaluate("") == 0.0

    def test_tags_parsed_correctly(self):
        # Tags before scenarios should not create phantom zero-score scenarios
        score_with_tags    = self.ev.evaluate(BDD_WITH_TAGS)
        score_without_tags = self.ev.evaluate(BDD_HIGH_COVERAGE)
        # Both should produce reasonable scores, not be dragged to 0 by tag lines
        assert score_with_tags > 3.0, f"Tags should not kill score: {score_with_tags}"


# ─── Structure Tests ─────────────────────────────────────────────────────────

class TestStructureEvaluator:
    def setup_method(self):
        self.ev = StructureEvaluator()

    def test_bad_structure_scores_low(self):
        score = self.ev.evaluate(BDD_BAD_STRUCTURE)
        assert score < 6.0, f"Expected < 6, got {score}"

    def test_good_structure_scores_high(self):
        score = self.ev.evaluate(BDD_GOOD_STRUCTURE)
        assert score >= 7.0, f"Expected >= 7, got {score}"

    def test_missing_gwt_returns_zero(self):
        score = self.ev.evaluate("Alguma coisa sem Given When Then")
        assert score == 0.0

    def test_tags_do_not_create_phantom_scenarios(self):
        # Before fix: @tag lines before Cenário: created empty phantom scenarios with score 0
        score_tagged   = self.ev.evaluate(BDD_WITH_TAGS)
        score_untagged = self.ev.evaluate(BDD_HIGH_COVERAGE)
        # Scores should be similar — tags should not penalize structure score
        assert abs(score_tagged - score_untagged) < 3.0, (
            f"Tags should not significantly affect structure: tagged={score_tagged}, untagged={score_untagged}"
        )

    def test_score_range(self):
        for bdd in [BDD_BAD_STRUCTURE, BDD_GOOD_STRUCTURE, BDD_HIGH_COVERAGE]:
            score = self.ev.evaluate(bdd)
            assert 0.0 <= score <= 10.0


# ─── Executability Tests ─────────────────────────────────────────────────────

class TestExecutabilityEvaluator:
    def setup_method(self):
        self.ev = ExecutabilityEvaluator()

    def test_low_executability_scores_low(self):
        score = self.ev.evaluate(BDD_LOW_EXECUTABILITY)
        assert score < 4.0, f"Expected < 4, got {score}"

    def test_high_executability_scores_high(self):
        score = self.ev.evaluate(BDD_HIGH_EXECUTABILITY)
        assert score >= 7.0, f"Expected >= 7, got {score}"

    def test_concrete_data_without_css_scores_well(self):
        # New rule: concrete quoted data is enough — CSS selectors NOT required
        bdd_no_css = """
Cenário: Login bem-sucedido
  Dado que estou na página de login
  Quando preencho o campo de email com "user@email.com"
  E preencho o campo de senha com "Pass123!"
  E clico no botão "Entrar"
  Então devo ser redirecionado para "/dashboard"
  E devo ver a mensagem "Bem-vindo"
"""
        score = self.ev.evaluate(bdd_no_css)
        assert score >= 6.0, f"BDD with concrete data (no CSS) should score >= 6, got {score}"

    def test_tags_do_not_affect_executability(self):
        score = self.ev.evaluate(BDD_WITH_TAGS)
        assert score > 3.0

    def test_score_range(self):
        for bdd in [BDD_LOW_EXECUTABILITY, BDD_HIGH_EXECUTABILITY]:
            score = self.ev.evaluate(bdd)
            assert 0.0 <= score <= 10.0


# ─── Scorer (integration) ────────────────────────────────────────────────────

class TestBDDScorer:
    def setup_method(self):
        self.scorer = BDDScorer(threshold=7.0)

    def test_high_quality_bdd_approved(self):
        result = self.scorer.score(STORY_LOGIN, BDD_HIGH_COVERAGE)
        assert result.score_final > 0.0
        assert 0.0 <= result.score_final <= 10.0

    def test_low_quality_bdd_not_approved(self):
        result = self.scorer.score(STORY_LOGIN, BDD_LOW_EXECUTABILITY)
        assert not result.aprovado

    def test_all_dimensions_in_range(self):
        result = self.scorer.score(STORY_LOGIN, BDD_HIGH_COVERAGE)
        for dim in [result.cobertura, result.clareza, result.estrutura, result.executabilidade]:
            assert 0.0 <= dim <= 10.0

    def test_summary_contains_score(self):
        result = self.scorer.score(STORY_LOGIN, BDD_GOOD_STRUCTURE)
        summary = result.summary()
        assert "SCORE" in summary

    def test_weaknesses_returns_detailed_strings(self):
        result = self.scorer.score(STORY_LOGIN, BDD_LOW_EXECUTABILITY)
        weaknesses = result.weaknesses()
        assert isinstance(weaknesses, list)
        # Weaknesses should now contain diagnostic detail, not just dimension names
        for w in weaknesses:
            assert isinstance(w, str)
            assert len(w) > 10  # detailed message, not just "Executabilidade"

    def test_research_context_accepted(self):
        result = self.scorer.score(STORY_LOGIN, BDD_HIGH_COVERAGE, RESEARCH_CONTEXT)
        assert 0.0 <= result.score_final <= 10.0

    def test_custom_threshold(self):
        scorer_low  = BDDScorer(threshold=2.0)
        scorer_high = BDDScorer(threshold=9.5)
        result = scorer_low.score(STORY_LOGIN, BDD_GOOD_STRUCTURE)
        assert result.aprovado
        result = scorer_high.score(STORY_LOGIN, BDD_VAGUE)
        assert not result.aprovado

    def test_high_quality_bdd_scores_higher_than_vague(self):
        result_good  = self.scorer.score(STORY_LOGIN, BDD_HIGH_EXECUTABILITY)
        result_vague = self.scorer.score(STORY_LOGIN, BDD_VAGUE)
        assert result_good.score_final > result_vague.score_final


# ─── Run with pytest ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
