"""HTTP request/response schemas for POST /api/unit-tests/generate and GET /api/unit-tests/languages."""
from pydantic import BaseModel, Field
from typing import List, Dict, Any


class UnitTestRequest(BaseModel):
    bdd_text: str = Field(..., min_length=10, description="Gherkin BDD text to convert into unit tests")
    language: str = Field(..., description="Target language id: python | javascript | typescript | java | csharp | go | ruby | kotlin")
    framework: str = Field(..., description="Test framework id for the chosen language (e.g. pytest, jest, junit5)")
    model: str = Field(
        default="flash",
        description="LLM model alias: flash | pro | flash-lite | sonnet | opus | haiku",
    )


class UnitTestResponse(BaseModel):
    code: str
    language: str
    framework: str
    file_extension: str
    num_tests: int
    total_tokens: int
    duration_seconds: float


class FrameworkSchema(BaseModel):
    id: str
    label: str
    file_extension: str
    hint: str


class LanguageSchema(BaseModel):
    id: str
    label: str
    default_framework: str
    frameworks: List[FrameworkSchema]


LanguageCatalogResponse = Dict[str, Any]
