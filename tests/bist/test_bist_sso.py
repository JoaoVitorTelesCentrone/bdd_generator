"""
Tests for bist/bist_sso.py — SSOManager: OAuth2 authorization and SAML processing.

Cenários cobertos:
  Schema:
    - Tabelas sso_sessions e saml_configs criadas ao instanciar
  OAuth2:
    - oauth2_authorize_url retorna URL com parâmetro state
    - oauth2_authorize_url persiste sessão no banco
    - oauth2_authorize_url aceita scopes customizados
    - oauth2_exchange_code retorna None para state inválido
    - oauth2_exchange_code retorna None para sessão expirada
  SAML configure:
    - saml_configure persiste configuração do IdP
    - get_saml_config retorna None para tenant sem configuração
    - saml_configure atualiza em conflito (ON CONFLICT upsert)
    - saml_configure persiste attribute_email e attribute_name customizados
  SAML login URL:
    - saml_login_url retorna idp_sso_url configurado
    - saml_login_url levanta ValueError para tenant sem configuração
  SAML process response:
    - retorna None para tenant sem configuração
    - retorna None para base64 inválido
    - retorna None para XML inválido
    - extrai email do SAML response
    - extrai displayName do SAML response
    - resultado contém tenant_id correto
    - resultado contém dict de atributos
  saml_process_response_verified:
    - levanta RuntimeError quando python3-saml não está instalado
"""
import base64
import os
import sqlite3
import sys
import time
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import pytest
from bist.bist_sso import SSOManager

_SAML_NS = "urn:oasis:names:tc:SAML:2.0:assertion"


# ── helpers ───────────────────────────────────────────────────────────────────

def _saml_xml(email: str = "user@example.com", name: str = "Test User") -> bytes:
    """Minimal SAML response XML with standard assertion attributes."""
    return f"""<samlp:Response xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol">
  <saml:Assertion xmlns:saml="{_SAML_NS}">
    <saml:AttributeStatement>
      <saml:Attribute Name="email">
        <saml:AttributeValue>{email}</saml:AttributeValue>
      </saml:Attribute>
      <saml:Attribute Name="displayName">
        <saml:AttributeValue>{name}</saml:AttributeValue>
      </saml:Attribute>
    </saml:AttributeStatement>
  </saml:Assertion>
</samlp:Response>""".encode()


# ── fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def sso(tmp_path):
    return SSOManager(db_path=tmp_path / "sso_test.db")


@pytest.fixture
def sso_with_config(tmp_path):
    s = SSOManager(db_path=tmp_path / "sso_config_test.db")
    s.saml_configure(
        tenant_id=1,
        idp_entity_id="https://idp.example.com/saml",
        idp_sso_url="https://idp.example.com/sso",
        idp_cert="MIIC_test_cert",
        sp_entity_id="bist_sp_1",
        attribute_email="email",
        attribute_name="displayName",
    )
    return s


# ── schema ────────────────────────────────────────────────────────────────────

class TestSchema:

    def test_tables_created(self, sso):
        with sqlite3.connect(str(sso.db_path)) as conn:
            tables = {
                r[0] for r in
                conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
            }
        assert "sso_sessions" in tables
        assert "saml_configs" in tables

    def test_second_instantiation_does_not_raise(self, tmp_path):
        p = tmp_path / "double_sso.db"
        SSOManager(db_path=p)
        SSOManager(db_path=p)


# ── OAuth2 ────────────────────────────────────────────────────────────────────

class TestOAuth2AuthorizeUrl:

    def test_returns_string_url(self, sso):
        url = sso.oauth2_authorize_url(tenant_id=1)
        assert isinstance(url, str)
        assert url.startswith("http")

    def test_url_contains_state_param(self, sso):
        url = sso.oauth2_authorize_url(tenant_id=1)
        assert "state=" in url

    def test_url_contains_scope_param(self, sso):
        url = sso.oauth2_authorize_url(scopes=["openid", "email"])
        assert "scope=" in url

    def test_different_calls_generate_different_states(self, sso):
        url1 = sso.oauth2_authorize_url()
        url2 = sso.oauth2_authorize_url()
        state1 = [p for p in url1.split("&") if p.startswith("state=")][0]
        state2 = [p for p in url2.split("&") if p.startswith("state=")][0]
        assert state1 != state2

    def test_persists_session_in_db(self, sso):
        sso.oauth2_authorize_url(tenant_id=1)
        with sqlite3.connect(str(sso.db_path)) as conn:
            count = conn.execute("SELECT COUNT(*) FROM sso_sessions").fetchone()[0]
        assert count == 1

    def test_session_has_correct_provider(self, sso):
        sso.oauth2_authorize_url(tenant_id=1)
        with sqlite3.connect(str(sso.db_path)) as conn:
            row = conn.execute("SELECT provider FROM sso_sessions").fetchone()
        assert row[0] == "oauth2"


