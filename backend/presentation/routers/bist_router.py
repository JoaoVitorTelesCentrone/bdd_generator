"""BIST REST API — test runs, stats, and live WebSocket streaming.

Routes:
  POST  /api/bist/run          Trigger full pipeline (generate + execute) async
  POST  /api/bist/execute      Execute a pre-generated .feature file async
  GET   /api/bist/runs         List recent test runs
  GET   /api/bist/runs/{id}    Run detail with scenarios + steps
  GET   /api/bist/stats        Aggregate stats: pass rate, flaky, trend
  WS    /ws/bist/run/{id}      Stream live logs while pipeline runs
"""
import asyncio
import sys
import threading
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Header, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

_ROOT = Path(__file__).parent.parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from bist.bist_database import get_database
from bist.bist_tenants import TenantManager, TierLimitExceeded
from bist.bist_billing import BillingManager

router = APIRouter(tags=["bist"])

_db      = get_database()
_tenants = TenantManager()
_billing = BillingManager()


def _resolve_tenant(x_api_key: Optional[str]) -> Optional[dict]:
    """Validate X-Api-Key header and return tenant info, or None if no key provided."""
    if not x_api_key:
        return None
    info = _tenants.validate_api_key(x_api_key)
    if info is None:
        raise HTTPException(status_code=401, detail="Invalid or revoked API key")
    return info

# In-memory log queues: run_id → [Queue, ...]
_log_queues: dict[int, list[asyncio.Queue]] = {}
_log_lock = threading.Lock()


# ── Helpers ───────────────────────────────────────────────────────────────────

def _broadcast(run_id: int, payload: dict) -> None:
    with _log_lock:
        queues = list(_log_queues.get(run_id, []))
    for q in queues:
        try:
            q.put_nowait(payload)
        except Exception:
            pass


def _run_execute_only(data: dict) -> None:
    """Background thread: execute a pre-generated .feature file."""
    run_id: int = data["run_id"]
    try:
        from bist.bist_executor import BISTExecutor

        _broadcast(run_id, {"type": "log", "message": f"Executando feature: {data['feature_path']}"})

        executor = BISTExecutor(db=_db)
        exec_result = executor.execute(data["feature_path"], data["env_url"])

        status = exec_result.status
        _db.finish_run(run_id, status, exec_result.duration_ms)
        _broadcast(run_id, {"type": "done", "status": status})

    except Exception as exc:
        _db.finish_run(run_id, "error", 0)
        _broadcast(run_id, {"type": "done", "status": "error", "message": str(exc)})


def _run_pipeline(data: dict) -> None:
    """Background thread: generate BDD then execute tests."""
    run_id: int = data["run_id"]
    try:
        from bist.bist_agent import BISTAgent
        from bist.bist_executor import BISTExecutor

        _broadcast(run_id, {"type": "log", "message": "Iniciando geração de BDD..."})

        agent = BISTAgent(
            model=data.get("model", "sonnet"),
            threshold=data.get("threshold", 7.0),
            max_attempts=data.get("max_attempts", 5),
        )
        agent_result = agent.generate(data["user_story"])

        _broadcast(run_id, {
            "type": "log",
            "message": f"BDD gerado — score {agent_result.score_final:.1f} em "
                       f"{agent_result.attempts} tentativa(s). Executando testes...",
        })

        executor = BISTExecutor(db=_db)
        exec_result = executor.execute(agent_result.feature_path, data["env_url"])

        status = exec_result.status
        _db.finish_run(run_id, status, exec_result.duration_ms)
        _broadcast(run_id, {"type": "done", "status": status})

    except Exception as exc:
        _db.finish_run(run_id, "error", 0)
        _broadcast(run_id, {"type": "done", "status": "error", "message": str(exc)})


# ── Pydantic schemas ──────────────────────────────────────────────────────────

class RunRequest(BaseModel):
    user_story: str
    env_url: str
    model: str = "sonnet"
    threshold: float = 7.0
    max_attempts: int = 5


class ExecuteRequest(BaseModel):
    feature_path: str
    env_url: str


class StepOut(BaseModel):
    id: int
    scenario_id: int
    step_text: str
    status: str
    duration_ms: int
    screenshot_path: str


class ScenarioOut(BaseModel):
    id: int
    run_id: int
    name: str
    status: str
    duration_ms: int
    error: str
    video_path: str
    steps: list[StepOut] = []


class RunOut(BaseModel):
    id: int
    started_at: float
    finished_at: Optional[float] = None
    env_url: str
    status: str
    duration_ms: int
    feature_path: str
    scenarios: list[ScenarioOut] = []


class RunSummaryOut(BaseModel):
    id: int
    started_at: float
    finished_at: Optional[float] = None
    env_url: str
    status: str
    duration_ms: int
    feature_path: str


class FlakyScenario(BaseModel):
    name: str
    total_runs: int
    failures: int
    failure_rate: float


class StatsOut(BaseModel):
    total_runs: int
    passed_runs: int
    failed_runs: int
    pass_rate: float
    avg_duration_ms: float
    flaky_scenarios: list[FlakyScenario]
    runs_over_time: list[dict]


# ── REST Routes ───────────────────────────────────────────────────────────────

