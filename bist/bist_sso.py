"""OAuth2 and SAML SSO for BIST multi-tenant authentication.

OAuth2 flow (Google by default — override via env vars):
  1. GET  /api/sso/oauth2/authorize  → redirect to IdP
  2. GET  /api/sso/oauth2/callback   → exchange code → return user info

SAML flow (enterprise):
  1. POST /api/sso/saml/{tenant_id}/configure  → store IdP metadata
  2. GET  /api/sso/saml/{tenant_id}/login      → redirect to IdP SSO URL
  3. POST /api/sso/saml/{tenant_id}/acs        → process IdP response → return user info

Environment variables (OAuth2):
  OAUTH2_CLIENT_ID
  OAUTH2_CLIENT_SECRET
  OAUTH2_AUTHORIZE_URL   (default: Google)
  OAUTH2_TOKEN_URL       (default: Google)
  OAUTH2_USERINFO_URL    (default: Google)
  OAUTH2_REDIRECT_URI    (default: http://localhost:8000/api/sso/oauth2/callback)

Environment variable (SAML):
  SAML_ACS_URL_BASE      (default: http://localhost:8000/api/sso/saml)
"""

import base64
import json
import os
import secrets
import sqlite3
import time
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional
from urllib.parse import urlencode

import httpx

DB_PATH = Path.home() / ".bist" / "bist.db"

_OAUTH2_CLIENT_ID     = os.getenv("OAUTH2_CLIENT_ID", "")
_OAUTH2_CLIENT_SECRET = os.getenv("OAUTH2_CLIENT_SECRET", "")
_OAUTH2_AUTHORIZE_URL = os.getenv("OAUTH2_AUTHORIZE_URL", "https://accounts.google.com/o/oauth2/v2/auth")
_OAUTH2_TOKEN_URL     = os.getenv("OAUTH2_TOKEN_URL", "https://oauth2.googleapis.com/token")
_OAUTH2_USERINFO_URL  = os.getenv("OAUTH2_USERINFO_URL", "https://www.googleapis.com/oauth2/v3/userinfo")
_OAUTH2_REDIRECT_URI  = os.getenv("OAUTH2_REDIRECT_URI", "http://localhost:8000/api/sso/oauth2/callback")
_SAML_ACS_URL_BASE    = os.getenv("SAML_ACS_URL_BASE", "http://localhost:8000/api/sso/saml")

_SAML_NS = "urn:oasis:names:tc:SAML:2.0:assertion"


