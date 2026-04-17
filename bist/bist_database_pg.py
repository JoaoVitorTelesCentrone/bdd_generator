"""PostgreSQL-backed BIST database using SQLAlchemy Core.

Drop-in replacement for BISTDatabase when DATABASE_URL points to PostgreSQL.
Install:  pip install sqlalchemy psycopg2-binary
Migrate:  alembic -c bist/alembic.ini upgrade head
"""
from __future__ import annotations

import os
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from sqlalchemy import (
    Column, ForeignKey, Integer, Float, String, Text,
    MetaData, Table, UniqueConstraint, create_engine, text,
)
from sqlalchemy.engine import Connection, Engine

_metadata = MetaData()

test_runs = Table(
    "test_runs", _metadata,
    Column("id",           Integer, primary_key=True, autoincrement=True),
    Column("started_at",   Float,   nullable=False),
    Column("env_url",      Text,    nullable=False),
    Column("status",       String(20), nullable=False),
    Column("duration_ms",  Integer, default=0),
    Column("feature_path", Text,    default=""),
    Column("tenant_id",    Integer, nullable=True),
)

scenarios = Table(
    "scenarios", _metadata,
    Column("id",          Integer, primary_key=True, autoincrement=True),
    Column("run_id",      Integer, ForeignKey("test_runs.id"), nullable=False),
    Column("name",        Text,    nullable=False),
    Column("status",      String(20), nullable=False),
    Column("duration_ms", Integer, default=0),
    Column("error",       Text,    default=""),
    Column("video_path",  Text,    default=""),
)

steps = Table(
    "steps", _metadata,
    Column("id",              Integer, primary_key=True, autoincrement=True),
    Column("scenario_id",     Integer, ForeignKey("scenarios.id"), nullable=False),
    Column("step_text",       Text,    nullable=False),
    Column("status",          String(20), nullable=False),
    Column("duration_ms",     Integer, default=0),
    Column("screenshot_path", Text,    default=""),
)

selector_cache = Table(
    "selector_cache", _metadata,
    Column("id",            Integer, primary_key=True, autoincrement=True),
    Column("step_pattern",  Text,    nullable=False),
    Column("selector",      Text,    nullable=False),
    Column("success_count", Integer, default=1),
    Column("last_used",     Float,   nullable=False),
    UniqueConstraint("step_pattern", "selector"),
)

healing_log = Table(
    "healing_log", _metadata,
    Column("id",              Integer, primary_key=True, autoincrement=True),
    Column("scenario_id",     Integer, ForeignKey("scenarios.id"), nullable=True),
    Column("step_text",       Text,    nullable=False),
    Column("failed_selector", Text,    nullable=False),
    Column("healed_selector", Text,    nullable=False),
    Column("timestamp",       Float,   nullable=False),
)


def _row_to_dict(row) -> dict:
    return dict(row._mapping) if hasattr(row, "_mapping") else dict(row)


