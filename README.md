# AI Output Evaluator & QA Engine

A reproducible Python project that evaluates sample model outputs against explicit test-case requirements.

## What it checks

- **Expected keyword coverage:** checks whether required phrases appear in an output (case-insensitive).
- **Minimum output length:** checks whether an output meets a configured character minimum.
- **Pass/fail reporting:** records matched and missing keywords, individual check results, failure reasons, and the overall pass rate.
- **JSON input and output:** reads test cases from `data/test_cases.json` and writes a report to `reports/evaluation_results.json`.

## Important scope

This is a **rule-based baseline evaluator**. It does not call an LLM and does not determine whether an answer is factually correct, contextually appropriate, safe, or semantically equivalent to an expected answer. Keyword presence is a simple, explainable signal, not a complete measure of AI quality.

## Requirements

- Python 3.10 or newer
- No third-party packages required

## Run the evaluator

From the repository root:

```bash
python main.py
```

Optional input, output, and keyword threshold:

```bash
python main.py --input data/test_cases.json --output reports/evaluation_results.json --threshold 0.8
```

The threshold must be between `0.0` and `1.0`.

## Run tests

```bash
python -m unittest discover -s tests -v
```

The tests cover successful evaluations, missing keywords, insufficient length, case-insensitive matching, invalid test cases, threshold validation, and an empty test suite.

## Test-case format

Each item in the input JSON list must include:

- `id`: descriptive case identifier
- `prompt`: the task given to the model
- `model_output`: the response being checked
- `expected_keywords`: list of required phrases (an empty list skips keyword matching)
- `min_length`: minimum number of characters required

## Example report

The generated report includes total, passed, and failed test counts; pass rate; evaluation method; and per-case details. Reports are generated locally and are not committed automatically.

## Author

**Hiba Almamoori**
