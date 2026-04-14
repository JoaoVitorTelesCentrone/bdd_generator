"""POST /api/evaluate — score a pre-written BDD text."""
from fastapi import APIRouter, HTTPException

from backend.container import get_evaluate_use_case
from backend.application.dtos import EvaluateInputDTO
from backend.presentation.schemas.evaluate import EvaluateRequest, EvaluateResponse
from backend.presentation.schemas.common import ScoreSchema

router = APIRouter(prefix="/api", tags=["evaluate"])


@router.post("/evaluate", response_model=EvaluateResponse)
def evaluate(req: EvaluateRequest):
    try:
        use_case = get_evaluate_use_case(req.threshold)
        result   = use_case.execute(
            EvaluateInputDTO(
                story     = req.story,
                bdd_text  = req.bdd_text,
                threshold = req.threshold,
            )
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    return EvaluateResponse(score=ScoreSchema(**vars(result.score)))
