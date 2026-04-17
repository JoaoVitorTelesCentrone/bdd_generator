"""Multi-tenancy: tenant management, API key generation/validation, tier enforcement.

Tables (added to bist.db by _init_schema):
  tenants   — one row per organisation
  api_keys  — hashed keys scoped to a tenant

Tier limits (runs per calendar month):
  free     → 50 runs
  pro      → 1 000 runs
  business → unlimited
"""

import hashlib
import secrets
import sqlite3
import time
from pathlib import Path
from typing import Optional

DB_PATH = Path.home() / ".bist" / "bist.db"

TIER_LIMITS: dict[str, dict] = {
    "free":     {"runs_per_month": 50,    "api_calls_per_month": 500},
    "pro":      {"runs_per_month": 1_000, "api_calls_per_month": 10_000},
    "business": {"runs_per_month": -1,    "api_calls_per_month": -1},
}


class TierLimitExceeded(Exception):
    pass


class TenantManager:
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS tenants (
                    id         INTEGER PRIMARY KEY AUTOINCREMENT,
                    name       TEXT    NOT NULL,
                    tier       TEXT    NOT NULL DEFAULT 'free',
                    created_at REAL    NOT NULL,
                    active     INTEGER NOT NULL DEFAULT 1
                );
                CREATE TABLE IF NOT EXISTS api_keys (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id   INTEGER NOT NULL REFERENCES tenants(id),
                    key_hash    TEXT    NOT NULL UNIQUE,
                    key_prefix  TEXT    NOT NULL,
                    label       TEXT    NOT NULL DEFAULT '',
                    created_at  REAL    NOT NULL,
                    last_used   REAL,
                    active      INTEGER NOT NULL DEFAULT 1
                );
            """)

    # ── Tenant CRUD ───────────────────────────────────────────────────────────

    def create_tenant(self, name: str, tier: str = "free") -> dict:
        if tier not in TIER_LIMITS:
            raise ValueError(f"Unknown tier '{tier}'. Valid: {list(TIER_LIMITS)}")
        with self._connect() as conn:
            cur = conn.execute(
                "INSERT INTO tenants (name, tier, created_at) VALUES (?, ?, ?)",
                (name, tier, time.time()),
            )
            return {"id": cur.lastrowid, "name": name, "tier": tier}

    def get_tenant(self, tenant_id: int) -> Optional[dict]:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM tenants WHERE id = ?", (tenant_id,)).fetchone()
            return dict(row) if row else None

    def list_tenants(self) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM tenants ORDER BY created_at DESC").fetchall()
            return [dict(r) for r in rows]

    def update_tier(self, tenant_id: int, tier: str) -> None:
        if tier not in TIER_LIMITS:
            raise ValueError(f"Unknown tier '{tier}'.")
        with self._connect() as conn:
            conn.execute("UPDATE tenants SET tier = ? WHERE id = ?", (tier, tenant_id))

    def deactivate_tenant(self, tenant_id: int) -> None:
        with self._connect() as conn:
            conn.execute("UPDATE tenants SET active = 0 WHERE id = ?", (tenant_id,))

    # ── API key management ────────────────────────────────────────────────────

    def create_api_key(self, tenant_id: int, label: str = "") -> str:
        """Generate a new API key and return the raw value (shown once)."""
        raw = f"bist_{secrets.token_urlsafe(32)}"
        prefix = raw[:12]
        key_hash = hashlib.sha256(raw.encode()).hexdigest()
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO api_keys (tenant_id, key_hash, key_prefix, label, created_at) "
                "VALUES (?, ?, ?, ?, ?)",
                (tenant_id, key_hash, prefix, label, time.time()),
            )
        return raw

    def validate_api_key(self, raw_key: str) -> Optional[dict]:
        """Return tenant info dict if the key is valid and active, else None."""
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
        with self._connect() as conn:
            row = conn.execute(
                """SELECT ak.id, ak.tenant_id, t.name, t.tier,
                          t.active AS tenant_active, ak.active
                   FROM api_keys ak
                   JOIN tenants t ON t.id = ak.tenant_id
                   WHERE ak.key_hash = ?""",
                (key_hash,),
            ).fetchone()
            if not row or not row["active"] or not row["tenant_active"]:
                return None
            conn.execute(
                "UPDATE api_keys SET last_used = ? WHERE id = ?",
                (time.time(), row["id"]),
            )
            return {
                "tenant_id":   row["tenant_id"],
                "tenant_name": row["name"],
                "tier":        row["tier"],
            }

    def list_api_keys(self, tenant_id: int) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT id, key_prefix, label, created_at, last_used, active "
                "FROM api_keys WHERE tenant_id = ? ORDER BY created_at DESC",
                (tenant_id,),
            ).fetchall()
            return [dict(r) for r in rows]

    def revoke_api_key(self, key_prefix: str, tenant_id: int) -> bool:
        with self._connect() as conn:
            cur = conn.execute(
                "UPDATE api_keys SET active = 0 WHERE key_prefix = ? AND tenant_id = ?",
                (key_prefix, tenant_id),
            )
            return cur.rowcount > 0

    # ── Tier enforcement ──────────────────────────────────────────────────────

    def enforce_run_limit(self, tenant_id: int, tier: str, monthly_runs: int) -> None:
        """Raise TierLimitExceeded when the tenant has hit their monthly run quota."""
        max_runs = TIER_LIMITS.get(tier, TIER_LIMITS["free"])["runs_per_month"]
        if max_runs != -1 and monthly_runs >= max_runs:
            raise TierLimitExceeded(
                f"Tier '{tier}' limit of {max_runs} runs/month reached. "
                "Upgrade your plan to continue."
            )
