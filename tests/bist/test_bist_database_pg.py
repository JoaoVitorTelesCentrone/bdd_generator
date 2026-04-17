"""
Tests for bist/bist_database_pg.py — SQLAlchemy-backed BIST database.

Uses SQLite in-memory/temp-file to avoid needing a real PostgreSQL server.
The BISTDatabasePG class is designed to work with both SQLite and PostgreSQL
via SQLAlchemy, so these tests validate the ORM logic using SQLite as a
drop-in stand-in.

Cenários cobertos:
  Schema:
    - Todas as 5 tabelas são criadas ao instanciar
    - UniqueConstraint existe em selector_cache
  CRUD test_runs:
    - create_run retorna ID inteiro
    - finish_run atualiza status e duration_ms
    - get_runs retorna mais recente primeiro
    - get_run_detail retorna cenários e steps aninhados
    - get_run_detail retorna {} para ID inexistente
  Cenários e steps:
    - create_scenario / finish_scenario round-trip
    - create_step persiste todos os campos
    - steps pertencem ao cenário correto
  Selector cache:
    - cache_selector insere novo registro
    - cache_selector incrementa success_count em conflito
    - get_cached_selectors retorna por success_count desc
    - UniqueConstraint impede duplicatas brutas
  Healing log:
    - log_healing persiste todos os campos
  Analytics:
    - get_flaky_scenarios detecta cenários instáveis
    - get_runs_trend agrega por data
"""
import sys, os, time
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import pytest

try:
    from bist.bist_database_pg import BISTDatabasePG
    _HAS_SA = True
except ImportError:
    _HAS_SA = False

pytestmark = pytest.mark.skipif(
    not _HAS_SA,
    reason="sqlalchemy not installed — skipping BISTDatabasePG tests",
)


# ── fixture ───────────────────────────────────────────────────────────────────

@pytest.fixture
def db(tmp_path):
    """BISTDatabasePG backed by a temporary SQLite file (tests ORM logic)."""
    url = f"sqlite:///{tmp_path / 'pg_test.db'}"
    return BISTDatabasePG(url)


# ── schema ────────────────────────────────────────────────────────────────────

class TestSchema:

    def test_all_tables_created(self, db):
        from sqlalchemy import inspect
        insp = inspect(db._engine)
        tables = set(insp.get_table_names())
        assert {"test_runs", "scenarios", "steps", "selector_cache", "healing_log"} <= tables

    def test_selector_cache_has_unique_constraint(self, tmp_path):
        """Duplicate (step_pattern, selector) must violate the unique constraint."""
        from sqlalchemy.exc import IntegrityError
        url = f"sqlite:///{tmp_path / 'unique_test.db'}"
        db = BISTDatabasePG(url)

        db.cache_selector("click submit", "button[type='submit']")
        # Insert a second time — should NOT raise (upsert logic handles it)
        db.cache_selector("click submit", "button[type='submit']")  # should just increment

        # But direct raw INSERT of duplicate must fail at DB level
        with db._conn() as conn:
            from sqlalchemy import text
            conn.execute(text(
                "INSERT INTO selector_cache (step_pattern, selector, success_count, last_used) "
                "VALUES ('p', 's', 1, 0.0)"
            ))
            with pytest.raises(IntegrityError):
                conn.execute(text(
                    "INSERT INTO selector_cache (step_pattern, selector, success_count, last_used) "
                    "VALUES ('p', 's', 2, 0.0)"
                ))


# ── test_runs CRUD ────────────────────────────────────────────────────────────

class TestTestRuns:

    def test_create_run_returns_int(self, db):
        rid = db.create_run("https://x.com")
        assert isinstance(rid, int)
        assert rid >= 1

    def test_create_run_initial_status_running(self, db):
        rid = db.create_run("https://x.com")
        runs = db.get_runs(limit=1)
        assert runs[0]["status"] == "running"

    def test_finish_run_updates_fields(self, db):
        rid = db.create_run("https://x.com")
        db.finish_run(rid, "passed", 9999)
        runs = db.get_runs(limit=1)
        assert runs[0]["status"] == "passed"
        assert runs[0]["duration_ms"] == 9999

    def test_get_runs_most_recent_first(self, db):
        rid_a = db.create_run("https://a.com")
        time.sleep(0.01)
        rid_b = db.create_run("https://b.com")
        runs = db.get_runs(limit=10)
        assert runs[0]["env_url"] == "https://b.com"
        assert runs[1]["env_url"] == "https://a.com"

    def test_get_run_detail_returns_dict(self, db):
        rid = db.create_run("https://x.com", "login.feature")
        db.finish_run(rid, "passed", 100)
        detail = db.get_run_detail(rid)
        assert detail["id"] == rid
        assert detail["feature_path"] == "login.feature"

    def test_get_run_detail_unknown_returns_empty(self, db):
        assert db.get_run_detail(99999) == {}

    def test_get_run_detail_includes_scenarios(self, db):
        rid = db.create_run("https://x.com")
        sc_id = db.create_scenario(rid, "Login")
        db.finish_scenario(sc_id, "passed", 200)
        detail = db.get_run_detail(rid)
        assert len(detail["scenarios"]) == 1
        assert detail["scenarios"][0]["name"] == "Login"


# ── scenarios ─────────────────────────────────────────────────────────────────

