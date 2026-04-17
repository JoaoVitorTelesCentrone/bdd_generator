"""
Tests for backend/presentation/routers/tenants_router.py — Phase 4 REST API.

Cenários cobertos:
  POST /api/tenants:
    - Retorna 201 com id/name/tier
    - Tier customizado é persistido
    - Tier inválido retorna 400
  GET /api/tenants:
    - Retorna 200 com lista
  GET /api/tenants/{id}:
    - Retorna 200 com dados do tenant
    - Retorna 404 para tenant inexistente
  PATCH /api/tenants/{id}/tier:
    - Retorna 200 e atualiza tier
    - Tier inválido retorna 400
    - Tenant inexistente retorna 404
  POST /api/tenants/{id}/api-keys:
    - Retorna 201 com raw_key prefixada "bist_"
    - Tenant inexistente retorna 404
  GET /api/tenants/{id}/api-keys:
    - Retorna 200 com lista de chaves
  DELETE /api/tenants/{id}/api-keys/{prefix}:
    - Retorna 204 para chave existente
    - Retorna 404 para chave inexistente
  GET /api/tenants/{id}/usage:
    - Retorna 200 com runs e api_calls
    - Tenant inexistente retorna 404
  POST /api/billing/webhook:
    - Assinatura inválida retorna 400
    - Evento válido retorna {received: true}
  GET /api/sso/oauth2/authorize:
    - Retorna redirect (302/307)
  GET /api/sso/oauth2/callback:
    - State inválido retorna 400
  POST /api/sso/saml/{id}/configure:
    - Retorna 204
  GET /api/sso/saml/{id}/login:
    - Retorna redirect para tenant com configuração
    - Tenant sem configuração retorna 404
  POST /api/sso/saml/{id}/acs:
    - Sem SAMLResponse retorna 400
    - Com SAMLResponse válido retorna 200
"""
import base64
import json
import os
import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from bist.bist_tenants import TenantManager
from bist.bist_billing import BillingManager
from bist.bist_sso import SSOManager
import backend.presentation.routers.tenants_router as tenants_router_module
from backend.presentation.routers.tenants_router import router


# ── fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def managers(tmp_path):
    """Isolated TenantManager, BillingManager, SSOManager sharing the same temp DB."""
    db = tmp_path / "router_phase4_test.db"
    tm  = TenantManager(db_path=db)
    bm  = BillingManager(db_path=db)
    sso = SSOManager(db_path=db)
    return tm, bm, sso


@pytest.fixture
def client(managers):
    """TestClient with module-level singletons replaced by test instances."""
    tm, bm, sso = managers
    app = FastAPI()
    app.include_router(router)
    tenants_router_module._tenants = tm
    tenants_router_module._billing = bm
    tenants_router_module._sso     = sso
    return TestClient(app, raise_server_exceptions=True)


# ── POST /api/tenants ─────────────────────────────────────────────────────────

class TestCreateTenant:

    def test_returns_201_with_fields(self, client):
        resp = client.post("/api/tenants", json={"name": "Acme Corp"})
        assert resp.status_code == 201
        body = resp.json()
        assert body["name"] == "Acme Corp"
        assert body["tier"] == "free"
        assert isinstance(body["id"], int)

    def test_custom_tier_returned(self, client):
        resp = client.post("/api/tenants", json={"name": "BigCorp", "tier": "pro"})
        assert resp.status_code == 201
        assert resp.json()["tier"] == "pro"

    def test_invalid_tier_returns_400(self, client):
        resp = client.post("/api/tenants", json={"name": "Corp", "tier": "invalid_tier"})
        assert resp.status_code == 400

    def test_missing_name_returns_422(self, client):
        resp = client.post("/api/tenants", json={"tier": "free"})
        assert resp.status_code == 422


# ── GET /api/tenants ──────────────────────────────────────────────────────────

