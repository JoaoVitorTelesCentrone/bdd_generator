"""Autoresearch API — autonomous optimizer for BDD scorer configuration.

Routes:
  POST  /api/autoresearch/run             Start an autoresearch run (async)
  GET   /api/autoresearch/runs            List recent runs (most recent first)
  GET   /api/autoresearch/runs/{id}       Run detail + full experiments log
  GET   /api/autoresearch/runs/{id}/config  Download best_config.json
  WS    /ws/autoresearch/run/{id}         Stream live experiment progress
"""
import asyncio
import csv
import json
import random
import sys
import threading
import time
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field

_ROOT = Path(__file__).parent.parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

router = APIRouter(tags=["autoresearch"])

# ── In-memory state ───────────────────────────────────────────────────────────

_runs: dict[int, dict] = {}
_run_counter: int = 0
_runs_lock = threading.Lock()

_log_queues: dict[int, list[asyncio.Queue]] = {}
_log_lock = threading.Lock()

_event_loop: asyncio.AbstractEventLoop | None = None


def _next_id() -> int:
    global _run_counter
    with _runs_lock:
        _run_counter += 1
        return _run_counter


def _broadcast(run_id: int, payload: dict) -> None:
    with _log_lock:
        queues = list(_log_queues.get(run_id, []))
    if not queues:
        return
    loop = _event_loop
    if loop is not None and loop.is_running():
        for q in queues:
            loop.call_soon_threadsafe(q.put_nowait, payload)
    else:
        for q in queues:
            try:
                q.put_nowait(payload)
            except Exception:
                pass


# ── Pydantic schemas ──────────────────────────────────────────────────────────

class AutoresearchRunRequest(BaseModel):
    stories: list[str] = Field(..., min_length=1, description="User stories para avaliação")
    model: str = Field("flash", description="Modelo LLM (flash, pro, sonnet, opus…)")
    n_experiments: int = Field(30, ge=1, le=200, description="Número de mutações a testar")
    sample_size: int = Field(10, ge=1, le=100, description="Stories por experimento (orçamento fixo)")
    seed: Optional[int] = Field(None, description="Semente aleatória para reprodutibilidade")
    resume_config: Optional[dict] = Field(None, description="ResearchConfig JSON para retomar de um ponto anterior")


class ExperimentRow(BaseModel):
    experiment: int
    mutation: str
    cobertura: float
    clareza: float
    estrutura: float
    executabilidade: float
    threshold: float
    max_attempts: int
    avg_score: float
    n_approved: int
    total_tokens: int
    accepted: bool
    is_best: bool


class AutoresearchRunSummary(BaseModel):
    id: int
    started_at: float
    finished_at: Optional[float] = None
    status: str
    model: str
    n_experiments: int
    sample_size: int
    seed: Optional[int] = None
    baseline_score: Optional[float] = None
    best_score: Optional[float] = None
    improvement: Optional[float] = None
    n_accepted: Optional[int] = None
    total_tokens: Optional[int] = None
    duration_seconds: Optional[float] = None
    error: Optional[str] = None


class AutoresearchRunDetail(AutoresearchRunSummary):
    best_config: Optional[dict] = None
    experiments: list[ExperimentRow] = []


# ── Background task ───────────────────────────────────────────────────────────

