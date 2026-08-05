import pytest
from pathlib import Path
from ingestion.scanner import scan_directory

FIXTURES = Path(__file__).parent / "fixtures"

def test_scan_returns_labelled_content(tmp_path):
    (tmp_path / "notes.txt").write_text("Team notes here", encoding="utf-8")
    (tmp_path / "retro.md").write_text("# Retro\nWent well.", encoding="utf-8")
    content, files = scan_directory(tmp_path)
    assert "notes.txt" in content
    assert "Team notes here" in content
    assert "retro.md" in content
    assert "Went well." in content
    assert any("notes.txt" in f for f in files)
    assert any("retro.md" in f for f in files)

def test_scan_traverses_subdirectories(tmp_path):
    subdir = tmp_path / "retros"
    subdir.mkdir()
    (subdir / "sprint1.md").write_text("Sprint retro notes", encoding="utf-8")
    (tmp_path / "standup.txt").write_text("Standup notes", encoding="utf-8")
    content, files = scan_directory(tmp_path)
    assert "Sprint retro notes" in content
    assert "Standup notes" in content
    assert "retros/sprint1.md" in content or "retros\\sprint1.md" in content
    assert any("sprint1.md" in f for f in files)

def test_scan_skips_unsupported_extensions(tmp_path):
    (tmp_path / "notes.txt").write_text("Valid content", encoding="utf-8")
    (tmp_path / "image.png").write_bytes(b"\x89PNG")
    content, files = scan_directory(tmp_path)
    assert "Valid content" in content
    assert "image.png" not in content
    assert not any("image.png" in f for f in files)

def test_scan_empty_directory_returns_empty_string(tmp_path):
    content, files = scan_directory(tmp_path)
    assert content == ""
    assert files == []

def test_scan_raises_for_nonexistent_directory():
    with pytest.raises(NotADirectoryError):
        scan_directory(Path("/nonexistent/path"))

def test_scan_returns_files_in_alphabetical_order(tmp_path):
    (tmp_path / "zebra.txt").write_text("Zebra content", encoding="utf-8")
    (tmp_path / "alpha.txt").write_text("Alpha content", encoding="utf-8")
    content, files = scan_directory(tmp_path)
    alpha_pos = content.index("alpha.txt")
    zebra_pos = content.index("zebra.txt")
    assert alpha_pos < zebra_pos

def test_scan_continues_on_reader_error(tmp_path):
    (tmp_path / "good.txt").write_text("Good content", encoding="utf-8")
    (tmp_path / "bad.json").write_text("{not valid json", encoding="utf-8")
    content, files = scan_directory(tmp_path)
    assert "Good content" in content
    assert "good.txt" in files
    assert "bad.json" not in files
