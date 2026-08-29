"""Scoring Agent orchestrator.

Runs after the Benchmark Engine Deep Dive: scores every qualified model on
each evaluation metric from the scenario's `BenchmarkPlan`, plus cost, and
produces a ranked scorecard per model.

Quality-of-response metrics (Accuracy, Faithfulness, Reasoning Quality, etc.)
are judged by an LLM-as-judge agent against the benchmark test cases. The
operational metrics Cost, Latency, and Throughput are computed directly from
Model Catalog data instead, since those are objective facts, not something an
LLM should guess.
"""

from __future__ import annotations

from benchmark_engine.schema import BenchmarkResult
from llm_advisor.analyzer_schema import EvaluationMetric, ScenarioEvaluationBlueprint
from model_catalog.repository import list_models
from model_qualification.schema import ModelQualificationResult

from scoring_agent.judge_agent import ScoringAgentSettings, score_model_quality
from scoring_agent.quantitative_scoring import QUANTITATIVE_METRICS, compute_quantitative_scores
from scoring_agent.schema import ModelScoreCard, ScoringResult


def score_benchmark_results(
    blueprint: ScenarioEvaluationBlueprint,
    qualification: ModelQualificationResult,
    benchmark_results: list[BenchmarkResult],
    scoring_settings: ScoringAgentSettings | None = None,
) -> ScoringResult:
    settings = scoring_settings or ScoringAgentSettings.default()

    qualified_model_names = [m.model_name for m in qualification.qualified_models]
    requested_metrics = list(dict.fromkeys([*blueprint.benchmark_plan.evaluation_metrics, EvaluationMetric.COST]))
    qualitative_metrics = [m for m in requested_metrics if m not in QUANTITATIVE_METRICS]

    quantitative_scores = compute_quantitative_scores(
        metrics=requested_metrics,
        qualified_model_names=qualified_model_names,
        catalog_models=list_models(),
        context_window_need=blueprint.workload_profile.context_window,
        monthly_request_volume=blueprint.business_context.monthly_request_volume,
    )

    results_by_model: dict[str, list[BenchmarkResult]] = {}
    for result in benchmark_results:
        results_by_model.setdefault(result.model_name, []).append(result)

    scorecards = []
    for model_name in qualified_model_names:
        metric_scores = list(
            score_model_quality(
                settings.judge_model_name,
                results_by_model.get(model_name, []),
                qualitative_metrics,
            )
        )
        metric_scores.extend(quantitative_scores.get(model_name, []))

        overall_score = (
            sum(s.score for s in metric_scores) / len(metric_scores) if metric_scores else 0.0
        )
        scorecards.append(
            ModelScoreCard(model_name=model_name, metric_scores=metric_scores, overall_score=overall_score)
        )

    scorecards.sort(key=lambda card: card.overall_score, reverse=True)
    return ScoringResult(scorecards=scorecards)
