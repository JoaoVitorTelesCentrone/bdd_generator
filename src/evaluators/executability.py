import re
from typing import List


_ACTION_VERBS = [
    "preencho", "preencha", "clico", "clique", "seleciono", "selecione",
    "marco", "marque", "desmarco", "navego", "navegue", "espero", "aguardo",
    "acesso", "acesse", "submeto", "submeta", "envio", "envie",
    "digito", "digite", "abro", "abra", "arrasto", "arraste",
    "faço upload", "baixo", "aperto", "aperte",
]

_VALIDATION_VERBS = [
    "vejo", "veja", "não vejo", "verifico", "verificar", "confirmo",
    "exibe", "exibir", "mostra", "mostrar", "contém", "conter",
    "redirecionado", "aparece", "aparecer", "recebo", "receber",
    "deve ser", "deve ter", "deve exibir", "deve mostrar", "deve conter",
    "encontro", "encontrar",
]

_VAGUE_TERMS = [
    "algum", "qualquer", "um valor", "algo", "etc", "entre outros",
    "corretamente", "adequadamente", "como esperado", "de forma",
    "normalmente", "devidamente", "propriamente", "apropriadamente",
]

# Concrete data patterns
_CONCRETE_PATTERNS = [
    re.compile(r'"[^"]+"'),            # "valor entre aspas duplas"
    re.compile(r"'[^']+'"),            # 'valor entre aspas simples'
    re.compile(r"\b\d+[\d.,]*\b"),     # números (42, 3.14, 1.500,00)
    re.compile(r"\w+@\w+\.\w+"),       # emails
    re.compile(r"https?://\S+"),       # URLs
    re.compile(r"R\$\s*[\d.,]+"),      # valores monetários
]

_HAS_STEPS = re.compile(r"\b(Dado|Quando|Então)\b", re.IGNORECASE)


def _strip_tags(text: str) -> str:
    return re.sub(r"^\s*@\w[\w:/-]*\s*\n", "", text, flags=re.MULTILINE)


def _extract_scenarios(bdd_text: str) -> List[str]:
    clean = _strip_tags(bdd_text)
    parts = re.split(r"\n\s*Cenário[^:]*:", clean, flags=re.IGNORECASE)
    return [p.strip() for p in parts if p.strip() and _HAS_STEPS.search(p)]


def _has_verb(step_lower: str) -> bool:
    return (
        any(v in step_lower for v in _ACTION_VERBS)
        or any(v in step_lower for v in _VALIDATION_VERBS)
    )


def _has_concrete_data(step: str) -> bool:
    return any(p.search(step) for p in _CONCRETE_PATTERNS)


def _is_vague(step_lower: str) -> bool:
    return any(t in step_lower for t in _VAGUE_TERMS)


def _score_scenario(scenario: str) -> float:
    steps = re.findall(
        r"(?:Dado(?:\s+que)?|Quando|Então|E|Mas)\s+(.+)",
        scenario,
        re.IGNORECASE,
    )

    if not steps:
        return 0.0

    total_points = 0
    max_points = len(steps) * 5  # 5 pts per step

    for step in steps:
        step_lower = step.lower()
        pts = 0

        # 1. Has specific action or validation verb (2 pts)
        if _has_verb(step_lower):
            pts += 2

        # 2. Has concrete data — quoted value, number, email, URL, currency (2 pts)
        if _has_concrete_data(step):
            pts += 2

        # 3. Not vague/abstract (1 pt)
        if not _is_vague(step_lower):
            pts += 1

        total_points += pts

    raw_score = (total_points / max_points) * 10 if max_points > 0 else 0
    return round(min(raw_score, 10.0), 2)


class ExecutabilityEvaluator:
    """
    Métrica 4 — Executabilidade (0-10).

    Avalia se os steps são específicos o suficiente para serem automatizados:
    - Verbos de ação ou validação concretos (2 pts/step)
    - Dados concretos entre aspas, números, emails ou URLs (2 pts/step)
    - Ausência de termos vagos/abstratos (1 pt/step)

    NÃO exige seletores CSS/XPath — esses são detalhes de implementação,
    não de especificação BDD.
    """

    def evaluate(self, bdd_text: str) -> float:
        scenarios = _extract_scenarios(bdd_text)
        if not scenarios:
            return 0.0
        scores = [_score_scenario(s) for s in scenarios]
        return round(sum(scores) / len(scores), 2)
