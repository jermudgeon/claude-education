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
    if health is not None:
        health_str = f"{health}"
    else:
        health_str = "N/A (insufficient signal)"

    # Check embedded overall_health_trend first, fall back to legacy top-level trend arg
    oht = snapshot.get("overall_health_trend")
    if oht:
        delta = oht["delta"]
        direction = DIRECTION_ARROWS[oht["direction"]]
        prior = oht["compared_to"]
        if health is not None:
            health_line = f"Overall Health: {health_str} / 5  ({direction} {_fmt_delta(delta)} from {prior})"
        else:
            health_line = f"Overall Health: {health_str}"
    elif trend:
        delta = trend["overall_health_delta"]
        direction = DIRECTION_ARROWS[trend["overall_direction"]]
        prior = trend["before_period"]
        if health is not None:
            health_line = f"Overall Health: {health_str} / 5  ({direction} {_fmt_delta(delta)} from {prior})"
        else:
            health_line = f"Overall Health: {health_str}"
    else:
        health_line = f"Overall Health: {health_str} / 5"

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

        # Prefer trend embedded in dimension (new schema), fall back to top-level trend arg
        dim_trend = dim.get("trend")
        if dim_trend is None and trend and key in trend.get("dimensions", {}):
            dim_trend = trend["dimensions"][key]

        if dim_trend:
            arrow = DIRECTION_ARROWS[dim_trend["direction"]]
            delta_str = f"{arrow} {_fmt_delta(dim_trend['delta'])}"
            warning = "  ⚠" if dim_trend["warning"] else ""
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

    # Facet Detail section — only if any dimension has facets
    facet_lines = _render_facet_detail(dims_sorted)
    if facet_lines:
        lines.append("")
        lines.extend(facet_lines)

    lines.append("")
    lines.append(f"*Inputs: {', '.join(snapshot['input_files'])}*")
    lines.append(f"*Run date: {snapshot['run_date']}*")

    return "\n".join(lines)


def _render_facet_detail(dims_sorted: list) -> list[str]:
    """Render medium+high confidence facets grouped by dimension. Returns [] if nothing to show."""
    section_lines = []
    for key, dim in dims_sorted:
        facets = dim.get("facets", {})
        if not facets:
            continue

        observable = {
            fkey: fdata
            for fkey, fdata in facets.items()
            if fdata.get("confidence") in ("medium", "high")
        }
        if not observable:
            continue

        label = DIMENSION_LABELS.get(key, key.title())
        dim_score = dim["score"]
        section_lines.append(f"### {label} ({dim_score:.1f})")
        for fkey, fdata in observable.items():
            fscore = fdata["score"]
            fconf = fdata["confidence"]
            bar = _score_bar(fscore)
            section_lines.append(f"  {fkey}  {bar}  {fscore:.1f}  ({fconf} confidence)")
            for ev in fdata.get("evidence", []):
                section_lines.append(f'    - "{ev}"')
        section_lines.append("")

    if section_lines:
        return ["## Facet Detail", ""] + section_lines
    return []


def _sort_dimensions_by_score(dimensions: dict) -> list:
    return sorted(dimensions.items(), key=lambda x: x[1]["score"])


def _score_bar(score: float) -> str:
    filled = int(score + 0.5)
    return "█" * filled + "░" * (5 - filled)


def _fmt_delta(delta: float) -> str:
    delta = delta or 0.0  # normalize -0.0 to 0.0
    return f"+{delta:.1f}" if delta >= 0 else f"{delta:.1f}"