@router.post("/api/bist/run", status_code=202)
def trigger_run(
    req: RunRequest,
    background_tasks: BackgroundTasks,
    x_api_key: Optional[str] = Header(default=None),
):
    """Trigger the full BDD pipeline (generate + execute) in a background thread."""
    tenant = _resolve_tenant(x_api_key)
    tenant_id: Optional[int] = tenant["tenant_id"] if tenant else None
    tier = tenant["tier"] if tenant else "free"

    if tenant_id is not None:
        monthly_runs = _billing.get_monthly_usage(tenant_id, "run_started")
        try:
            _tenants.enforce_run_limit(tenant_id, tier, monthly_runs)
        except TierLimitExceeded as exc:
            raise HTTPException(status_code=402, detail=str(exc))
        _billing.record_usage(tenant_id, "run_started")

    run_id = _db.create_run(req.env_url, tenant_id=tenant_id)
    background_tasks.add_task(_run_pipeline, {
        "run_id":       run_id,
        "user_story":   req.user_story,
        "env_url":      req.env_url,
        "model":        req.model,
        "threshold":    req.threshold,
        "max_attempts": req.max_attempts,
    })
    return {"run_id": run_id, "status": "queued", "tenant_id": tenant_id}


@router.post("/api/bist/execute", status_code=202)
def execute_run(
    req: ExecuteRequest,
    background_tasks: BackgroundTasks,
    x_api_key: Optional[str] = Header(default=None),
):
    """Execute a pre-generated .feature file in a background thread (no BDD generation)."""
    tenant = _resolve_tenant(x_api_key)
    tenant_id: Optional[int] = tenant["tenant_id"] if tenant else None

    run_id = _db.create_run(req.env_url, feature_path=req.feature_path, tenant_id=tenant_id)
    background_tasks.add_task(_run_execute_only, {
        "run_id":        run_id,
        "feature_path":  req.feature_path,
        "env_url":       req.env_url,
    })
    return {"run_id": run_id, "status": "queued", "tenant_id": tenant_id}


@router.get("/api/bist/runs", response_model=list[RunSummaryOut])
def list_runs(limit: int = 20, x_api_key: Optional[str] = Header(default=None)):
    """List recent test runs (most recent first). Scoped to tenant when key provided."""
    tenant = _resolve_tenant(x_api_key)
    tenant_id = tenant["tenant_id"] if tenant else None
    return _db.get_runs(limit=limit, tenant_id=tenant_id)


@router.get("/api/bist/runs/{run_id}", response_model=RunOut)
def get_run(run_id: int, x_api_key: Optional[str] = Header(default=None)):
    """Full run detail: scenarios, steps, errors, screenshots."""
    tenant = _resolve_tenant(x_api_key)
    tenant_id = tenant["tenant_id"] if tenant else None
    data = _db.get_run_detail(run_id, tenant_id=tenant_id)
    if not data:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")
    return data


@router.get("/api/bist/stats", response_model=StatsOut)
def get_stats(x_api_key: Optional[str] = Header(default=None)):
    """Aggregate stats: pass rate, average duration, flaky scenarios, trend."""
    tenant = _resolve_tenant(x_api_key)
    tenant_id = tenant["tenant_id"] if tenant else None
    runs = _db.get_runs(limit=10_000, tenant_id=tenant_id)
    total = len(runs)
    passed = sum(1 for r in runs if r["status"] == "passed")
    failed = sum(1 for r in runs if r["status"] in ("failed", "error"))
    avg_dur = sum(r["duration_ms"] for r in runs) / total if total else 0.0

    return StatsOut(
        total_runs=total,
        passed_runs=passed,
        failed_runs=failed,
        pass_rate=round(passed / total * 100, 1) if total else 0.0,
        avg_duration_ms=round(avg_dur, 1),
        flaky_scenarios=_db.get_flaky_scenarios(limit=10, tenant_id=tenant_id),
        runs_over_time=_db.get_runs_trend(days=30, tenant_id=tenant_id),
    )


# ── WebSocket ─────────────────────────────────────────────────────────────────

@router.websocket("/ws/bist/run/{run_id}")
async def ws_run_log(websocket: WebSocket, run_id: int):
    """Stream live pipeline logs.  Sends {type:"log",message:"..."} events,
    followed by {type:"done",status:"passed"|"failed"|"error"} when complete.
    Sends {type:"ping"} every 30 s while waiting to keep the connection alive.
    """
    await websocket.accept()

    queue: asyncio.Queue = asyncio.Queue(maxsize=200)
    with _log_lock:
        _log_queues.setdefault(run_id, []).append(queue)

    try:
        # If run is already finished, report immediately
        run = _db.get_run_detail(run_id)
        if run and run.get("status") not in ("running",):
            await websocket.send_json({"type": "done", "status": run.get("status", "unknown")})
            return

        while True:
            try:
                msg = await asyncio.wait_for(queue.get(), timeout=30.0)
                await websocket.send_json(msg)
                if msg.get("type") == "done":
                    break
            except asyncio.TimeoutError:
                await websocket.send_json({"type": "ping"})

    except WebSocketDisconnect:
        pass
    finally:
        with _log_lock:
            qs = _log_queues.get(run_id, [])
            if queue in qs:
                qs.remove(queue)
            if not qs:
                _log_queues.pop(run_id, None)
