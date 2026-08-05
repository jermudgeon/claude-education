import csv
import json
from pathlib import Path


def read_txt(path: Path) -> str:
    return Path(path).read_text(encoding="utf-8")


def read_md(path: Path) -> str:
    return Path(path).read_text(encoding="utf-8")


def read_csv(path: Path) -> str:
    lines = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            lines.append(" | ".join(f"{k}: {v}" for k, v in row.items()))
    return "\n".join(lines)


def read_json(path: Path) -> str:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return json.dumps(data, indent=2)
