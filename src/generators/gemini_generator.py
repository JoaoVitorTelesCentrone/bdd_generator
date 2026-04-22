import os
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types
from .base import BaseLLMGenerator, GenerationResult
from ..auth.config import get_api_key

# Carrega .env da raiz do projeto (suporte a dev local)
load_dotenv(Path(__file__).resolve().parents[2] / ".env")

MODEL_IDS = {
    # Aliases amigáveis → modelo real disponível
    "flash":        "gemini-2.5-flash",
    "flash-lite":   "gemini-2.0-flash-lite-001",
    "pro":          "gemini-2.5-pro",
    "flash-001":    "gemini-2.0-flash-001",
    # Full IDs aceitos diretamente
    "gemini-2.5-flash":         "gemini-2.5-flash",
    "gemini-2.5-pro":           "gemini-2.5-pro",
    "gemini-2.0-flash-001":     "gemini-2.0-flash-001",
    "gemini-2.0-flash-lite-001":"gemini-2.0-flash-lite-001",
    "gemini-2.0-flash-lite":    "gemini-2.0-flash-lite-001",
}

SYSTEM_INSTRUCTION = (
    "Você é um especialista sênior em BDD (Behavior-Driven Development) e QA. "
    "Gera cenários Gherkin de alta qualidade em português, seguindo estritamente o padrão "
    "Given-When-Then (Dado-Quando-Então). Seus cenários são claros, específicos, executáveis "
    "e cobrem todos os critérios de aceitação fornecidos. "
    "Retorne APENAS os cenários Gherkin, sem explicações adicionais."
)


class GeminiGenerator(BaseLLMGenerator):
    """BDD generator usando o novo SDK google-genai."""

    def __init__(self, model: str = "flash", max_tokens: int = 4096):
        api_key = get_api_key("GEMINI_API_KEY")
        if not api_key:
            raise EnvironmentError(
                "GEMINI_API_KEY não encontrada.\n"
                "Configure com: bdd config set-key GEMINI_API_KEY <sua-chave>\n"
                "Obtenha sua chave em: https://aistudio.google.com/apikey"
            )

        self.model_id = MODEL_IDS.get(model, model)
        self.max_tokens = max_tokens
        self._client = genai.Client(api_key=api_key)

    def get_model_name(self) -> str:
        return self.model_id

    # Gemini 2.5 Flash is a "thinking" model — temperature is incompatible with
    # the default thinking mode. We disable thinking via budget_tokens=0 so we
    # can use temperature freely (same behaviour as 2.0 Flash).
    _THINKING_MODELS = frozenset({"gemini-2.5-flash", "gemini-2.5-pro"})

    def _build_config(self, system_instruction: str | None) -> types.GenerateContentConfig:
        kwargs: dict = dict(
            system_instruction=system_instruction or SYSTEM_INSTRUCTION,
            max_output_tokens=self.max_tokens,
        )
        if self.model_id in self._THINKING_MODELS:
            # Disable thinking budget so temperature can be set normally.
            kwargs["thinking_config"] = types.ThinkingConfig(thinking_budget=0)
        else:
            kwargs["temperature"] = 0.7
        return types.GenerateContentConfig(**kwargs)

    def generate(self, prompt: str, system_instruction: str | None = None) -> GenerationResult:
        try:
            response = self._client.models.generate_content(
                model=self.model_id,
                contents=prompt,
                config=self._build_config(system_instruction),
            )

            text = response.text.strip() if response.text else ""

            input_tokens  = 0
            output_tokens = 0
            if response.usage_metadata:
                input_tokens  = response.usage_metadata.prompt_token_count or 0
                output_tokens = response.usage_metadata.candidates_token_count or 0

            return GenerationResult(
                success=True,
                bdd_text=text,
                model=self.model_id,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
            )

        except Exception as e:
            error_msg = str(e)
            if "API_KEY" in error_msg or "api key" in error_msg.lower():
                error_msg = "Gemini API key inválida. Verifique o arquivo .env"
            elif "quota" in error_msg.lower() or "429" in error_msg:
                error_msg = "Quota da API Gemini atingida."
            elif "Method Not Allowed" in error_msg or "405" in error_msg:
                error_msg = (
                    f"Gemini API rejeitou a requisição (405 Method Not Allowed). "
                    f"Verifique se o modelo '{self.model_id}' está disponível para sua chave. "
                    f"Detalhe original: {str(e)}"
                )
            return GenerationResult(success=False, error=error_msg)
