import csv
import json
import time
from dataclasses import dataclass
from pathlib import Path

from ..generators.base import BaseLLMGenerator
from ..utils.prompts import PromptTemplates

STUDY_SYSTEM_INSTRUCTION = (
    "Você é um especialista sênior em BDD e qualidade de software. "
    "Sua tarefa é analisar conjuntos de cenários BDD gerados automaticamente, "
    "identificar padrões de qualidade e produzir guias de boas práticas concretos "
    "que possam ser usados para melhorar gerações futuras. "
    "Seja analítico, específico e use exemplos reais do material fornecido."
)


@dataclass
class StudyResult:
    insights: str
    top_examples: list
    low_examples: list
    input_tokens: int
    output_tokens: int
    duration_seconds: float
    output_path: Path


class BatchAnalyzer:
    """
    Analyzes batch results to extract quality patterns from high-scoring BDDs.

    Produces a study insights file (JSON) containing:
    - LLM analysis of what makes good BDD in this dataset
    - Top-scoring examples to use as few-shot references
    - Low-scoring examples as anti-patterns to avoid

    The output file is consumed by future batch runs via --learn-from.
    """

    def __init__(self, generator: BaseLLMGenerator, verbose: bool = False):
        self.generator = generator
        self.verbose = verbose

    def analyze(
        self,
        results_csv: str,
        output_path: str = "results/study_insights.json",
        top_n: int = 5,
        bottom_n: int = 3,
    ) -> StudyResult:
        rows = self._load_csv(results_csv)

        # Sort by score
        scored = [r for r in rows if r.get("feature_file")]
        scored.sort(key=lambda r: float(r.get("score_final", 0)), reverse=True)

        top_rows    = scored[:top_n]
        bottom_rows = scored[-bottom_n:] if len(scored) > top_n else []

        top_examples    = self._load_examples(top_rows)
        bottom_examples = self._load_examples(bottom_rows)

        if self.verbose:
            print(f"  Top {len(top_examples)} BDDs (alta qualidade) carregados")
            print(f"  Bottom {len(bottom_examples)} BDDs (baixa qualidade) carregados")
            print("  Enviando para análise do LLM...")

        prompt = PromptTemplates.study_results(top_examples, bottom_examples)
        t0 = time.time()
        result = self.generator.generate(
            prompt,
            system_instruction=STUDY_SYSTEM_INSTRUCTION,
        )
        duration = time.time() - t0

        insights = result.bdd_text if result.success else f"Análise falhou: {result.error}"

        # Persist
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "insights": insights,
            "top_examples": top_examples,
            "low_examples": bottom_examples,
            "meta": {
                "source_csv": str(results_csv),
                "total_stories": len(rows),
                "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                "model": self.generator.get_model_name(),
            },
        }
        out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

        return StudyResult(
            insights=insights,
            top_examples=top_examples,
            low_examples=bottom_examples,
            input_tokens=result.input_tokens,
            output_tokens=result.output_tokens,
            duration_seconds=duration,
            output_path=out,
        )

    # ── helpers ───────────────────────────────────────────────────────────────

    def _load_csv(self, csv_path: str) -> list:
        rows = []
        with open(csv_path, encoding="utf-8-sig") as f:
            for row in csv.DictReader(f):
                rows.append(dict(row))
        return rows

    def _load_examples(self, rows: list) -> list:
        examples = []
        for r in rows:
            feature_path = Path(r.get("feature_file", ""))
            if not feature_path.exists():
                continue
            bdd_text = feature_path.read_text(encoding="utf-8")
            examples.append({
                "title":           r.get("title", ""),
                "score":           float(r.get("score_final", 0)),
                "cobertura":       float(r.get("cobertura", 0)),
                "clareza":         float(r.get("clareza", 0)),
                "estrutura":       float(r.get("estrutura", 0)),
                "executabilidade": float(r.get("executabilidade", 0)),
                "tentativas":      r.get("tentativas", "?"),
                "bdd":             bdd_text,
            })
        return examples


def load_study_context(study_file: str, max_examples: int = 3) -> str:
    """
    Reads a study insights JSON and builds a context string for few-shot prompting.
    Called by the CLI --learn-from flag.
    """
    data = json.loads(Path(study_file).read_text(encoding="utf-8"))

    parts = [
        "=" * 60,
        "GUIA DE ESTILO (gerado por análise de BDDs anteriores)",
        "=" * 60,
        data.get("insights", ""),
    ]

    top = data.get("top_examples", [])[:max_examples]
    if top:
        parts.append("\n" + "=" * 60)
        parts.append("EXEMPLOS DE REFERÊNCIA (alta qualidade — imite o estilo)")
        parts.append("=" * 60)
        for i, ex in enumerate(top, 1):
            parts.append(
                f"\n[Exemplo {i} | Score {ex['score']:.1f}/10 | {ex['title'][:80]}]"
            )
            # Include the BDD but strip the header comment lines
            bdd_lines = [
                ln for ln in ex["bdd"].splitlines()
                if not ln.startswith("#")
            ]
            parts.append("\n".join(bdd_lines).strip())

    return "\n".join(parts)
