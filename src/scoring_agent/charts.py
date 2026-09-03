"""Altair chart builders for visualizing Scoring Agent + Sustainability Engine results."""

from __future__ import annotations

import altair as alt
import pandas as pd

from scoring_agent.quantitative_scoring import QUANTITATIVE_METRICS
from scoring_agent.schema import ScoringResult

# See formatting._RELATIVE_METRIC_NAMES -- same relative-vs-absolute distinction,
# surfaced here as a tooltip field since a bar chart has no room for a footnote.
_RELATIVE_METRIC_NAMES = {m.value for m in QUANTITATIVE_METRICS}


def _basis(metric_name: str) -> str:
    if metric_name == "Overall":
        return "Mixed (relative + absolute)"
    if metric_name in _RELATIVE_METRIC_NAMES:
        return "Relative to other qualified models"
    return "Absolute (judged)"

# Validated categorical palette (see dataviz skill references/palette.md) --
# fixed hue order, never cycled.
_CATEGORICAL_PALETTE = [
    "#2a78d6",  # blue
    "#eb6834",  # orange
    "#1baf7a",  # aqua
    "#eda100",  # yellow
    "#e87ba4",  # magenta
    "#008300",  # green
    "#4a3aa7",  # violet
    "#e34948",  # red
]

_INK = "#52514e"
_AXIS_LINE = "#c3c2b7"
_GRID = "#e1e0d9"


def _axis(title: str | None, **kwargs) -> alt.Axis:
    return alt.Axis(
        title=title,
        gridColor=_GRID,
        domainColor=_AXIS_LINE,
        tickColor=_AXIS_LINE,
        labelColor=_INK,
        titleColor=_INK,
        **kwargs,
    )


def _color_encoding(model_names: list[str]) -> alt.Color:
    return alt.Color(
        "model:N",
        title="Model",
        sort=model_names,
        scale=alt.Scale(domain=model_names, range=_CATEGORICAL_PALETTE[: len(model_names)]),
        legend=alt.Legend(title="Model") if len(model_names) > 1 else None,
    )


def build_metric_score_chart(result: ScoringResult) -> alt.Chart | None:
    """Grouped bar chart comparing every qualified model's per-metric and overall scores (0-100)."""
    model_names = [card.model_name for card in result.scorecards]
    rows = [
        {
            "model": card.model_name,
            "metric": metric_score.metric,
            "score": metric_score.score,
            "basis": _basis(metric_score.metric),
        }
        for card in result.scorecards
        for metric_score in card.metric_scores
    ]
    rows += [
        {"model": card.model_name, "metric": "Overall", "score": card.overall_score, "basis": _basis("Overall")}
        for card in result.scorecards
    ]
    if not rows:
        return None

    return (
        alt.Chart(pd.DataFrame(rows))
        .mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3)
        .encode(
            x=alt.X("metric:N", title=None, axis=_axis(None, labelAngle=-30)),
            xOffset=alt.XOffset("model:N", sort=model_names),
            y=alt.Y("score:Q", scale=alt.Scale(domain=[0, 100]), axis=_axis("Score (0-100)")),
            color=_color_encoding(model_names),
            tooltip=[
                alt.Tooltip("model:N", title="Model"),
                alt.Tooltip("metric:N", title="Metric"),
                alt.Tooltip("score:Q", title="Score", format=".0f"),
                alt.Tooltip("basis:N", title="Basis"),
            ],
        )
        .properties(height=320, title="Model Scoring — per-metric and overall scores")
        .configure_view(strokeWidth=0)
    )


def build_sustainability_ratio_chart(result: ScoringResult) -> alt.Chart | None:
    """Grouped bar chart comparing every qualified model's carbon and energy ratios."""
    model_names = [card.model_name for card in result.scorecards]
    rows = [
        {"model": card.model_name, "ratio": label, "value": value}
        for card in result.scorecards
        for label, value in (("Carbon Ratio", card.carbon_score), ("Energy Ratio", card.energy_score))
    ]
    if not rows:
        return None

    return (
        alt.Chart(pd.DataFrame(rows))
        .mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3)
        .encode(
            x=alt.X("ratio:N", title=None, axis=_axis(None)),
            xOffset=alt.XOffset("model:N", sort=model_names),
            y=alt.Y("value:Q", axis=_axis("Quality delivered per unit")),
            color=_color_encoding(model_names),
            tooltip=[
                alt.Tooltip("model:N", title="Model"),
                alt.Tooltip("ratio:N", title="Ratio"),
                alt.Tooltip("value:Q", title="Value", format=".2f"),
            ],
        )
        .properties(height=240, title="Carbon Ratio vs. Energy Ratio")
        .configure_view(strokeWidth=0)
    )
