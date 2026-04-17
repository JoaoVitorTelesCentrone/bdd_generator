"""SQLite / PostgreSQL persistence layer for BIST test runs, scenarios, and steps.

Default: SQLite at ~/.bist/bist.db.
PostgreSQL: set DATABASE_URL=postgresql://user:pass@host/db and install sqlalchemy+psycopg2.
Use get_database() factory for automatic selection based on DATABASE_URL.
"""

import os
import sqlite3
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

DB_PATH = Path.home() / ".bist" / "bist.db"
DATABASE_URL = os.getenv("DATABASE_URL", "")


class BISTDatabase:
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self):
        with self._connect() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS test_runs (
                    id           INTEGER PRIMARY KEY AUTOINCREMENT,
                    started_at   REAL    NOT NULL,
                    env_url      TEXT    NOT NULL,
                    status       TEXT    NOT NULL,
                    duration_ms  INTEGER DEFAULT 0,
                    feature_path TEXT    DEFAULT '',
                    tenant_id    INTEGER DEFAULT NULL
                );
                CREATE TABLE IF NOT EXISTS scenarios (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id      INTEGER NOT NULL REFERENCES test_runs(id),
                    name        TEXT    NOT NULL,
                    status      TEXT    NOT NULL,
                    duration_ms INTEGER DEFAULT 0,
                    error       TEXT    DEFAULT '',
                    video_path  TEXT    DEFAULT ''
                );
                CREATE TABLE IF NOT EXISTS steps (
                    id              INTEGER PRIMARY KEY AUTOINCREMENT,
                    scenario_id     INTEGER NOT NULL REFERENCES scenarios(id),
                    step_text       TEXT    NOT NULL,
                    status          TEXT    NOT NULL,
                    duration_ms     INTEGER DEFAULT 0,
                    screenshot_path TEXT    DEFAULT ''
                );
                CREATE TABLE IF NOT EXISTS selector_cache (
                    id            INTEGER PRIMARY KEY AUTOINCREMENT,
                    step_pattern  TEXT    NOT NULL,
                    selector      TEXT    NOT NULL,
                    success_count INTEGER DEFAULT 1,
                    last_used     REAL    NOT NULL,
                    UNIQUE(step_pattern, selector)
                );
                CREATE TABLE IF NOT EXISTS healing_log (
                    id               INTEGER PRIMARY KEY AUTOINCREMENT,
                    scenario_id      INTEGER REFERENCES scenarios(id),
                    step_text        TEXT NOT NULL,
                    failed_selector  TEXT NOT NULL,
                    healed_selector  TEXT NOT NULL,
                    timestamp        REAL NOT NULL
                );
            """)
            # Migrate existing databases that pre-date the tenant_id column
            try:
                conn.execute("ALTER TABLE test_runs ADD COLUMN tenant_id INTEGER DEFAULT NULL")
            except Exception:
                pass

    # ── Test runs ──────────────────────────────────────────────────────────────

    def create_run(
        self, env_url: str, feature_path: str = "", tenant_id: Optional[int] = None
    ) -> int:
        with self._connect() as conn:
            cur = conn.execute(
                "INSERT INTO test_runs (started_at, env_url, status, feature_path, tenant_id) "
                "VALUES (?, ?, 'running', ?, ?)",
                (time.time(), env_url, feature_path, tenant_id),
            )
            return cur.lastrowid

    def finish_run(self, run_id: int, status: str, duration_ms: int):
        with self._connect() as conn:
            conn.execute(
                "UPDATE test_runs SET status=?, duration_ms=? WHERE id=?",
                (status, duration_ms, run_id),
            )

    def get_runs(self, limit: int = 20, tenant_id: Optional[int] = None) -> list[dict]:
        with self._connect() as conn:
            if tenant_id is not None:
                rows = conn.execute(
                    "SELECT * FROM test_runs WHERE tenant_id=? ORDER BY started_at DESC LIMIT ?",
                    (tenant_id, limit),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM test_runs ORDER BY started_at DESC LIMIT ?", (limit,)
                ).fetchall()
            return [dict(r) for r in rows]

    def get_run_detail(self, run_id: int, tenant_id: Optional[int] = None) -> dict:
        with self._connect() as conn:
            if tenant_id is not None:
                row = conn.execute(
                    "SELECT * FROM test_runs WHERE id=? AND tenant_id=?", (run_id, tenant_id)
                ).fetchone()
            else:
                row = conn.execute("SELECT * FROM test_runs WHERE id=?", (run_id,)).fetchone()
            if not row:
                return {}
            run = dict(row)
            scenarios = conn.execute(
                "SELECT * FROM scenarios WHERE run_id=?", (run_id,)
            ).fetchall()
            result_scenarios = []
            for s in scenarios:
                sd = dict(s)
                steps = conn.execute(
                    "SELECT * FROM steps WHERE scenario_id=?", (s["id"],)
                ).fetchall()
                sd["steps"] = [dict(st) for st in steps]
                result_scenarios.append(sd)
            run["scenarios"] = result_scenarios
            return run

    # ── Scenarios ──────────────────────────────────────────────────────────────

    def create_scenario(self, run_id: int, name: str) -> int:
        with self._connect() as conn:
            cur = conn.execute(
                "INSERT INTO scenarios (run_id, name, status) VALUES (?, ?, 'running')",
                (run_id, name),
            )
            return cur.lastrowid

    def finish_scenario(
        self,
        scenario_id: int,
        status: str,
        duration_ms: int,
        error: str = "",
        video_path: str = "",
    ):
        with self._connect() as conn:
            conn.execute(
                "UPDATE scenarios SET status=?, duration_ms=?, error=?, video_path=? WHERE id=?",
                (status, duration_ms, error, video_path, scenario_id),
            )

    # ── Selector cache ─────────────────────────────────────────────────────────

    def cache_selector(self, step_pattern: str, selector: str) -> None:
        with self._connect() as conn:
            conn.execute(
                """INSERT INTO selector_cache (step_pattern, selector, success_count, last_used)
                   VALUES (?, ?, 1, ?)
                   ON CONFLICT(step_pattern, selector)
                   DO UPDATE SET success_count = success_count + 1, last_used = excluded.last_used""",
                (step_pattern, selector, time.time()),
            )

    def get_cached_selectors(self, step_pattern: str, limit: int = 5) -> list[str]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT selector FROM selector_cache WHERE step_pattern=? "
                "ORDER BY success_count DESC, last_used DESC LIMIT ?",
                (step_pattern, limit),
            ).fetchall()
            return [r["selector"] for r in rows]

    def log_healing(
        self,
        scenario_id: Optional[int],
        step_text: str,
        failed_selector: str,
        healed_selector: str,
    ) -> None:
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO healing_log (scenario_id, step_text, failed_selector, healed_selector, timestamp) "
                "VALUES (?, ?, ?, ?, ?)",
                (scenario_id, step_text, failed_selector, healed_selector, time.time()),
            )

    # ── Steps ──────────────────────────────────────────────────────────────────

    def create_step(
        self,
        scenario_id: int,
        step_text: str,
        status: str,
        duration_ms: int = 0,
        screenshot_path: str = "",
    ) -> int:
        with self._connect() as conn:
            cur = conn.execute(
                "INSERT INTO steps (scenario_id, step_text, status, duration_ms, screenshot_path) "
                "VALUES (?, ?, ?, ?, ?)",
                (scenario_id, step_text, status, duration_ms, screenshot_path),
            )
            return cur.lastrowid

    # ── Analytics ──────────────────────────────────────────────────────────────

    def get_flaky_scenarios(self, limit: int = 10, tenant_id: Optional[int] = None) -> list[dict]:
        """Scenarios with both passing and failing runs (flaky = unstable)."""
        with self._connect() as conn:
            if tenant_id is not None:
                rows = conn.execute(
                    """
                    SELECT s.name,
                        COUNT(*) AS total_runs,
                        SUM(CASE WHEN s.status = 'failed' THEN 1 ELSE 0 END) AS failures,
                        ROUND(
                            CAST(SUM(CASE WHEN s.status = 'failed' THEN 1 ELSE 0 END) AS REAL)
                            / COUNT(*) * 100, 1
                        ) AS failure_rate
                    FROM scenarios s
                    JOIN test_runs tr ON tr.id = s.run_id
                    WHERE tr.tenant_id = ?
                    GROUP BY s.name
                    HAVING SUM(CASE WHEN s.status = 'failed' THEN 1 ELSE 0 END) > 0
                       AND COUNT(*) > 1
                    ORDER BY failure_rate DESC
                    LIMIT ?
                    """,
                    (tenant_id, limit),
                ).fetchall()
            else:
                rows = conn.execute(
                    """
                    SELECT
                        name,
                        COUNT(*) AS total_runs,
                        SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) AS failures,
                        ROUND(
                            CAST(SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) AS REAL)
                            / COUNT(*) * 100, 1
                        ) AS failure_rate
                    FROM scenarios
                    GROUP BY name
                    HAVING SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) > 0
                       AND COUNT(*) > 1
                    ORDER BY failure_rate DESC
                    LIMIT ?
                    """,
                    (limit,),
                ).fetchall()
            return [dict(r) for r in rows]

    def get_runs_trend(self, days: int = 30, tenant_id: Optional[int] = None) -> list[dict]:
        """Daily passed/failed counts for the last N days (portable, Python-side grouping)."""
        cutoff = time.time() - days * 86400
        runs = self.get_runs(limit=10_000, tenant_id=tenant_id)
        groups: dict[str, dict] = defaultdict(lambda: {"date": "", "passed": 0, "failed": 0})
        for r in runs:
            if r["started_at"] < cutoff:
                continue
            date = datetime.fromtimestamp(r["started_at"], tz=timezone.utc).strftime("%Y-%m-%d")
            groups[date]["date"] = date
            if r["status"] == "passed":
                groups[date]["passed"] += 1
            elif r["status"] in ("failed", "error"):
                groups[date]["failed"] += 1
        return sorted(groups.values(), key=lambda x: x["date"])


# ── Factory ────────────────────────────────────────────────────────────────────

def get_database() -> BISTDatabase:
    """Return a BISTDatabase instance, using PostgreSQL when DATABASE_URL is set.
    DATABASE_URL is read from the environment at call time so tests can patch it.
    """
    url = os.getenv("DATABASE_URL", "")
    if url and ("postgresql" in url or "postgres" in url):
        try:
            from .bist_database_pg import BISTDatabasePG  # type: ignore
            return BISTDatabasePG(url)  # type: ignore
        except ImportError as exc:
            raise RuntimeError(
                "PostgreSQL support requires SQLAlchemy + psycopg2:\n"
                "  pip install sqlalchemy psycopg2-binary\n"
                f"Original error: {exc}"
            ) from exc
    return BISTDatabase()