class TestListTenants:

    def test_returns_200_with_list(self, client, managers):
        tm, _, _ = managers
        tm.create_tenant("Alpha")
        resp = client.get("/api/tenants")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)
        assert len(resp.json()) >= 1

    def test_empty_list_when_no_tenants(self, client):
        resp = client.get("/api/tenants")
        assert resp.status_code == 200
        assert resp.json() == []


# ── GET /api/tenants/{id} ─────────────────────────────────────────────────────

class TestGetTenant:

    def test_returns_200_with_tenant_data(self, client, managers):
        tm, _, _ = managers
        t = tm.create_tenant("Corp")
        resp = client.get(f"/api/tenants/{t['id']}")
        assert resp.status_code == 200
        assert resp.json()["id"] == t["id"]
        assert resp.json()["name"] == "Corp"

    def test_unknown_tenant_returns_404(self, client):
        resp = client.get("/api/tenants/99999")
        assert resp.status_code == 404


# ── PATCH /api/tenants/{id}/tier ─────────────────────────────────────────────

class TestUpdateTier:

    def test_returns_200_with_new_tier(self, client, managers):
        tm, _, _ = managers
        t = tm.create_tenant("Corp")
        resp = client.patch(f"/api/tenants/{t['id']}/tier", json={"tier": "pro"})
        assert resp.status_code == 200
        assert resp.json()["tier"] == "pro"

    def test_invalid_tier_returns_400(self, client, managers):
        tm, _, _ = managers
        t = tm.create_tenant("Corp")
        resp = client.patch(f"/api/tenants/{t['id']}/tier", json={"tier": "platinum"})
        assert resp.status_code == 400

    def test_unknown_tenant_returns_404(self, client):
        resp = client.patch("/api/tenants/99999/tier", json={"tier": "pro"})
        assert resp.status_code == 404

    def test_tier_persisted_in_db(self, client, managers):
        tm, _, _ = managers
        t = tm.create_tenant("Corp")
        client.patch(f"/api/tenants/{t['id']}/tier", json={"tier": "business"})
        assert tm.get_tenant(t["id"])["tier"] == "business"


# ── POST /api/tenants/{id}/api-keys ──────────────────────────────────────────

class TestCreateApiKey:

    def test_returns_201_with_raw_key(self, client, managers):
        tm, _, _ = managers
        t = tm.create_tenant("Corp")
        resp = client.post(f"/api/tenants/{t['id']}/api-keys", json={"label": "CI"})
        assert resp.status_code == 201
        body = resp.json()
        assert body["raw_key"].startswith("bist_")
        assert body["label"] == "CI"
        assert "key_prefix" in body

    def test_unknown_tenant_returns_404(self, client):
        resp = client.post("/api/tenants/99999/api-keys", json={"label": "x"})
        assert resp.status_code == 404


# ── GET /api/tenants/{id}/api-keys ───────────────────────────────────────────

class TestListApiKeys:

    def test_returns_200_with_keys(self, client, managers):
        tm, _, _ = managers
        t = tm.create_tenant("Corp")
        tm.create_api_key(t["id"], label="key1")
        tm.create_api_key(t["id"], label="key2")
        resp = client.get(f"/api/tenants/{t['id']}/api-keys")
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    def test_empty_list_for_new_tenant(self, client, managers):
        tm, _, _ = managers
        t = tm.create_tenant("Corp")
        resp = client.get(f"/api/tenants/{t['id']}/api-keys")
        assert resp.json() == []

    def test_unknown_tenant_returns_404(self, client):
        resp = client.get("/api/tenants/99999/api-keys")
        assert resp.status_code == 404


# ── DELETE /api/tenants/{id}/api-keys/{prefix} ───────────────────────────────

class TestRevokeApiKey:

    def test_returns_204_for_existing_key(self, client, managers):
        tm, _, _ = managers
        t = tm.create_tenant("Corp")
        raw = tm.create_api_key(t["id"])
        prefix = raw[:12]
        resp = client.delete(f"/api/tenants/{t['id']}/api-keys/{prefix}")
        assert resp.status_code == 204

    def test_returns_404_for_nonexistent_key(self, client, managers):
        tm, _, _ = managers
        t = tm.create_tenant("Corp")
        resp = client.delete(f"/api/tenants/{t['id']}/api-keys/bist_XXXXXXXX")
        assert resp.status_code == 404


