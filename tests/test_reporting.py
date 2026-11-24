"""Tests for human-readable Markdown reports."""

import tempfile
import unittest
from pathlib import Path

from src.reporting import render_markdown_report, write_markdown_report


class MarkdownReportTests(unittest.TestCase):
    def setUp(self):
        self.summary = {
            "total_tests": 2,
            "passed_tests": 1,
            "failed_tests": 1,
            "pass_rate": 0.5,
            "keyword_threshold": 0.8,
            "details": [
                {
                    "id": "TC_PASS",
                    "prompt": "Explain AI",
                    "passed": True,
                    "keyword_coverage": 1.0,
                    "output_length": 42,
                    "matched_keywords": ["AI", "data"],
                    "missing_keywords": [],
                    "duplicate_expected_keywords": [],
                    "minimum_length": 10,
                    "failure_reasons": [],
                },
                {
                    "id": "TC_FAIL",
                    "prompt": "Explain safety",
                    "passed": False,
                    "keyword_coverage": 0.5,
                    "output_length": 8,
                    "matched_keywords": ["safety"],
                    "missing_keywords": ["privacy"],
                    "duplicate_expected_keywords": [],
                    "minimum_length": 20,
                    "failure_reasons": ["keyword_coverage", "minimum_length"],
                },
            ],
        }

    def test_report_contains_summary_and_case_details(self):
        report = render_markdown_report(self.summary)
        self.assertIn("# AI Output Evaluation Report", report)
        self.assertIn("| Pass rate | 50.0% |", report)
        self.assertIn("TC_PASS", report)
        self.assertIn("TC_FAIL", report)
        self.assertIn("keyword_coverage, minimum_length", report)
        self.assertIn("does not assess semantic correctness", report)

    def test_report_is_written_to_requested_path(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "reports" / "summary.md"
            returned_path = write_markdown_report(self.summary, path)
            self.assertEqual(returned_path, path)
            self.assertTrue(path.exists())
            self.assertIn("AI Output Evaluation Report", path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
