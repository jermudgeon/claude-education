import pytest
from unittest.mock import MagicMock
from scorer.claude_scorer import ClaudeScorer, ScoringError, build_scoring_tool

# Simplified rubric with 2 facets per dimension to keep mocks manageable
SAMPLE_RUBRIC = {
    "framework": "five-dysfunctions",
    "dimensions": {
        "trust": {
            "name": "Absence of Trust",
            "order": 1,
            "description": "",
            "healthy_signals": [],
            "dysfunction_signals": [],
            "scoring_guidance": "",
            "facets": [
                {"name": "Vulnerability & Psychological Safety", "healthy": [], "dysfunction": []},
                {"name": "Contractual Trust — Reliability of Character", "healthy": [], "dysfunction": []},
            ],
        },
        "conflict": {
            "name": "Fear of Conflict",
            "order": 2,
            "description": "",
            "healthy_signals": [],
            "dysfunction_signals": [],
            "scoring_guidance": "",
            "facets": [
                {"name": "Surfacing Disagreement", "healthy": [], "dysfunction": []},
                {"name": "Quality of Debate", "healthy": [], "dysfunction": []},
            ],
        },
        "commitment": {
            "name": "Lack of Commitment",
            "order": 3,
            "description": "",
            "healthy_signals": [],
            "dysfunction_signals": [],
            "scoring_guidance": "",
            "facets": [
                {"name": "Clarity of Mission, Goals & Roles", "healthy": [], "dysfunction": []},
                {"name": "Buy-In & Decision Closure", "healthy": [], "dysfunction": []},
            ],
        },
        "accountability": {
            "name": "Avoidance of Accountability",
            "order": 4,
            "description": "",
            "healthy_signals": [],
            "dysfunction_signals": [],
            "scoring_guidance": "",
            "facets": [
                {"name": "Peer-to-Peer Accountability", "healthy": [], "dysfunction": []},
                {"name": "Expectation Setting (Antecedents)", "healthy": [], "dysfunction": []},
            ],
        },
        "results": {
            "name": "Inattention to Results",
            "order": 5,
            "description": "",
            "healthy_signals": [],
            "dysfunction_signals": [],
            "scoring_guidance": "",
            "facets": [
                {"name": "Collective Goal Focus vs. Individual Status", "healthy": [], "dysfunction": []},
                {"name": "Dependability & Delivery", "healthy": [], "dysfunction": []},
            ],
        },
    },
}

