import tomllib
from pathlib import Path


DEFAULT_CONFIG = {
    "claude": {"model": "claude-sonnet-4-6", "api_key_env": "ANTHROPIC_API_KEY"},
    "output": {"format": "markdown"},
    "rubric": {"framework": "five-dysfunctions", "path": "rubric/five-dysfunctions.yaml"},
    "paths": {"snapshots_dir": "snapshots", "output_dir": "output"},
}


def load_config(path: str = "config.toml") -> dict:
    config_path = Path(path)
    if not config_path.exists():
        return DEFAULT_CONFIG
    with config_path.open("rb") as f:
        user_config = tomllib.load(f)
    return _merge(DEFAULT_CONFIG, user_config)


def _merge(base: dict, override: dict) -> dict:
    result = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and key in result and isinstance(result[key], dict):
            result[key] = _merge(result[key], value)
        else:
            result[key] = value
    return result
