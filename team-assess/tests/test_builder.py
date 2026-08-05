from prompts.builder import build_scoring_prompt

SAMPLE_RUBRIC = {
    "framework": "five-dysfunctions",
    "dimensions": {
        "trust": {
            "name": "Absence of Trust",
            "order": 1,
            "description": "Team members are unwilling to be vulnerable.",
            "healthy_signals": ["Admitting mistakes"],
            "dysfunction_signals": ["Concealing mistakes"],
            "scoring_guidance": "Score 1-2: guardedness. Score 4-5: open vulnerability.",
            "facets": [
                {
                    "name": "Vulnerability & Psychological Safety",
                    "healthy": ["Admits a mistake unprompted"],
                    "dysfunction": ["Conceals errors from the team"],
                },
                {
                    "name": "Contractual Trust — Reliability of Character",
                    "healthy": ["States a commitment with a specific owner and date"],
                    "dysfunction": [],
                },
            ],
        },
    },
}

SAMPLE_CONTENT = "Alice admitted she was blocked and asked for help."


def test_prompt_returns_tuple():
    result = build_scoring_prompt(SAMPLE_RUBRIC, SAMPLE_CONTENT)
    assert isinstance(result, tuple)
    assert len(result) == 2


def test_prompt_contains_dimension_name():
    system_prompt, _ = build_scoring_prompt(SAMPLE_RUBRIC, SAMPLE_CONTENT)
    assert "Absence of Trust" in system_prompt


def test_prompt_contains_healthy_signals():
    system_prompt, _ = build_scoring_prompt(SAMPLE_RUBRIC, SAMPLE_CONTENT)
    assert "Admitting mistakes" in system_prompt


def test_prompt_contains_dysfunction_signals():
    system_prompt, _ = build_scoring_prompt(SAMPLE_RUBRIC, SAMPLE_CONTENT)
    assert "Concealing mistakes" in system_prompt


def test_prompt_contains_team_content():
    _, user_prompt = build_scoring_prompt(SAMPLE_RUBRIC, SAMPLE_CONTENT)
    assert "Alice admitted she was blocked" in user_prompt


def test_prompt_contains_scoring_guidance():
    system_prompt, _ = build_scoring_prompt(SAMPLE_RUBRIC, SAMPLE_CONTENT)
    assert "Score 1-2" in system_prompt


def test_system_prompt_contains_facet_keys():
    system_prompt, _ = build_scoring_prompt(SAMPLE_RUBRIC, SAMPLE_CONTENT)
    assert "vulnerability_psychological_safety" in system_prompt
    assert "contractual_trust_reliability_of_character" in system_prompt


def test_user_prompt_contains_team_artifacts_header():
    _, user_prompt = build_scoring_prompt(SAMPLE_RUBRIC, SAMPLE_CONTENT)
    assert "## Team Artifacts" in user_prompt


def test_system_prompt_does_not_contain_artifacts():
    system_prompt, _ = build_scoring_prompt(SAMPLE_RUBRIC, SAMPLE_CONTENT)
    assert "Alice admitted she was blocked" not in system_prompt


def test_system_prompt_contains_exclusion_language():
    system_prompt, _ = build_scoring_prompt(SAMPLE_RUBRIC, SAMPLE_CONTENT)
    assert "excluded" in system_prompt.lower()
