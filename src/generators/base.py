from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class GenerationResult:
    success: bool
    bdd_text: str = ""
    model: str = ""
    input_tokens: int = 0
    output_tokens: int = 0
    error: Optional[str] = None

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens


class BaseLLMGenerator(ABC):
    """Abstract base class for LLM-based BDD generators."""

    @abstractmethod
    def generate(self, prompt: str, system_instruction: Optional[str] = None) -> GenerationResult:
        """Generate text from a prompt.

        Args:
            prompt: The user prompt.
            system_instruction: Optional override for the system-level instruction.
                                Useful when the same generator is used for non-BDD
                                tasks (e.g. auto-research analysis).
        """
        pass

    @abstractmethod
    def get_model_name(self) -> str:
        """Return the model identifier."""
        pass
