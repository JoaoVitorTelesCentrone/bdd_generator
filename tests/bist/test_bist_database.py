"""
Tests for bist/bist_database.py — SQLite persistence layer.

Cenários cobertos:
  - Schema é criado com as três tabelas ao instanciar BISTDatabase
  - create_run retorna um ID inteiro único
  - finish_run persiste status e duration_ms
  - get_runs retorna runs em ordem cronológica inversa
  - get_run_detail retorna run com cenários e steps aninhados
  - create_scenario / finish_scenario round-trip
  - create_step persiste todos os campos
  - Runs distintos são isolados entre si
"""
import sys, os, time, tempfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import pytest
from bist.bist_database import BISTDatabase


# ── fixture ───────────────────────────────────────────────────────────────────

@pytest.fixture
def db(tmp_path):
    """Fresh in-memory-style database for every test."""
    return BISTDatabase(db_path=tmp_path / "test_bist.db")


# ── schema ────────────────────────────────────────────────────────────────────

class TestSchema:
    """Cenário: Schema é criado com as três tabelas ao instanciar BISTDatabase"""

    def test_tables_exist(self, db):
        import sqlite3
        with sqlite3.connect(str(db.db_path)) as conn:
            tables = {
                r[0] for r in
                conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
            }
        assert "test_runs" in tables
        assert "scenarios" in tables
        assert "steps" in tables

    def test_test_runs_columns(self, db):
        import sqlite3
        with sqlite3.connect(str(db.db_path)) as conn:
            cols = {r[1] for r in conn.execute("PRAGMA table_info(test_runs)").fetchall()}
        assert {"id", "started_at", "env_url", "status", "duration_ms", "feature_path"} <= cols

    def test_scenarios_columns(self, db):
        import sqlite3
        with sqlite3.connect(str(db.db_path)) as conn:
            cols = {r[1] for r in conn.execute("PRAGMA table_info(scenarios)").fetchall()}
        assert {"id", "run_id", "name", "status", "duration_ms", "error", "video_path"} <= cols

    def test_steps_columns(self, db):
        import sqlite3
        with sqlite3.connect(str(db.db_path)) as conn:
            cols = {r[1] for r in conn.execute("PRAGMA table_info(steps)").fetchall()}
        assert {"id", "scenario_id", "step_text", "status", "duration_ms", "screenshot_path"} <= cols

    def test_second_instantiation_does_not_raise(self, tmp_path):
        path = tmp_path / "reopen.db"
        BISTDatabase(db_path=path)
        BISTDatabase(db_path=path)  # should not raise


# ── test runs ─────────────────────────────────────────────────────────────────

class TestTestRuns:
    """Cenário: create_run / finish_run round-trip"""

    def test_create_run_returns_int(self, db):
        run_id = db.create_run("https://example.com", "tests/login.feature")
        assert isinstance(run_id, int)
        assert run_id >= 1

    def test_create_run_initial_status_running(self, db):
        run_id = db.create_run("https://example.com")
        runs = db.get_runs(limit=1)
        assert runs[0]["status"] == "running"

    def test_finish_run_updates_status(self, db):
        run_id = db.create_run("https://staging.app.com")
        db.finish_run(run_id, "passed", 1234)
        runs = db.get_runs(limit=1)
        assert runs[0]["status"] == "passed"
        assert runs[0]["duration_ms"] == 1234

    def test_finish_run_failed_status(self, db):
        run_id = db.create_run("https://prod.app.com")
        db.finish_run(run_id, "failed", 5678)
        runs = db.get_runs(limit=1)
        assert runs[0]["status"] == "failed"

    def test_get_runs_returns_most_recent_first(self, db):
        id1 = db.create_run("https://a.com")
        time.sleep(0.01)
        id2 = db.create_run("https://b.com")
        runs = db.get_runs(limit=10)
        assert runs[0]["env_url"] == "https://b.com"
        assert runs[1]["env_url"] == "https://a.com"

    def test_get_runs_respects_limit(self, db):
        for i in range(5):
            db.create_run(f"https://env{i}.com")
        runs = db.get_runs(limit=3)
        assert len(runs) == 3

    def test_get_runs_empty_when_no_runs(self, db):
        assert db.get_runs() == []

    def test_create_run_persists_feature_path(self, db):
        db.create_run("https://x.com", "tests/login.feature")
        runs = db.get_runs(limit=1)
        assert runs[0]["feature_path"] == "tests/login.feature"

    def test_multiple_runs_have_unique_ids(self, db):
        ids = [db.create_run("https://x.com") for _ in range(5)]
        assert len(set(ids)) == 5


