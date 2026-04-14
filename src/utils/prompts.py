from typing import Optional


class PromptTemplates:
    """BDD generation prompt templates."""

    @staticmethod
    def generate_bdd(user_story: str, context: Optional[str] = None) -> str:
        context_block = ""
        if context:
            context_block = f"\n\n{context}\n"

        return f"""Gere uma suíte COMPLETA de cenários BDD (Gherkin) em português para a seguinte user story:

USER STORY:
{user_story}
{context_block}
REGRAS OBRIGATÓRIAS (cada regra afeta o score final — siga à risca):

1. ESTRUTURA GWT:
   - DADO que: apenas contexto/estado inicial. PROIBIDO verbos de ação (clico, preencho, acesso)
   - QUANDO: exatamente UMA ação com verbo explícito: clico, preencho, seleciono, digito, envio, acesso, navego, submeto
   - ENTÃO: resultado observável com verbo explícito: vejo, exibe, mostra, contém, redirecionado, aparece, recebo, deve ser, deve ter, deve exibir

2. EXECUTABILIDADE (cada step precisa de AMBOS):
   - Verbo de ação ou validação explícito (clico, preencho, vejo, verifico, deve conter...)
   - Dado concreto entre aspas duplas, número, email ou URL:
     * "admin@empresa.com", "Senha@123", "Nome do Produto"
     * R$ 99,90, 5 itens, 30 segundos
     * https://app.exemplo.com/login

3. CLAREZA:
   - PROIBIDO: "algo", "coisa", "corretamente", "adequadamente", "como esperado", "qualquer"
   - Cada step: entre 5 e 20 palavras
   - Seja específico: "preencho o campo de email com" em vez de "insiro os dados"

4. COBERTURA:
   - Analise a complexidade: simples → 3-4 cenários, média → 4-6, complexa → 6-8
   - Cubra: caminho feliz, variações válidas, erros, validações de borda
   - CADA critério de aceitação da user story deve ter pelo menos um cenário

Retorne APENAS os cenários Gherkin, sem explicações ou comentários."""

    @staticmethod
    def refine_bdd(
        user_story: str,
        previous_bdd: str,
        score_summary: str,
        weaknesses: list[str],
    ) -> str:
        issues = "\n".join(f"  - {w}" for w in weaknesses)

        issues = "\n".join(f"  • {w}" for w in weaknesses)

        return f"""Os cenários BDD abaixo foram avaliados por métricas automáticas e precisam melhorar.
Leia o diagnóstico de cada dimensão com atenção e corrija EXATAMENTE o que está indicado.

USER STORY ORIGINAL:
{user_story}

CENÁRIOS ANTERIORES (score insuficiente):
{previous_bdd}

AVALIAÇÃO ATUAL:
{score_summary}

DIMENSÕES QUE PRECISAM MELHORAR (com instruções específicas):
{issues}

REGRAS GERAIS (sempre aplicar):
- Estrutura obrigatória: Cenário: / Dado que / Quando / Então
- DADO = apenas contexto/estado. PROIBIDO verbos de ação no Dado
- QUANDO = UMA ação com verbo explícito (clico, preencho, seleciono, navego...)
- ENTÃO = resultado observável (vejo, exibe, deve conter, redirecionado...)
- Não remova cenários que já estavam bons
- Não adicione comentários fora dos cenários Gherkin

Gere a versão MELHORADA. Retorne APENAS os cenários Gherkin."""

    @staticmethod
    def study_results(top_examples: list, low_examples: list) -> str:
        def fmt_examples(examples: list, label: str) -> str:
            if not examples:
                return ""
            lines = [f"\n{'─'*55}\n{label}\n{'─'*55}"]
            for i, ex in enumerate(examples, 1):
                lines.append(
                    f"\nExemplo {i} | Score {ex['score']:.1f}/10 "
                    f"(cobertura={ex['cobertura']:.1f} clareza={ex['clareza']:.1f} "
                    f"estrutura={ex['estrutura']:.1f} exec={ex['executabilidade']:.1f})\n"
                    f"Story: {ex['title']}\n"
                    f"BDD:\n{ex['bdd'][:800]}"
                )
            return "\n".join(lines)

        top_block = fmt_examples(top_examples, "MELHORES BDDs (alta qualidade)")
        low_block = fmt_examples(low_examples, "PIORES BDDs (baixa qualidade — anti-padrões)")

        return f"""Você recebeu cenários BDD gerados automaticamente para um dataset de user stories.
Analise os exemplos abaixo e produza um guia de boas práticas CONCRETO e ESPECÍFICO.
{top_block}
{low_block}

PRODUZA A ANÁLISE NAS SEGUINTES SEÇÕES:

## 1. PADRÕES DE ALTA QUALIDADE
O que os melhores BDDs têm em comum? Seja específico — cite steps reais como exemplo.

## 2. ANTI-PADRÕES IDENTIFICADOS
O que os piores BDDs fazem de errado? Cite exemplos concretos dos steps problemáticos.

## 3. ESTRUTURA IDEAL DE STEPS
Como deve ser um Given, When e Then de alta qualidade neste domínio?
Forneça templates com exemplos reais.

## 4. VOCABULÁRIO DO DOMÍNIO
Quais verbos, substantivos e dados concretos aparecem nos melhores cenários?
Liste os termos mais relevantes para este domínio.

## 5. REGRAS RESUMIDAS
Lista de 5 a 10 regras práticas, em ordem de impacto, para gerar BDD de alta qualidade
neste dataset específico."""

    @staticmethod
    def research_story(user_story: str) -> str:
        return f"""Você é um analista de QA sênior. Analise a user story abaixo e produza uma análise estruturada que será usada como base para gerar cenários BDD completos.

USER STORY:
{user_story}

Produza a análise nas seguintes seções:

## CRITÉRIOS DE ACEITAÇÃO
Liste todos os critérios de aceitação, incluindo os que estão implícitos na story. Seja específico e mensurável.

## REGRAS DE NEGÓCIO
Liste as regras de negócio relevantes que impactam o comportamento esperado do sistema.

## CASOS EXTREMOS E ERROS
Liste edge cases, condições de contorno, entradas inválidas e cenários de erro que devem ser cobertos.

## FLUXOS PRINCIPAIS
Descreva os fluxos: caminho feliz, variações válidas e caminhos alternativos.

## DADOS DE TESTE SUGERIDOS
Sugira valores concretos (emails, IDs, valores numéricos, datas) para uso nos steps Gherkin.

Seja específico e objetivo. Não gere os cenários Gherkin ainda — apenas a análise."""

    @staticmethod
    def build_context(similar_issues: list[dict]) -> str:
        if not similar_issues:
            return ""
        lines = ["EXEMPLOS DE ISSUES SIMILARES (use como referência de escopo):"]
        for i, issue in enumerate(similar_issues, 1):
            lines.append(f"\nExemplo {i}: {issue['title']}")
            if issue.get("description"):
                lines.append(f"  {issue['description'][:300]}...")
        return "\n".join(lines)
