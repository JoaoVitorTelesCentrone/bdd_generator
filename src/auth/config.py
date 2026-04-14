"""
Gerenciamento de configuração e autenticação do CLI.

Armazena o estado em ~/.config/bdd-generator/config.json
"""
import json
import os
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, asdict


CONFIG_DIR  = Path.home() / ".config" / "bdd-generator"
CONFIG_FILE = CONFIG_DIR / "config.json"

MANAGED_API_URL = os.getenv("BDD_API_URL", "https://api.bdd-generator.com")


@dataclass
class AuthState:
    token:      str
    user_email: str
    user_name:  str
    plan:       str   # "free" | "pro"
    api_url:    str   = MANAGED_API_URL


@dataclass
class Config:
    mode:  str             = "byok"   # "byok" | "managed"
    auth:  Optional[AuthState] = None


def load_config() -> Config:
    if not CONFIG_FILE.exists():
        return Config()
    try:
        data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        auth = None
        if data.get("auth"):
            auth = AuthState(**data["auth"])
        return Config(mode=data.get("mode", "byok"), auth=auth)
    except Exception:
        return Config()


def save_config(config: Config) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    data = {
        "mode": config.mode,
        "auth": asdict(config.auth) if config.auth else None,
    }
    CONFIG_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    # Permissões restritas no arquivo (só dono lê)
    try:
        CONFIG_FILE.chmod(0o600)
    except Exception:
        pass


def clear_auth() -> None:
    config = load_config()
    config.mode = "byok"
    config.auth = None
    save_config(config)


def is_authenticated() -> bool:
    config = load_config()
    return config.mode == "managed" and config.auth is not None


def get_token() -> Optional[str]:
    config = load_config()
    return config.auth.token if config.auth else None


def get_plan() -> str:
    config = load_config()
    return config.auth.plan if config.auth else "byok"