MOCK_CLAUDE_RESPONSE = {
    "dimensions": {
        "trust": {
            "facets": {
                "vulnerability_psychological_safety": {"score": 3.0, "confidence": "medium", "evidence": ["Alice asked for help"]},
                "contractual_trust_reliability_of_character": {"score": 3.5, "confidence": "high", "evidence": ["Commitments met"]},
            }
        },
        "conflict": {
            "facets": {
                "surfacing_disagreement": {"score": 2.5, "confidence": "high", "evidence": ["No debate observed"]},
                "quality_of_debate": {"score": 2.0, "confidence": "medium", "evidence": []},
            }
        },
        "commitment": {
            "facets": {
                "clarity_of_mission_goals_roles": {"score": 3.5, "confidence": "medium", "evidence": ["Decisions followed through"]},
                "buy_in_decision_closure": {"score": 4.0, "confidence": "high", "evidence": []},
            }
        },
        "accountability": {
            "facets": {
                "peer_to_peer_accountability": {"score": 2.0, "confidence": "low", "evidence": []},
                "expectation_setting_antecedents": {"score": 2.5, "confidence": "low", "evidence": []},
            }
        },
        "results": {
            "facets": {
                "collective_goal_focus_vs_individual_status": {"score": 3.2, "confidence": "medium", "evidence": ["Team goal mentioned"]},
                "dependability_delivery": {"score": 4.0, "confidence": "high", "evidence": ["Shipped on time"]},
            }
        },
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
    mock_client.messages.stream.return_value.__enter__.return_value.get_final_message.return_value = mock_message
    return mock_client


def test_score_returns_snapshot_with_included_dimensions():
    mock_client = _make_mock_client(MOCK_CLAUDE_RESPONSE)
    scorer = ClaudeScorer({"model": "claude-sonnet-4-6"}, client=mock_client)
    snapshot = scorer.score("Some team content", SAMPLE_RUBRIC, "Q1-2025", ["notes.txt"])
    # accountability has all-low confidence → excluded (Option X)
    assert "trust" in snapshot["dimensions"]
    assert "conflict" in snapshot["dimensions"]
    assert "commitment" in snapshot["dimensions"]
    assert "accountability" not in snapshot["dimensions"]
    assert "results" in snapshot["dimensions"]


def test_score_computes_overall_health_from_included_dimensions_only():
    mock_client = _make_mock_client(MOCK_CLAUDE_RESPONSE)
    scorer = ClaudeScorer({"model": "claude-sonnet-4-6"}, client=mock_client)
    snapshot = scorer.score("Some team content", SAMPLE_RUBRIC, "Q1-2025", ["notes.txt"])
    # trust: mean(3.0, 3.5) = 3.25; conflict: mean(2.5, 2.0) = 2.25
    # commitment: mean(3.5, 4.0) = 3.75; results: mean(3.2, 4.0) = 3.6
    expected = round((3.25 + 2.25 + 3.75 + 3.6) / 4, 2)
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


def test_score_raises_scoring_error_when_no_tool_use():
    mock_content = MagicMock()
    mock_content.type = "text"  # not tool_use
    mock_message = MagicMock()
    mock_message.content = [mock_content]
    mock_client = MagicMock()
    mock_client.messages.stream.return_value.__enter__.return_value.get_final_message.return_value = mock_message
    scorer = ClaudeScorer({"model": "claude-sonnet-4-6"}, client=mock_client)
    with pytest.raises(ScoringError):
        scorer.score("content", SAMPLE_RUBRIC, "Q1-2025", ["f.txt"])


def test_option_x_excludes_all_low_confidence_dimension():
    mock_client = _make_mock_client(MOCK_CLAUDE_RESPONSE)
    scorer = ClaudeScorer({"model": "claude-sonnet-4-6"}, client=mock_client)
    snapshot = scorer.score("Some team content", SAMPLE_RUBRIC, "Q1-2025", ["notes.txt"])
    assert "accountability" not in snapshot["dimensions"]


def test_low_confidence_facets_stored_but_excluded_from_scoring():
    # accountability is excluded but trust's facets are all medium/high — verify facets stored
    mock_client = _make_mock_client(MOCK_CLAUDE_RESPONSE)
    scorer = ClaudeScorer({"model": "claude-sonnet-4-6"}, client=mock_client)
    snapshot = scorer.score("Some team content", SAMPLE_RUBRIC, "Q1-2025", ["notes.txt"])
    trust = snapshot["dimensions"]["trust"]
    assert "facets" in trust
    assert "vulnerability_psychological_safety" in trust["facets"]
    assert trust["facets"]["vulnerability_psychological_safety"]["confidence"] == "medium"


def test_trend_embedded_when_prior_snapshot_provided():
    mock_client = _make_mock_client(MOCK_CLAUDE_RESPONSE)
    scorer = ClaudeScorer({"model": "claude-sonnet-4-6"}, client=mock_client)
    prior = {
        "period": "Q4-2024",
        "overall_health": 2.5,
        "dimensions": {
            "trust": {"score": 2.5, "evidence": [], "facets": {}},
            "conflict": {"score": 2.0, "evidence": [], "facets": {}},
            "commitment": {"score": 3.0, "evidence": [], "facets": {}},
            "results": {"score": 3.0, "evidence": [], "facets": {}},
        },
    }
    snapshot = scorer.score("Some team content", SAMPLE_RUBRIC, "Q1-2025", ["notes.txt"], prior_snapshot=prior)
    assert "trend" in snapshot["dimensions"]["trust"]
    assert snapshot["dimensions"]["trust"]["trend"]["compared_to"] == "Q4-2024"
    assert snapshot["dimensions"]["trust"]["trend"]["direction"] in ("improving", "declining", "stable")


def test_no_trend_when_no_prior_snapshot():
    mock_client = _make_mock_client(MOCK_CLAUDE_RESPONSE)
    scorer = ClaudeScorer({"model": "claude-sonnet-4-6"}, client=mock_client)
    snapshot = scorer.score("Some team content", SAMPLE_RUBRIC, "Q1-2025", ["notes.txt"])
    for dim in snapshot["dimensions"].values():
        assert "trend" not in dim


def test_build_scoring_tool_contains_facet_keys():
    tool = build_scoring_tool(SAMPLE_RUBRIC)
    trust_props = (
        tool["input_schema"]["properties"]["dimensions"]["properties"]["trust"]
        ["properties"]["facets"]["properties"]
    )
    assert "vulnerability_psychological_safety" in trust_props
    assert "contractual_trust_reliability_of_character" in trust_props
