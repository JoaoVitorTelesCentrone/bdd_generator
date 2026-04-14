import re
from typing import List


_ACTION_VERBS = [
    "clico", "clique", "preencho", "preencha", "envio", "envie",
    "seleciono", "selecione", "digito", "digite", "acesso", "acesse",
    "abro", "abra", "fecho", "feche", "marco", "marque", "desmarco",
    "submeto", "submeta", "navego", "navegue", "arrasto", "arraste",
]

_VALIDATION_VERBS = [
    "vejo", "veja", "exibir", "exibe", "mostrar", "mostra",
    "conter", "contém", "redirecionar", "redirecionado", "aparecer",
    "aparece", "receber", "recebo", "encontrar", "encontro",
    "deve ser", "deve ter", "deve exibir", "deve mostrar", "deve conter",
    "verifico", "verificar", "confirmo", "confirmar",
]

_HAS_STEPS = re.compile(r"\b(Dado|Quando|Então)\b", re.IGNORECASE)


def _strip_tags(text: str) -> str:
    """Remove @tag lines so they don't pollute scenario parsing."""
    return re.sub(r"^\s*@\w[\w:/-]*\s*\n", "", text, flags=re.MULTILINE)


def _extract_scenarios(bdd_text: str) -> List[str]:
    clean = _strip_tags(bdd_text)
    parts = re.split(r"\n\s*Cenário[^:]*:", clean, flags=re.IGNORECASE)
    # Only keep parts that contain actual BDD steps (Dado/Quando/Então)
    return [p.strip() for p in parts if p.strip() and _HAS_STEPS.search(p)]


def _score_scenario(scenario: str) -> float:
    text = scenario

    # 1. Presence of Given / When / Then (mandatory — 3 pts)
    has_given = bool(re.search(r"\bDado\b", text, re.IGNORECASE))
    has_when  = bool(re.search(r"\bQuando\b", text, re.IGNORECASE))
    has_then  = bool(re.search(r"\bEntão\b", text, re.IGNORECASE))

    if not (has_given and has_when and has_then):
        return 0.0

    points = 3.0

    # 2. Given should be context, not action (2 pts)
    givens = re.findall(r"Dado(?:\s+que)?\s+(.+)", text, re.IGNORECASE)
    given_clean = all(
        not any(v in g.lower() for v in _ACTION_VERBS)
        for g in givens
    )
    if given_clean:
        points += 2.0

    # 3. When should contain exactly one clear user action (2.5 pts)
    whens = re.findall(r"Quando\s+(.+)", text, re.IGNORECASE)
    if len(whens) == 1:
        points += 2.5 if any(v in whens[0].lower() for v in _ACTION_VERBS) else 1.0
    elif len(whens) > 1:
        points += 1.0  # multiple Whens is acceptable but not ideal

    # 4. Then should validate an observable result (2.5 pts)
    thens = re.findall(r"Então(?:\s+devo)?\s+(.+)", text, re.IGNORECASE)
    if any(any(v in t.lower() for v in _VALIDATION_VERBS) for t in thens):
        points += 2.5
    elif thens:
        points += 1.0  # Then exists but no clear validation verb

    return round(min(points, 10.0), 2)


class StructureEvaluator:
    """
    Métrica 3 — Estrutura GWT (0-10).

    Valida aderência ao padrão Given-When-Then.
    Tags (@tag) antes de cenários são ignoradas para não contaminar a nota.
    """

    def evaluate(self, bdd_text: str) -> float:
        scenarios = _extract_scenarios(bdd_text)
        if not scenarios:
            return 0.0
        scores = [_score_scenario(s) for s in scenarios]
        return round(sum(scores) / len(scores), 2)
