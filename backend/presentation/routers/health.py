"""GET /health — liveness probe."""
from fastapi import APIRouter

router = APIRouter(tags=["infra"])


@router.get("/health")
def health():
    return {"status": "ok", "version": "1.0.0"}
