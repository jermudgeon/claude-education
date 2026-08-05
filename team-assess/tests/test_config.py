# tests/test_config.py
import pytest
from pathlib import Path
from config import load_config, DEFAULT_CONFIG

def test_load_config_returns_defaults_when_file_missing(tmp_path):
    result = load_config(str(tmp_path / "nonexistent.toml"))
    assert result["claude"]["model"] == "claude-opus-4-7"
    assert result["paths"]["snapshots_dir"] == "snapshots"

def test_load_config_defaults_are_not_mutated(tmp_path):
    result = load_config(str(tmp_path / "nonexistent.toml"))
    result["claude"]["model"] = "changed"
    # Mutating the returned dict must not affect DEFAULT_CONFIG
    assert DEFAULT_CONFIG["claude"]["model"] == "claude-opus-4-7"

def test_load_config_overrides_merge_deeply(tmp_path):
    config_file = tmp_path / "config.toml"
    config_file.write_text('[claude]\nmodel = "claude-opus-4-7"\n', encoding="utf-8")
    result = load_config(str(config_file))
    assert result["claude"]["model"] == "claude-opus-4-7"
    # api_key_env should still come from defaults
    assert result["claude"]["api_key_env"] == "ANTHROPIC_API_KEY"

def test_load_config_loads_actual_config_toml():
    # Verify the project's own config.toml loads cleanly from team-assess/ dir
    result = load_config(str(Path(__file__).parent.parent / "config.toml"))
    assert result["claude"]["model"] == "claude-opus-4-7"
    assert "path" in result["rubric"]
