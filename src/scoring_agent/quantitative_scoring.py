"""Scores the operational evaluation metrics (Cost, Latency, Throughput) directly
from Model Catalog data instead of via an LLM judge -- these are objective facts
recorded per model, not something a judge should guess."""

from __future__ import annotations

from llm_advisor.analyzer_schema import EvaluationMetric
from model_catalog.models import ModelRecord
from model_qualification.qualifier import _estimate_monthly_cost_usd, _parse_context_window_tokens
from scoring_agent.schema import MetricScore

QUANTITATIVE_METRICS = {EvaluationMetric.COST, EvaluationMetric.LATENCY, EvaluationMetric.THROUGHPUT}


def _normalize(raw_values: dict[str, float], higher_is_better: bool) -> dict[str, float]:
    """Min-max normalize raw values across models to a 0-100 score."""
    if not raw_values:
        return {}

    lo, hi = min(raw_values.values()), max(raw_values.values())
    if hi == lo:
        return {name: 100.0 for name in raw_values}

    return {
        name: 100.0 * ((value - lo) / (hi - lo) if higher_is_better else (hi - value) / (hi - lo))
        for name, value in raw_values.items()
    }


def compute_quantitative_scores(
    metrics: list[EvaluationMetric],
    qualified_model_names: list[str],
    catalog_models: list[ModelRecord],
    context_window_need: str,
    monthly_request_volume: float,
) -> dict[str, list[MetricScore]]:
    """Compute Cost/Latency/Throughput scores for each qualified model, normalized
    relative to the other qualified models (higher score is always better)."""
    requested = [m for m in metrics if m in QUANTITATIVE_METRICS]
    if not requested:
        return {}

    models_by_name = {m.model_name: m for m in catalog_models}
    qualified_records = [
        models_by_name[name] for name in qualified_model_names if name in models_by_name
    ]

    scores_by_model: dict[str, list[MetricScore]] = {name: [] for name in qualified_model_names}

    if EvaluationMetric.COST in requested:
        required_context_window = _parse_context_window_tokens(context_window_need) or 0
        costs = {
            record.model_name: _estimate_monthly_cost_usd(
                record, required_context_window, monthly_request_volume
            )
            for record in qualified_records
        }
        for name, score in _normalize(costs, higher_is_better=False).items():
            scores_by_model[name].append(
                MetricScore(
                    metric=EvaluationMetric.COST.value,
                    score=score,
                    rationale=f"Estimated monthly cost: ${costs[name]:,.2f}",
                    raw_value=costs[name],
                )
            )

    if EvaluationMetric.LATENCY in requested:
        latencies = {record.model_name: record.latency_ms for record in qualified_records}
        for name, score in _normalize(latencies, higher_is_better=False).items():
            scores_by_model[name].append(
                MetricScore(
                    metric=EvaluationMetric.LATENCY.value,
                    score=score,
                    rationale=f"Average latency: {latencies[name]:,.0f} ms",
                )
            )

    if EvaluationMetric.THROUGHPUT in requested:
        throughputs = {record.model_name: record.throughput_rps for record in qualified_records}
        for name, score in _normalize(throughputs, higher_is_better=True).items():
            scores_by_model[name].append(
                MetricScore(
                    metric=EvaluationMetric.THROUGHPUT.value,
                    score=score,
                    rationale=f"Throughput: {throughputs[name]:,.1f} req/s",
                )
            )

    return scores_by_model
