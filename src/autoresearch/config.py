import json
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class ResearchConfig:
    cobertura: float = 0.30
    clareza: float = 0.20
    estrutura: float = 0.30
    executabilidade: float = 0.20
    threshold: float = 7.0
    max_attempts: int = 3

    def as_weights(self) -> dict:
        return {
            "cobertura":       self.cobertura,
            "clareza":         self.clareza,
            "estrutura":       self.estrutura,
            "executabilidade": self.executabilidade,
        }

    def save(self, path: Path) -> None:
        path.write_text(json.dumps(asdict(self), indent=2, ensure_ascii=False), encoding="utf-8")

    @classmethod
    def load(cls, path: Path) -> "ResearchConfig":
        return cls(**json.loads(path.read_text(encoding="utf-8")))

    def label(self) -> str:
        return (
            f"cob={self.cobertura:.2f} cla={self.clareza:.2f} "
            f"est={self.estrutura:.2f} exe={self.executabilidade:.2f} "
            f"thr={self.threshold:.1f} att={self.max_attempts}"
        )
