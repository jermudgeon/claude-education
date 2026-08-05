def build_scoring_prompt(rubric: dict, content: str) -> str:
    dimensions_text = _format_dimensions(rubric["dimensions"])
    return f"""You are an expert team coach assessing team health using the {rubric.get("framework", "Five Dysfunctions")} framework.

Below are the dimensions to score, followed by team artifacts to analyze.

## Scoring Dimensions

{dimensions_text}

## Team Artifacts

{content}

## Instructions

Analyze the team artifacts above and score each dimension on a scale of 1 to 5:
- 1 = severe dysfunction clearly present
- 3 = mixed signals, some healthy and some dysfunctional behavior
- 5 = healthy team behavior strongly demonstrated

For each dimension provide:
- score: a number from 1.0 to 5.0 (decimals allowed)
- confidence: "low", "medium", or "high" based on how much relevant signal was present
- evidence: a list of 2-4 direct quotes or specific behavioral observations from the artifacts

Also provide:
- recommendations: a list of 3-5 specific, actionable recommendations for the team, ordered by priority (most dysfunctional dimension first)

Return ONLY valid JSON matching the schema provided via the tool definition. Do not add commentary outside the JSON.
"""


def _format_dimensions(dimensions: dict) -> str:
    sorted_dims = sorted(dimensions.items(), key=lambda x: x[1]["order"])
    parts = []
    for key, dim in sorted_dims:
        healthy = "\n  - ".join(dim["healthy_signals"])
        dysfunctional = "\n  - ".join(dim["dysfunction_signals"])
        parts.append(f"""### {dim['order']}. {dim['name']} (key: `{key}`)
{dim['description']}

Healthy signals:
  - {healthy}

Dysfunction signals:
  - {dysfunctional}

Scoring guidance:
{dim['scoring_guidance']}""")
    return "\n\n".join(parts)
