import re
from typing import List, Optional


_CRITERIA_PATTERNS = [
    r"[-•*]\s*(.+)",
    r"\d+\.\s*(.+)",
    r"critério[^:]*:\s*(.+)",
    r"deve\s+(.+)",
    r"precisa\s+(.+)",
    r"##\s*critérios[^:]*:?\s*\n((?:.+\n?)*)",
]

_STOP_WORDS = {
    "o", "a", "os", "as", "um", "uma", "de", "do", "da", "dos", "das",
    "em", "no", "na", "nos", "nas", "para", "por", "com", "sem", "que",
    "se", "ao", "aos", "às", "e", "ou", "mas", "como", "também", "isso",
    "este", "esta", "esse", "essa", "seu", "sua", "seus", "suas",
    "the", "a", "an", "of", "to", "for", "with", "and", "or", "in",
}


def _extract_keywords(text: str) -> List[str]:
    # Strip @tags before keyword extraction
    clean = re.sub(r"@\w[\w:/-]*", "", text)
    words = re.findall(r"\b\w{4,}\b", clean.lower())
    return [w for w in words if w not in _STOP_WORDS]


def _extract_criteria(user_story: str) -> List[str]:
    """Extract acceptance criteria items from a user story."""
    criteria = []
    for pattern in _CRITERIA_PATTERNS:
        matches = re.findall(pattern, user_story, re.IGNORECASE)
        criteria.extend([m.strip() for m in matches if len(m.strip()) > 5])

    seen = set()
    unique = []
    for c in criteria:
        key = c.lower()[:40]
        if key not in seen:
            seen.add(key)
            unique.append(c)
    return unique


def _extract_criteria_from_research(research_context: str) -> List[str]:
    """
    Extract acceptance criteria from auto-research output.
    Looks for the '## CRITÉRIOS DE ACEITAÇÃO' section.
    """
    criteria = []
    # Find the AC section
    match = re.search(
        r"##\s*CRITÉRIOS DE ACEITAÇÃO\s*\n((?:(?!##).|\n)*)",
        research_context,
        re.IGNORECASE,
    )
    if match:
        section = match.group(1)
        # Extract bullet/numbered items
        items = re.findall(r"[-•*\d.]\s*(.+)", section)
        criteria.extend([i.strip() for i in items if len(i.strip()) > 5])

    return criteria


def _coverage_ratio(criteria: List[str], bdd_lower: str) -> float:
    """Returns the fraction of criteria covered in the BDD text (0.0–1.0)."""
    if not criteria:
        return 0.0
    covered = 0
    for criterion in criteria:
        keywords = _extract_keywords(criterion)
        if not keywords:
            continue
        hits = sum(1 for kw in keywords if kw in bdd_lower)
        if hits >= max(1, len(keywords) // 2):
            covered += 1
    return covered / len(criteria)


def _count_scenarios(bdd_text: str) -> int:
    return len(re.findall(r"\n\s*Cenário[^:]*:", bdd_text, re.IGNORECASE))


class CoverageEvaluator:
    """
    Métrica 1 — Cobertura (0-10).

    Mede quantos critérios de aceitação da user story estão cobertos
    pelos cenários BDD gerados.

    Se research_context for fornecido, usa os ACs extraídos pelo LLM
    (mais completos que o parsing por regex) como critério adicional.
    """

    def evaluate(
        self,
        user_story: str,
        bdd_text: str,
        research_context: Optional[str] = None,
    ) -> float:
        bdd_lower = bdd_text.lower()

        # --- Critérios da story original ---
        story_criteria = _extract_criteria(user_story)

        # --- Critérios do research (se disponível) ---
        research_criteria: List[str] = []
        if research_context:
            research_criteria = _extract_criteria_from_research(research_context)

        # --- Caso sem critérios: fallback por keyword overlap ---
        if not story_criteria and not research_criteria:
            story_keywords = set(_extract_keywords(user_story))
            bdd_keywords   = set(_extract_keywords(bdd_text))
            if not story_keywords:
                return 5.0
            overlap = len(story_keywords & bdd_keywords) / len(story_keywords)
            return round(min(overlap * 10, 10.0), 2)  # sem multiplicador inflado

        # --- Cobertura dos critérios da story ---
        story_ratio = _coverage_ratio(story_criteria, bdd_lower) if story_criteria else 1.0

        # --- Cobertura dos critérios do research ---
        research_ratio = _coverage_ratio(research_criteria, bdd_lower) if research_criteria else None

        # Ponderação: se temos ambos, research recebe 40% do peso
        if research_ratio is not None:
            base_score = story_ratio * 0.60 + research_ratio * 0.40
        else:
            base_score = story_ratio

        # --- Bônus por quantidade de cenários adequada ---
        # Estima complexidade pelo número de critérios
        total_criteria = len(story_criteria) + len(research_criteria)
        n_scenarios = _count_scenarios(bdd_text)
        expected_min = max(2, total_criteria)
        scenario_bonus = 0.0
        if n_scenarios >= expected_min:
            scenario_bonus = 0.05  # bônus de 5% por ter cenários suficientes

        final = min(1.0, base_score + scenario_bonus)
        return round(final * 10, 2)