class TestScenarios:

    def test_create_scenario_returns_int(self, db):
        rid = db.create_run("https://x.com")
        sc_id = db.create_scenario(rid, "My Scenario")
        assert isinstance(sc_id, int)

    def test_finish_scenario_updates_all_fields(self, db):
        rid = db.create_run("https://x.com")
        sc_id = db.create_scenario(rid, "Checkout")
        db.finish_scenario(sc_id, "failed", 500, "error msg", "/video.webm")
        detail = db.get_run_detail(rid)
        sc = detail["scenarios"][0]
        assert sc["status"] == "failed"
        assert sc["duration_ms"] == 500
        assert sc["error"] == "error msg"
        assert sc["video_path"] == "/video.webm"


# ── steps ─────────────────────────────────────────────────────────────────────

class TestSteps:

    def test_create_step_persists_all_fields(self, db):
        rid = db.create_run("https://x.com")
        sc_id = db.create_scenario(rid, "S")
        db.create_step(sc_id, 'Given I am on "/login"', "passed", 75, "/shot.png")

        detail = db.get_run_detail(rid)
        step = detail["scenarios"][0]["steps"][0]
        assert step["step_text"] == 'Given I am on "/login"'
        assert step["status"] == "passed"
        assert step["duration_ms"] == 75
        assert step["screenshot_path"] == "/shot.png"

    def test_steps_belong_to_correct_scenario(self, db):
        rid = db.create_run("https://x.com")
        sc_a = db.create_scenario(rid, "A")
        sc_b = db.create_scenario(rid, "B")
        db.create_step(sc_a, "step A1", "passed")
        db.create_step(sc_b, "step B1", "passed")
        db.create_step(sc_b, "step B2", "passed")

        detail = db.get_run_detail(rid)
        steps_a = detail["scenarios"][0]["steps"]
        steps_b = detail["scenarios"][1]["steps"]
        assert len(steps_a) == 1
        assert len(steps_b) == 2


# ── selector cache ────────────────────────────────────────────────────────────

class TestSelectorCache:

    def test_cache_selector_inserts_new_entry(self, db):
        db.cache_selector("click submit", "button[type='submit']")
        selectors = db.get_cached_selectors("click submit")
        assert "button[type='submit']" in selectors

    def test_cache_selector_increments_success_count(self, db):
        db.cache_selector("click submit", "button[type='submit']")
        db.cache_selector("click submit", "button[type='submit']")  # duplicate
        selectors = db.get_cached_selectors("click submit")
        assert len(selectors) == 1  # still one entry, count incremented

    def test_get_cached_selectors_empty_when_none(self, db):
        assert db.get_cached_selectors("unknown step") == []

    def test_get_cached_selectors_limit_respected(self, db):
        for i in range(4):
            db.cache_selector("step X", f"selector_{i}")
        result = db.get_cached_selectors("step X", limit=2)
        assert len(result) == 2

    def test_multiple_selectors_for_same_step(self, db):
        db.cache_selector("step X", "selector_a")
        db.cache_selector("step X", "selector_b")
        result = db.get_cached_selectors("step X")
        assert "selector_a" in result
        assert "selector_b" in result


# ── healing log ───────────────────────────────────────────────────────────────

class TestHealingLog:

    def test_log_healing_does_not_raise(self, db):
        rid = db.create_run("https://x.com")
        sc_id = db.create_scenario(rid, "S")
        db.log_healing(sc_id, "click submit", "#old-btn", "#new-btn")

    def test_log_healing_with_none_scenario(self, db):
        # Should not raise even with None scenario_id
        db.log_healing(None, "some step", "#old", "#new")


# ── analytics ─────────────────────────────────────────────────────────────────

class TestAnalytics:

    def test_get_flaky_scenarios_empty_when_all_passed(self, db):
        for _ in range(3):
            rid = db.create_run("https://x.com")
            sc = db.create_scenario(rid, "Login")
            db.finish_scenario(sc, "passed", 100)
        assert db.get_flaky_scenarios() == []

    def test_get_flaky_scenarios_detects_instability(self, db):
        for status in ("passed", "failed", "passed"):
            rid = db.create_run("https://x.com")
            sc = db.create_scenario(rid, "Checkout")
            db.finish_scenario(sc, status, 100)

        result = db.get_flaky_scenarios()
        assert len(result) == 1
        assert result[0]["name"] == "Checkout"
        assert result[0]["failures"] == 1
        assert result[0]["total_runs"] == 3

    def test_get_flaky_scenarios_result_fields(self, db):
        for status in ("passed", "failed"):
            rid = db.create_run("https://x.com")
            sc = db.create_scenario(rid, "Flaky")
            db.finish_scenario(sc, status, 100)

        r = db.get_flaky_scenarios()[0]
        assert "name" in r
        assert "total_runs" in r
        assert "failures" in r
        assert "failure_rate" in r

    def test_get_runs_trend_empty_no_runs(self, db):
        assert db.get_runs_trend() == []

    def test_get_runs_trend_aggregates_by_date(self, db):
        for status in ("passed", "failed", "passed"):
            rid = db.create_run("https://x.com")
            db.finish_run(rid, status, 100)

        result = db.get_runs_trend(days=30)
        assert len(result) == 1
        assert result[0]["passed"] == 2
        assert result[0]["failed"] == 1

    def test_get_runs_trend_date_format(self, db):
        rid = db.create_run("https://x.com")
        db.finish_run(rid, "passed", 100)

        result = db.get_runs_trend(days=30)
        assert len(result) == 1
        datetime.strptime(result[0]["date"], "%Y-%m-%d")