# ── GET /api/tenants/{id}/usage ───────────────────────────────────────────────

class TestUsage:

    def test_returns_200_with_usage_summary(self, client, managers):
        tm, bm, _ = managers
        t = tm.create_tenant("Corp")
        bm.record_usage(t["id"], "run_started", quantity=5)
        resp = client.get(f"/api/tenants/{t['id']}/usage")
        assert resp.status_code == 200
        body = resp.json()
        assert body["runs"] == 5
        assert body["tenant_id"] == t["id"]

    def test_zero_usage_for_new_tenant(self, client, managers):
        tm, _, _ = managers
        t = tm.create_tenant("Corp")
        resp = client.get(f"/api/tenants/{t['id']}/usage")
        assert resp.status_code == 200
        assert resp.json()["runs"] == 0

    def test_unknown_tenant_returns_404(self, client):
        resp = client.get("/api/tenants/99999/usage")
        assert resp.status_code == 404

    def test_days_param_forwarded(self, client, managers):
        tm, _, _ = managers
        t = tm.create_tenant("Corp")
        resp = client.get(f"/api/tenants/{t['id']}/usage?days=7")
        assert resp.status_code == 200
        assert resp.json()["period_days"] == 7


# ── POST /api/billing/webhook ─────────────────────────────────────────────────

class TestBillingWebhook:

    def test_invalid_signature_returns_400(self, client):
        resp = client.post(
            "/api/billing/webhook",
            content=b'{"type":"test"}',
            headers={"stripe-signature": "t=1,v1=invalid_sig"},
        )
        assert resp.status_code == 400

    def test_valid_event_returns_received_true(self, client, managers):
        _, bm, _ = managers
        payload = json.dumps({
            "type": "payment_intent.created",
            "data": {"object": {}},
        }).encode()
        with patch.object(bm, "verify_webhook_signature", return_value=True):
            resp = client.post(
                "/api/billing/webhook",
                content=payload,
                headers={"stripe-signature": "t=1,v1=mock"},
            )
        assert resp.status_code == 200
        assert resp.json()["received"] is True

    def test_valid_event_returns_event_type(self, client, managers):
        _, bm, _ = managers
        payload = json.dumps({
            "type": "customer.subscription.deleted",
            "data": {"object": {"customer": "cus_none"}},
        }).encode()
        with patch.object(bm, "verify_webhook_signature", return_value=True):
            resp = client.post(
                "/api/billing/webhook",
                content=payload,
                headers={"stripe-signature": "t=1,v1=mock"},
            )
        assert resp.json()["event_type"] == "customer.subscription.deleted"

    def test_invalid_json_returns_400(self, client, managers):
        _, bm, _ = managers
        with patch.object(bm, "verify_webhook_signature", return_value=True):
            resp = client.post(
                "/api/billing/webhook",
                content=b"not json at all",
                headers={"stripe-signature": "t=1,v1=mock"},
            )
        assert resp.status_code == 400


# ── GET /api/sso/oauth2/authorize ─────────────────────────────────────────────

class TestOAuth2Authorize:

    def test_returns_redirect(self, client):
        resp = client.get("/api/sso/oauth2/authorize", follow_redirects=False)
        assert resp.status_code in (302, 307)

    def test_redirect_location_contains_state(self, client):
        resp = client.get("/api/sso/oauth2/authorize", follow_redirects=False)
        location = resp.headers.get("location", "")
        assert "state=" in location

    def test_accepts_tenant_id_param(self, client):
        resp = client.get("/api/sso/oauth2/authorize?tenant_id=1", follow_redirects=False)
        assert resp.status_code in (302, 307)


# ── GET /api/sso/oauth2/callback ──────────────────────────────────────────────

