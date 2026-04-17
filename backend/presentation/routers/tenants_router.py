"""Phase 4 REST routes: tenants, API keys, billing webhooks, and SSO.

Routes:
  POST   /api/tenants                        Create tenant (admin)
  GET    /api/tenants                        List tenants (admin)
  GET    /api/tenants/{id}                   Get tenant detail
  PATCH  /api/tenants/{id}/tier              Change tier (admin / Stripe webhook)
  POST   /api/tenants/{id}/api-keys          Create API key
  GET    /api/tenants/{id}/api-keys          List API keys
  DELETE /api/tenants/{id}/api-keys/{prefix} Revoke API key
  GET    /api/tenants/{id}/usage             Monthly usage summary

  POST   /api/billing/webhook                Stripe webhook endpoint

  GET    /api/sso/oauth2/authorize            Start OAuth2 login
  GET    /api/sso/oauth2/callback             OAuth2 callback
  POST   /api/sso/saml/{tenant_id}/configure  Configure SAML IdP
  GET    /api/sso/saml/{tenant_id}/login      Redirect to SAML IdP
  POST   /api/sso/saml/{tenant_id}/acs        SAML ACS (assertion consumer)
"""
import sys
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Header, HTTPException, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

_ROOT = Path(__file__).parent.parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from bist.bist_tenants import TenantManager, TIER_LIMITS
from bist.bist_billing import BillingManager
from bist.bist_sso import SSOManager

router = APIRouter(tags=["tenants", "billing", "sso"])

_tenants = TenantManager()
_billing = BillingManager()
_sso     = SSOManager()

_ADMIN_KEY = None  # set BIST_ADMIN_KEY env var to protect admin routes


def _require_admin(x_admin_key: Optional[str] = Header(default=None)) -> None:
    import os
    admin_key = os.getenv("BIST_ADMIN_KEY", "")
    if admin_key and x_admin_key != admin_key:
        raise HTTPException(status_code=403, detail="Admin key required")


# ── Pydantic schemas ──────────────────────────────────────────────────────────

class CreateTenantRequest(BaseModel):
    name: str
    tier: str = "free"


class TenantOut(BaseModel):
    id: int
    name: str
    tier: str
    created_at: float
    active: int


class UpdateTierRequest(BaseModel):
    tier: str


class CreateApiKeyRequest(BaseModel):
    label: str = ""


class ApiKeyCreated(BaseModel):
    raw_key: str
    key_prefix: str
    label: str
    message: str = "Store this key securely — it will not be shown again."


class ApiKeyOut(BaseModel):
    id: int
    key_prefix: str
    label: str
    created_at: float
    last_used: Optional[float]
    active: int


class SamlConfigRequest(BaseModel):
    idp_entity_id:   str
    idp_sso_url:     str
    idp_cert:        str
    sp_entity_id:    str = ""
    attribute_email: str = "email"
    attribute_name:  str = "displayName"


# ── Tenant routes ─────────────────────────────────────────────────────────────

@router.post("/api/tenants", status_code=201)
def create_tenant(req: CreateTenantRequest, x_admin_key: Optional[str] = Header(default=None)):
    _require_admin(x_admin_key)
    try:
        return _tenants.create_tenant(req.name, req.tier)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/api/tenants", response_model=list[TenantOut])
def list_tenants(x_admin_key: Optional[str] = Header(default=None)):
    _require_admin(x_admin_key)
    return _tenants.list_tenants()


@router.get("/api/tenants/{tenant_id}", response_model=TenantOut)
def get_tenant(tenant_id: int):
    tenant = _tenants.get_tenant(tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail=f"Tenant {tenant_id} not found")
    return tenant


@router.patch("/api/tenants/{tenant_id}/tier")
def update_tier(
    tenant_id: int,
    req: UpdateTierRequest,
    x_admin_key: Optional[str] = Header(default=None),
):
    _require_admin(x_admin_key)
    if not _tenants.get_tenant(tenant_id):
        raise HTTPException(status_code=404, detail=f"Tenant {tenant_id} not found")
    try:
        _tenants.update_tier(tenant_id, req.tier)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {"tenant_id": tenant_id, "tier": req.tier}


# ── API key routes ────────────────────────────────────────────────────────────

