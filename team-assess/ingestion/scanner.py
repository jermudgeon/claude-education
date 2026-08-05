import sys
from pathlib import Path
from ingestion.readers import read_txt, read_md, read_csv, read_json, read_pdf


READERS = {
    ".txt": read_txt,
    ".md": read_md,
    ".csv": read_csv,
    ".json": read_json,
    ".pdf": read_pdf,
}


def scan_directory(directory: Path) -> tuple[str, list[str]]:
    directory = Path(directory)
    if not directory.is_dir():
        raise NotADirectoryError(f"Not a directory: {directory}")

    sections = []
    input_files = []
    for file_path in sorted(directory.rglob("*")):
        if not file_path.is_file():
            continue
        reader = READERS.get(file_path.suffix.lower())
        if reader is None:
            continue
        try:
            content = reader(file_path)
        except Exception as e:
            print(f"Warning: failed to read {file_path}: {e}", file=sys.stderr)
            continue
        if content.strip():
            label = file_path.relative_to(directory)
            sections.append(f"--- {label} ---\n{content}")
            input_files.append(str(label))

    return "\n\n".join(sections), input_files
