"""Gherkin .feature file parser with Portuguese keyword support."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class Step:
    keyword: str
    text: str

    def full_text(self) -> str:
        return f"{self.keyword} {self.text}"


@dataclass
class Scenario:
    name: str
    steps: list[Step] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)


@dataclass
class Feature:
    name: str
    description: str = ""
    scenarios: list[Scenario] = field(default_factory=list)
    background_steps: list[Step] = field(default_factory=list)


# English + Portuguese step keywords
_STEP_KEYWORDS = (
    "Given", "When", "Then", "And", "But",
    "Dado", "Quando", "Então", "E", "Mas",
)

_FEATURE_PREFIXES = ("feature:", "funcionalidade:")
_BACKGROUND_PREFIXES = ("background:", "contexto:")
_SCENARIO_PREFIXES = ("scenario outline:", "cenário:", "esquema do cenário:", "scenario:")


def parse_feature_file(path: str) -> Feature:
    return parse_feature_text(Path(path).read_text(encoding="utf-8"))


def parse_feature_text(text: str) -> Feature:
    feature = Feature(name="")
    current_scenario: Optional[Scenario] = None
    in_background = False
    in_feature_desc = False
    pending_tags: list[str] = []
    desc_lines: list[str] = []

    for raw_line in text.splitlines():
        line = raw_line.strip()

        if not line or line.startswith("#"):
            continue

        if line.startswith("@"):
            pending_tags = [t.lstrip("@") for t in line.split()]
            continue

        lower = line.lower()

        if any(lower.startswith(p) for p in _FEATURE_PREFIXES):
            prefix = next(p for p in _FEATURE_PREFIXES if lower.startswith(p))
            feature.name = line[len(prefix):].strip()
            in_feature_desc = True
            continue

        if any(lower.startswith(p) for p in _BACKGROUND_PREFIXES):
            in_feature_desc = False
            in_background = True
            current_scenario = None
            continue

        if any(lower.startswith(p) for p in _SCENARIO_PREFIXES):
            in_feature_desc = False
            in_background = False
            prefix = next(p for p in _SCENARIO_PREFIXES if lower.startswith(p))
            name = line[len(prefix):].strip()
            current_scenario = Scenario(name=name, tags=pending_tags[:])
            feature.scenarios.append(current_scenario)
            pending_tags = []
            continue

        matched_kw = next(
            (kw for kw in _STEP_KEYWORDS if line.startswith(kw + " ") or line == kw),
            None,
        )
        if matched_kw:
            in_feature_desc = False
            step_text = line[len(matched_kw):].strip()
            step = Step(keyword=matched_kw, text=step_text)
            if in_background:
                feature.background_steps.append(step)
            elif current_scenario is not None:
                current_scenario.steps.append(step)
            continue

        if in_feature_desc:
            desc_lines.append(line)

    feature.description = "\n".join(desc_lines)
    return feature
