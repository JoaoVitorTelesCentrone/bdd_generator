"""
TDD — PromptTemplates: geração, refinamento, research, study e build_context.

Gherkin mapeado:
  - "Primeira tentativa usa prompt de geração inicial" (conteúdo do prompt)
  - "Tentativas subsequentes usam prompt de refinamento com fraquezas"
  - "Pesquisa de user story extrai critérios de aceitação, regras e edge cases"
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from src.utils.prompts import PromptTemplates


STORY = "Como usuário quero fazer login para acessar minha conta."
PREVIOUS_BDD = """
Cenário: Login vago
  Dado que o sistema funciona
  Quando o usuário faz login
  Então funciona
"""
SCORE_SUMMARY = """
======================================
  SCORE FINAL: 4.5/10  [REPROVADO]
======================================
"""
WEAKNESSES = [
    "Clareza (3.0/10): Use dados concretos",
    "Executabilidade (2.0/10): Adicione verbos de ação",
]


# ─── generate_bdd ────────────────────────────────────────────────────────────

class TestGenerateBddPrompt:
    def test_contains_user_story(self):
        prompt = PromptTemplates.generate_bdd(STORY)
        assert STORY in prompt

    def test_contains_gwt_instructions(self):
        prompt = PromptTemplates.generate_bdd(STORY)
        assert "DADO" in prompt.upper() or "Dado" in prompt
        assert "QUANDO" in prompt.upper() or "Quando" in prompt
        assert "ENTÃO" in prompt.upper() or "Então" in prompt

    def test_contains_coverage_instructions(self):
        prompt = PromptTemplates.generate_bdd(STORY)
        # deve orientar sobre cobertura/cenários
        assert "cenário" in prompt.lower() or "cobertura" in prompt.lower()

    def test_no_context_block_when_none(self):
        prompt = PromptTemplates.generate_bdd(STORY, context=None)
        # sem contexto → sem bloco extra
        assert "GUIA DE ESTILO" not in prompt
        assert "EXEMPLOS DE REFERÊNCIA" not in prompt

    def test_context_injected_when_provided(self):
        ctx = "Contexto adicional de negócio"
        prompt = PromptTemplates.generate_bdd(STORY, context=ctx)
        assert ctx in prompt

    def test_instructs_to_return_only_gherkin(self):
        prompt = PromptTemplates.generate_bdd(STORY)
        # deve pedir para retornar APENAS os cenários
        assert "APENAS" in prompt or "apenas" in prompt


# ─── refine_bdd ──────────────────────────────────────────────────────────────

class TestRefineBddPrompt:
    def test_contains_user_story(self):
        prompt = PromptTemplates.refine_bdd(STORY, PREVIOUS_BDD, SCORE_SUMMARY, WEAKNESSES)
        assert STORY in prompt

    def test_contains_previous_bdd(self):
        prompt = PromptTemplates.refine_bdd(STORY, PREVIOUS_BDD, SCORE_SUMMARY, WEAKNESSES)
        assert "Login vago" in prompt  # texto do BDD anterior

    def test_contains_score_summary(self):
        prompt = PromptTemplates.refine_bdd(STORY, PREVIOUS_BDD, SCORE_SUMMARY, WEAKNESSES)
        assert "REPROVADO" in prompt or "4.5" in prompt

    def test_contains_each_weakness(self):
        prompt = PromptTemplates.refine_bdd(STORY, PREVIOUS_BDD, SCORE_SUMMARY, WEAKNESSES)
        for weakness in WEAKNESSES:
            assert weakness in prompt or weakness.split(":")[0] in prompt

    def test_instructs_not_to_remove_good_scenarios(self):
        prompt = PromptTemplates.refine_bdd(STORY, PREVIOUS_BDD, SCORE_SUMMARY, WEAKNESSES)
        lower = prompt.lower()
        assert "não remova" in lower or "nao remova" in lower or "não retire" in lower

    def test_empty_weaknesses_list(self):
        # deve funcionar sem erros com lista vazia
        prompt = PromptTemplates.refine_bdd(STORY, PREVIOUS_BDD, SCORE_SUMMARY, [])
        assert STORY in prompt

    def test_instructs_to_return_only_gherkin(self):
        prompt = PromptTemplates.refine_bdd(STORY, PREVIOUS_BDD, SCORE_SUMMARY, WEAKNESSES)
        assert "APENAS" in prompt or "apenas" in prompt


# ─── research_story ──────────────────────────────────────────────────────────

class TestResearchStoryPrompt:
    def test_contains_user_story(self):
        prompt = PromptTemplates.research_story(STORY)
        assert STORY in prompt

    def test_contains_criterios_section(self):
        prompt = PromptTemplates.research_story(STORY)
        assert "CRITÉRIOS DE ACEITAÇÃO" in prompt

    def test_contains_regras_section(self):
        prompt = PromptTemplates.research_story(STORY)
        assert "REGRAS DE NEGÓCIO" in prompt

    def test_contains_casos_extremos_section(self):
        prompt = PromptTemplates.research_story(STORY)
        assert "CASOS EXTREMOS" in prompt

    def test_contains_dados_de_teste_section(self):
        prompt = PromptTemplates.research_story(STORY)
        assert "DADOS DE TESTE" in prompt

    def test_instructs_not_to_generate_gherkin(self):
        prompt = PromptTemplates.research_story(STORY)
        lower = prompt.lower()
        assert "não gere" in lower or "apenas a análise" in lower

    def test_asks_for_structured_analysis(self):
        prompt = PromptTemplates.research_story(STORY)
        # deve pedir análise estruturada, não cenários
        assert "análise" in prompt.lower()


# ─── study_results ───────────────────────────────────────────────────────────

class TestStudyResultsPrompt:
    def _make_examples(self, n=2) -> list:
        return [
            {
                "title": f"Story {i}",
                "score": 8.0 + i * 0.5,
                "cobertura": 8.0, "clareza": 8.0,
                "estrutura": 8.0, "executabilidade": 8.0,
                "bdd": f"Cenário: Exemplo {i}\n  Dado que algo\n  Quando ação\n  Então resultado",
            }
            for i in range(n)
        ]

    def test_contains_top_examples_block(self):
        top = self._make_examples(2)
        prompt = PromptTemplates.study_results(top, [])
        assert "MELHORES" in prompt or "alta qualidade" in prompt.lower()

    def test_contains_low_examples_block_when_provided(self):
        top = self._make_examples(2)
        low = self._make_examples(1)
        prompt = PromptTemplates.study_results(top, low)
        assert "PIORES" in prompt or "anti-padrão" in prompt.lower() or "baixa qualidade" in prompt.lower()

    def test_contains_analysis_sections(self):
        prompt = PromptTemplates.study_results(self._make_examples(), [])
        assert "PADRÕES" in prompt or "padrões" in prompt.lower()

    def test_empty_examples_no_crash(self):
        prompt = PromptTemplates.study_results([], [])
        assert isinstance(prompt, str)
        assert len(prompt) > 0


# ─── build_context ───────────────────────────────────────────────────────────

class TestBuildContextPrompt:
    def test_empty_list_returns_empty_string(self):
        assert PromptTemplates.build_context([]) == ""

    def test_contains_issue_title(self):
        issues = [{"title": "Cadastrar cliente", "description": "Desc"}]
        ctx = PromptTemplates.build_context(issues)
        assert "Cadastrar cliente" in ctx

    def test_contains_description_snippet(self):
        issues = [{"title": "Título", "description": "Descrição longa do problema"}]
        ctx = PromptTemplates.build_context(issues)
        assert "Descrição longa" in ctx

    def test_multiple_issues_all_present(self):
        issues = [
            {"title": "Story A", "description": "Desc A"},
            {"title": "Story B", "description": "Desc B"},
        ]
        ctx = PromptTemplates.build_context(issues)
        assert "Story A" in ctx
        assert "Story B" in ctx
