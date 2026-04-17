"""
Tests for analytics methods added in Phase 3 to bist/bist_database.py.

Cenários cobertos:
  get_flaky_scenarios:
    - retorna lista vazia quando não há cenários
    - retorna lista vazia quando todos cenários passaram
    - retorna lista vazia quando cenário rodou apenas uma vez (total_runs <= 1)
    - detecta cenário com falhas em runs múltiplos
    - ordena por failure_rate decrescente
    - limita resultado pelo parâmetro limit
    - campos name, total_runs, failures, failure_rate corretos

  get_runs_trend:
    - retorna lista vazia quando não há runs
    - agrupa runs por data (UTC)
    - conta "passed" e "failed/error" separadamente
    - ordena por data crescente
    - exclui runs fora da janela de dias
    - inclui apenas runs dentro do período

  get_database factory:
    - retorna BISTDatabase por padrão (sem DATABASE_URL)
    - levanta RuntimeError quando DATABASE_URL inválido sem sqlalchemy
"""
import sys, os, time
from pathlib import Path
from unittest.mock import patch
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import pytest
from bist.bist_database import BISTDatabase, get_database


# ── fixture ───────────────────────────────────────────────────────────────────

@pytest.fixture
def db(tmp_path):
    return BISTDatabase(db_path=tmp_path / "analytics_test.db")


def _ts(days_ago: float = 0) -> float:
    """Timestamp N days in the past."""
    return time.time() - days_ago * 86400


# ── get_flaky_scenarios ───────────────────────────────────────────────────────

class TestGetFlakyScenarios:

    def test_empty_when_no_scenarios(self, db):
        result = db.get_flaky_scenarios()
        assert result == []

    def test_empty_when_all_passed(self, db):
        run_a = db.create_run("https://a.com")
        run_b = db.create_run("https://b.com")
        sc_a = db.create_scenario(run_a, "Login")
        sc_b = db.create_scenario(run_b, "Login")
        db.finish_scenario(sc_a, "passed", 100)
        db.finish_scenario(sc_b, "passed", 110)
        assert db.get_flaky_scenarios() == []

    def test_empty_when_single_run(self, db):
        run = db.create_run("https://x.com")
        sc = db.create_scenario(run, "Checkout")
        db.finish_scenario(sc, "failed", 200)
        # Only 1 run → not flaky (total_runs must be > 1)
        assert db.get_flaky_scenarios() == []

    def test_detects_flaky_scenario(self, db):
        for status in ("passed", "failed", "passed"):
            run = db.create_run("https://x.com")
            sc = db.create_scenario(run, "Login")
            db.finish_scenario(sc, status, 100)

        result = db.get_flaky_scenarios()
        assert len(result) == 1
        r = result[0]
        assert r["name"] == "Login"
        assert r["total_runs"] == 3
        assert r["failures"] == 1
        assert isinstance(r["failure_rate"], (int, float))
        assert 33.0 <= float(r["failure_rate"]) <= 34.0

    def test_multiple_scenarios_only_flaky_returned(self, db):
        # "Login" is flaky (1 fail in 2 runs); "Checkout" always passes
        for status in ("passed", "failed"):
            run = db.create_run("https://x.com")
            sc = db.create_scenario(run, "Login")
            db.finish_scenario(sc, status, 100)
        for _ in range(3):
            run = db.create_run("https://x.com")
            sc = db.create_scenario(run, "Checkout")
            db.finish_scenario(sc, "passed", 100)

        result = db.get_flaky_scenarios()
        names = [r["name"] for r in result]
        assert "Login" in names
        assert "Checkout" not in names

    def test_ordered_by_failure_rate_desc(self, db):
        # "PageA": 1/2 = 50%; "PageB": 1/3 ≈ 33%
        for status in ("passed", "failed"):
            run = db.create_run("https://x.com")
            sc = db.create_scenario(run, "PageA")
            db.finish_scenario(sc, status, 100)
        for status in ("passed", "passed", "failed"):
            run = db.create_run("https://x.com")
            sc = db.create_scenario(run, "PageB")
            db.finish_scenario(sc, status, 100)

        result = db.get_flaky_scenarios()
        assert len(result) == 2
        assert result[0]["name"] == "PageA"
        assert result[1]["name"] == "PageB"

    def test_limit_is_respected(self, db):
        for name in ("A", "B", "C"):
            for status in ("passed", "failed"):
                run = db.create_run("https://x.com")
                sc = db.create_scenario(run, name)
                db.finish_scenario(sc, status, 100)

        assert len(db.get_flaky_scenarios(limit=2)) == 2
        assert len(db.get_flaky_scenarios(limit=1)) == 1

    def test_failure_rate_100_percent(self, db):
        for _ in range(2):
            run = db.create_run("https://x.com")
            sc = db.create_scenario(run, "AlwaysFails")
            db.finish_scenario(sc, "failed", 100)

        result = db.get_flaky_scenarios()
        assert len(result) == 1
        assert float(result[0]["failure_rate"]) == 100.0

    def test_result_fields_are_complete(self, db):
        for status in ("passed", "failed"):
            run = db.create_run("https://x.com")
            sc = db.create_scenario(run, "Scenario X")
            db.finish_scenario(sc, status, 100)

        r = db.get_flaky_scenarios()[0]
        assert set(r.keys()) >= {"name", "total_runs", "failures", "failure_rate"}


