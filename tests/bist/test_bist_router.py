"""
Tests for backend/presentation/routers/bist_router.py — BIST REST API.

Cenários cobertos:
  POST /api/bist/run:
    - retorna 202 com run_id e status "queued"
    - cria um run no banco em estado "running"
    - retorna 422 quando user_story está ausente
    - retorna 422 quando env_url está ausente

  GET /api/bist/runs:
    - retorna 200 com lista vazia quando não há runs
    - retorna runs existentes em formato correto
    - parâmetro limit é respeitado
    - campos obrigatórios presentes em cada run

  GET /api/bist/runs/{id}:
    - retorna 200 com detalhes do run
    - retorna 404 quando run não existe
    - resposta inclui lista de cenários (mesmo que vazia)
    - cenários incluem steps aninhados

  GET /api/bist/stats:
    - retorna 200 com estrutura completa
    - retorna zeros quando não há runs
    - pass_rate calculado corretamente
    - flaky_scenarios e runs_over_time são listas

  WS /ws/bist/run/{id}:
    - envia {type:"done"} imediatamente se run já finalizou
    - envia {type:"done"} com status correto
"""
import sys, os, time
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from bist.bist_database import BISTDatabase
import backend.presentation.routers.bist_router as bist_router_module
from backend.presentation.routers.bist_router import router


# ── fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def test_db(tmp_path):
    """Fresh in-memory SQLite database for each test."""
    return BISTDatabase(db_path=tmp_path / "router_test.db")


@pytest.fixture
def client(test_db):
    """TestClient backed by an isolated test database."""
    app = FastAPI()
    app.include_router(router)
    # Redirect the module-level _db to our test database
    bist_router_module._db = test_db
    return TestClient(app, raise_server_exceptions=True)


# ── POST /api/bist/run ────────────────────────────────────────────────────────

class TestTriggerRun:

    def test_returns_202_with_run_id(self, client, test_db):
        with patch.object(bist_router_module, "_run_pipeline"):
            resp = client.post("/api/bist/run", json={
                "user_story": "Como usuário quero fazer login",
                "env_url": "https://staging.example.com",
            })
        assert resp.status_code == 202
        body = resp.json()
        assert "run_id" in body
        assert isinstance(body["run_id"], int)
        assert body["status"] == "queued"

    def test_creates_run_in_database(self, client, test_db):
        with patch.object(bist_router_module, "_run_pipeline"):
            resp = client.post("/api/bist/run", json={
                "user_story": "Como usuário quero fazer login",
                "env_url": "https://staging.example.com",
            })
        run_id = resp.json()["run_id"]
        detail = test_db.get_run_detail(run_id)
        assert detail != {}
        assert detail["env_url"] == "https://staging.example.com"
        assert detail["status"] == "running"

    def test_missing_user_story_returns_422(self, client):
        resp = client.post("/api/bist/run", json={"env_url": "https://x.com"})
        assert resp.status_code == 422

    def test_missing_env_url_returns_422(self, client):
        resp = client.post("/api/bist/run", json={
            "user_story": "Como usuário quero fazer login",
        })
        assert resp.status_code == 422

    def test_default_model_is_sonnet(self, client, test_db):
        captured: list[dict] = []

        def capture(data):
            captured.append(data)

        with patch.object(bist_router_module, "_run_pipeline", side_effect=capture):
            client.post("/api/bist/run", json={
                "user_story": "story",
                "env_url": "https://x.com",
            })
        # Background tasks run synchronously in TestClient
        assert captured[0]["model"] == "sonnet"

    def test_custom_model_forwarded(self, client, test_db):
        captured: list[dict] = []

        def capture(data):
            captured.append(data)

        with patch.object(bist_router_module, "_run_pipeline", side_effect=capture):
            client.post("/api/bist/run", json={
                "user_story": "story",
                "env_url": "https://x.com",
                "model": "flash",
                "threshold": 8.5,
                "max_attempts": 3,
            })
        d = captured[0]
        assert d["model"] == "flash"
        assert d["threshold"] == 8.5
        assert d["max_attempts"] == 3


# ── GET /api/bist/runs ────────────────────────────────────────────────────────

class TestListRuns:

    def test_returns_empty_list_when_no_runs(self, client):
        resp = client.get("/api/bist/runs")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_returns_existing_runs(self, client, test_db):
        rid = test_db.create_run("https://a.com", "login.feature")
        test_db.finish_run(rid, "passed", 1234)

        resp = client.get("/api/bist/runs")
        assert resp.status_code == 200
        runs = resp.json()
        assert len(runs) == 1
        assert runs[0]["id"] == rid
        assert runs[0]["status"] == "passed"
        assert runs[0]["env_url"] == "https://a.com"

    def test_limit_parameter_respected(self, client, test_db):
        for i in range(5):
            test_db.create_run(f"https://env{i}.com")

        resp = client.get("/api/bist/runs?limit=3")
        assert resp.status_code == 200
        assert len(resp.json()) == 3

    def test_required_fields_present(self, client, test_db):
        rid = test_db.create_run("https://x.com")
        test_db.finish_run(rid, "passed", 500)

        resp = client.get("/api/bist/runs")
        run = resp.json()[0]
        for field in ("id", "started_at", "env_url", "status", "duration_ms", "feature_path"):
            assert field in run, f"missing field: {field}"

    def test_runs_returned_most_recent_first(self, client, test_db):
        rid_a = test_db.create_run("https://a.com")
        time.sleep(0.01)
        rid_b = test_db.create_run("https://b.com")

        runs = client.get("/api/bist/runs").json()
        assert runs[0]["id"] == rid_b
        assert runs[1]["id"] == rid_a


