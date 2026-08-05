import pytest
import json
from pathlib import Path
from snapshots.store import save_snapshot, load_snapshot, SnapshotNotFoundError

SAMPLE_SNAPSHOT = {
    "period": "Q1-2025",
    "run_date": "2026-08-04",
    "input_files": ["notes.txt"],
    "dimensions": {
        "trust": {"score": 3.0, "confidence": "medium", "evidence": ["Alice asked for help"]},
    },
    "overall_health": 3.0,
    "recommendations": ["Improve trust"],
}


def test_save_and_load_roundtrip(tmp_path):
    save_snapshot(SAMPLE_SNAPSHOT, snapshots_dir=tmp_path)
    loaded = load_snapshot("Q1-2025", snapshots_dir=tmp_path)
    assert loaded["period"] == "Q1-2025"
    assert loaded["overall_health"] == 3.0

def test_save_creates_json_file(tmp_path):
    save_snapshot(SAMPLE_SNAPSHOT, snapshots_dir=tmp_path)
    assert (tmp_path / "Q1-2025.json").exists()

def test_load_missing_snapshot_raises(tmp_path):
    with pytest.raises(SnapshotNotFoundError):
        load_snapshot("Q4-2099", snapshots_dir=tmp_path)

def test_save_overwrites_existing(tmp_path):
    save_snapshot(SAMPLE_SNAPSHOT, snapshots_dir=tmp_path)
    updated = {**SAMPLE_SNAPSHOT, "overall_health": 4.0}
    save_snapshot(updated, snapshots_dir=tmp_path)
    loaded = load_snapshot("Q1-2025", snapshots_dir=tmp_path)
    assert loaded["overall_health"] == 4.0
