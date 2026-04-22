from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Optional


# Keywords that introduce a step. "And" / "But" inherit the previous keyword type.
_STEP_KEYWORDS = re.compile(
    r"^\s*(Given|When|Then|And|But)\s+(.+)$", re.IGNORECASE
)
_SCENARIO_KEYWORDS = re.compile(
    r"^\s*(Scenario(?:\s+Outline)?)\s*:\s*(.*)$", re.IGNORECASE
)
_FEATURE_KEYWORD = re.compile(r"^\s*Feature\s*:\s*(.*)$", re.IGNORECASE)
_BACKGROUND_KEYWORD = re.compile(r"^\s*Background\s*:\s*(.*)$", re.IGNORECASE)
_EXAMPLES_KEYWORD = re.compile(r"^\s*Examples\s*:.*$", re.IGNORECASE)
_TABLE_ROW = re.compile(r"^\s*\|.+\|")
_TAG_LINE = re.compile(r"^\s*@\S+")


@dataclass
class GherkinStep:
    keyword: str        # "Given" | "When" | "Then" | "And" | "But"
    canonical: str      # canonical keyword resolved from And/But ("Given"|"When"|"Then")
    text: str


@dataclass
class GherkinScenario:
    name: str
    steps: List[GherkinStep] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    is_outline: bool = False
    examples: List[List[str]] = field(default_factory=list)  # rows from Examples table

    @property
    def given_steps(self) -> List[GherkinStep]:
        return [s for s in self.steps if s.canonical == "Given"]

    @property
    def when_steps(self) -> List[GherkinStep]:
        return [s for s in self.steps if s.canonical == "When"]

    @property
    def then_steps(self) -> List[GherkinStep]:
        return [s for s in self.steps if s.canonical == "Then"]


@dataclass
class GherkinFeature:
    name: str
    description: str = ""
    background_steps: List[GherkinStep] = field(default_factory=list)
    scenarios: List[GherkinScenario] = field(default_factory=list)

    @property
    def scenario_count(self) -> int:
        return len(self.scenarios)


class GherkinParser:
    """Lightweight Gherkin parser — no external dependencies."""

    def parse(self, text: str) -> GherkinFeature:
        lines = text.splitlines()
        feature = GherkinFeature(name="")

        current_scenario: Optional[GherkinScenario] = None
        current_tags: List[str] = []
        in_background = False
        in_examples = False
        last_canonical = "Given"
        description_lines: List[str] = []
        collecting_description = False

        for raw_line in lines:
            line = raw_line.strip()

            # Skip blank lines and comments
            if not line or line.startswith("#"):
                continue

            # Tags
            if _TAG_LINE.match(line):
                current_tags = re.findall(r"@(\S+)", line)
                continue

            # Feature
            m = _FEATURE_KEYWORD.match(line)
            if m:
                feature.name = m.group(1).strip()
                collecting_description = True
                in_background = False
                continue

            # Background
            m = _BACKGROUND_KEYWORD.match(line)
            if m:
                in_background = True
                collecting_description = False
                current_scenario = None
                continue

            # Scenario / Scenario Outline
            m = _SCENARIO_KEYWORDS.match(line)
            if m:
                collecting_description = False
                in_background = False
                in_examples = False
                keyword = m.group(1)
                name = m.group(2).strip()
                current_scenario = GherkinScenario(
                    name=name,
                    tags=current_tags[:],
                    is_outline="outline" in keyword.lower(),
                )
                current_tags = []
                last_canonical = "Given"
                feature.scenarios.append(current_scenario)
                continue

            # Examples table header
            if _EXAMPLES_KEYWORD.match(line):
                in_examples = True
                continue

            # Table rows (inside Examples)
            if _TABLE_ROW.match(line) and in_examples and current_scenario:
                cells = [c.strip() for c in line.strip("|").split("|")]
                current_scenario.examples.append(cells)
                continue

            # Step
            m = _STEP_KEYWORDS.match(line)
            if m:
                keyword = m.group(1).capitalize()
                text = m.group(2).strip()
                in_examples = False

                if keyword in ("And", "But"):
                    canonical = last_canonical
                else:
                    canonical = keyword
                    last_canonical = canonical

                step = GherkinStep(keyword=keyword, canonical=canonical, text=text)

                if in_background:
                    feature.background_steps.append(step)
                elif current_scenario is not None:
                    current_scenario.steps.append(step)
                continue

            # Feature description lines (free text before first Scenario)
            if collecting_description and feature.name:
                description_lines.append(line)

        feature.description = "\n".join(description_lines).strip()
        return feature