class TestOAuth2ExchangeCode:

    def test_invalid_state_returns_none(self, sso):
        result = sso.oauth2_exchange_code("some_code", "nonexistent_state")
        assert result is None

    def test_expired_state_returns_none(self, sso):
        state = "expired_state_token"
        with sqlite3.connect(str(sso.db_path)) as conn:
            conn.execute(
                "INSERT INTO sso_sessions "
                "(tenant_id, state, provider, created_at, expires_at) "
                "VALUES (1, ?, 'oauth2', ?, ?)",
                (state, time.time() - 1000, time.time() - 500),  # expired
            )
        result = sso.oauth2_exchange_code("any_code", state)
        assert result is None

    def test_wrong_provider_returns_none(self, sso):
        state = "saml_state"
        with sqlite3.connect(str(sso.db_path)) as conn:
            conn.execute(
                "INSERT INTO sso_sessions "
                "(tenant_id, state, provider, created_at, expires_at) "
                "VALUES (1, ?, 'saml', ?, ?)",
                (state, time.time(), time.time() + 600),
            )
        result = sso.oauth2_exchange_code("code", state)
        assert result is None


# ── SAML configure ────────────────────────────────────────────────────────────

class TestSamlConfigure:

    def test_stores_config(self, sso):
        sso.saml_configure(1, "https://idp.com", "https://idp.com/sso", "cert")
        config = sso.get_saml_config(1)
        assert config is not None
        assert config["idp_sso_url"] == "https://idp.com/sso"

    def test_get_config_returns_none_for_unknown_tenant(self, sso):
        assert sso.get_saml_config(99999) is None

    def test_upsert_on_conflict(self, sso):
        sso.saml_configure(1, "https://idp1.com", "https://idp1.com/sso", "cert1")
        sso.saml_configure(1, "https://idp2.com", "https://idp2.com/sso", "cert2")
        config = sso.get_saml_config(1)
        assert config["idp_entity_id"] == "https://idp2.com"

    def test_stores_custom_attribute_mappings(self, sso):
        sso.saml_configure(
            1, "entity", "sso_url", "cert",
            attribute_email="mail",
            attribute_name="cn",
        )
        config = sso.get_saml_config(1)
        assert config["attribute_email"] == "mail"
        assert config["attribute_name"] == "cn"

    def test_stores_sp_entity_id(self, sso):
        sso.saml_configure(1, "entity", "sso", "cert", sp_entity_id="bist_sp_1")
        assert sso.get_saml_config(1)["sp_entity_id"] == "bist_sp_1"


# ── SAML login URL ────────────────────────────────────────────────────────────

class TestSamlLoginUrl:

    def test_returns_idp_sso_url(self, sso_with_config):
        url = sso_with_config.saml_login_url(1)
        assert url == "https://idp.example.com/sso"

    def test_raises_for_unconfigured_tenant(self, sso):
        with pytest.raises(ValueError, match="No SAML config"):
            sso.saml_login_url(99999)


# ── SAML process response ─────────────────────────────────────────────────────

class TestSamlProcessResponse:

    def test_returns_none_for_unconfigured_tenant(self, sso):
        b64 = base64.b64encode(b"<xml/>").decode()
        result = sso.saml_process_response(99999, b64)
        assert result is None

    def test_returns_none_for_invalid_base64(self, sso_with_config):
        result = sso_with_config.saml_process_response(1, "!!!not_base64!!!")
        assert result is None

    def test_returns_none_for_invalid_xml(self, sso_with_config):
        b64 = base64.b64encode(b"this is definitely not xml").decode()
        result = sso_with_config.saml_process_response(1, b64)
        assert result is None

    def test_extracts_email(self, sso_with_config):
        b64 = base64.b64encode(_saml_xml(email="alice@corp.com")).decode()
        result = sso_with_config.saml_process_response(1, b64)
        assert result is not None
        assert result["email"] == "alice@corp.com"

    def test_extracts_display_name(self, sso_with_config):
        b64 = base64.b64encode(_saml_xml(name="Alice Smith")).decode()
        result = sso_with_config.saml_process_response(1, b64)
        assert result["name"] == "Alice Smith"

    def test_result_contains_tenant_id(self, sso_with_config):
        b64 = base64.b64encode(_saml_xml()).decode()
        result = sso_with_config.saml_process_response(1, b64)
        assert result["tenant_id"] == 1

    def test_result_contains_attributes_dict(self, sso_with_config):
        b64 = base64.b64encode(_saml_xml()).decode()
        result = sso_with_config.saml_process_response(1, b64)
        assert isinstance(result["attributes"], dict)

    def test_result_attributes_contain_email_key(self, sso_with_config):
        b64 = base64.b64encode(_saml_xml(email="bob@x.com")).decode()
        result = sso_with_config.saml_process_response(1, b64)
        assert "email" in result["attributes"]
        assert result["attributes"]["email"] == "bob@x.com"

    def test_empty_saml_response_still_returns_dict(self, sso_with_config):
        """Empty but valid XML returns dict with empty strings, not None."""
        empty_xml = b'<root xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion"/>'
        b64 = base64.b64encode(empty_xml).decode()
        result = sso_with_config.saml_process_response(1, b64)
        assert result is not None
        assert result["email"] == ""
        assert result["name"] == ""


# ── saml_process_response_verified ───────────────────────────────────────────

class TestSamlProcessResponseVerified:

    def test_raises_runtime_error_without_python3_saml(self, sso_with_config):
        with pytest.raises(RuntimeError, match="python3-saml"):
            sso_with_config.saml_process_response_verified(1, {})

    def test_returns_none_for_unconfigured_tenant(self, sso):
        result = sso.saml_process_response_verified(99999, {})
        assert result is None
