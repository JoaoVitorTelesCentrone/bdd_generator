"""
Tests for bist/bist_billing.py — BillingManager: usage metering, subscriptions, Stripe webhook.

Cenários cobertos:
  Schema:
    - Tabelas usage_events e stripe_subscriptions criadas ao instanciar
  Metering:
    - record_usage insere evento
    - record_usage com quantity acumula corretamente
    - usage isolado por tenant e por event_type
    - zero quando não há eventos
    - eventos fora da janela de dias são excluídos
    - get_usage_summary retorna estrutura correta
  Subscription:
    - get_subscription retorna None inicialmente
    - upsert_subscription insere nova linha
    - upsert_subscription atualiza em conflito (ON CONFLICT)
  Webhook signature:
    - retorna False quando STRIPE_WEBHOOK_SECRET está vazio
    - retorna False para header malformado
    - retorna False para assinatura errada
    - retorna True para assinatura HMAC-SHA256 válida
  Webhook event handling:
    - subscription.created/updated atualiza tier e chama update_tier
    - subscription.deleted faz downgrade para free
    - evento desconhecido retorna o tipo sem chamar update_tier
"""
import hashlib
import hmac
import json
import os
import sqlite3
import sys
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import pytest
from bist.bist_billing import BillingManager


# ── helpers ───────────────────────────────────────────────────────────────────

def _make_stripe_sig(secret: str, payload: bytes) -> str:
    """Build a valid Stripe-Signature header value for the given payload."""
    ts = str(int(time.time()))
    signed = f"{ts}.{payload.decode()}"
    v1 = hmac.new(secret.encode(), signed.encode(), hashlib.sha256).hexdigest()
    return f"t={ts},v1={v1}"


def _sub_event(event_type: str, price_id: str, customer_id: str, sub_id: str = "sub_xxx") -> dict:
    return {
        "type": event_type,
        "data": {
            "object": {
                "id":       sub_id,
                "customer": customer_id,
                "status":   "active",
                "items":    {"data": [{"price": {"id": price_id}}]},
                "current_period_start": 0.0,
                "current_period_end":   0.0,
            }
        },
    }


# ── fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def bm(tmp_path):
    return BillingManager(db_path=tmp_path / "billing_test.db")


@pytest.fixture
def tm_mock():
    m = MagicMock()
    m.update_tier = MagicMock()
    return m


# ── schema ────────────────────────────────────────────────────────────────────

class TestSchema:

    def test_tables_created(self, bm):
        with sqlite3.connect(str(bm.db_path)) as conn:
            tables = {
                r[0] for r in
                conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
            }
        assert "usage_events" in tables
        assert "stripe_subscriptions" in tables

    def test_second_instantiation_does_not_raise(self, tmp_path):
        p = tmp_path / "double.db"
        BillingManager(db_path=p)
        BillingManager(db_path=p)


# ── usage metering ────────────────────────────────────────────────────────────

