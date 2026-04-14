"""
TDD — AutoResearcher behavior.

Gherkin mapeado:
  - "Pesquisa de user story extrai critérios de aceitação, regras e edge cases"
  - "Falha na fase de pesquisa não interrompe a geração"
  - "Tokens de research rastreados em research_tokens"
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from unittest.mock import MagicMock

from src.generators.base import GenerationResult
from src.research.auto_researcher import AutoResearcher, ResearchResult


# ─── helpers ────────────────────────────────────────────────────────────────

def _make_researcher(bdd_text="", success=True, input_tokens=80, output_tokens=40,
                     error=None) -> AutoResearcher:
    generator = MagicMock()
    generator.generate.return_value = GenerationResult(
        success=success,
        bdd_text=bdd_text,
        model="mock",
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        error=error,
    )
    return AutoResearcher(generator=generator, verbose=False)


RICH_CONTEXT = """
## CRITÉRIOS DE ACEITAÇÃO
- O usuário deve conseguir transferir valores entre contas do mesmo banco
- O saldo deve ser atualizado imediatamente após a transferência
- O sistema deve rejeitar transferências que excedam o saldo disponível

## REGRAS DE NEGÓCIO
- Limite diário de transferência: R$ 10.000,00
- Transferências acima de R$ 1.000,00 exigem autenticação extra

## CASOS EXTREMOS E ERROS
- Conta de destino inexistente
- Saldo insuficiente
- Transferência de valor zero ou negativo

## DADOS DE TESTE SUGERIDOS
- Conta origem: "001234-5", Saldo: R$ 5.000,00
- Conta destino: "006789-0"
"""


# ─── ResearchResult dataclass ─────────────────────────────────────────────

class TestResearchResultDataclass:
    def test_total_tokens_property(self):
        r = ResearchResult(
            context="ctx",
            input_tokens=100,
            output_tokens=50,
            duration_seconds=1.0,
            success=True,
        )
        assert r.total_tokens == 150

    def test_success_false_on_failure(self):
        r = ResearchResult(
            context="",
            input_tokens=0,
            output_tokens=0,
            duration_seconds=0.1,
            success=False,
        )
        assert r.success is False
        assert r.context == ""


# ─── successful research ─────────────────────────────────────────────────────

class TestAutoResearcherSuccess:
    """
    Cenário: Pesquisa de user story extrai critérios de aceitação, regras e edge cases
    """

    def test_research_returns_success_true(self):
        researcher = _make_researcher(bdd_text=RICH_CONTEXT)
        result = researcher.research("Transferência bancária")
        assert result.success is True

    def test_research_returns_non_empty_context(self):
        researcher = _make_researcher(bdd_text=RICH_CONTEXT)
        result = researcher.research("Transferência bancária")
        assert result.context != ""

    def test_research_context_contains_criterios(self):
        researcher = _make_researcher(bdd_text=RICH_CONTEXT)
        result = researcher.research("Transferência bancária")
        assert "CRITÉRIOS DE ACEITAÇÃO" in result.context

    def test_research_context_contains_regras(self):
        researcher = _make_researcher(bdd_text=RICH_CONTEXT)
        result = researcher.research("Transferência bancária")
        assert "REGRAS DE NEGÓCIO" in result.context

    def test_research_tracks_tokens(self):
        researcher = _make_researcher(bdd_text=RICH_CONTEXT, input_tokens=80, output_tokens=40)
        result = researcher.research("Qualquer story")
        assert result.input_tokens == 80
        assert result.output_tokens == 40
        assert result.total_tokens == 120

    def test_research_tracks_duration(self):
        researcher = _make_researcher(bdd_text=RICH_CONTEXT)
        result = researcher.research("Story")
        assert result.duration_seconds >= 0.0

    def test_research_calls_generator_once(self):
        generator = MagicMock()
        generator.generate.return_value = GenerationResult(
            success=True, bdd_text=RICH_CONTEXT, model="m",
            input_tokens=80, output_tokens=40,
        )
        researcher = AutoResearcher(generator=generator)
        researcher.research("Story")
        generator.generate.assert_called_once()

    def test_research_uses_system_instruction(self):
        """O research deve passar system_instruction ao generate (não a instrução BDD padrão)."""
        generator = MagicMock()
        generator.generate.return_value = GenerationResult(
            success=True, bdd_text="ctx", model="m",
            input_tokens=10, output_tokens=10,
        )
        researcher = AutoResearcher(generator=generator)
        researcher.research("Story")
        _, kwargs = generator.generate.call_args
        assert "system_instruction" in kwargs
        assert kwargs["system_instruction"] is not None
        # instrução de research deve mencionar QA, não Gherkin
        assert "QA" in kwargs["system_instruction"] or "analista" in kwargs["system_instruction"].lower()


# ─── failure handling ────────────────────────────────────────────────────────

class TestAutoResearcherFailure:
    """
    Cenário: Falha na fase de pesquisa não interrompe a geração
    """

    def test_research_failure_returns_success_false(self):
        researcher = _make_researcher(success=False, error="API timeout")
        result = researcher.research("Story")
        assert result.success is False

    def test_research_failure_returns_empty_context(self):
        researcher = _make_researcher(success=False, error="API timeout")
        result = researcher.research("Story")
        assert result.context == ""

    def test_research_failure_tokens_are_tracked(self):
        researcher = _make_researcher(success=False, error="err",
                                      input_tokens=10, output_tokens=0)
        result = researcher.research("Story")
        # mesmo com falha, os tokens enviados são rastreados
        assert result.input_tokens == 10

    def test_research_loop_integration_continues_on_failure(self):
        """
        Integração: RefinementLoop com researcher que falha deve continuar a geração.
        """
        from src.evaluators.scorer import BDDScorer, ScoreResult
        from src.refinement.loop import RefinementLoop

        # researcher que falha
        bad_generator = MagicMock()
        bad_generator.generate.return_value = GenerationResult(
            success=False, bdd_text="", model="m", error="fail"
        )
        researcher = AutoResearcher(generator=bad_generator)

        # gerador principal que funciona
        good_generator = MagicMock()
        good_generator.generate.return_value = GenerationResult(
            success=True,
            bdd_text="""
