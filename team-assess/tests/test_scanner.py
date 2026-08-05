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

def test_scan_traverses_subdirectories(tmp_path):
    subdir = tmp_path / "retros"
    subdir.mkdir()
    (subdir / "sprint1.md").write_text("Sprint retro notes", encoding="utf-8")
    (tmp_path / "standup.txt").write_text("Standup notes", encoding="utf-8")
    result = scan_directory(tmp_path)
    assert "Sprint retro notes" in result
    assert "Standup notes" in result
    assert "retros/sprint1.md" in result or "retros\\sprint1.md" in result

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

def test_scan_returns_files_in_alphabetical_order(tmp_path):
    (tmp_path / "zebra.txt").write_text("Zebra content", encoding="utf-8")
    (tmp_path / "alpha.txt").write_text("Alpha content", encoding="utf-8")
    result = scan_directory(tmp_path)
    alpha_pos = result.index("alpha.txt")
    zebra_pos = result.index("zebra.txt")
    assert alpha_pos < zebra_pos