# ── scenarios ─────────────────────────────────────────────────────────────────

class TestScenarios:
    """Cenário: create_scenario / finish_scenario round-trip"""

    def test_create_scenario_returns_int(self, db):
        run_id = db.create_run("https://x.com")
        sc_id = db.create_scenario(run_id, "Login válido")
        assert isinstance(sc_id, int)

    def test_scenario_initial_status_running(self, db):
        run_id = db.create_run("https://x.com")
        sc_id = db.create_scenario(run_id, "Login válido")
        detail = db.get_run_detail(run_id)
        assert detail["scenarios"][0]["status"] == "running"

    def test_finish_scenario_updates_all_fields(self, db):
        run_id = db.create_run("https://x.com")
        sc_id = db.create_scenario(run_id, "Login falhou")
        db.finish_scenario(sc_id, "failed", 800, "selector not found", "/videos/clip.webm")
        detail = db.get_run_detail(run_id)
        sc = detail["scenarios"][0]
        assert sc["status"] == "failed"
        assert sc["duration_ms"] == 800
        assert sc["error"] == "selector not found"
        assert sc["video_path"] == "/videos/clip.webm"

    def test_multiple_scenarios_per_run(self, db):
        run_id = db.create_run("https://x.com")
        db.create_scenario(run_id, "Scenario A")
        db.create_scenario(run_id, "Scenario B")
        detail = db.get_run_detail(run_id)
        assert len(detail["scenarios"]) == 2


# ── steps ─────────────────────────────────────────────────────────────────────

class TestSteps:
    """Cenário: create_step persiste todos os campos"""

    def _setup(self, db):
        run_id = db.create_run("https://x.com")
        sc_id = db.create_scenario(run_id, "Checkout")
        return run_id, sc_id

    def test_create_step_persists_text_and_status(self, db):
        run_id, sc_id = self._setup(db)
        db.create_step(sc_id, 'When I click "Submit"', "passed", 120)
        detail = db.get_run_detail(run_id)
        step = detail["scenarios"][0]["steps"][0]
        assert step["step_text"] == 'When I click "Submit"'
        assert step["status"] == "passed"
        assert step["duration_ms"] == 120

    def test_create_step_persists_screenshot_path(self, db):
        run_id, sc_id = self._setup(db)
        db.create_step(sc_id, "Then I see error", "failed", 0, "/shots/fail.png")
        detail = db.get_run_detail(run_id)
        step = detail["scenarios"][0]["steps"][0]
        assert step["screenshot_path"] == "/shots/fail.png"

    def test_multiple_steps_per_scenario(self, db):
        run_id, sc_id = self._setup(db)
        db.create_step(sc_id, "Given I am on login page", "passed")
        db.create_step(sc_id, 'When I fill "email"', "passed")
        db.create_step(sc_id, 'Then I see "Dashboard"', "passed")
        detail = db.get_run_detail(run_id)
        assert len(detail["scenarios"][0]["steps"]) == 3


# ── isolation ─────────────────────────────────────────────────────────────────

class TestIsolation:
    """Cenário: Runs distintos são isolados entre si"""

    def test_get_run_detail_returns_only_own_scenarios(self, db):
        run_a = db.create_run("https://a.com")
        run_b = db.create_run("https://b.com")
        db.create_scenario(run_a, "Scenario A1")
        db.create_scenario(run_b, "Scenario B1")
        db.create_scenario(run_b, "Scenario B2")

        detail_a = db.get_run_detail(run_a)
        detail_b = db.get_run_detail(run_b)

        assert len(detail_a["scenarios"]) == 1
        assert len(detail_b["scenarios"]) == 2

    def test_get_run_detail_unknown_id_returns_empty(self, db):
        result = db.get_run_detail(99999)
        assert result == {}

    def test_steps_belong_to_correct_scenario(self, db):
        run_id = db.create_run("https://x.com")
        sc_a = db.create_scenario(run_id, "Scenario A")
        sc_b = db.create_scenario(run_id, "Scenario B")
        db.create_step(sc_a, "Given A step", "passed")
        db.create_step(sc_b, "Given B step", "passed")
        db.create_step(sc_b, "Then B result", "passed")

        detail = db.get_run_detail(run_id)
        steps_a = detail["scenarios"][0]["steps"]
        steps_b = detail["scenarios"][1]["steps"]

        assert len(steps_a) == 1
        assert len(steps_b) == 2
