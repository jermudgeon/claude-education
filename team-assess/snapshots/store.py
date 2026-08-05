import json
import re
from pathlib import Path

DEFAULT_SNAPSHOTS_DIR = Path("snapshots")


class SnapshotNotFoundError(Exception):
    pass


def _safe_filename(period: str) -> str:
    # Strip anything that isn't alphanumeric, dash, underscore, or dot
    safe = re.sub(r'[^A-Za-z0-9._-]', '_', period)
    # Prevent directory traversal
    safe = safe.replace('..', '_')
    if not safe:
        raise ValueError(f"Invalid period name: {period!r}")
    return safe


def save_snapshot(snapshot: dict, snapshots_dir: Path = DEFAULT_SNAPSHOTS_DIR) -> Path:
    snapshots_dir = Path(snapshots_dir)
    snapshots_dir.mkdir(parents=True, exist_ok=True)
    path = snapshots_dir / f"{_safe_filename(snapshot['period'])}.json"
    with path.open("w", encoding="utf-8") as f:
        json.dump(snapshot, f, indent=2)
    return path


def load_snapshot(period: str, snapshots_dir: Path = DEFAULT_SNAPSHOTS_DIR) -> dict:
    path = Path(snapshots_dir) / f"{_safe_filename(period)}.json"
    if not path.exists():
        raise SnapshotNotFoundError(f"No snapshot found for period: {period}")
    with path.open(encoding="utf-8") as f:
        return json.load(f)
