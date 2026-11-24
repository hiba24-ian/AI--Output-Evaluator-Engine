"""Unit tests for the rule-based evaluator."""

import json
import tempfile
import unittest
from pathlib import Path

from src.evaluator import LLMEvaluator


class EvaluatorTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.input_path = Path(self.temp_dir.name) / "cases.json"
        self.cases = [
            {
                "id": "PASS",
                "prompt": "Explain AI",
                "model_output": "AI systems learn from data",
                "expected_keywords": ["learn", "data"],
                "min_length": 10,
            },
            {
                "id": "FAIL_KEYWORDS",
                "prompt": "Explain AI",
                "model_output": "AI systems learn",
                "expected_keywords": ["learn", "data"],
                "min_length": 5,
            },
            {
                "id": "FAIL_LENGTH",
                "prompt": "Say hi",
                "model_output": "hi",
                "expected_keywords": ["hi"],
                "min_length": 5,
            },
            {
                "id": "NO_KEYWORDS",
                "prompt": "Say hello",
                "model_output": "hello there",
                "expected_keywords": [],
                "min_length": 1,
            },
        ]
        self.input_path.write_text(json.dumps(self.cases), encoding="utf-8")

    def test_evaluation_summary_and_report(self):
        evaluator = LLMEvaluator(self.input_path)
        report_path = Path(self.temp_dir.name) / "reports" / "result.json"
        summary = evaluator.run_evaluations(report_path)
        self.assertEqual(summary["total_tests"], 4)
        self.assertEqual(summary["passed_tests"], 2)
        self.assertEqual(summary["failed_tests"], 2)
        self.assertTrue(report_path.exists())
        self.assertEqual(json.loads(report_path.read_text())["pass_rate"], 0.5)

    def test_keyword_matching_is_case_insensitive(self):
        evaluator = LLMEvaluator(self.input_path)
        result = evaluator.evaluate_case(self.cases[0])
        self.assertEqual(result["keyword_coverage"], 1.0)
        self.assertTrue(result["passed"])

    def test_keyword_threshold_boundary(self):
        case = {
            "id": "THRESHOLD_BOUNDARY",
            "prompt": "Explain AI",
            "model_output": "AI learns from data",
            "expected_keywords": ["learns", "data", "safety"],
            "min_length": 1,
        }
        passing_evaluator = LLMEvaluator(self.input_path, keyword_threshold=0.66)
        failing_evaluator = LLMEvaluator(self.input_path, keyword_threshold=0.67)

        passing_result = passing_evaluator.evaluate_case(case)
        failing_result = failing_evaluator.evaluate_case(case)

        self.assertEqual(passing_result["keyword_coverage"], 0.667)
        self.assertTrue(passing_result["checks"]["keyword_coverage"])
        self.assertFalse(failing_result["checks"]["keyword_coverage"])
        self.assertFalse(failing_result["passed"])

    def test_invalid_threshold_is_rejected(self):
        with self.assertRaises(ValueError):
            LLMEvaluator(self.input_path, keyword_threshold=1.5)

    def test_boolean_threshold_is_rejected(self):
        with self.assertRaises(TypeError):
            LLMEvaluator(self.input_path, keyword_threshold=True)

    def test_invalid_case_is_rejected(self):
        bad_path = Path(self.temp_dir.name) / "bad.json"
        bad_path.write_text(json.dumps([{"id": "broken"}]), encoding="utf-8")
        with self.assertRaises(ValueError):
            LLMEvaluator(bad_path)

    def test_empty_test_suite_has_zero_pass_rate(self):
        empty_path = Path(self.temp_dir.name) / "empty.json"
        empty_path.write_text("[]", encoding="utf-8")
        summary = LLMEvaluator(empty_path).run_evaluations(
            Path(self.temp_dir.name) / "empty-report.json"
        )
        self.assertEqual(summary["pass_rate"], 0.0)
        self.assertEqual(summary["total_tests"], 0)


if __name__ == "__main__":
    unittest.main()
