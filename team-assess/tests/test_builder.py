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
        },
    },
}

SAMPLE_CONTENT = "Alice admitted she was blocked and asked for help."


def test_prompt_contains_dimension_name():
    prompt = build_scoring_prompt(SAMPLE_RUBRIC, SAMPLE_CONTENT)
    assert "Absence of Trust" in prompt

def test_prompt_contains_healthy_signals():
    prompt = build_scoring_prompt(SAMPLE_RUBRIC, SAMPLE_CONTENT)
    assert "Admitting mistakes" in prompt

def test_prompt_contains_dysfunction_signals():
    prompt = build_scoring_prompt(SAMPLE_RUBRIC, SAMPLE_CONTENT)
    assert "Concealing mistakes" in prompt

def test_prompt_contains_team_content():
    prompt = build_scoring_prompt(SAMPLE_RUBRIC, SAMPLE_CONTENT)
    assert "Alice admitted she was blocked" in prompt

def test_prompt_contains_scoring_guidance():
    prompt = build_scoring_prompt(SAMPLE_RUBRIC, SAMPLE_CONTENT)
    assert "Score 1-2" in prompt