class TestUsageMetering:

    def test_record_usage_inserts_event(self, bm):
        bm.record_usage(1, "run_started")
        assert bm.get_monthly_usage(1, "run_started") == 1

    def test_record_usage_with_quantity(self, bm):
        bm.record_usage(1, "api_call", quantity=5)
        assert bm.get_monthly_usage(1, "api_call") == 5

    def test_record_usage_accumulates(self, bm):
        for _ in range(3):
            bm.record_usage(1, "run_started")
        assert bm.get_monthly_usage(1, "run_started") == 3

    def test_usage_isolated_by_tenant(self, bm):
        bm.record_usage(1, "run_started")
        bm.record_usage(2, "run_started")
        assert bm.get_monthly_usage(1, "run_started") == 1
        assert bm.get_monthly_usage(2, "run_started") == 1

    def test_usage_isolated_by_event_type(self, bm):
        bm.record_usage(1, "run_started")
        bm.record_usage(1, "api_call")
        assert bm.get_monthly_usage(1, "run_started") == 1
        assert bm.get_monthly_usage(1, "api_call") == 1

    def test_zero_when_no_events(self, bm):
        assert bm.get_monthly_usage(1, "run_started") == 0

    def test_old_events_excluded_from_window(self, bm):
        bm.record_usage(1, "run_started")
        # Force event to 60 days ago
        old_ts = time.time() - 60 * 86_400
        with sqlite3.connect(str(bm.db_path)) as conn:
            conn.execute("UPDATE usage_events SET recorded_at=?", (old_ts,))
        assert bm.get_monthly_usage(1, "run_started", days=30) == 0

    def test_recent_events_included_in_window(self, bm):
        bm.record_usage(1, "run_started", quantity=2)
        assert bm.get_monthly_usage(1, "run_started", days=30) == 2

    def test_get_usage_summary_structure(self, bm):
        bm.record_usage(1, "run_started", quantity=3)
        bm.record_usage(1, "api_call", quantity=7)
        summary = bm.get_usage_summary(1)
        assert summary["tenant_id"] == 1
        assert summary["runs"] == 3
        assert summary["api_calls"] == 7
        assert "period_days" in summary

    def test_get_usage_summary_zeros_for_new_tenant(self, bm):
        summary = bm.get_usage_summary(42)
        assert summary["runs"] == 0
        assert summary["api_calls"] == 0

    def test_get_usage_summary_custom_days(self, bm):
        summary = bm.get_usage_summary(1, days=7)
        assert summary["period_days"] == 7


# ── subscription ──────────────────────────────────────────────────────────────

class TestSubscription:

    def test_get_subscription_returns_none_initially(self, bm):
        assert bm.get_subscription(1) is None

    def test_upsert_subscription_inserts(self, bm):
        bm.upsert_subscription(1, "cus_xxx", "sub_xxx", "pro", "active", 0.0, 0.0)
        sub = bm.get_subscription(1)
        assert sub is not None
        assert sub["tier"] == "pro"
        assert sub["status"] == "active"
        assert sub["stripe_customer_id"] == "cus_xxx"

    def test_upsert_subscription_updates_on_conflict(self, bm):
        bm.upsert_subscription(1, "cus_xxx", "sub_xxx", "pro", "active", 0.0, 0.0)
        bm.upsert_subscription(1, "cus_xxx", "sub_yyy", "business", "active", 1.0, 2.0)
        sub = bm.get_subscription(1)
        assert sub["tier"] == "business"
        assert sub["stripe_subscription_id"] == "sub_yyy"

    def test_subscriptions_isolated_per_tenant(self, bm):
        bm.upsert_subscription(1, "cus_a", "sub_a", "free",   "active", 0.0, 0.0)
        bm.upsert_subscription(2, "cus_b", "sub_b", "business", "active", 0.0, 0.0)
        assert bm.get_subscription(1)["tier"] == "free"
        assert bm.get_subscription(2)["tier"] == "business"


# ── webhook signature ─────────────────────────────────────────────────────────

class TestWebhookSignature:

    def test_returns_false_when_no_secret(self, bm):
        with patch.dict(os.environ, {"STRIPE_WEBHOOK_SECRET": ""}):
            result = bm.verify_webhook_signature(b"payload", "t=1,v1=abc")
        assert result is False

    def test_returns_false_for_header_without_timestamp(self, bm):
        with patch.dict(os.environ, {"STRIPE_WEBHOOK_SECRET": "secret"}):
            result = bm.verify_webhook_signature(b"payload", "v1=abc")
        assert result is False

    def test_returns_false_for_header_without_v1(self, bm):
        with patch.dict(os.environ, {"STRIPE_WEBHOOK_SECRET": "secret"}):
            result = bm.verify_webhook_signature(b"payload", "t=123")
        assert result is False

    def test_returns_false_for_wrong_signature(self, bm):
        with patch.dict(os.environ, {"STRIPE_WEBHOOK_SECRET": "real_secret"}):
            result = bm.verify_webhook_signature(b"payload", "t=123,v1=wrong_sig")
        assert result is False

    def test_returns_true_for_valid_signature(self, bm):
        secret = "whsec_test_secret"
        payload = b'{"type":"customer.subscription.created"}'
        sig_header = _make_stripe_sig(secret, payload)
        with patch.dict(os.environ, {"STRIPE_WEBHOOK_SECRET": secret}):
            result = bm.verify_webhook_signature(payload, sig_header)
        assert result is True

    def test_returns_false_for_tampered_payload(self, bm):
        secret = "whsec_test_secret"
        original = b'{"type":"test"}'
        tampered = b'{"type":"other"}'
        sig_header = _make_stripe_sig(secret, original)
        with patch.dict(os.environ, {"STRIPE_WEBHOOK_SECRET": secret}):
            result = bm.verify_webhook_signature(tampered, sig_header)
        assert result is False


