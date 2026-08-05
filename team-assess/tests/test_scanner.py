import pytest
from pathlib import Path
from ingestion.scanner import scan_directory, UnsupportedFormatError

FIXTURES = Path(__file__).parent / "fixtures"

def test_scan_returns_labelled_content(tmp_path):
    (tmp_path / "notes.txt").write_text("Team notes here", encoding="utf-8")
    (tmp_path / "retro.md").write_text("# Retro\nWent well.", encoding="utf-8")
    result = scan_directory(tmp_path)
    assert "notes.txt" in result
    assert "Team notes here" in result
    assert "retro.md" in result
    assert "Went well." in result

def test_scan_skips_unsupported_extensions(tmp_path):
    (tmp_path / "notes.txt").write_text("Valid content", encoding="utf-8")
    (tmp_path / "image.png").write_bytes(b"\x89PNG")
    result = scan_directory(tmp_path)
    assert "Valid content" in result
    assert "image.png" not in result

def test_scan_empty_directory_returns_empty_string(tmp_path):
    result = scan_directory(tmp_path)
    assert result == ""

def test_scan_raises_for_nonexistent_directory():
    with pytest.raises(NotADirectoryError):
        scan_directory(Path("/nonexistent/path"))
