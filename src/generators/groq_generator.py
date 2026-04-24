from pathlib import Path
from dotenv import load_dotenv
from groq import Groq
from .base import BaseLLMGenerator, GenerationResult
from ..auth.config import get_api_key

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

MODEL_IDS = {
    "llama":       "llama-3.3-70b-versatile",
    "llama-fast":  "llama-3.1-8b-instant",
    "deepseek":    "deepseek-r1-distill-llama-70b",
    "gemma":       "gemma2-9b-it",
    # Full IDs aceitos diretamente
    "llama-3.3-70b-versatile":        "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant":           "llama-3.1-8b-instant",
    "deepseek-r1-distill-llama-70b":  "deepseek-r1-distill-llama-70b",
    "gemma2-9b-it":                   "gemma2-9b-it",
}

SYSTEM_PROMPT = (
    "Você é um especialista sênior em BDD (Behavior-Driven Development) e QA. "
    "Gera cenários Gherkin de alta qualidade em português, seguindo estritamente o padrão "
    "Given-When-Then (Dado-Quando-Então). Seus cenários são claros, específicos, executáveis "
    "e cobrem todos os critérios de aceitação fornecidos. "
    "Retorne APENAS os cenários Gherkin, sem explicações adicionais."
)


class GroqGenerator(BaseLLMGenerator):
    """BDD generator using the Groq API (free tier available)."""

    def __init__(self, model: str = "llama", max_tokens: int = 4096):
        api_key = get_api_key("GROQ_API_KEY")
        if not api_key:
            raise EnvironmentError(
                "GROQ_API_KEY não encontrada.\n"
                "Configure com: bdd config set-key GROQ_API_KEY <sua-chave>\n"
                "Obtenha sua chave gratuita em: https://console.groq.com/keys"
            )
        self.model_id = MODEL_IDS.get(model, model)
        self.max_tokens = max_tokens
        self._client = Groq(api_key=api_key)

    def get_model_name(self) -> str:
        return self.model_id

    @staticmethod
    def _clean(text: str) -> str:
        """Strip markdown code fences and any preamble before the Gherkin block."""
        import re
        # Remove ```gherkin ... ``` or ``` ... ``` wrappers
        text = re.sub(r"^```[a-zA-Z]*\n?", "", text.strip())
        text = re.sub(r"\n?```$", "", text.strip())
        # If there's still a preamble before Funcionalidade/Feature, drop it
        m = re.search(r"^(Funcionalidade|Feature)\s*:", text, re.MULTILINE | re.IGNORECASE)
        if m and m.start() > 0:
            text = text[m.start():]
        return text.strip()

    def generate(self, prompt: str, system_instruction: str | None = None) -> GenerationResult:
        try:
            response = self._client.chat.completions.create(
                model=self.model_id,
                max_tokens=self.max_tokens,
                messages=[
                    {"role": "system", "content": system_instruction or SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
            )
            text = self._clean(response.choices[0].message.content or "")
            usage = response.usage
            return GenerationResult(
                success=True,
                bdd_text=text,
                model=self.model_id,
                input_tokens=usage.prompt_tokens if usage else 0,
                output_tokens=usage.completion_tokens if usage else 0,
            )
        except Exception as e:
            error_msg = str(e)
            if "api_key" in error_msg.lower() or "authentication" in error_msg.lower():
                error_msg = "GROQ_API_KEY inválida. Verifique em https://console.groq.com/keys"
            elif "rate_limit" in error_msg.lower() or "429" in error_msg:
                error_msg = "Rate limit do Groq atingido. Aguarde alguns segundos."
            return GenerationResult(success=False, error=error_msg)
