"""POST /api/generate — BDD generation with auto-refinement."""
from fastapi import APIRouter, HTTPException

from backend.container import get_generate_use_case
from backend.application.dtos import GenerateInputDTO
from backend.presentation.schemas.generate import GenerateRequest, GenerateResponse
from backend.presentation.schemas.common import ScoreSchema

router = APIRouter(prefix="/api", tags=["generate"])


@router.post("/generate", response_model=GenerateResponse)
def generate(req: GenerateRequest):
    try:
        use_case = get_generate_use_case(req.model, req.threshold)
        result   = use_case.execute(
            GenerateInputDTO(
                story           = req.story,
                model           = req.model,
                threshold       = req.threshold,
                max_attempts    = req.max_attempts,
                research        = req.research,
                until_converged = req.until_converged,
            )
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    return GenerateResponse(
        bdd_text         = result.bdd_text,
        score            = ScoreSchema(**vars(result.score)),
        attempts         = result.attempts,
        total_tokens     = result.total_tokens,
        research_tokens  = result.research_tokens,
        converged        = result.converged,
        duration_seconds = result.duration_seconds,
    )