# ── get_runs_trend ────────────────────────────────────────────────────────────

class TestGetRunsTrend:

    def test_empty_when_no_runs(self, db):
        assert db.get_runs_trend() == []

    def test_single_run_creates_one_entry(self, db):
        run = db.create_run("https://x.com")
        db.finish_run(run, "passed", 1000)

        result = db.get_runs_trend(days=30)
        assert len(result) == 1
        entry = result[0]
        assert "date" in entry
        assert entry["passed"] == 1
        assert entry["failed"] == 0

    def test_failed_and_error_both_counted_as_failed(self, db):
        run_a = db.create_run("https://x.com")
        db.finish_run(run_a, "failed", 100)
        run_b = db.create_run("https://x.com")
        db.finish_run(run_b, "error", 100)
        run_c = db.create_run("https://x.com")
        db.finish_run(run_c, "passed", 100)

        result = db.get_runs_trend(days=30)
        assert len(result) == 1
        assert result[0]["passed"] == 1
        assert result[0]["failed"] == 2

    def test_ordered_by_date_ascending(self, db):
        # Create two runs on different days (mock timestamps)
        import sqlite3
        yesterday_ts = _ts(days_ago=1)
        today_ts     = _ts(days_ago=0)

        run_a = db.create_run("https://x.com")
        run_b = db.create_run("https://y.com")

        # Force the started_at timestamps
        with sqlite3.connect(str(db.db_path)) as conn:
            conn.execute("UPDATE test_runs SET started_at=? WHERE id=?", (yesterday_ts, run_a))
            conn.execute("UPDATE test_runs SET started_at=? WHERE id=?", (today_ts, run_b))
            conn.execute("UPDATE test_runs SET status='passed' WHERE id IN (?,?)", (run_a, run_b))
            conn.execute("UPDATE test_runs SET duration_ms=100 WHERE id IN (?,?)", (run_a, run_b))

        result = db.get_runs_trend(days=30)
        assert len(result) >= 1
        dates = [r["date"] for r in result]
        assert dates == sorted(dates)

    def test_runs_outside_window_excluded(self, db):
        old_run = db.create_run("https://old.com")
        db.finish_run(old_run, "passed", 100)

        # Force started_at to 60 days ago
        import sqlite3
        with sqlite3.connect(str(db.db_path)) as conn:
            conn.execute(
                "UPDATE test_runs SET started_at=? WHERE id=?",
                (_ts(days_ago=60), old_run),
            )

        result = db.get_runs_trend(days=30)
        assert result == []

    def test_runs_within_window_included(self, db):
        recent_run = db.create_run("https://recent.com")
        db.finish_run(recent_run, "passed", 100)

        import sqlite3
        with sqlite3.connect(str(db.db_path)) as conn:
            conn.execute(
                "UPDATE test_runs SET started_at=? WHERE id=?",
                (_ts(days_ago=5), recent_run),
            )

        result = db.get_runs_trend(days=30)
        assert len(result) == 1

    def test_date_format_is_iso(self, db):
        run = db.create_run("https://x.com")
        db.finish_run(run, "passed", 100)

        result = db.get_runs_trend(days=30)
        assert len(result) == 1
        date_str = result[0]["date"]
        # Must be YYYY-MM-DD
        datetime.strptime(date_str, "%Y-%m-%d")  # raises if format wrong

    def test_multiple_runs_same_day_aggregated(self, db):
        now = time.time()
        for i in range(3):
            run = db.create_run("https://x.com")
            db.finish_run(run, "passed" if i < 2 else "failed", 100)
            # Same day timestamp — all within last hour
            import sqlite3
            with sqlite3.connect(str(db.db_path)) as conn:
                conn.execute(
                    "UPDATE test_runs SET started_at=? WHERE id=?",
                    (now - i * 100, run),  # slightly different but same day
                )

        result = db.get_runs_trend(days=1)
        assert len(result) == 1
        assert result[0]["passed"] == 2
        assert result[0]["failed"] == 1


# ── get_database factory ──────────────────────────────────────────────────────

class TestGetDatabase:

    def test_returns_bist_database_by_default(self):
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("DATABASE_URL", None)
            db = get_database()
            assert isinstance(db, BISTDatabase)

    def test_returns_bist_database_when_database_url_empty(self):
        with patch.dict(os.environ, {"DATABASE_URL": ""}):
            db = get_database()
            assert isinstance(db, BISTDatabase)

    def test_raises_runtime_error_for_pg_without_sqlalchemy(self):
        """When DATABASE_URL is postgres but the PG module is unavailable, raise RuntimeError.

        Patches sys.modules to simulate missing sqlalchemy (None sentinel → ImportError),
        and patches os.environ so get_database() reads the postgres URL at call time.
        """
        import sys

        with patch.dict(sys.modules, {"bist.bist_database_pg": None}), \
             patch.dict(os.environ, {"DATABASE_URL": "postgresql://user:pass@localhost/db"}):
            with pytest.raises(RuntimeError, match="PostgreSQL support requires"):
                get_database()

    def test_sqlite_url_not_treated_as_postgres(self):
        """DATABASE_URL with sqlite:// should fall through to plain BISTDatabase."""
        with patch.dict(os.environ, {"DATABASE_URL": "sqlite:///some/path.db"}):
            # sqlite URL doesn't match "postgresql" or "postgres" — returns plain BISTDatabase
            db = get_database()
            assert isinstance(db, BISTDatabase)
