import time
from dataclasses import dataclass

from ..generators.base import BaseLLMGenerator
from ..utils.prompts import PromptTemplates

# System instruction for the research phase — different from the BDD generation
# instruction so generators configured for "Gherkin only" don't suppress the analysis.
RESEARCH_SYSTEM_INSTRUCTION = (
    "Você é um analista de QA sênior especialista em levantamento de requisitos e "
    "definição de critérios de aceitação. Sua tarefa é analisar user stories e produzir "
    "análises estruturadas de alta qualidade que sirvam de base para a criação de "
    "cenários BDD. Responda sempre em português, de forma organizada e objetiva."
)


@dataclass
class ResearchResult:
    context: str
    input_tokens: int
    output_tokens: int
    duration_seconds: float
    success: bool

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens


class AutoResearcher:
    """
    Analyzes a user story before BDD generation using an LLM call.

    Extracts acceptance criteria, business rules, edge cases and domain
    context so the generator receives richer input on the first attempt,
    reducing the number of refinement iterations needed to pass the threshold.

    Uses a dedicated system instruction (RESEARCH_SYSTEM_INSTRUCTION) so
    generators that default to "return ONLY Gherkin" (e.g. GeminiGenerator)
    produce a proper analysis instead.
    """

    def __init__(self, generator: BaseLLMGenerator, verbose: bool = False):
        self.generator = generator
        self.verbose = verbose

    def research(self, user_story: str) -> ResearchResult:
        if self.verbose:
            print("\n  [Auto-Research] Analisando user story...")

        prompt = PromptTemplates.research_story(user_story)
        t0 = time.time()
        result = self.generator.generate(
            prompt,
            system_instruction=RESEARCH_SYSTEM_INSTRUCTION,
        )
        duration = time.time() - t0

        if self.verbose:
            if result.success:
                print(
                    f"  [Auto-Research] Contexto extraído "
                    f"({result.total_tokens} tokens, {duration:.1f}s)"
                )
            else:
                print(f"  [Auto-Research] Falha: {result.error}")

        return ResearchResult(
            context=result.bdd_text if result.success else "",
            input_tokens=result.input_tokens,
            output_tokens=result.output_tokens,
            duration_seconds=duration,
            success=result.success,
        )
