from __future__ import annotations

import re
import time
from dataclasses import dataclass
from typing import Optional

from ..generators.base import BaseLLMGenerator
from .gherkin_parser import GherkinParser, GherkinFeature
from .prompt_builder import PromptBuilder
from .languages import LANGUAGE_CATALOG


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------

@dataclass
class UnitTestResult:
    success: bool
    code: str = ""
    language_id: str = ""
    framework_id: str = ""
    num_tests: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    duration_seconds: float = 0.0
    error: Optional[str] = None

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens

    @property
    def file_extension(self) -> str:
        lang = LANGUAGE_CATALOG.get(self.language_id)
        if not lang:
            return ".txt"
        for fw in lang.frameworks:
            if fw.id == self.framework_id:
                return fw.file_extension
        return ".txt"


# ---------------------------------------------------------------------------
# Test counter — heuristic regex per language
# ---------------------------------------------------------------------------

_TEST_COUNTERS: dict[str, re.Pattern] = {
    "python":     re.compile(r"^\s*def test_", re.MULTILINE),
    "javascript": re.compile(r"\b(?:test|it)\s*\(", re.MULTILINE),
    "typescript": re.compile(r"\b(?:test|it)\s*\(", re.MULTILINE),
    "java":       re.compile(r"@Test\b", re.MULTILINE),
    "kotlin":     re.compile(r"@Test\b|^\s*test\s*\(", re.MULTILINE),
    "csharp":     re.compile(r"\[(?:Test|Fact|Theory|TestMethod)\]", re.MULTILINE),
    "go":         re.compile(r"^func Test", re.MULTILINE),
    "ruby":       re.compile(r"(?:^\s*it\s+['\"]|^\s*def test_)", re.MULTILINE),
}


def _count_tests(code: str, language_id: str) -> int:
    pattern = _TEST_COUNTERS.get(language_id)
    if not pattern:
        return 0
    return len(pattern.findall(code))


# ---------------------------------------------------------------------------
# Code fence stripper
# ---------------------------------------------------------------------------

_FENCE_RE = re.compile(
    r"^```[^\n]*\n(.*?)^```",
    re.DOTALL | re.MULTILINE,
)


def _strip_fences(text: str) -> str:
    """Remove markdown code fences the LLM may wrap around its output.

    Handles: fences not at position 0 (preamble text), multiple code blocks
    (returns the largest — most likely the full generated test suite).
    """
    matches = _FENCE_RE.findall(text.strip())
    if not matches:
        return text.strip()
    return max(matches, key=len)


# ---------------------------------------------------------------------------
# Main generator class
# ---------------------------------------------------------------------------

class UnitTestGenerator:
    """
    Generates unit test stubs for a given BDD text in the requested
    language/framework, using the same BaseLLMGenerator interface as the
    rest of the pipeline.
    """

    def __init__(self, generator: BaseLLMGenerator):
        self.generator = generator
        self._parser = GherkinParser()
        self._builder = PromptBuilder()

    def generate(
        self,
        bdd_text: str,
        language_id: str,
        framework_id: str,
    ) -> UnitTestResult:
        if not bdd_text.strip():
            return UnitTestResult(
                success=False,
                language_id=language_id,
                framework_id=framework_id,
                error="BDD text is empty.",
            )

        # Parse Gherkin into structured feature
        feature: GherkinFeature = self._parser.parse(bdd_text)

        if feature.scenario_count == 0:
            return UnitTestResult(
                success=False,
                language_id=language_id,
                framework_id=framework_id,
                error="No scenarios found in the provided BDD text.",
            )

        # Build prompt
        system_instruction, prompt = self._builder.build(
            feature=feature,
            language_id=language_id,
            framework_id=framework_id,
            original_bdd=bdd_text,
        )

        # Call LLM
        t0 = time.time()
        result = self.generator.generate(prompt, system_instruction=system_instruction)
        duration = time.time() - t0

        if not result.success:
            return UnitTestResult(
                success=False,
                language_id=language_id,
                framework_id=framework_id,
                input_tokens=result.input_tokens,
                output_tokens=result.output_tokens,
                duration_seconds=duration,
                error=result.error or "LLM generation failed.",
            )

        code = _strip_fences(result.bdd_text)
        num_tests = _count_tests(code, language_id)

        return UnitTestResult(
            success=True,
            code=code,
            language_id=language_id,
            framework_id=framework_id,
            num_tests=num_tests,
            input_tokens=result.input_tokens,
            output_tokens=result.output_tokens,
            duration_seconds=duration,
        )
