import pytest
from pathlib import Path
from ingestion.readers import read_txt, read_md, read_csv, read_json

FIXTURES = Path(__file__).parent / "fixtures"

def test_read_txt_returns_string():
    result = read_txt(FIXTURES / "sample.txt")
    assert "Alice admitted she was blocked" in result
    assert isinstance(result, str)

def test_read_md_returns_string():
    result = read_md(FIXTURES / "sample.md")
    assert "Retrospective Notes" in result
    assert isinstance(result, str)

def test_read_csv_returns_string_with_all_rows():
    result = read_csv(FIXTURES / "sample.csv")
    assert "Alice" in result
    assert "Bob" in result
    assert isinstance(result, str)

def test_read_json_returns_string():
    result = read_json(FIXTURES / "sample.json")
    assert "Alice" in result
    assert isinstance(result, str)

def test_read_txt_missing_file_raises():
    with pytest.raises(FileNotFoundError):
        read_txt(FIXTURES / "nonexistent.txt")
