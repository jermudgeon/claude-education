DIMENSION_LABELS = {
    "trust": "Trust",
    "conflict": "Conflict",
    "commitment": "Commitment",
    "accountability": "Accountability",
    "results": "Results",
}

DIRECTION_ARROWS = {
    "improving": "↑",
    "declining": "↓",
    "stable": "→",
}


def render_markdown(snapshot: dict, trend: dict | None = None) -> str:
    lines = []
    period = snapshot["period"]

    health = snapshot["overall_health"]
    if trend:
        delta = trend["overall_health_delta"]
        direction = DIRECTION_ARROWS[trend["overall_direction"]]
        prior = trend["before_period"]
        health_line = f"Overall Health: {health} / 5  ({direction} {_fmt_delta(delta)} from {prior})"
    else:
        health_line = f"Overall Health: {health} / 5"

    lines.append(f"# Team Health Assessment — {period}")
    lines.append(f"{health_line}")
    lines.append("")

    lines.append("## Dimension Scores")
    lines.append("")

    dims_sorted = _sort_dimensions_by_score(snapshot["dimensions"])
    for key, dim in dims_sorted:
        label = DIMENSION_LABELS.get(key, key.title())
        score = dim["score"]
        bar = _score_bar(score)
        if trend and key in trend["dimensions"]:
            t = trend["dimensions"][key]
            arrow = DIRECTION_ARROWS[t["direction"]]
            delta_str = f"{arrow} {_fmt_delta(t['delta'])}"
            warning = "  ⚠" if t["warning"] else ""
            lines.append(f"{label:<16} {bar}  {score:.1f}  {delta_str}{warning}")
        else:
            lines.append(f"{label:<16} {bar}  {score:.1f}")

    lines.append("")
    lines.append("## Priority Actions")
    lines.append("")
    for i, rec in enumerate(snapshot["recommendations"], 1):
        lines.append(f"{i}. {rec}")

    lines.append("")
    lines.append("## Evidence Highlights")
    for key, dim in dims_sorted:
        label = DIMENSION_LABELS.get(key, key.title())
        lines.append(f"\n### {label}")
        for evidence in dim.get("evidence", []):
            lines.append(f'- "{evidence}"')

    lines.append("")
    lines.append(f"*Inputs: {', '.join(snapshot['input_files'])}*")
    lines.append(f"*Run date: {snapshot['run_date']}*")

    return "\n".join(lines)


def _sort_dimensions_by_score(dimensions: dict) -> list:
    return sorted(dimensions.items(), key=lambda x: x[1]["score"])


def _score_bar(score: float) -> str:
    filled = int(score + 0.5)
    return "█" * filled + "░" * (5 - filled)


def _fmt_delta(delta: float) -> str:
    delta = delta or 0.0  # normalize -0.0 to 0.0
    return f"+{delta:.1f}" if delta >= 0 else f"{delta:.1f}"