def _run_autoresearch_task(data: dict) -> None:
    run_id: int = data["run_id"]

    try:
        from src.autoresearch.config import ResearchConfig
        from src.autoresearch.loop import run_autoresearch
        from src.generators.gemini_generator import GeminiGenerator
        from src.generators.claude_generator import ClaudeGenerator

        _GEMINI_ALIASES = {
            "flash", "flash-lite", "pro", "flash-1.5",
            "gemini-2.0-flash", "gemini-2.0-flash-lite",
            "gemini-1.5-pro", "gemini-1.5-flash",
        }
        model = data["model"]
        if model in _GEMINI_ALIASES or model.startswith("gemini"):
            generator = GeminiGenerator(model=model)
        else:
            generator = ClaudeGenerator(model=model)

        initial_config: Optional[ResearchConfig] = None
        if data.get("resume_config"):
            initial_config = ResearchConfig(**data["resume_config"])

        run_dir = _ROOT / f"results/autoresearch_{run_id}"

        _broadcast(run_id, {
            "type": "log",
            "message": (
                f"Iniciando autoresearch | modelo: {model} | "
                f"{data['n_experiments']} experimentos | "
                f"sample: {data['sample_size']} stories"
            ),
        })

        def on_experiment(i, mutation_desc, config, result, accepted, is_best):
            _broadcast(run_id, {
                "type": "experiment",
                "i": i,
                "total": data["n_experiments"],
                "mutation": mutation_desc,
                "avg_score": result.avg_score,
                "n_approved": result.n_approved,
                "n_stories": result.n_stories,
                "total_tokens": result.total_tokens,
                "accepted": accepted,
                "is_best": is_best,
                "config": {
                    "cobertura":       config.cobertura,
                    "clareza":         config.clareza,
                    "estrutura":       config.estrutura,
                    "executabilidade": config.executabilidade,
                    "threshold":       config.threshold,
                    "max_attempts":    config.max_attempts,
                },
            })
            status_tag = "aceito" if accepted else "rejeitado"
            best_tag   = "  [novo melhor]" if is_best else ""
            _broadcast(run_id, {
                "type": "log",
                "message": (
                    f"[{i}/{data['n_experiments']}] {mutation_desc} "
                    f"-> score={result.avg_score:.4f} {status_tag}{best_tag}"
                ),
            })

        ar_result = run_autoresearch(
            stories=data["stories"],
            generator=generator,
            initial_config=initial_config,
            n_experiments=data["n_experiments"],
            run_dir=run_dir,
            seed=data.get("seed"),
            on_experiment=on_experiment,
        )

        improvement = round(ar_result.best_score - ar_result.baseline_score, 4)
        with _runs_lock:
            _runs[run_id].update({
                "status":           "done",
                "finished_at":      time.time(),
                "baseline_score":   ar_result.baseline_score,
                "best_score":       ar_result.best_score,
                "improvement":      improvement,
                "n_accepted":       ar_result.n_accepted,
                "total_tokens":     ar_result.total_tokens,
                "duration_seconds": ar_result.duration_seconds,
                "best_config":      json.loads(ar_result.best_config_path.read_text(encoding="utf-8")),
            })

        _broadcast(run_id, {
            "type":           "done",
            "status":         "done",
            "baseline_score": ar_result.baseline_score,
            "best_score":     ar_result.best_score,
            "improvement":    improvement,
            "n_accepted":     ar_result.n_accepted,
            "total_tokens":   ar_result.total_tokens,
        })

    except Exception as exc:
        with _runs_lock:
            _runs[run_id].update({
                "status":      "error",
                "finished_at": time.time(),
                "error":       str(exc),
            })
        _broadcast(run_id, {"type": "done", "status": "error", "message": str(exc)})


# ── REST routes ───────────────────────────────────────────────────────────────

@router.post("/api/autoresearch/run", status_code=202)
def start_run(req: AutoresearchRunRequest, background_tasks: BackgroundTasks):
    """Start an autoresearch run in the background.
    Returns run_id immediately; use the WebSocket or GET endpoint to track progress."""
    if not req.stories:
        raise HTTPException(status_code=422, detail="Envie ao menos uma user story.")

    stories = req.stories
    if len(stories) > req.sample_size:
        rng = random.Random(req.seed)
        stories = rng.sample(stories, req.sample_size)

    run_id = _next_id()
    with _runs_lock:
        _runs[run_id] = {
            "id":               run_id,
            "started_at":       time.time(),
            "finished_at":      None,
            "status":           "running",
            "model":            req.model,
            "n_experiments":    req.n_experiments,
            "sample_size":      len(stories),
            "seed":             req.seed,
            "baseline_score":   None,
            "best_score":       None,
            "improvement":      None,
            "n_accepted":       None,
            "total_tokens":     None,
            "duration_seconds": None,
            "best_config":      None,
            "error":            None,
        }

    background_tasks.add_task(_run_autoresearch_task, {
        "run_id":        run_id,
        "stories":       stories,
        "model":         req.model,
        "n_experiments": req.n_experiments,
        "sample_size":   len(stories),
        "seed":          req.seed,
        "resume_config": req.resume_config,
    })

    return {"run_id": run_id, "status": "queued"}


