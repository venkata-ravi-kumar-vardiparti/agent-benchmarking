"""Benchmark Engine Deep Dive.

Runs after Model Qualification:
1. Select the test case markdown file that best matches the scenario.
2. Run each qualified model against every test case in that file.
3. Record the model name, original question, original (expected) answer, and
   the model's own answer for each run.
"""

from __future__ import annotations

from llm_advisor.analyzer_schema import ScenarioEvaluationBlueprint
from model_qualification.schema import ModelQualificationResult

from benchmark_engine.agents import BenchmarkModelRoster, run_test_case
from benchmark_engine.schema import BenchmarkResult
from benchmark_engine.test_case_loader import load_test_cases, select_test_case_file


def run_benchmark_deep_dive(
    blueprint: ScenarioEvaluationBlueprint,
    qualification: ModelQualificationResult,
) -> list[BenchmarkResult]:
    """Evaluate every qualified model against the scenario's test cases."""
    test_case_file = select_test_case_file(
        blueprint.business_context.industry.value,
        blueprint.business_context.use_case,
    )
    test_cases = load_test_cases(test_case_file)

    roster = BenchmarkModelRoster.from_qualified_models(qualification.qualified_models)

    return [
        run_test_case(model_name, test_case)
        for model_name in roster.model_names
        for test_case in test_cases
    ]
