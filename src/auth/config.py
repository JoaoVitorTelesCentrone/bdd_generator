"""
Gerenciamento de configuração do CLI (modo BYOK).

Armazena o estado em ~/.config/bdd-generator/config.json
"""
import json
import os
from pathlib import Path
from typing import Optional

CONFIG_DIR  = Path.home() / ".config" / "bdd-generator"
CONFIG_FILE = CONFIG_DIR / "config.json"


def load_config() -> dict:
    if not CONFIG_FILE.exists():
        return {}
    try:
        return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_config(data: dict) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    try:
        CONFIG_FILE.chmod(0o600)
    except Exception:
        pass


def get_api_key(name: str) -> Optional[str]:
    """Retorna a chave de API salva. Prioridade: variável de ambiente > config file."""
    env_val = os.environ.get(name)
    if env_val:
        return env_val
    return load_config().get(name)


def set_api_key(name: str, value: str) -> None:
    data = load_config()
    data[name] = value
    save_config(data)


def show_config() -> dict:
    return load_config()
