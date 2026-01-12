import json
import os
from pathlib import Path

DEFAULT_PORT = 7860


def _load_network_config(base_dir: Path) -> dict:
    config_path = base_dir / "data" / "network_auth.json"
    try:
        with open(config_path, "r") as handle:
            data = json.load(handle)
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError, ValueError):
        return {}


def get_configured_port(base_dir: Path, default: int = DEFAULT_PORT) -> int:
    env_port = os.environ.get("DEXTALKER_PORT")
    if env_port:
        try:
            return int(env_port)
        except ValueError:
            pass

    data = _load_network_config(base_dir)
    config = data.get("config", {})
    port = config.get("port", default)
    try:
        return int(port)
    except (TypeError, ValueError):
        return default
