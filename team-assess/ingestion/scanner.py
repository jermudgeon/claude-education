from pathlib import Path
from ingestion.readers import read_txt, read_md, read_csv, read_json, read_pdf


class UnsupportedFormatError(Exception):
    pass


READERS = {
    ".txt": read_txt,
    ".md": read_md,
    ".csv": read_csv,
    ".json": read_json,
    ".pdf": read_pdf,
}


def scan_directory(directory: Path) -> str:
    directory = Path(directory)
    if not directory.is_dir():
        raise NotADirectoryError(f"Not a directory: {directory}")

    sections = []
    for file_path in sorted(directory.iterdir()):
        if not file_path.is_file():
            continue
        reader = READERS.get(file_path.suffix.lower())
        if reader is None:
            continue
        try:
            content = reader(file_path)
        except Exception as e:
            raise UnsupportedFormatError(f"Failed to read {file_path.name}: {e}") from e
        if content.strip():
            sections.append(f"--- {file_path.name} ---\n{content}")

    return "\n\n".join(sections)
