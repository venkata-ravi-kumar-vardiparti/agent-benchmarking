"""Presentation helpers for rendering Scoring Agent results."""

from scoring_agent.quantitative_scoring import QUANTITATIVE_METRICS
from scoring_agent.schema import ScoringResult

_COLUMN_TITLES = {"Cost": "Cost ($/mo)"}

# Cost/Latency/Throughput are computed from Model Catalog data and normalized
# against the *other qualified models in this run* -- a 100 means "best of this
# set," not an absolute guarantee. Every other metric is judged independently
# by the LLM judge on an absolute 0-100 scale. Flagging the relative ones with
# "†" keeps that distinction visible in the table itself, not just a caption
# someone can miss.
_RELATIVE_METRIC_NAMES = {m.value for m in QUANTITATIVE_METRICS}


def format_scores(result: ScoringResult) -> str:
    if not result.scorecards:
        return "**Model Scoring**\n\nNo qualified models were available to score."

    metric_names: list[str] = []
    seen: set[str] = set()
    for card in result.scorecards:
        for metric_score in card.metric_scores:
            if metric_score.metric not in seen:
                seen.add(metric_score.metric)
                metric_names.append(metric_score.metric)

    def _heading(name: str) -> str:
        title = _COLUMN_TITLES.get(name, name)
        return f"{title} †" if name in _RELATIVE_METRIC_NAMES else title

    header = ["Model", *(_heading(name) for name in metric_names), "Overall", "Carbon Ratio", "Energy Ratio"]
    table_lines = [
        "| " + " | ".join(header) + " |",
        "| " + " | ".join(["---"] * len(header)) + " |",
    ]
    for card in result.scorecards:
        scores_by_metric = {ms.metric: ms for ms in card.metric_scores}
        row = [card.model_name]
        for name in metric_names:
            metric_score = scores_by_metric.get(name)
            if metric_score is None:
                row.append("-")
            elif name == "Cost" and metric_score.raw_value is not None:
                row.append(f"${metric_score.raw_value:,.2f}")
            else:
                row.append(f"{metric_score.score:.0f}")
        row.append(f"{card.overall_score:.0f}")
        row.append(f"{card.carbon_score:.2f}")
        row.append(f"{card.energy_score:.2f}")
        table_lines.append("| " + " | ".join(row) + " |")

    note = (
        "† **Relative** score/value, normalized against only the other models "
        "qualified in this run (100 = best of this set, not an absolute "
        "guarantee). Unmarked metrics are **absolute** 0-100 judgments from the "
        "LLM judge, independent of the other qualified models. **Overall** "
        "blends both kinds of score together."
    )

    return "\n\n".join(["**Model Scoring — Benchmark Deep Dive**", "\n".join(table_lines), note])
