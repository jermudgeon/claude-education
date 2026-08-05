import argparse
import os
import sys
from pathlib import Path

from config import load_config
from ingestion.scanner import scan_directory
from rubric.loader import load_rubric
from scorer.claude_scorer import ClaudeScorer
from snapshots.store import save_snapshot, load_snapshot, SnapshotNotFoundError
from renderer.markdown import render_markdown


def main():
    parser = argparse.ArgumentParser(
        description="Assess team health using the Five Dysfunctions framework"
    )
    parser.add_argument("--input", required=True, help="Directory of input files")
    parser.add_argument("--period", required=True, help="Label for this snapshot (e.g. Q1-2025)")
    parser.add_argument("--compare", help="Period label to diff against")
    parser.add_argument("--output", help="Output directory (overrides config)")
    parser.add_argument("--config", default="config.toml", help="Path to config.toml")
    args = parser.parse_args()

    cfg = load_config(args.config)

    api_key_env = cfg["claude"]["api_key_env"]
    if not os.environ.get(api_key_env):
        print(f"Error: environment variable {api_key_env} is not set. Set it before running (e.g. export {api_key_env}=your-key).", file=sys.stderr)
        sys.exit(1)

    output_dir = Path(args.output or cfg["paths"]["output_dir"])
    snapshots_dir = Path(cfg["paths"]["snapshots_dir"])

    print(f"Scanning input directory: {args.input}")
    content, input_files = scan_directory(Path(args.input))
    if not content.strip():
        print("Error: no readable content found in input directory.", file=sys.stderr)
        sys.exit(1)

    content_chars = len(content)
    approx_tokens = content_chars // 4
    print(f"Ingested {len(input_files)} files, {content_chars:,} chars (~{approx_tokens:,} tokens)")
    if approx_tokens > 800_000:
        print(f"Warning: approx {approx_tokens:,} tokens is close to the 1M context limit.", file=sys.stderr)

    print(f"Loading rubric: {cfg['rubric']['path']}")
    rubric = load_rubric(cfg["rubric"]["path"])

    # Load prior snapshot for trend embedding if --compare given
    prior_snapshot = None
    if args.compare:
        try:
            prior_snapshot = load_snapshot(args.compare, snapshots_dir=snapshots_dir)
        except SnapshotNotFoundError:
            print(
                f"Warning: no snapshot found for period '{args.compare}' in {snapshots_dir}, skipping trend.",
                file=sys.stderr,
            )

    print("Scoring with Claude...")
    scorer = ClaudeScorer(cfg["claude"])
    try:
        snapshot = scorer.score(content, rubric, args.period, input_files, prior_snapshot=prior_snapshot)
    except Exception as e:
        print(f"Error scoring with Claude: {e}", file=sys.stderr)
        sys.exit(1)

    save_snapshot(snapshot, snapshots_dir=snapshots_dir)
    print(f"Snapshot saved to {snapshots_dir}/{args.period}.json")

    report = render_markdown(snapshot)

    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / f"report-{args.period}.md"
    report_path.write_text(report, encoding="utf-8")
    print(f"Report written to {report_path}")


if __name__ == "__main__":
    main()
