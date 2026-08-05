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


def read_pdf(path: Path) -> str:
    from pypdf import PdfReader
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    reader = PdfReader(str(path))
    pages = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            pages.append(text)
    return "\n".join(pages)
