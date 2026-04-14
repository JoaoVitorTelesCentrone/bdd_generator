"""
Cliente HTTP para o modo managed do CLI.
Todas as chamadas passam pelo backend BDD Generator ao invés de direto na LLM.
"""
import time
from typing import Optional
from dataclasses import dataclass

import httpx

from .config import load_config, MANAGED_API_URL


@dataclass
class QuotaInfo:
    plan:             str
    tokens_used:      int
    tokens_limit:     int   # -1 = ilimitado (Pro)
    tokens_remaining: int   # -1 = ilimitado
    generations_used: int
    reset_at:         str   # ISO date do próximo reset


@dataclass
class ManagedGenerateResult:
    bdd_text:         str
    score_final:      float
    cobertura:        float
    clareza:          float
    estrutura:        float
    executabilidade:  float
    aprovado:         bool
    attempts:         int
    total_tokens:     int
    research_tokens:  int
    converged:        bool
    duration_seconds: float


def _headers() -> dict:
    config = load_config()
    token  = config.auth.token if config.auth else ""
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type":  "application/json",
        "X-CLI-Version": "1.0.0",
    }


def _base_url() -> str:
    config = load_config()
    return config.auth.api_url if config.auth else MANAGED_API_URL


def validate_token(token: str, api_url: str = MANAGED_API_URL) -> Optional[dict]:
    """Valida o token e retorna info do usuário, ou None se inválido."""
    try:
        r = httpx.get(
            f"{api_url}/api/cli/me",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10,
        )
        if r.status_code == 200:
            return r.json()
        return None
    except Exception:
        return None


def get_quota() -> Optional[QuotaInfo]:
    try:
        r = httpx.get(
            f"{_base_url()}/api/cli/quota",
            headers=_headers(),
            timeout=10,
        )
        if r.status_code == 200:
            d = r.json()
            return QuotaInfo(**d)
        return None
    except Exception:
        return None


def managed_generate(
    story:           str,
    model:           str   = "flash",
    threshold:       float = 7.0,
    max_attempts:    int   = 5,
    research:        bool  = False,
    until_converged: bool  = False,
) -> ManagedGenerateResult:
    """Gera BDD via backend managed (rastreia tokens no servidor)."""
    r = httpx.post(
        f"{_base_url()}/api/cli/generate",
        headers=_headers(),
        json={
            "story":           story,
            "model":           model,
            "threshold":       threshold,
            "max_attempts":    max_attempts,
            "research":        research,
            "until_converged": until_converged,
        },
        timeout=300,  # gerações longas podem demorar
    )

    if r.status_code == 402:
        raise QuotaExceededError(r.json().get("detail", "Cota de tokens esgotada."))

    if r.status_code == 401:
        raise AuthError("Token inválido ou expirado. Execute: bdd auth login")

    r.raise_for_status()
    d = r.json()

    return ManagedGenerateResult(
        bdd_text=d["bdd_text"],
        score_final=d["score"]["score_final"],
        cobertura=d["score"]["cobertura"],
        clareza=d["score"]["clareza"],
        estrutura=d["score"]["estrutura"],
        executabilidade=d["score"]["executabilidade"],
        aprovado=d["score"]["aprovado"],
        attempts=d["attempts"],
        total_tokens=d["total_tokens"],
        research_tokens=d["research_tokens"],
        converged=d["converged"],
        duration_seconds=d["duration_seconds"],
    )


class QuotaExceededError(Exception):
    pass

class AuthError(Exception):
    pass