class TestOAuth2Callback:

    def test_invalid_state_returns_400(self, client):
        resp = client.get("/api/sso/oauth2/callback?code=xxx&state=nonexistent_state")
        assert resp.status_code == 400


# ── POST /api/sso/saml/{id}/configure ────────────────────────────────────────

class TestSamlConfigure:

    def test_returns_204(self, client, managers):
        tm, _, _ = managers
        t = tm.create_tenant("Corp")
        resp = client.post(
            f"/api/sso/saml/{t['id']}/configure",
            json={
                "idp_entity_id": "https://idp.example.com",
                "idp_sso_url":   "https://idp.example.com/sso",
                "idp_cert":      "MIIC_test_cert",
            },
        )
        assert resp.status_code == 204

    def test_unknown_tenant_returns_404(self, client):
        resp = client.post(
            "/api/sso/saml/99999/configure",
            json={
                "idp_entity_id": "https://idp.example.com",
                "idp_sso_url":   "https://idp.example.com/sso",
                "idp_cert":      "cert",
            },
        )
        assert resp.status_code == 404

    def test_stores_config_in_db(self, client, managers):
        tm, _, sso = managers
        t = tm.create_tenant("Corp")
        client.post(
            f"/api/sso/saml/{t['id']}/configure",
            json={
                "idp_entity_id": "https://idp.example.com",
                "idp_sso_url":   "https://sso.example.com",
                "idp_cert":      "cert",
            },
        )
        config = sso.get_saml_config(t["id"])
        assert config is not None
        assert config["idp_sso_url"] == "https://sso.example.com"


# ── GET /api/sso/saml/{id}/login ─────────────────────────────────────────────

class TestSamlLogin:

    def test_redirects_to_idp(self, client, managers):
        tm, _, sso = managers
        t = tm.create_tenant("Corp")
        sso.saml_configure(t["id"], "entity", "https://idp.example.com/sso", "cert")
        resp = client.get(f"/api/sso/saml/{t['id']}/login", follow_redirects=False)
        assert resp.status_code in (302, 307)
        assert "idp.example.com" in resp.headers.get("location", "")

    def test_unconfigured_tenant_returns_404(self, client, managers):
        tm, _, _ = managers
        t = tm.create_tenant("Corp")
        resp = client.get(f"/api/sso/saml/{t['id']}/login", follow_redirects=False)
        assert resp.status_code == 404


# ── POST /api/sso/saml/{id}/acs ───────────────────────────────────────────────

class TestSamlAcs:

    def _configure(self, managers):
        tm, _, sso = managers
        t = tm.create_tenant("Corp")
        sso.saml_configure(
            t["id"], "entity", "https://idp.example.com/sso", "cert"
        )
        return t

    def test_missing_saml_response_returns_400(self, client, managers):
        t = self._configure(managers)
        resp = client.post(f"/api/sso/saml/{t['id']}/acs", data={})
        assert resp.status_code == 400

    def test_valid_saml_response_returns_200(self, client, managers):
        t = self._configure(managers)
        xml = (
            '<root xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion">'
            "<saml:Assertion>"
            "<saml:AttributeStatement>"
            '<saml:Attribute Name="email">'
            "<saml:AttributeValue>user@corp.com</saml:AttributeValue>"
            "</saml:Attribute>"
            "</saml:AttributeStatement>"
            "</saml:Assertion>"
            "</root>"
        )
        b64 = base64.b64encode(xml.encode()).decode()
        resp = client.post(
            f"/api/sso/saml/{t['id']}/acs",
            data={"SAMLResponse": b64},
        )
        assert resp.status_code == 200
        assert resp.json()["tenant_id"] == t["id"]

    def test_invalid_saml_response_returns_400(self, client, managers):
        t = self._configure(managers)
        # Invalid base64 → saml_process_response returns None → 400
        resp = client.post(
            f"/api/sso/saml/{t['id']}/acs",
            data={"SAMLResponse": "!!!invalid_base64!!!"},
        )
        assert resp.status_code == 400
