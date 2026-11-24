"""Command-line entry point for the AI Output Evaluator."""

import argparse
from pathlib import Path

from src.evaluator import LLMEvaluator
from src.reporting import write_markdown_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Evaluate model outputs against simple, explicit quality checks."
    )
    parser.add_argument(
        "--input", default="data/test_cases.json",
        help="Path to the JSON file containing test cases.",
    )
    parser.add_argument(
        "--output", default="reports/evaluation_results.json",
        help="Path where the JSON evaluation report will be written.",
    )
    parser.add_argument(
        "--threshold", type=float, default=0.8,
        help="Minimum keyword coverage required to pass (0.0 to 1.0).",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        evaluator = LLMEvaluator(args.input, keyword_threshold=args.threshold)
        summary = evaluator.run_evaluations(args.output)
        markdown_path = Path(args.output).with_suffix(".md")
        write_markdown_report(summary, markdown_path)
    except (OSError, ValueError, TypeError) as exc:
        print(f"Evaluation could not be completed: {exc}")
        return 1

    print("AI Output Evaluation Engine")
    print(f"Total tests: {summary['total_tests']}")
    print(f"Passed: {summary['passed_tests']}")
    print(f"Failed: {summary['failed_tests']}")
    print(f"Pass rate: {summary['pass_rate']:.1%}")
    print(f"JSON report saved to: {Path(args.output)}")
    print(f"Readable Markdown report saved to: {markdown_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