Cenário: Login
  Dado que estou na página de login
  Quando preencho o email com "u@e.com"
  Então devo ver "Dashboard"
""",
            model="m", input_tokens=100, output_tokens=50,
        )
        good_generator.get_model_name.return_value = "mock"

        scorer = BDDScorer(threshold=7.0)
        loop = RefinementLoop(
            generator=good_generator,
            scorer=scorer,
            max_attempts=1,
            researcher=researcher,
        )
        result = loop.run("Story", enable_research=True)
        # deve ter gerado BDD mesmo com research falhando
        assert result.bdd_text != ""
        assert result.research_tokens == 0  # pesquisa falhou → 0 tokens úteis


# ─── prompt used for research ────────────────────────────────────────────────

class TestResearchPrompt:
    def test_research_prompt_contains_user_story(self):
        from src.utils.prompts import PromptTemplates
        story = "Transferência bancária entre contas"
        prompt = PromptTemplates.research_story(story)
        assert story in prompt

    def test_research_prompt_contains_section_headers(self):
        from src.utils.prompts import PromptTemplates
        prompt = PromptTemplates.research_story("Qualquer story")
        assert "CRITÉRIOS DE ACEITAÇÃO" in prompt
        assert "REGRAS DE NEGÓCIO" in prompt
        assert "CASOS EXTREMOS" in prompt

    def test_research_prompt_asks_not_to_generate_gherkin(self):
        from src.utils.prompts import PromptTemplates
        prompt = PromptTemplates.research_story("Story")
        assert "Não gere" in prompt or "não gere" in prompt or "apenas a análise" in prompt
