"""Stripe billing: usage metering, webhook handling, subscription sync.

Environment variables:
  STRIPE_SECRET_KEY       — Stripe secret key (sk_live_... / sk_test_...)
  STRIPE_WEBHOOK_SECRET   — Webhook signing secret (whsec_...)
  STRIPE_PRICE_PRO        — Stripe Price ID that maps to the 'pro' tier
  STRIPE_PRICE_BUSINESS   — Stripe Price ID that maps to the 'business' tier

Tables added to bist.db:
  usage_events          — per-tenant event log (run started, API call, etc.)
  stripe_subscriptions  — mirrors Stripe subscription state per tenant
"""

import hashlib
import hmac
import json
import os
import sqlite3
import time
from pathlib import Path
from typing import Optional

DB_PATH = Path.home() / ".bist" / "bist.db"

_STRIPE_SECRET_KEY      = os.getenv("STRIPE_SECRET_KEY", "")
_STRIPE_WEBHOOK_SECRET  = os.getenv("STRIPE_WEBHOOK_SECRET", "")
_STRIPE_PRICE_PRO       = os.getenv("STRIPE_PRICE_PRO", "price_pro")
_STRIPE_PRICE_BUSINESS  = os.getenv("STRIPE_PRICE_BUSINESS", "price_business")

PLAN_TIER_MAP: dict[str, str] = {
    _STRIPE_PRICE_PRO:      "pro",
    _STRIPE_PRICE_BUSINESS: "business",
}


class BillingManager:
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
                CREATE TABLE IF NOT EXISTS usage_events (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id   INTEGER NOT NULL,
                    event_type  TEXT    NOT NULL,
                    quantity    INTEGER NOT NULL DEFAULT 1,
                    metadata    TEXT    NOT NULL DEFAULT '{}',
                    recorded_at REAL    NOT NULL
                );
                CREATE TABLE IF NOT EXISTS stripe_subscriptions (
                    id                     INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id              INTEGER NOT NULL UNIQUE,
                    stripe_customer_id     TEXT    NOT NULL,
                    stripe_subscription_id TEXT    NOT NULL,
                    tier                   TEXT    NOT NULL DEFAULT 'free',
                    status                 TEXT    NOT NULL DEFAULT 'active',
                    current_period_start   REAL,
                    current_period_end     REAL,
                    updated_at             REAL    NOT NULL
                );
            """)

    # ── Usage metering ────────────────────────────────────────────────────────

    def record_usage(
        self,
        tenant_id: int,
        event_type: str,
        quantity: int = 1,
        metadata: Optional[dict] = None,
    ) -> None:
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO usage_events (tenant_id, event_type, quantity, metadata, recorded_at) "
                "VALUES (?, ?, ?, ?, ?)",
                (tenant_id, event_type, quantity, json.dumps(metadata or {}), time.time()),
            )

    def get_monthly_usage(self, tenant_id: int, event_type: str, days: int = 30) -> int:
        cutoff = time.time() - days * 86_400
        with self._connect() as conn:
            row = conn.execute(
                "SELECT COALESCE(SUM(quantity), 0) AS total FROM usage_events "
                "WHERE tenant_id = ? AND event_type = ? AND recorded_at >= ?",
                (tenant_id, event_type, cutoff),
            ).fetchone()
            return int(row["total"])

    def get_usage_summary(self, tenant_id: int, days: int = 30) -> dict:
        runs = self.get_monthly_usage(tenant_id, "run_started", days)
        api_calls = self.get_monthly_usage(tenant_id, "api_call", days)
        return {"tenant_id": tenant_id, "period_days": days, "runs": runs, "api_calls": api_calls}

    # ── Stripe subscription sync ──────────────────────────────────────────────

    def get_subscription(self, tenant_id: int) -> Optional[dict]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM stripe_subscriptions WHERE tenant_id = ?", (tenant_id,)
            ).fetchone()
            return dict(row) if row else None

    def upsert_subscription(
        self,
        tenant_id: int,
        customer_id: str,
        subscription_id: str,
        tier: str,
        status: str,
        period_start: float,
        period_end: float,
    ) -> None:
        with self._connect() as conn:
            conn.execute(
                """INSERT INTO stripe_subscriptions
                       (tenant_id, stripe_customer_id, stripe_subscription_id,
                        tier, status, current_period_start, current_period_end, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                   ON CONFLICT(tenant_id) DO UPDATE SET
                       stripe_customer_id=excluded.stripe_customer_id,
                       stripe_subscription_id=excluded.stripe_subscription_id,
                       tier=excluded.tier,
                       status=excluded.status,
                       current_period_start=excluded.current_period_start,
                       current_period_end=excluded.current_period_end,
                       updated_at=excluded.updated_at""",
                (tenant_id, customer_id, subscription_id, tier, status,
                 period_start, period_end, time.time()),
            )

    # ── Webhook ───────────────────────────────────────────────────────────────

    def verify_webhook_signature(self, payload: bytes, sig_header: str) -> bool:
        """Verify Stripe webhook signature (Stripe-Signature header)."""
        secret = os.getenv("STRIPE_WEBHOOK_SECRET", _STRIPE_WEBHOOK_SECRET)
        if not secret:
            return False
        parts: dict[str, str] = {}
        for part in sig_header.split(","):
            if "=" in part:
                k, v = part.split("=", 1)
                parts[k.strip()] = v.strip()
        timestamp = parts.get("t", "")
        v1_sig = parts.get("v1", "")
        if not timestamp or not v1_sig:
            return False
        signed_payload = f"{timestamp}.{payload.decode('utf-8')}"
        expected = hmac.new(
            secret.encode("utf-8"),
            signed_payload.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        return hmac.compare_digest(expected, v1_sig)

    def handle_webhook_event(self, event: dict, tenant_manager) -> str:
        """Process a verified Stripe event dict. Returns the event type string."""
        event_type: str = event.get("type", "")
        obj: dict = event.get("data", {}).get("object", {})

        if event_type in (
            "customer.subscription.created",
            "customer.subscription.updated",
        ):
            customer_id = obj.get("customer", "")
            subscription_id = obj.get("id", "")
            status = obj.get("status", "active")
            items = obj.get("items", {}).get("data", [])
            price_id = items[0].get("price", {}).get("id", "") if items else ""
            tier = PLAN_TIER_MAP.get(price_id, "free")
            period_start = float(obj.get("current_period_start", 0))
            period_end = float(obj.get("current_period_end", 0))

            tenant_id = self._tenant_id_from_customer(customer_id)
            if tenant_id:
                self.upsert_subscription(
                    tenant_id, customer_id, subscription_id,
                    tier, status, period_start, period_end,
                )
                tenant_manager.update_tier(tenant_id, tier)

        elif event_type == "customer.subscription.deleted":
            customer_id = obj.get("customer", "")
            tenant_id = self._tenant_id_from_customer(customer_id)
            if tenant_id:
                tenant_manager.update_tier(tenant_id, "free")
                with self._connect() as conn:
                    conn.execute(
                        "UPDATE stripe_subscriptions SET status='canceled', updated_at=? WHERE tenant_id=?",
                        (time.time(), tenant_id),
                    )

        return event_type

    def _tenant_id_from_customer(self, customer_id: str) -> Optional[int]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT tenant_id FROM stripe_subscriptions WHERE stripe_customer_id = ?",
                (customer_id,),
            ).fetchone()
            return row["tenant_id"] if row else None
