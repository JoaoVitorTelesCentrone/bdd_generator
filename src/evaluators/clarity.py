import re
from typing import List


_VAGUE_TERMS = [
    "algo", "coisa", "corretamente", "adequadamente", "necessário",
    "esperado", "apropriado", "relevante", "qualquer", "algum",
    "funcionar", "funcione", "funciona", "acontecer", "ocorrer",
    "normalmente", "devidamente", "propriamente", "de forma",
    "something", "anything", "correctly", "appropriately",
    "etc", "entre outros", "e assim", "dentre outros",
]

# Concrete data patterns (same as executability)
_CONCRETE_PATTERNS = [
    re.compile(r'"[^"]+"'),
    re.compile(r"'[^']+'"),
    re.compile(r"\b\d+[\d.,]*\b"),
    re.compile(r"\w+@\w+\.\w+"),
    re.compile(r"https?://\S+"),
    re.compile(r"R\$\s*[\d.,]+"),
]

_HAS_STEPS = re.compile(r"\b(Dado|Quando|Então)\b", re.IGNORECASE)


def _strip_tags(text: str) -> str:
    return re.sub(r"^\s*@\w[\w:/-]*\s*\n", "", text, flags=re.MULTILINE)


def _extract_scenarios(bdd_text: str) -> List[str]:
    clean = _strip_tags(bdd_text)
    parts = re.split(r"\n\s*Cenário[^:]*:", clean, flags=re.IGNORECASE)
    return [p.strip() for p in parts if p.strip() and _HAS_STEPS.search(p)]


def _score_scenario(scenario: str) -> float:
    steps = re.findall(
        r"(?:Dado(?:\s+que)?|Quando|Então|E|Mas)\s+(.+)",
        scenario,
        re.IGNORECASE,
    )

    if not steps:
        return 0.0

    # 1. Step length score — ideal: 5-20 words per step
    length_penalties = 0
    for step in steps:
        words = len(step.split())
        if words < 4:
            length_penalties += 2.5
        elif words > 25:
            length_penalties += 1.5
    length_score = max(0.0, 10.0 - length_penalties)

    # 2. Vague terms penalty — each unique vague term found costs 2.5 pts
    text_lower = scenario.lower()
    vague_count = sum(1 for t in _VAGUE_TERMS if t in text_lower)
    vagueness_score = max(0.0, 10.0 - vague_count * 2.5)

    # 3. Concrete data score — starts at 0; each pattern type found adds 2.5 pts
    #    (max 10 with 4 different types present)
    concrete_hits = sum(bool(p.search(scenario)) for p in _CONCRETE_PATTERNS)
    concrete_score = min(10.0, concrete_hits * 2.5)

    # Weighted average
    score = length_score * 0.30 + vagueness_score * 0.35 + concrete_score * 0.35
    return round(max(0.0, min(10.0, score)), 2)


class ClarityEvaluator:
    """
    Métrica 2 — Clareza (0-10).

    Avalia legibilidade, ausência de termos vagos e presença de dados concretos.
    - Tamanho dos steps (30%)
    - Ausência de termos vagos (35%)
    - Dados concretos: aspas, números, emails, URLs (35%)

    Nota: concrete_score começa em 0 (não em 6). Steps sem dados concretos
    são penalizados de forma justa.
    """

    def evaluate(self, bdd_text: str) -> float:
        scenarios = _extract_scenarios(bdd_text)
        if not scenarios:
            return 0.0
        scores = [_score_scenario(s) for s in scenarios]
        return round(sum(scores) / len(scores), 2)
