"""BIST REST API — test runs, stats, and live WebSocket streaming.

Routes:
  POST  /api/bist/run          Trigger full pipeline (generate + execute) async
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

from fastapi import APIRouter, BackgroundTasks, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

_ROOT = Path(__file__).parent.parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from bist.bist_database import get_database

router = APIRouter(tags=["bist"])

_db = get_database()

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
    env_url: str
    status: str
    duration_ms: int
    feature_path: str
    scenarios: list[ScenarioOut] = []


class RunSummaryOut(BaseModel):
    id: int
    started_at: float
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
def trigger_run(req: RunRequest, background_tasks: BackgroundTasks):
    """Trigger the full BDD pipeline (generate + execute) in a background thread."""
    run_id = _db.create_run(req.env_url)
    background_tasks.add_task(_run_pipeline, {
        "run_id":       run_id,
        "user_story":   req.user_story,
        "env_url":      req.env_url,
        "model":        req.model,
        "threshold":    req.threshold,
        "max_attempts": req.max_attempts,
    })
    return {"run_id": run_id, "status": "queued"}


@router.get("/api/bist/runs", response_model=list[RunSummaryOut])
def list_runs(limit: int = 20):
    """List recent test runs (most recent first)."""
    return _db.get_runs(limit=limit)


@router.get("/api/bist/runs/{run_id}", response_model=RunOut)
def get_run(run_id: int):
    """Full run detail: scenarios, steps, errors, screenshots."""
    data = _db.get_run_detail(run_id)
    if not data:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")
    return data


@router.get("/api/bist/stats", response_model=StatsOut)
def get_stats():
    """Aggregate stats: pass rate, average duration, flaky scenarios, trend."""
    runs = _db.get_runs(limit=10_000)
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
        flaky_scenarios=_db.get_flaky_scenarios(limit=10),
        runs_over_time=_db.get_runs_trend(days=30),
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
