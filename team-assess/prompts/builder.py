import re


def build_scoring_prompt(rubric: dict, content: str) -> tuple[str, str]:
    """Return (system_prompt, user_prompt).

    system_prompt — static rubric description + dimension/facet definitions + instructions.
    user_prompt   — the team artifacts to analyse.
    """
    dimensions_text = _format_dimensions(rubric["dimensions"])
    framework = rubric.get("framework", "Five Dysfunctions")

    system_prompt = f"""You are an expert team coach assessing team health using the {framework} framework.

Below are the dimensions and facets to score.

## Scoring Dimensions

{dimensions_text}

## Instructions

Analyze the team artifacts provided by the user and score each facet on a scale of 1 to 5:
- 1 = severe dysfunction clearly present
- 3 = mixed signals, some healthy and some dysfunctional behavior
- 5 = healthy team behavior strongly demonstrated

For each facet provide:
- score: a number from 1.0 to 5.0 (decimals allowed)
- confidence: "low" (little or no signal), "medium" (some signal), or "high" (strong signal)
- evidence: a list of 0-4 direct quotes or specific behavioral observations from the artifacts

Also provide:
- recommendations: a list of 3-5 specific, actionable recommendations for the team, ordered by priority (most dysfunctional dimension first)

Return ONLY valid JSON matching the schema provided via the tool definition. Do not add commentary outside the JSON."""

    user_prompt = f"## Team Artifacts\n\n{content}"

    return system_prompt, user_prompt


def _facet_key(name: str) -> str:
    return re.sub(r'[^a-z0-9]+', '_', name.lower()).strip('_')


def _format_dimensions(dimensions: dict) -> str:
    sorted_dims = sorted(dimensions.items(), key=lambda x: x[1]["order"])
    parts = []
    for key, dim in sorted_dims:
        healthy = "\n  - ".join(dim["healthy_signals"])
        dysfunctional = "\n  - ".join(dim["dysfunction_signals"])

        # Build facets block
        facets_lines = [f"\n### Facets to score within {dim['name']}\n"]
        facets_lines.append(
            "For each facet below, score 1–5 and provide confidence (low/medium/high) and evidence.\n"
            "Return the facet using the key shown in backticks.\n"
        )
        for facet in dim.get("facets", []):
            fkey = _facet_key(facet["name"])
            facets_lines.append(f"  `{fkey}`: {facet['name']}")
            if facet.get("healthy"):
                h_items = "\n      + ".join(facet["healthy"])
                facets_lines.append(f"    + healthy indicators: {h_items}")
            if facet.get("dysfunction"):
                d_items = "\n      - ".join(facet["dysfunction"])
                facets_lines.append(f"    - dysfunction indicators: {d_items}")
            facets_lines.append("")

        facets_block = "\n".join(facets_lines)

        parts.append(f"""### {dim['order']}. {dim['name']} (key: `{key}`)
{dim['description']}

Healthy signals:
  - {healthy}

Dysfunction signals:
  - {dysfunctional}

Scoring guidance:
{dim['scoring_guidance']}{facets_block}""")
    return "\n\n".join(parts)
