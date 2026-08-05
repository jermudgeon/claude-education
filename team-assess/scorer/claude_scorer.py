import os
from datetime import date
from prompts.builder import build_scoring_prompt

SCORING_TOOL = {
    "name": "record_team_assessment",
    "description": "Record the structured team health assessment results",
    "input_schema": {
        "type": "object",
        "properties": {
            "dimensions": {
                "type": "object",
                "description": "Scores for each dysfunction dimension",
                "additionalProperties": {
                    "type": "object",
                    "properties": {
                        "score": {"type": "number", "minimum": 1, "maximum": 5},
                        "confidence": {"type": "string", "enum": ["low", "medium", "high"]},
                        "evidence": {"type": "array", "items": {"type": "string"}, "minItems": 1},
                    },
                    "required": ["score", "confidence", "evidence"],
                },
            },
            "recommendations": {
                "type": "array",
                "items": {"type": "string"},
                "minItems": 1,
                "description": "Prioritized action recommendations for the team",
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

    def score(self, content: str, rubric: dict, period: str, input_files: list[str]) -> dict:
        prompt = build_scoring_prompt(rubric, content)
        message = self._client.messages.create(
            model=self._model,
            max_tokens=4096,
            tools=[SCORING_TOOL],
            tool_choice={"type": "any"},
            messages=[{"role": "user", "content": prompt}],
        )

        tool_result = self._extract_tool_result(message)
        return self._build_snapshot(tool_result, period, input_files)

    def _extract_tool_result(self, message) -> dict:
        for block in message.content:
            if block.type == "tool_use":
                return block.input
        raise ScoringError("Claude did not return a tool_use response")

    def _build_snapshot(self, tool_result: dict, period: str, input_files: list[str]) -> dict:
        dimensions = tool_result["dimensions"]
        scores = [dim["score"] for dim in dimensions.values()]
        overall_health = round(sum(scores) / len(scores), 2) if scores else 0.0
        return {
            "period": period,
            "run_date": date.today().isoformat(),
            "input_files": input_files,
            "dimensions": dimensions,
            "overall_health": overall_health,
            "recommendations": tool_result["recommendations"],
        }