class BISTDatabasePG:
    """SQLAlchemy-backed database for SQLite + PostgreSQL."""

    def __init__(self, database_url: str):
        kw: dict = {}
        if "sqlite" in database_url:
            Path(database_url.replace("sqlite:///", "")).parent.mkdir(parents=True, exist_ok=True)
            kw["connect_args"] = {"check_same_thread": False}
        else:
            kw["pool_pre_ping"] = True
        self._engine: Engine = create_engine(database_url, **kw)
        _metadata.create_all(self._engine)

    # ── Internal ───────────────────────────────────────────────────────────────

    def _conn(self) -> Connection:
        return self._engine.begin()

    # ── Test runs ──────────────────────────────────────────────────────────────

    def create_run(
        self, env_url: str, feature_path: str = "", tenant_id: Optional[int] = None
    ) -> int:
        with self._conn() as conn:
            result = conn.execute(
                test_runs.insert().values(
                    started_at=time.time(), env_url=env_url,
                    status="running", feature_path=feature_path,
                    tenant_id=tenant_id,
                )
            )
            return result.inserted_primary_key[0]

    def finish_run(self, run_id: int, status: str, duration_ms: int) -> None:
        with self._conn() as conn:
            conn.execute(
                test_runs.update()
                .where(test_runs.c.id == run_id)
                .values(status=status, duration_ms=duration_ms)
            )

    def get_runs(self, limit: int = 20, tenant_id: Optional[int] = None) -> list[dict]:
        with self._conn() as conn:
            q = test_runs.select().order_by(test_runs.c.started_at.desc()).limit(limit)
            if tenant_id is not None:
                q = q.where(test_runs.c.tenant_id == tenant_id)
            rows = conn.execute(q).fetchall()
            return [_row_to_dict(r) for r in rows]

    def get_run_detail(self, run_id: int, tenant_id: Optional[int] = None) -> dict:
        with self._conn() as conn:
            q = test_runs.select().where(test_runs.c.id == run_id)
            if tenant_id is not None:
                q = q.where(test_runs.c.tenant_id == tenant_id)
            row = conn.execute(q).fetchone()
            if not row:
                return {}
            run = _row_to_dict(row)
            scen_rows = conn.execute(
                scenarios.select().where(scenarios.c.run_id == run_id)
            ).fetchall()
            result_scenarios = []
            for s in scen_rows:
                sd = _row_to_dict(s)
                step_rows = conn.execute(
                    steps.select().where(steps.c.scenario_id == s.id)
                ).fetchall()
                sd["steps"] = [_row_to_dict(st) for st in step_rows]
                result_scenarios.append(sd)
            run["scenarios"] = result_scenarios
            return run

    # ── Scenarios ──────────────────────────────────────────────────────────────

    def create_scenario(self, run_id: int, name: str) -> int:
        with self._conn() as conn:
            result = conn.execute(
                scenarios.insert().values(run_id=run_id, name=name, status="running")
            )
            return result.inserted_primary_key[0]

    def finish_scenario(
        self, scenario_id: int, status: str, duration_ms: int,
        error: str = "", video_path: str = "",
    ) -> None:
        with self._conn() as conn:
            conn.execute(
                scenarios.update()
                .where(scenarios.c.id == scenario_id)
                .values(status=status, duration_ms=duration_ms, error=error, video_path=video_path)
            )

    # ── Steps ──────────────────────────────────────────────────────────────────

    def create_step(
        self, scenario_id: int, step_text: str, status: str,
        duration_ms: int = 0, screenshot_path: str = "",
    ) -> int:
        with self._conn() as conn:
            result = conn.execute(
                steps.insert().values(
                    scenario_id=scenario_id, step_text=step_text, status=status,
                    duration_ms=duration_ms, screenshot_path=screenshot_path,
                )
            )
            return result.inserted_primary_key[0]

    # ── Selector cache ─────────────────────────────────────────────────────────

    def cache_selector(self, step_pattern: str, selector: str) -> None:
        with self._conn() as conn:
            existing = conn.execute(
                selector_cache.select()
                .where(selector_cache.c.step_pattern == step_pattern)
                .where(selector_cache.c.selector == selector)
            ).fetchone()
            if existing:
                conn.execute(
                    selector_cache.update()
                    .where(selector_cache.c.id == existing.id)
                    .values(success_count=existing.success_count + 1, last_used=time.time())
                )
            else:
                conn.execute(
                    selector_cache.insert().values(
                        step_pattern=step_pattern, selector=selector,
                        success_count=1, last_used=time.time(),
                    )
                )

    def get_cached_selectors(self, step_pattern: str, limit: int = 5) -> list[str]:
        with self._conn() as conn:
            rows = conn.execute(
                selector_cache.select()
                .where(selector_cache.c.step_pattern == step_pattern)
                .order_by(
                    selector_cache.c.success_count.desc(),
                    selector_cache.c.last_used.desc(),
                )
                .limit(limit)
            ).fetchall()
            return [r.selector for r in rows]

    def log_healing(
        self, scenario_id: Optional[int], step_text: str,
        failed_selector: str, healed_selector: str,
    ) -> None:
        with self._conn() as conn:
            conn.execute(
                healing_log.insert().values(
                    scenario_id=scenario_id, step_text=step_text,
                    failed_selector=failed_selector, healed_selector=healed_selector,
                    timestamp=time.time(),
                )
            )

    # ── Analytics ──────────────────────────────────────────────────────────────

    def get_flaky_scenarios(self, limit: int = 10, tenant_id: Optional[int] = None) -> list[dict]:
        with self._conn() as conn:
            if tenant_id is not None:
                rows = conn.execute(text("""
                    SELECT s.name,
                        COUNT(*) AS total_runs,
                        SUM(CASE WHEN s.status = 'failed' THEN 1 ELSE 0 END) AS failures,
                        ROUND(
                            CAST(SUM(CASE WHEN s.status = 'failed' THEN 1 ELSE 0 END) AS REAL)
                            / COUNT(*) * 100, 1
                        ) AS failure_rate
                    FROM scenarios s
                    JOIN test_runs tr ON tr.id = s.run_id
                    WHERE tr.tenant_id = :tenant_id
                    GROUP BY s.name
                    HAVING SUM(CASE WHEN s.status = 'failed' THEN 1 ELSE 0 END) > 0
                       AND COUNT(*) > 1
                    ORDER BY failure_rate DESC
                    LIMIT :limit
                """), {"tenant_id": tenant_id, "limit": limit}).fetchall()
            else:
                rows = conn.execute(text("""
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
                    LIMIT :limit
                """), {"limit": limit}).fetchall()
            return [_row_to_dict(r) for r in rows]

    def get_runs_trend(self, days: int = 30, tenant_id: Optional[int] = None) -> list[dict]:
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
