"""
Tests for bist/bist_tenants.py — TenantManager: tenants, API keys, tier enforcement.

Cenários cobertos:
  Schema:
    - Tabelas tenants e api_keys criadas ao instanciar
    - Segunda instanciação não levanta exceção
  create_tenant:
    - Retorna dict com id/name/tier
    - Tier customizado é persistido
    - Tier inválido levanta ValueError
    - Múltiplos tenants têm IDs únicos
  get_tenant:
    - Retorna dict para tenant conhecido
    - Retorna None para tenant desconhecido
    - active=1 por padrão
  list_tenants:
    - Retorna lista; mais recente primeiro
  update_tier:
    - Atualiza tier corretamente
    - Tier inválido levanta ValueError
    - Todos os tiers válidos são aceitos
  deactivate_tenant:
    - Seta active=0
  API keys:
    - create_api_key retorna string prefixada com "bist_"
    - Chaves geradas são únicas
    - validate_api_key retorna info do tenant para chave válida
    - validate_api_key retorna None para chave inválida
    - validate_api_key retorna None para chave revogada
    - validate_api_key retorna None quando tenant está desativado
    - list_api_keys retorna chaves do tenant
    - revoke_api_key retorna True para chave existente
    - revoke_api_key retorna False para chave inexistente
  enforce_run_limit:
    - Não levanta quando abaixo do limite
    - Levanta TierLimitExceeded ao atingir limite
    - Tier business é ilimitado
    - Limite do tier pro é respeitado
"""
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import pytest
from bist.bist_tenants import TenantManager, TierLimitExceeded, TIER_LIMITS


# ── fixture ───────────────────────────────────────────────────────────────────

@pytest.fixture
def tm(tmp_path):
    return TenantManager(db_path=tmp_path / "tenants_test.db")


# ── schema ────────────────────────────────────────────────────────────────────

class TestSchema:

    def test_tables_created(self, tm):
        import sqlite3
        with sqlite3.connect(str(tm.db_path)) as conn:
            tables = {
                r[0] for r in
                conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
            }
        assert "tenants" in tables
        assert "api_keys" in tables

    def test_second_instantiation_does_not_raise(self, tmp_path):
        p = tmp_path / "double.db"
        TenantManager(db_path=p)
        TenantManager(db_path=p)


# ── create_tenant ─────────────────────────────────────────────────────────────

class TestCreateTenant:

    def test_returns_dict_with_id_name_tier(self, tm):
        result = tm.create_tenant("Acme Corp")
        assert isinstance(result["id"], int)
        assert result["name"] == "Acme Corp"
        assert result["tier"] == "free"

    def test_custom_tier_stored(self, tm):
        result = tm.create_tenant("Big Corp", tier="pro")
        assert result["tier"] == "pro"

    def test_invalid_tier_raises_value_error(self, tm):
        with pytest.raises(ValueError, match="Unknown tier"):
            tm.create_tenant("Bad Corp", tier="platinum")

    def test_multiple_tenants_have_unique_ids(self, tm):
        ids = [tm.create_tenant(f"Org {i}")["id"] for i in range(3)]
        assert len(set(ids)) == 3

    def test_all_valid_tiers_accepted(self, tm):
        for i, tier in enumerate(TIER_LIMITS):
            result = tm.create_tenant(f"Corp {i}", tier=tier)
            assert result["tier"] == tier


# ── get_tenant ────────────────────────────────────────────────────────────────

class TestGetTenant:

    def test_returns_dict_for_known_tenant(self, tm):
        t = tm.create_tenant("Acme")
        result = tm.get_tenant(t["id"])
        assert result is not None
        assert result["name"] == "Acme"

    def test_returns_none_for_unknown_tenant(self, tm):
        assert tm.get_tenant(99999) is None

    def test_active_is_1_by_default(self, tm):
        t = tm.create_tenant("Active Corp")
        assert tm.get_tenant(t["id"])["active"] == 1

    def test_tier_matches_creation_tier(self, tm):
        t = tm.create_tenant("Corp", tier="business")
        assert tm.get_tenant(t["id"])["tier"] == "business"


# ── list_tenants ──────────────────────────────────────────────────────────────

class TestListTenants:

    def test_returns_list(self, tm):
        tm.create_tenant("Alpha")
        assert isinstance(tm.list_tenants(), list)

    def test_most_recent_first(self, tm):
        tm.create_tenant("First")
        time.sleep(0.01)
        tm.create_tenant("Second")
        result = tm.list_tenants()
        assert result[0]["name"] == "Second"

    def test_empty_list_when_no_tenants(self, tm):
        assert tm.list_tenants() == []


# ── update_tier ───────────────────────────────────────────────────────────────

class TestUpdateTier:

    def test_updates_tier(self, tm):
        t = tm.create_tenant("Corp")
        tm.update_tier(t["id"], "pro")
        assert tm.get_tenant(t["id"])["tier"] == "pro"

    def test_invalid_tier_raises_value_error(self, tm):
        t = tm.create_tenant("Corp")
        with pytest.raises(ValueError):
            tm.update_tier(t["id"], "enterprise")

    def test_all_valid_tiers_accepted(self, tm):
        t = tm.create_tenant("Corp")
        for tier in TIER_LIMITS:
            tm.update_tier(t["id"], tier)
            assert tm.get_tenant(t["id"])["tier"] == tier


