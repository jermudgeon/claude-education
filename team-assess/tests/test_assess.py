# tests/test_assess.py
import pytest
import sys
from unittest.mock import patch, MagicMock
from pathlib import Path


def test_main_exits_on_empty_input(tmp_path):
    """assess.py exits with code 1 when no readable content found."""
    # Empty directory — scan_directory returns ""
    with patch("sys.argv", ["assess.py", "--input", str(tmp_path), "--period", "Q1-2025"]):
        with pytest.raises(SystemExit) as exc_info:
            import assess
            assess.main()
        assert exc_info.value.code == 1


def test_main_exits_on_empty_input_second_call(tmp_path):
    """Verify the exit behavior is repeatable (not a module-load side effect)."""
    with patch("sys.argv", ["assess.py", "--input", str(tmp_path), "--period", "Q2-2025"]):
        import assess
        with pytest.raises(SystemExit) as exc_info:
            assess.main()
        assert exc_info.value.code == 1
