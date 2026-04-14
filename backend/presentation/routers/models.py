"""GET /api/models — available LLM model catalogue."""
from fastapi import APIRouter
from backend.infrastructure.generator_factory import GeneratorFactory

router = APIRouter(prefix="/api", tags=["models"])


@router.get("/models")
def list_models():
    return {"models": GeneratorFactory.catalogue()}
