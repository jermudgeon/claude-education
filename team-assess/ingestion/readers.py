import csv
import io
import json
from pathlib import Path

from pypdf import PdfReader


def _read_text_with_fallback(path: Path) -> str:
    path = Path(path)
    for encoding in ("utf-8", "cp1252", "latin-1"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    # latin-1 always succeeds, so this shouldn't fire
    return path.read_text(encoding="latin-1", errors="replace")


def read_txt(path: Path) -> str:
    return _read_text_with_fallback(path)


def read_md(path: Path) -> str:
    return _read_text_with_fallback(path)


def read_csv(path: Path) -> str:
    raw = _read_text_with_fallback(path)
    lines = []
    reader = csv.DictReader(io.StringIO(raw))
    for row in reader:
        lines.append(" | ".join(f"{k}: {v}" for k, v in row.items()))
    return "\n".join(lines)


def read_json(path: Path) -> str:
    raw = _read_text_with_fallback(path)
    data = json.loads(raw)
    return json.dumps(data, indent=2)


def read_pdf(path: Path) -> str:
    path = Path(path)
    reader = PdfReader(str(path))
    pages = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            pages.append(text)
    return "\n".join(pages)