# ── GET /api/bist/runs/{id} ───────────────────────────────────────────────────

class TestGetRun:

    def test_returns_200_with_run_detail(self, client, test_db):
        rid = test_db.create_run("https://x.com", "login.feature")
        test_db.finish_run(rid, "passed", 2000)

        resp = client.get(f"/api/bist/runs/{rid}")
        assert resp.status_code == 200
        body = resp.json()
        assert body["id"] == rid
        assert body["status"] == "passed"
        assert body["duration_ms"] == 2000

    def test_returns_404_for_unknown_id(self, client):
        resp = client.get("/api/bist/runs/99999")
        assert resp.status_code == 404

    def test_response_includes_empty_scenarios_list(self, client, test_db):
        rid = test_db.create_run("https://x.com")
        resp = client.get(f"/api/bist/runs/{rid}")
        assert resp.status_code == 200
        assert resp.json()["scenarios"] == []

    def test_response_includes_nested_scenarios_and_steps(self, client, test_db):
        rid = test_db.create_run("https://x.com")
        sc_id = test_db.create_scenario(rid, "Login válido")
        test_db.finish_scenario(sc_id, "passed", 300)
        test_db.create_step(sc_id, 'Given I am on "/login"', "passed", 50)
        test_db.create_step(sc_id, 'When I fill "email"', "passed", 80)
        test_db.finish_run(rid, "passed", 400)

        body = client.get(f"/api/bist/runs/{rid}").json()
        scenarios = body["scenarios"]
        assert len(scenarios) == 1
        assert scenarios[0]["name"] == "Login válido"
        assert len(scenarios[0]["steps"]) == 2

    def test_step_fields_present(self, client, test_db):
        rid = test_db.create_run("https://x.com")
        sc_id = test_db.create_scenario(rid, "Checkout")
        test_db.create_step(sc_id, "Given I click 'buy'", "passed", 100, "/shots/s1.png")

        step = client.get(f"/api/bist/runs/{rid}").json()["scenarios"][0]["steps"][0]
        for field in ("id", "scenario_id", "step_text", "status", "duration_ms", "screenshot_path"):
            assert field in step, f"missing field: {field}"


# ── GET /api/bist/stats ───────────────────────────────────────────────────────

class TestGetStats:

    def test_returns_200(self, client):
        resp = client.get("/api/bist/stats")
        assert resp.status_code == 200

    def test_zeros_when_no_runs(self, client):
        body = client.get("/api/bist/stats").json()
        assert body["total_runs"] == 0
        assert body["passed_runs"] == 0
        assert body["failed_runs"] == 0
        assert body["pass_rate"] == 0.0
        assert body["flaky_scenarios"] == []
        assert body["runs_over_time"] == []

    def test_pass_rate_calculation(self, client, test_db):
        for status in ("passed", "passed", "failed", "passed"):
            rid = test_db.create_run("https://x.com")
            test_db.finish_run(rid, status, 100)

        body = client.get("/api/bist/stats").json()
        assert body["total_runs"] == 4
        assert body["passed_runs"] == 3
        assert body["failed_runs"] == 1
        assert body["pass_rate"] == 75.0

    def test_avg_duration_calculated(self, client, test_db):
        for ms in (1000, 2000, 3000):
            rid = test_db.create_run("https://x.com")
            test_db.finish_run(rid, "passed", ms)

        body = client.get("/api/bist/stats").json()
        assert body["avg_duration_ms"] == 2000.0

    def test_response_structure_complete(self, client):
        body = client.get("/api/bist/stats").json()
        for field in (
            "total_runs", "passed_runs", "failed_runs",
            "pass_rate", "avg_duration_ms",
            "flaky_scenarios", "runs_over_time",
        ):
            assert field in body, f"missing field: {field}"

    def test_flaky_scenarios_is_list(self, client):
        body = client.get("/api/bist/stats").json()
        assert isinstance(body["flaky_scenarios"], list)

    def test_runs_over_time_is_list(self, client):
        body = client.get("/api/bist/stats").json()
        assert isinstance(body["runs_over_time"], list)

    def test_error_status_counted_as_failed(self, client, test_db):
        rid = test_db.create_run("https://x.com")
        test_db.finish_run(rid, "error", 100)

        body = client.get("/api/bist/stats").json()
        assert body["failed_runs"] == 1
        assert body["passed_runs"] == 0


# ── WS /ws/bist/run/{id} ─────────────────────────────────────────────────────

class TestWebSocket:

    def test_sends_done_immediately_for_finished_run(self, client, test_db):
        rid = test_db.create_run("https://x.com")
        test_db.finish_run(rid, "passed", 1000)

        with client.websocket_connect(f"/ws/bist/run/{rid}") as ws:
            msg = ws.receive_json()
        assert msg["type"] == "done"
        assert msg["status"] == "passed"

    def test_sends_done_failed_for_failed_run(self, client, test_db):
        rid = test_db.create_run("https://x.com")
        test_db.finish_run(rid, "failed", 500)

        with client.websocket_connect(f"/ws/bist/run/{rid}") as ws:
            msg = ws.receive_json()
        assert msg["type"] == "done"
        assert msg["status"] == "failed"

    def test_sends_done_error_for_error_run(self, client, test_db):
        rid = test_db.create_run("https://x.com")
        test_db.finish_run(rid, "error", 0)

        with client.websocket_connect(f"/ws/bist/run/{rid}") as ws:
            msg = ws.receive_json()
        assert msg["type"] == "done"
        assert msg["status"] == "error"
