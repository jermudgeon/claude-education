import pytest
from unittest.mock import MagicMock
from scorer.claude_scorer import ClaudeScorer, ScoringError

SAMPLE_RUBRIC = {
    "framework": "five-dysfunctions",
    "dimensions": {
        "trust": {"name": "Absence of Trust", "order": 1, "description": "", "healthy_signals": [], "dysfunction_signals": [], "scoring_guidance": ""},
        "conflict": {"name": "Fear of Conflict", "order": 2, "description": "", "healthy_signals": [], "dysfunction_signals": [], "scoring_guidance": ""},
        "commitment": {"name": "Lack of Commitment", "order": 3, "description": "", "healthy_signals": [], "dysfunction_signals": [], "scoring_guidance": ""},
        "accountability": {"name": "Avoidance of Accountability", "order": 4, "description": "", "healthy_signals": [], "dysfunction_signals": [], "scoring_guidance": ""},
        "results": {"name": "Inattention to Results", "order": 5, "description": "", "healthy_signals": [], "dysfunction_signals": [], "scoring_guidance": ""},
    },
}

MOCK_CLAUDE_RESPONSE = {
    "dimensions": {
        "trust": {"score": 3.0, "confidence": "medium", "evidence": ["Alice asked for help"]},
        "conflict": {"score": 2.5, "confidence": "high", "evidence": ["No debate observed"]},
        "commitment": {"score": 3.5, "confidence": "medium", "evidence": ["Decisions followed through"]},
        "accountability": {"score": 2.0, "confidence": "low", "evidence": ["No peer feedback seen"]},
        "results": {"score": 3.2, "confidence": "medium", "evidence": ["Team goal mentioned"]},
    },
    "recommendations": ["Address accountability directly", "Introduce structured conflict norms"],
}


def _make_mock_client(response_data: dict):
    mock_content = MagicMock()
    mock_content.type = "tool_use"
    mock_content.input = response_data

    mock_message = MagicMock()
    mock_message.content = [mock_content]
    mock_message.stop_reason = "tool_use"

    mock_client = MagicMock()
    mock_client.messages.create.return_value = mock_message
    return mock_client


def test_score_returns_snapshot_with_all_dimensions():
    mock_client = _make_mock_client(MOCK_CLAUDE_RESPONSE)
    scorer = ClaudeScorer({"model": "claude-sonnet-4-6"}, client=mock_client)
    snapshot = scorer.score("Some team content", SAMPLE_RUBRIC, "Q1-2025", ["notes.txt"])
    assert set(snapshot["dimensions"].keys()) == {"trust", "conflict", "commitment", "accountability", "results"}

def test_score_computes_overall_health():
    mock_client = _make_mock_client(MOCK_CLAUDE_RESPONSE)
    scorer = ClaudeScorer({"model": "claude-sonnet-4-6"}, client=mock_client)
    snapshot = scorer.score("Some team content", SAMPLE_RUBRIC, "Q1-2025", ["notes.txt"])
    expected = round((3.0 + 2.5 + 3.5 + 2.0 + 3.2) / 5, 2)
    assert snapshot["overall_health"] == expected

def test_score_includes_period_and_metadata():
    mock_client = _make_mock_client(MOCK_CLAUDE_RESPONSE)
    scorer = ClaudeScorer({"model": "claude-sonnet-4-6"}, client=mock_client)
    snapshot = scorer.score("Some team content", SAMPLE_RUBRIC, "Q1-2025", ["notes.txt"])
    assert snapshot["period"] == "Q1-2025"
    assert "run_date" in snapshot
    assert snapshot["input_files"] == ["notes.txt"]

def test_score_includes_recommendations():
    mock_client = _make_mock_client(MOCK_CLAUDE_RESPONSE)
    scorer = ClaudeScorer({"model": "claude-sonnet-4-6"}, client=mock_client)
    snapshot = scorer.score("Some team content", SAMPLE_RUBRIC, "Q1-2025", ["notes.txt"])
    assert len(snapshot["recommendations"]) >= 1
