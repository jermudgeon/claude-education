import pytest
from pathlib import Path
from ingestion.readers import read_txt, read_md, read_csv, read_json, read_pdf

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

def test_read_pdf_returns_string(tmp_path):
    # Create a minimal PDF using pypdf's writer
    from pypdf import PdfWriter
    writer = PdfWriter()
    writer.add_blank_page(width=612, height=792)
    pdf_path = tmp_path / "test.pdf"
    with open(pdf_path, "wb") as f:
        writer.write(f)
    # Blank PDF returns empty string (no text), not an error
    result = read_pdf(pdf_path)
    assert isinstance(result, str)

def test_read_pdf_missing_file_raises():
    with pytest.raises(FileNotFoundError):
        read_pdf(FIXTURES / "nonexistent.pdf")
