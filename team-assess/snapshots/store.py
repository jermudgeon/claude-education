import json
from pathlib import Path

DEFAULT_SNAPSHOTS_DIR = Path("snapshots")


class SnapshotNotFoundError(Exception):
    pass


def save_snapshot(snapshot: dict, snapshots_dir: Path = DEFAULT_SNAPSHOTS_DIR) -> Path:
    snapshots_dir = Path(snapshots_dir)
    snapshots_dir.mkdir(parents=True, exist_ok=True)
    path = snapshots_dir / f"{snapshot['period']}.json"
    with path.open("w", encoding="utf-8") as f:
        json.dump(snapshot, f, indent=2)
    return path


def load_snapshot(period: str, snapshots_dir: Path = DEFAULT_SNAPSHOTS_DIR) -> dict:
    path = Path(snapshots_dir) / f"{period}.json"
    if not path.exists():
        raise SnapshotNotFoundError(f"No snapshot found for period: {period}")
    with path.open(encoding="utf-8") as f:
        return json.load(f)