# ── deactivate_tenant ─────────────────────────────────────────────────────────

class TestDeactivateTenant:

    def test_sets_active_to_zero(self, tm):
        t = tm.create_tenant("Corp")
        tm.deactivate_tenant(t["id"])
        assert tm.get_tenant(t["id"])["active"] == 0

    def test_deactivate_idempotent(self, tm):
        t = tm.create_tenant("Corp")
        tm.deactivate_tenant(t["id"])
        tm.deactivate_tenant(t["id"])
        assert tm.get_tenant(t["id"])["active"] == 0


# ── API keys ──────────────────────────────────────────────────────────────────

class TestApiKeys:

    def test_create_returns_bist_prefixed_string(self, tm):
        t = tm.create_tenant("Corp")
        key = tm.create_api_key(t["id"])
        assert key.startswith("bist_")

    def test_create_returns_unique_keys(self, tm):
        t = tm.create_tenant("Corp")
        k1 = tm.create_api_key(t["id"])
        k2 = tm.create_api_key(t["id"])
        assert k1 != k2

    def test_validate_valid_key_returns_tenant_info(self, tm):
        t = tm.create_tenant("Acme", tier="pro")
        key = tm.create_api_key(t["id"], label="CI")
        result = tm.validate_api_key(key)
        assert result is not None
        assert result["tenant_id"] == t["id"]
        assert result["tier"] == "pro"
        assert result["tenant_name"] == "Acme"

    def test_validate_invalid_key_returns_none(self, tm):
        assert tm.validate_api_key("bist_totally_invalid_xyz") is None

    def test_validate_revoked_key_returns_none(self, tm):
        t = tm.create_tenant("Corp")
        key = tm.create_api_key(t["id"])
        prefix = key[:12]
        tm.revoke_api_key(prefix, t["id"])
        assert tm.validate_api_key(key) is None

    def test_validate_deactivated_tenant_returns_none(self, tm):
        t = tm.create_tenant("Corp")
        key = tm.create_api_key(t["id"])
        tm.deactivate_tenant(t["id"])
        assert tm.validate_api_key(key) is None

    def test_list_returns_keys_for_tenant(self, tm):
        t = tm.create_tenant("Corp")
        tm.create_api_key(t["id"], label="CI")
        tm.create_api_key(t["id"], label="Dev")
        keys = tm.list_api_keys(t["id"])
        assert len(keys) == 2

    def test_list_empty_for_new_tenant(self, tm):
        t = tm.create_tenant("Corp")
        assert tm.list_api_keys(t["id"]) == []

    def test_list_keys_include_label(self, tm):
        t = tm.create_tenant("Corp")
        tm.create_api_key(t["id"], label="MyLabel")
        keys = tm.list_api_keys(t["id"])
        assert keys[0]["label"] == "MyLabel"

    def test_revoke_existing_key_returns_true(self, tm):
        t = tm.create_tenant("Corp")
        key = tm.create_api_key(t["id"])
        prefix = key[:12]
        assert tm.revoke_api_key(prefix, t["id"]) is True

    def test_revoke_nonexistent_key_returns_false(self, tm):
        t = tm.create_tenant("Corp")
        assert tm.revoke_api_key("bist_XXXXXXXX", t["id"]) is False

    def test_revoke_sets_key_inactive(self, tm):
        t = tm.create_tenant("Corp")
        key = tm.create_api_key(t["id"])
        prefix = key[:12]
        tm.revoke_api_key(prefix, t["id"])
        keys = tm.list_api_keys(t["id"])
        assert keys[0]["active"] == 0

    def test_keys_are_not_shared_across_tenants(self, tm):
        t1 = tm.create_tenant("Corp A")
        t2 = tm.create_tenant("Corp B")
        tm.create_api_key(t1["id"], label="T1 key")
        assert tm.list_api_keys(t2["id"]) == []


# ── enforce_run_limit ─────────────────────────────────────────────────────────

class TestEnforceRunLimit:

    def test_passes_when_under_limit(self, tm):
        t = tm.create_tenant("Corp", tier="free")
        tm.enforce_run_limit(t["id"], "free", 49)  # limit is 50

    def test_raises_at_limit(self, tm):
        t = tm.create_tenant("Corp", tier="free")
        with pytest.raises(TierLimitExceeded):
            tm.enforce_run_limit(t["id"], "free", 50)

    def test_raises_above_limit(self, tm):
        t = tm.create_tenant("Corp", tier="free")
        with pytest.raises(TierLimitExceeded):
            tm.enforce_run_limit(t["id"], "free", 200)

    def test_business_tier_is_unlimited(self, tm):
        t = tm.create_tenant("Corp", tier="business")
        tm.enforce_run_limit(t["id"], "business", 999_999)  # must not raise

    def test_pro_tier_under_limit_passes(self, tm):
        t = tm.create_tenant("Corp", tier="pro")
        tm.enforce_run_limit(t["id"], "pro", 999)  # limit is 1000

    def test_pro_tier_at_limit_raises(self, tm):
        t = tm.create_tenant("Corp", tier="pro")
        with pytest.raises(TierLimitExceeded):
            tm.enforce_run_limit(t["id"], "pro", 1000)

    def test_error_message_contains_tier(self, tm):
        t = tm.create_tenant("Corp", tier="free")
        with pytest.raises(TierLimitExceeded, match="free"):
            tm.enforce_run_limit(t["id"], "free", 50)
