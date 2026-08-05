import os
import sys
import re
from datetime import date
from prompts.builder import build_scoring_prompt, facet_key

STABLE_THRESHOLD = 0.2
WARNING_THRESHOLD = 1.0


def _direction(delta: float) -> str:
    if delta > STABLE_THRESHOLD:
        return "improving"
    if delta < -STABLE_THRESHOLD:
        return "declining"
    return "stable"


def build_scoring_tool(rubric: dict) -> dict:
    """Build a dynamic tool schema that requires one facet entry per dimension facet."""
    dim_properties = {}
    dim_required = []

    sorted_dims = sorted(rubric["dimensions"].items(), key=lambda x: x[1]["order"])
    for dim_key, dim in sorted_dims:
        facets = dim.get("facets", [])
        facet_properties = {}
        facet_required = []
        for facet in facets:
            fkey = facet_key(facet["name"])
            facet_properties[fkey] = {
                "type": "object",
                "properties": {
                    "score": {"type": "number", "minimum": 1, "maximum": 5},
                    "confidence": {"type": "string", "enum": ["low", "medium", "high"]},
                    "evidence": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["score", "confidence", "evidence"],
            }
            facet_required.append(fkey)

        dim_properties[dim_key] = {
            "type": "object",
            "properties": {
                "facets": {
                    "type": "object",
                    "properties": facet_properties,
                    "required": facet_required,
                }
            },
            "required": ["facets"],
        }
        dim_required.append(dim_key)

    return {
        "name": "record_team_assessment",
        "description": "Record the structured team health assessment results",
        "input_schema": {
            "type": "object",
            "properties": {
                "dimensions": {
                    "type": "object",
                    "properties": dim_properties,
                    "required": dim_required,
                },
                "recommendations": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 1,
                },
            },
            "required": ["dimensions", "recommendations"],
        },
    }


class ScoringError(Exception):
    pass


class ClaudeScorer:
    def __init__(self, claude_config: dict, client=None):
        self._model = claude_config.get("model", "claude-sonnet-4-6")
        if client is not None:
            self._client = client
        else:
            import anthropic
            api_key_env = claude_config.get("api_key_env", "ANTHROPIC_API_KEY")
            self._client = anthropic.Anthropic(api_key=os.environ.get(api_key_env))

    def score(
        self,
        content: str,
        rubric: dict,
        period: str,
        input_files: list[str],
        prior_snapshot: dict | None = None,
    ) -> dict:
        system_prompt, user_prompt = build_scoring_prompt(rubric, content)
        scoring_tool = build_scoring_tool(rubric)

        message = self._client.messages.create(
            model=self._model,
            max_tokens=4096,
            system=[{"type": "text", "text": system_prompt, "cache_control": {"type": "ephemeral"}}],
            tools=[scoring_tool],
            tool_choice={"type": "any"},
            messages=[{"role": "user", "content": user_prompt}],
        )

        tool_result = self._extract_tool_result(message)
        return self._build_snapshot(tool_result, rubric, period, input_files, prior_snapshot)

    def _extract_tool_result(self, message) -> dict:
        for block in message.content:
            if block.type == "tool_use":
                return block.input
        raise ScoringError("Claude did not return a tool_use response")

    def _build_snapshot(
        self,
        tool_result: dict,
        rubric: dict,
        period: str,
        input_files: list[str],
        prior_snapshot: dict | None = None,
    ) -> dict:
        dimensions_out = {}
        dimension_scores = []

        sorted_dims = sorted(rubric["dimensions"].items(), key=lambda x: x[1]["order"])
        for dim_key, dim_def in sorted_dims:
            raw_dim = tool_result["dimensions"].get(dim_key, {})
            raw_facets = raw_dim.get("facets", {})

            # Build facets dict from rubric-expected keys
            facets_out = {}
            observable_scores = []
            observable_evidence = []

            for facet in dim_def.get("facets", []):
                fkey = facet_key(facet["name"])
                facet_data = raw_facets.get(fkey, {})
                score = facet_data.get("score", 1.0)
                confidence = facet_data.get("confidence", "low")
                evidence = facet_data.get("evidence", [])

                facets_out[fkey] = {
                    "score": score,
                    "confidence": confidence,
                    "evidence": evidence,
                }

                if confidence in ("medium", "high"):
                    observable_scores.append(score)
                    observable_evidence.extend(evidence)

            # Option X: if ALL facets are low confidence, exclude dimension entirely
            if not observable_scores:
                rubric_facets = rubric["dimensions"].get(dim_key, {}).get("facets", [])
                if not rubric_facets:
                    print(f"Warning: dimension '{dim_key}' has no facets defined in rubric, excluded.", file=sys.stderr)
                continue

            dim_score = round(sum(observable_scores) / len(observable_scores), 2)
            # Collect up to 4 evidence items from observable facets
            dim_evidence = observable_evidence[:4]

            dim_out = {
                "score": dim_score,
                "evidence": dim_evidence,
                "facets": facets_out,
            }

            # Embed trend if prior_snapshot provided and dim present in prior
            if prior_snapshot and dim_key in prior_snapshot.get("dimensions", {}):
                prior_score = prior_snapshot["dimensions"][dim_key]["score"]
                delta = round(dim_score - prior_score, 2)
                dim_out["trend"] = {
                    "compared_to": prior_snapshot["period"],
                    "delta": delta,
                    "direction": _direction(delta),
                    "warning": abs(delta) >= WARNING_THRESHOLD,
                }

            dimensions_out[dim_key] = dim_out
            dimension_scores.append(dim_score)

        overall_health = (
            round(sum(dimension_scores) / len(dimension_scores), 2)
            if dimension_scores
            else None
        )

        return {
            "period": period,
            "run_date": date.today().isoformat(),
            "input_files": input_files,
            "overall_health": overall_health,
            "dimensions": dimensions_out,
            "recommendations": tool_result["recommendations"],
        }
