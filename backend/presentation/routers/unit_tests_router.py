"""
POST /api/unit-tests/generate  — generate unit test stubs from BDD Gherkin
GET  /api/unit-tests/languages  — list supported languages and frameworks
"""
import logging
from fastapi import APIRouter, HTTPException

_log = logging.getLogger(__name__)

from backend.container import get_unit_test_use_case
from backend.application.dtos import UnitTestInputDTO
from backend.presentation.schemas.unit_tests import (
    UnitTestRequest,
    UnitTestResponse,
    LanguageCatalogResponse,
)
from src.unit_tests.languages import get_catalog_dict, validate_language_framework

router = APIRouter(prefix="/api/unit-tests", tags=["unit-tests"])


@router.get("/languages", response_model=LanguageCatalogResponse)
def list_languages():
    """Return all supported languages and their available test frameworks."""
    return get_catalog_dict()


@router.post("/generate", response_model=UnitTestResponse)
def generate_unit_tests(req: UnitTestRequest):
    """Generate unit test stubs in the requested language/framework from BDD Gherkin."""
    if not validate_language_framework(req.language, req.framework):
        raise HTTPException(
            status_code=422,
            detail=(
                f"Unsupported combination: language='{req.language}', "
                f"framework='{req.framework}'. "
                f"Call GET /api/unit-tests/languages for the full catalog."
            ),
        )

    try:
        use_case = get_unit_test_use_case(req.model)
        result = use_case.execute(
            UnitTestInputDTO(
                bdd_text=req.bdd_text,
                language=req.language,
                framework=req.framework,
                model=req.model,
            )
        )
    except ValueError as exc:
        _log.error("Unit test generation failed (ValueError): %s", exc, exc_info=True)
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception as exc:
        _log.error("Unit test generation failed (Exception): %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=f"{type(exc).__name__}: {exc}")

    return UnitTestResponse(
        code=result.code,
        language=result.language,
        framework=result.framework,
        file_extension=result.file_extension,
        num_tests=result.num_tests,
        total_tokens=result.total_tokens,
        duration_seconds=result.duration_seconds,
    )
