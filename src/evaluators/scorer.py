from dataclasses import dataclass
from typing import Optional

from .coverage import CoverageEvaluator
from .clarity import ClarityEvaluator
from .structure import StructureEvaluator
from .executability import ExecutabilityEvaluator

# Score weights (must sum to 1.0)
WEIGHTS = {
    "cobertura":       0.30,
    "clareza":         0.20,
    "estrutura":       0.30,
    "executabilidade": 0.20,
}

DEFAULT_THRESHOLD = 7.0


@dataclass
class ScoreResult:
    cobertura: float
    clareza: float
    estrutura: float
    executabilidade: float
    score_final: float
    aprovado: bool
    threshold: float

    def as_dict(self) -> dict:
        return {
            "cobertura":       self.cobertura,
            "clareza":         self.clareza,
            "estrutura":       self.estrutura,
            "executabilidade": self.executabilidade,
            "score_final":     self.score_final,
            "aprovado":        self.aprovado,
        }

    def summary(self) -> str:
        status = "APROVADO" if self.aprovado else "REPROVADO"
        bar = lambda v: "█" * int(v) + "░" * (10 - int(v))
        return (
            f"\n{'='*55}\n"
            f"  SCORE FINAL: {self.score_final:.1f}/10  [{status}]\n"
            f"{'─'*55}\n"
            f"  Cobertura       {self.cobertura:4.1f}/10  {bar(self.cobertura)}\n"
            f"  Clareza         {self.clareza:4.1f}/10  {bar(self.clareza)}\n"
            f"  Estrutura GWT   {self.estrutura:4.1f}/10  {bar(self.estrutura)}\n"
            f"  Executabilidade {self.executabilidade:4.1f}/10  {bar(self.executabilidade)}\n"
            f"{'='*55}"
        )

    def weaknesses(self) -> list[str]:
        """
        Returns dimensions scoring below threshold, with actionable detail
        so the refinement prompt can give specific guidance.
        """
        dims = [
            ("Cobertura",       self.cobertura),
            ("Clareza",         self.clareza),
            ("Estrutura GWT",   self.estrutura),
            ("Executabilidade", self.executabilidade),
        ]
        result = []
        for name, score in dims:
            if score < self.threshold:
                gap = self.threshold - score
                detail = _weakness_detail(name, score, gap)
                result.append(detail)
        return result


def _weakness_detail(name: str, score: float, gap: float) -> str:
    """Returns a short diagnostic message for each weak dimension."""
    hints = {
        "Cobertura": (
            f"Cobertura ({score:.1f}/10 — faltam {gap:.1f} pts): "
            "Adicione cenários para critérios de aceitação ainda não cobertos. "
            "Cada critério da story deve ter pelo menos um cenário."
        ),
        "Clareza": (
            f"Clareza ({score:.1f}/10 — faltam {gap:.1f} pts): "
            'Use dados concretos entre aspas duplas: "usuario@email.com", "Senha@123", "Produto X". '
            "Elimine termos vagos como 'corretamente', 'adequadamente', 'como esperado'."
        ),
        "Estrutura GWT": (
            f"Estrutura GWT ({score:.1f}/10 — faltam {gap:.1f} pts): "
            "Dado=contexto/estado (sem verbos de ação), "
            "Quando=UMA ação com verbo claro (clico/preencho/seleciono), "
            "Então=resultado observável (vejo/exibe/deve conter)."
        ),
        "Executabilidade": (
            f"Executabilidade ({score:.1f}/10 — faltam {gap:.1f} pts): "
            'Cada step precisa de: (1) verbo de ação/validação explícito E '
            '(2) dado concreto entre aspas ou número. '
            'Exemplo: Quando preencho o campo de email com "usuario@email.com"'
        ),
    }
    return hints.get(name, f"{name} ({score:.1f}/10)")


class BDDScorer:
    """Aggregates all four BDD quality metrics into a final score."""

    def __init__(self, threshold: float = DEFAULT_THRESHOLD):
        self.threshold = threshold
        self._coverage      = CoverageEvaluator()
        self._clarity       = ClarityEvaluator()
        self._structure     = StructureEvaluator()
        self._executability = ExecutabilityEvaluator()

    def score(
        self,
        user_story: str,
        bdd_text: str,
        research_context: Optional[str] = None,
    ) -> ScoreResult:
        cobertura       = self._coverage.evaluate(user_story, bdd_text, research_context)
        clareza         = self._clarity.evaluate(bdd_text)
        estrutura       = self._structure.evaluate(bdd_text)
        executabilidade = self._executability.evaluate(bdd_text)

        score_final = round(
            cobertura       * WEIGHTS["cobertura"]       +
            clareza         * WEIGHTS["clareza"]         +
            estrutura       * WEIGHTS["estrutura"]       +
            executabilidade * WEIGHTS["executabilidade"],
            2,
        )

        return ScoreResult(
            cobertura=cobertura,
            clareza=clareza,
            estrutura=estrutura,
            executabilidade=executabilidade,
            score_final=score_final,
            aprovado=score_final >= self.threshold,
            threshold=self.threshold,
        )