@router.get("/api/autoresearch/runs", response_model=list[AutoresearchRunSummary])
def list_runs(limit: int = 20):
    """List recent autoresearch runs, most recent first."""
    with _runs_lock:
        runs = sorted(_runs.values(), key=lambda r: r["started_at"], reverse=True)[:limit]
    return runs


@router.get("/api/autoresearch/runs/{run_id}", response_model=AutoresearchRunDetail)
def get_run(run_id: int):
    """Full run detail: metadata + complete experiments log read from CSV."""
    with _runs_lock:
        run = _runs.get(run_id)
    if not run:
        raise HTTPException(status_code=404, detail=f"Run {run_id} não encontrado")

    experiments: list[dict] = []
    log_path = _ROOT / f"results/autoresearch_{run_id}" / "experiments.csv"
    if log_path.exists():
        with open(log_path, encoding="utf-8") as f:
            for row in csv.DictReader(f):
                experiments.append({
                    "experiment":      int(row["experiment"]),
                    "mutation":        row["mutation"],
                    "cobertura":       float(row["cobertura"]),
                    "clareza":         float(row["clareza"]),
                    "estrutura":       float(row["estrutura"]),
                    "executabilidade": float(row["executabilidade"]),
                    "threshold":       float(row["threshold"]),
                    "max_attempts":    int(row["max_attempts"]),
                    "avg_score":       float(row["avg_score"]),
                    "n_approved":      int(row["n_approved"]),
                    "total_tokens":    int(row["total_tokens"]),
                    "accepted":        row["accepted"].strip().lower() == "true",
                    "is_best":         row["is_best"].strip().lower() == "true",
                })

    return {**run, "experiments": experiments}


@router.get("/api/autoresearch/runs/{run_id}/config")
def get_best_config(run_id: int):
    """Return the best ResearchConfig found as JSON (downloadable)."""
    with _runs_lock:
        run = _runs.get(run_id)
    if not run:
        raise HTTPException(status_code=404, detail=f"Run {run_id} não encontrado")
    if run["status"] != "done":
        raise HTTPException(status_code=409, detail="Run ainda não concluído")

    config_path = _ROOT / f"results/autoresearch_{run_id}" / "best_config.json"
    if not config_path.exists():
        raise HTTPException(status_code=404, detail="best_config.json não encontrado")

    return json.loads(config_path.read_text(encoding="utf-8"))


# ── WebSocket ─────────────────────────────────────────────────────────────────

@router.websocket("/ws/autoresearch/run/{run_id}")
async def ws_autoresearch_log(websocket: WebSocket, run_id: int):  # noqa: C901
    global _event_loop
    """Stream live autoresearch progress.

    Event shapes:
      {"type": "log",        "message": "..."}
      {"type": "experiment", "i": N, "total": M, "mutation": "...",
                             "avg_score": 7.4, "accepted": true, "is_best": false,
                             "config": {...}}
      {"type": "done",       "status": "done"|"error", "best_score": 7.8, ...}
      {"type": "ping"}       (keepalive every 30s)
    """
    await websocket.accept()
    _event_loop = asyncio.get_running_loop()

    queue: asyncio.Queue = asyncio.Queue(maxsize=500)
    with _log_lock:
        _log_queues.setdefault(run_id, []).append(queue)

    try:
        with _runs_lock:
            run = _runs.get(run_id)

        if run and run["status"] != "running":
            await websocket.send_json({"type": "done", "status": run["status"]})
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
