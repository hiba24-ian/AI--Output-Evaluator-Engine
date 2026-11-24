"""Transparent, rule-based evaluation of model outputs.

This module checks expected keyword coverage and minimum output length.
It does not assess semantic correctness or use an LLM.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.utils import load_json_file, save_json_file


class LLMEvaluator:
    """Evaluate a JSON collection of test cases using explicit rules."""

    def __init__(self, data_path: str | Path, keyword_threshold: float = 0.8):
        if isinstance(keyword_threshold, bool) or not isinstance(keyword_threshold, (int, float)):
            raise TypeError("keyword_threshold must be a number (not a boolean).")
        if not 0.0 <= keyword_threshold <= 1.0:
            raise ValueError("keyword_threshold must be between 0.0 and 1.0.")
        self.data_path = Path(data_path)
        self.keyword_threshold = float(keyword_threshold)
        loaded = load_json_file(self.data_path)
        if not isinstance(loaded, list):
            raise ValueError("The test-case JSON file must contain a list.")
        self.test_cases = loaded
        for index, case in enumerate(self.test_cases):
            self._validate_case(case, index)

    @staticmethod
    def _validate_case(case: Any, index: int) -> None:
        if not isinstance(case, dict):
            raise ValueError(f"Test case at index {index} must be a JSON object.")
        required = ("id", "prompt", "model_output", "expected_keywords", "min_length")
        missing = [field for field in required if field not in case]
        if missing:
            raise ValueError(f"Test case at index {index} is missing: {', '.join(missing)}.")
        for field in ("id", "prompt", "model_output"):
            if not isinstance(case[field], str):
                raise ValueError(f"Test case {index}: '{field}' must be a string.")
        if not isinstance(case["expected_keywords"], list) or not all(
            isinstance(word, str) and word.strip()
            for word in case["expected_keywords"]
        ):
            raise ValueError(
                f"Test case {index}: 'expected_keywords' must be a list of non-empty strings."
            )
        if isinstance(case["min_length"], bool) or not isinstance(case["min_length"], int):
            raise ValueError(f"Test case {index}: 'min_length' must be a non-negative integer.")
        if case["min_length"] < 0:
            raise ValueError(f"Test case {index}: 'min_length' cannot be negative.")

    def evaluate_case(self, case: dict[str, Any]) -> dict[str, Any]:
        """Return a deterministic evaluation result for one validated case."""
        self._validate_case(case, 0)
        output = case["model_output"]
        output_folded = output.casefold()

        # Keep the first spelling of each keyword and report repeated entries.
        unique_keywords = []
        seen_keywords = set()
        duplicate_keywords = []
        for word in case["expected_keywords"]:
            normalized = word.casefold()
            if normalized in seen_keywords:
                duplicate_keywords.append(word)
            else:
                seen_keywords.add(normalized)
                unique_keywords.append(word)

        found = [word for word in unique_keywords if word.casefold() in output_folded]
        missing = [word for word in unique_keywords if word.casefold() not in output_folded]
        score = len(found) / len(unique_keywords) if unique_keywords else 1.0
        length_passed = len(output) >= case["min_length"]
        keyword_passed = score >= self.keyword_threshold
        checks = {
            "keyword_coverage": keyword_passed,
            "minimum_length": length_passed,
        }
        return {
            "id": case["id"],
            "prompt": case["prompt"],
            "passed": all(checks.values()),
            "keyword_coverage": round(score, 3),
            "keyword_threshold": self.keyword_threshold,
            "matched_keywords": found,
            "missing_keywords": missing,
            "duplicate_expected_keywords": duplicate_keywords,
            "output_length": len(output),
            "minimum_length": case["min_length"],
            "checks": checks,
            "failure_reasons": [
                name for name, passed in checks.items() if not passed
            ],
        }

    def run_evaluations(self, output_report_path: str | Path) -> dict[str, Any]:
        """Evaluate all cases, save a JSON report, and return its contents."""
        results = [self.evaluate_case(case) for case in self.test_cases]
        total = len(results)
        passed = sum(result["passed"] for result in results)
        summary = {
            "evaluation_method": "rule_based_keyword_and_length_checks",
            "semantic_accuracy_assessed": False,
            "total_tests": total,
            "passed_tests": passed,
            "failed_tests": total - passed,
            "pass_rate": round(passed / total, 3) if total else 0.0,
            "keyword_threshold": self.keyword_threshold,
            "details": results,
        }
        save_json_file(summary, output_report_path)
        return summary
