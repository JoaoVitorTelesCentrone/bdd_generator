import anthropic
from .base import BaseLLMGenerator, GenerationResult

# Supported model aliases
MODEL_IDS = {
    "opus":   "claude-opus-4-6",
    "sonnet": "claude-sonnet-4-6",
    "haiku":  "claude-haiku-4-5",
    # Allow full IDs to be passed directly
    "claude-opus-4-6":   "claude-opus-4-6",
    "claude-sonnet-4-6": "claude-sonnet-4-6",
    "claude-haiku-4-5":  "claude-haiku-4-5",
}

SYSTEM_PROMPT = (
    "Você é um especialista sênior em BDD (Behavior-Driven Development) e QA. "
    "Gera cenários Gherkin de alta qualidade em português, seguindo estritamente o padrão "
    "Given-When-Then. Seus cenários são claros, específicos, executáveis e cobrem todos os "
    "critérios de aceitação fornecidos. Retorne APENAS os cenários Gherkin, sem explicações adicionais."
)


class ClaudeGenerator(BaseLLMGenerator):
    """BDD generator using the Anthropic Claude API."""

    def __init__(self, model: str = "sonnet", max_tokens: int = 4096):
        self.model_id = MODEL_IDS.get(model, model)
        self.max_tokens = max_tokens
        self.client = anthropic.Anthropic()

    def get_model_name(self) -> str:
        return self.model_id

    def generate(self, prompt: str, system_instruction: str | None = None) -> GenerationResult:
        try:
            with self.client.messages.stream(
                model=self.model_id,
                max_tokens=self.max_tokens,
                system=system_instruction or SYSTEM_PROMPT,
                messages=[{"role": "user", "content": prompt}],
            ) as stream:
                response = stream.get_final_message()

            text = next(
                (b.text for b in response.content if b.type == "text"), ""
            )
            return GenerationResult(
                success=True,
                bdd_text=text.strip(),
                model=self.model_id,
                input_tokens=response.usage.input_tokens,
                output_tokens=response.usage.output_tokens,
            )

        except anthropic.AuthenticationError:
            return GenerationResult(
                success=False,
                error="API key inválida. Configure ANTHROPIC_API_KEY.",
            )
        except anthropic.RateLimitError:
            return GenerationResult(
                success=False,
                error="Rate limit atingido. Aguarde e tente novamente.",
            )
        except anthropic.APIStatusError as e:
            return GenerationResult(
                success=False,
                error=f"Erro da API ({e.status_code}): {e.message}",
            )
        except Exception as e:
            return GenerationResult(success=False, error=str(e))
