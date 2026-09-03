"""Presentation helpers for rendering Scoring Agent results."""

from scoring_agent.schema import ScoringResult


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

    header = ["Model", *metric_names, "Overall", "Carbon Ratio", "Energy Ratio"]
    table_lines = [
        "| " + " | ".join(header) + " |",
        "| " + " | ".join(["---"] * len(header)) + " |",
    ]
    for card in result.scorecards:
        scores_by_metric = {ms.metric: ms.score for ms in card.metric_scores}
        row = [card.model_name]
        row += [f"{scores_by_metric[name]:.0f}" if name in scores_by_metric else "-" for name in metric_names]
        row.append(f"{card.overall_score:.0f}")
        row.append(f"{card.carbon_score:.2f}")
        row.append(f"{card.energy_score:.2f}")
        table_lines.append("| " + " | ".join(row) + " |")

    return "\n\n".join(["**Model Scoring — Benchmark Deep Dive**", "\n".join(table_lines)])