# ── webhook event handling ────────────────────────────────────────────────────

class TestWebhookEventHandling:

    def test_subscription_created_returns_event_type(self, bm, tm_mock):
        bm.upsert_subscription(1, "cus_test", "sub_test", "free", "active", 0.0, 0.0)
        price_pro = os.getenv("STRIPE_PRICE_PRO", "price_pro")
        event = _sub_event("customer.subscription.created", price_pro, "cus_test")
        result = bm.handle_webhook_event(event, tm_mock)
        assert result == "customer.subscription.created"

    def test_subscription_created_calls_update_tier(self, bm, tm_mock):
        bm.upsert_subscription(1, "cus_test", "sub_test", "free", "active", 0.0, 0.0)
        price_pro = os.getenv("STRIPE_PRICE_PRO", "price_pro")
        event = _sub_event("customer.subscription.created", price_pro, "cus_test")
        bm.handle_webhook_event(event, tm_mock)
        tm_mock.update_tier.assert_called_once()

    def test_subscription_updated_calls_update_tier(self, bm, tm_mock):
        bm.upsert_subscription(1, "cus_up", "sub_up", "pro", "active", 0.0, 0.0)
        price_business = os.getenv("STRIPE_PRICE_BUSINESS", "price_business")
        event = _sub_event("customer.subscription.updated", price_business, "cus_up")
        bm.handle_webhook_event(event, tm_mock)
        tm_mock.update_tier.assert_called_once()

    def test_subscription_deleted_downgrades_to_free(self, bm, tm_mock):
        bm.upsert_subscription(1, "cus_del", "sub_del", "pro", "active", 0.0, 0.0)
        event = {
            "type": "customer.subscription.deleted",
            "data": {"object": {"customer": "cus_del"}},
        }
        bm.handle_webhook_event(event, tm_mock)
        tm_mock.update_tier.assert_called_once_with(1, "free")

    def test_subscription_deleted_marks_canceled_in_db(self, bm, tm_mock):
        bm.upsert_subscription(1, "cus_del2", "sub_del2", "pro", "active", 0.0, 0.0)
        event = {
            "type": "customer.subscription.deleted",
            "data": {"object": {"customer": "cus_del2"}},
        }
        bm.handle_webhook_event(event, tm_mock)
        sub = bm.get_subscription(1)
        assert sub["status"] == "canceled"

    def test_unknown_event_returns_event_type_without_updating_tier(self, bm, tm_mock):
        event = {"type": "payment_intent.created", "data": {"object": {}}}
        result = bm.handle_webhook_event(event, tm_mock)
        assert result == "payment_intent.created"
        tm_mock.update_tier.assert_not_called()

    def test_event_for_unknown_customer_does_not_raise(self, bm, tm_mock):
        price_pro = os.getenv("STRIPE_PRICE_PRO", "price_pro")
        event = _sub_event("customer.subscription.created", price_pro, "cus_unknown_xyz")
        result = bm.handle_webhook_event(event, tm_mock)
        assert result == "customer.subscription.created"
        tm_mock.update_tier.assert_not_called()