class SSOManager:
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
                CREATE TABLE IF NOT EXISTS sso_sessions (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id   INTEGER,
                    state       TEXT    NOT NULL UNIQUE,
                    provider    TEXT    NOT NULL DEFAULT 'oauth2',
                    created_at  REAL    NOT NULL,
                    expires_at  REAL    NOT NULL,
                    user_info   TEXT    NOT NULL DEFAULT '{}'
                );
                CREATE TABLE IF NOT EXISTS saml_configs (
                    id              INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id       INTEGER NOT NULL UNIQUE,
                    idp_entity_id   TEXT    NOT NULL,
                    idp_sso_url     TEXT    NOT NULL,
                    idp_cert        TEXT    NOT NULL,
                    sp_entity_id    TEXT    NOT NULL DEFAULT '',
                    attribute_email TEXT    NOT NULL DEFAULT 'email',
                    attribute_name  TEXT    NOT NULL DEFAULT 'displayName',
                    created_at      REAL    NOT NULL
                );
            """)

    # ── OAuth2 ────────────────────────────────────────────────────────────────

    def oauth2_authorize_url(
        self,
        tenant_id: Optional[int] = None,
        scopes: Optional[list[str]] = None,
    ) -> str:
        """Generate the IdP redirect URL and persist a state token."""
        state = secrets.token_urlsafe(32)
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO sso_sessions (tenant_id, state, provider, created_at, expires_at) "
                "VALUES (?, ?, 'oauth2', ?, ?)",
                (tenant_id, state, time.time(), time.time() + 600),
            )
        params = {
            "client_id":     os.getenv("OAUTH2_CLIENT_ID", _OAUTH2_CLIENT_ID),
            "redirect_uri":  os.getenv("OAUTH2_REDIRECT_URI", _OAUTH2_REDIRECT_URI),
            "response_type": "code",
            "scope":         " ".join(scopes or ["openid", "email", "profile"]),
            "state":         state,
            "access_type":   "offline",
        }
        return f"{os.getenv('OAUTH2_AUTHORIZE_URL', _OAUTH2_AUTHORIZE_URL)}?{urlencode(params)}"

    def oauth2_exchange_code(self, code: str, state: str) -> Optional[dict]:
        """Exchange auth code for tokens, fetch user info, return result dict."""
        session = self._get_valid_session(state, "oauth2")
        if not session:
            return None

        token_r = httpx.post(
            os.getenv("OAUTH2_TOKEN_URL", _OAUTH2_TOKEN_URL),
            data={
                "code":          code,
                "client_id":     os.getenv("OAUTH2_CLIENT_ID", _OAUTH2_CLIENT_ID),
                "client_secret": os.getenv("OAUTH2_CLIENT_SECRET", _OAUTH2_CLIENT_SECRET),
                "redirect_uri":  os.getenv("OAUTH2_REDIRECT_URI", _OAUTH2_REDIRECT_URI),
                "grant_type":    "authorization_code",
            },
            timeout=15,
        )
        token_r.raise_for_status()
        access_token = token_r.json()["access_token"]

        user_r = httpx.get(
            os.getenv("OAUTH2_USERINFO_URL", _OAUTH2_USERINFO_URL),
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=10,
        )
        user_r.raise_for_status()
        user_info = user_r.json()

        with self._connect() as conn:
            conn.execute(
                "UPDATE sso_sessions SET user_info = ? WHERE state = ?",
                (json.dumps(user_info), state),
            )

        return {"user_info": user_info, "tenant_id": session["tenant_id"]}

    # ── SAML ──────────────────────────────────────────────────────────────────

    def saml_configure(
        self,
        tenant_id: int,
        idp_entity_id: str,
        idp_sso_url: str,
        idp_cert: str,
        sp_entity_id: str = "",
        attribute_email: str = "email",
        attribute_name: str = "displayName",
    ) -> None:
        with self._connect() as conn:
            conn.execute(
                """INSERT INTO saml_configs
                       (tenant_id, idp_entity_id, idp_sso_url, idp_cert, sp_entity_id,
                        attribute_email, attribute_name, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                   ON CONFLICT(tenant_id) DO UPDATE SET
                       idp_entity_id=excluded.idp_entity_id,
                       idp_sso_url=excluded.idp_sso_url,
                       idp_cert=excluded.idp_cert,
                       sp_entity_id=excluded.sp_entity_id,
                       attribute_email=excluded.attribute_email,
                       attribute_name=excluded.attribute_name""",
                (tenant_id, idp_entity_id, idp_sso_url, idp_cert, sp_entity_id,
                 attribute_email, attribute_name, time.time()),
            )

    def get_saml_config(self, tenant_id: int) -> Optional[dict]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM saml_configs WHERE tenant_id = ?", (tenant_id,)
            ).fetchone()
            return dict(row) if row else None

    def saml_login_url(self, tenant_id: int) -> str:
        """Return the IdP SSO URL for this tenant's SAML config."""
        config = self.get_saml_config(tenant_id)
        if not config:
            raise ValueError(f"No SAML config for tenant {tenant_id}")
        return config["idp_sso_url"]

    def saml_process_response(self, tenant_id: int, saml_response_b64: str) -> Optional[dict]:
        """Parse a base64-encoded SAML response, extract attributes without signature validation.

        For production use, install python3-saml and call saml_process_response_verified instead.
        This method does basic attribute extraction suitable for trusted IdPs.
        """
        config = self.get_saml_config(tenant_id)
        if not config:
            return None

        try:
            xml_bytes = base64.b64decode(saml_response_b64)
        except Exception:
            return None

        try:
            root = ET.fromstring(xml_bytes)
        except ET.ParseError:
            return None

        attrs: dict = {}
        for attr_elem in root.iter(f"{{{_SAML_NS}}}Attribute"):
            name = attr_elem.get("Name", "")
            values = [
                v.text or ""
                for v in attr_elem.iter(f"{{{_SAML_NS}}}AttributeValue")
            ]
            attrs[name] = values[0] if len(values) == 1 else values

        email = attrs.get(config["attribute_email"], "")
        display_name = attrs.get(config["attribute_name"], "")
        return {
            "tenant_id":  tenant_id,
            "email":      email,
            "name":       display_name,
            "attributes": attrs,
        }

    def saml_process_response_verified(self, tenant_id: int, request_data: dict) -> Optional[dict]:
        """Full SAML response processing with python3-saml signature verification.

        request_data must match OneLogin_Saml2_Auth's expected format:
          {"http_host": ..., "script_name": ..., "post_data": {"SAMLResponse": ...}}

        Raises RuntimeError if python3-saml is not installed.
        """
        config = self.get_saml_config(tenant_id)
        if not config:
            return None
        try:
            from onelogin.saml2.auth import OneLogin_Saml2_Auth  # type: ignore
        except ImportError as exc:
            raise RuntimeError(
                "Full SAML verification requires python3-saml: pip install python3-saml"
            ) from exc

        acs_url = f"{os.getenv('SAML_ACS_URL_BASE', _SAML_ACS_URL_BASE)}/{tenant_id}/acs"
        saml_settings = {
            "idp": {
                "entityId": config["idp_entity_id"],
                "singleSignOnService": {
                    "url":     config["idp_sso_url"],
                    "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect",
                },
                "x509cert": config["idp_cert"],
            },
            "sp": {
                "entityId": config["sp_entity_id"] or f"bist_sp_{tenant_id}",
                "assertionConsumerService": {
                    "url":     acs_url,
                    "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST",
                },
            },
            "strict": True,
            "debug":  False,
        }

        auth = OneLogin_Saml2_Auth(request_data, saml_settings)
        auth.process_response()
        errors = auth.get_errors()
        if errors:
            raise ValueError(f"SAML errors: {errors}")

        attrs = auth.get_attributes()
        email = (attrs.get(config["attribute_email"], [""])[0])
        name  = (attrs.get(config["attribute_name"],  [""])[0])
        return {"tenant_id": tenant_id, "email": email, "name": name, "attributes": attrs}

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _get_valid_session(self, state: str, provider: str) -> Optional[dict]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM sso_sessions WHERE state = ? AND provider = ? AND expires_at > ?",
                (state, provider, time.time()),
            ).fetchone()
            return dict(row) if row else None
