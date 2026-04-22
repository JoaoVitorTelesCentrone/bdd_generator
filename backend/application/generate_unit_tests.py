"""
Application layer — GenerateUnitTestsUseCase.

Orchestrates: parse Gherkin → build prompt → call LLM → return test code.
Depends only on the domain IGenerator interface; zero FastAPI / Pydantic.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from backend.domain.interfaces import IGenerator
from backend.application.dtos import UnitTestInputDTO, UnitTestOutputDTO
from src.unit_tests.generator import UnitTestGenerator


class GenerateUnitTestsUseCase:

    def __init__(self, generator: IGenerator) -> None:
        self._generator = generator

    def execute(self, dto: UnitTestInputDTO) -> UnitTestOutputDTO:
        gen = UnitTestGenerator(generator=self._generator)  # type: ignore[arg-type]
        result = gen.generate(
            bdd_text=dto.bdd_text,
            language_id=dto.language,
            framework_id=dto.framework,
        )

        if not result.success:
            raise ValueError(result.error or "Unit test generation failed.")

        return UnitTestOutputDTO(
            code=result.code,
            language=result.language_id,
            framework=result.framework_id,
            file_extension=result.file_extension,
            num_tests=result.num_tests,
            total_tokens=result.total_tokens,
            duration_seconds=round(result.duration_seconds, 2),
        )
