"""
Infrastructure layer — GeneratorFactory.

Knows about concrete LLM implementations and resolves an alias string
("flash", "sonnet", etc.) into the correct BaseLLMGenerator subclass.

This is the only place in the codebase that imports Gemini/Claude directly.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.generators.gemini_generator import GeminiGenerator
from src.generators.claude_generator import ClaudeGenerator
from src.generators.groq_generator import GroqGenerator
from src.generators.base import BaseLLMGenerator

_GEMINI_ALIASES: frozenset[str] = frozenset({
    "flash", "flash-lite", "pro", "flash-1.5",
    "gemini-2.5-flash", "gemini-2.5-pro",
    "gemini-2.0-flash", "gemini-2.0-flash-lite",
    "gemini-1.5-pro", "gemini-1.5-flash",
})

_GROQ_ALIASES: frozenset[str] = frozenset({
    "llama", "llama-fast", "deepseek", "gemma",
    "llama-3.3-70b-versatile", "llama-3.1-8b-instant",
    "deepseek-r1-distill-llama-70b", "gemma2-9b-it",
})

_MODEL_CATALOGUE = [
    {"id": "llama",      "name": "Llama 3.3 70B (Groq)",    "provider": "groq", "default": True, "free": True},
    {"id": "llama-fast", "name": "Llama 3.1 8B (Groq)",     "provider": "groq", "free": True},
    {"id": "deepseek",   "name": "DeepSeek R1 70B (Groq)",  "provider": "groq", "free": True},
    {"id": "gemma",      "name": "Gemma 2 9B (Groq)",       "provider": "groq", "free": True},
    {"id": "flash",      "name": "Gemini 2.5 Flash",         "provider": "gemini"},
    {"id": "pro",        "name": "Gemini 2.5 Pro",           "provider": "gemini"},
    {"id": "flash-lite", "name": "Gemini 2.0 Flash Lite",    "provider": "gemini"},
    {"id": "sonnet",     "name": "Claude Sonnet 4.6",        "provider": "claude"},
    {"id": "opus",       "name": "Claude Opus 4.6",          "provider": "claude"},
    {"id": "haiku",      "name": "Claude Haiku 4.5",         "provider": "claude"},
]


class GeneratorFactory:
    """Creates the correct LLM generator for a given model alias."""

    @staticmethod
    def create(model: str, max_tokens: int = 4096) -> BaseLLMGenerator:
        if model in _GROQ_ALIASES or model.startswith("llama") or model.startswith("deepseek") or model.startswith("gemma"):
            return GroqGenerator(model=model, max_tokens=max_tokens)
        if model in _GEMINI_ALIASES or model.startswith("gemini"):
            return GeminiGenerator(model=model, max_tokens=max_tokens)
        return ClaudeGenerator(model=model, max_tokens=max_tokens)

    @staticmethod
    def catalogue() -> list[dict]:
        """Returns the list of available models for the /api/models endpoint."""
        return _MODEL_CATALOGUE