@router.post("/api/tenants/{tenant_id}/api-keys", response_model=ApiKeyCreated, status_code=201)
def create_api_key(
    tenant_id: int,
    req: CreateApiKeyRequest,
    x_admin_key: Optional[str] = Header(default=None),
):
    _require_admin(x_admin_key)
    if not _tenants.get_tenant(tenant_id):
        raise HTTPException(status_code=404, detail=f"Tenant {tenant_id} not found")
    raw = _tenants.create_api_key(tenant_id, req.label)
    return ApiKeyCreated(raw_key=raw, key_prefix=raw[:12], label=req.label)


@router.get("/api/tenants/{tenant_id}/api-keys", response_model=list[ApiKeyOut])
def list_api_keys(tenant_id: int, x_admin_key: Optional[str] = Header(default=None)):
    _require_admin(x_admin_key)
    if not _tenants.get_tenant(tenant_id):
        raise HTTPException(status_code=404, detail=f"Tenant {tenant_id} not found")
    return _tenants.list_api_keys(tenant_id)


@router.delete("/api/tenants/{tenant_id}/api-keys/{key_prefix}", status_code=204)
def revoke_api_key(
    tenant_id: int,
    key_prefix: str,
    x_admin_key: Optional[str] = Header(default=None),
):
    _require_admin(x_admin_key)
    if not _tenants.revoke_api_key(key_prefix, tenant_id):
        raise HTTPException(status_code=404, detail="Key not found or already revoked")


@router.get("/api/tenants/{tenant_id}/usage")
def get_usage(tenant_id: int, days: int = 30):
    if not _tenants.get_tenant(tenant_id):
        raise HTTPException(status_code=404, detail=f"Tenant {tenant_id} not found")
    return _billing.get_usage_summary(tenant_id, days)


# ── Billing / Stripe webhook ──────────────────────────────────────────────────

@router.post("/api/billing/webhook")
async def stripe_webhook(request: Request):
    """Stripe sends signed POST events here. Configure in Stripe Dashboard."""
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")

    if not _billing.verify_webhook_signature(payload, sig_header):
        raise HTTPException(status_code=400, detail="Invalid Stripe webhook signature")

    import json
    try:
        event = json.loads(payload)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    event_type = _billing.handle_webhook_event(event, _tenants)
    return {"received": True, "event_type": event_type}


# ── SSO — OAuth2 ──────────────────────────────────────────────────────────────

@router.get("/api/sso/oauth2/authorize")
def oauth2_authorize(tenant_id: Optional[int] = None):
    """Redirect the user's browser to the OAuth2 IdP."""
    url = _sso.oauth2_authorize_url(tenant_id=tenant_id)
    return RedirectResponse(url=url)


@router.get("/api/sso/oauth2/callback")
def oauth2_callback(code: str, state: str):
    """Exchange the auth code for user info after IdP redirect."""
    try:
        result = _sso.oauth2_exchange_code(code, state)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    if not result:
        raise HTTPException(status_code=400, detail="Invalid or expired OAuth2 state")
    return result


# ── SSO — SAML ────────────────────────────────────────────────────────────────

@router.post("/api/sso/saml/{tenant_id}/configure", status_code=204)
def saml_configure(
    tenant_id: int,
    req: SamlConfigRequest,
    x_admin_key: Optional[str] = Header(default=None),
):
    """Store SAML IdP metadata for a tenant."""
    _require_admin(x_admin_key)
    if not _tenants.get_tenant(tenant_id):
        raise HTTPException(status_code=404, detail=f"Tenant {tenant_id} not found")
    _sso.saml_configure(
        tenant_id,
        req.idp_entity_id,
        req.idp_sso_url,
        req.idp_cert,
        req.sp_entity_id,
        req.attribute_email,
        req.attribute_name,
    )


@router.get("/api/sso/saml/{tenant_id}/login")
def saml_login(tenant_id: int):
    """Redirect user to the SAML IdP SSO URL."""
    try:
        sso_url = _sso.saml_login_url(tenant_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return RedirectResponse(url=sso_url)


@router.post("/api/sso/saml/{tenant_id}/acs")
async def saml_acs(tenant_id: int, request: Request):
    """SAML Assertion Consumer Service — process IdP POST."""
    form = await request.form()
    saml_response = form.get("SAMLResponse", "")
    if not saml_response:
        raise HTTPException(status_code=400, detail="Missing SAMLResponse field")
    result = _sso.saml_process_response(tenant_id, str(saml_response))
    if not result:
        raise HTTPException(status_code=400, detail="Failed to process SAML response")
    return result
