"""Data model for the Scoring Agent.

Runs after the Benchmark Engine Deep Dive: scores every qualified model on
each evaluation metric from the `BenchmarkPlan`, plus cost, and produces a
ranked scorecard per model.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class MetricScore:
    """A single model's score (0-100) on a single evaluation metric."""

    metric: str
    score: float
    rationale: str = ""
    raw_value: float | None = None
    """The metric's actual measured value (e.g. USD/month for Cost), independent
    of the 0-100 normalized `score` used for ranking. None for judged metrics
    that have no natural unit."""

    def to_dict(self) -> dict:
        return {
            "metric": self.metric,
            "score": self.score,
            "rationale": self.rationale,
            "raw_value": self.raw_value,
        }


@dataclass
class ModelScoreCard:
    """A qualified model's scores across every requested metric, plus an overall score."""

    model_name: str
    metric_scores: list[MetricScore] = field(default_factory=list)
    overall_score: float = 0.0
    sustainability_score: float = 0.0
    carbon_score: float = 0.0
    energy_score: float = 0.0

    def to_dict(self) -> dict:
        return {
            "model_name": self.model_name,
            "metric_scores": [m.to_dict() for m in self.metric_scores],
            "overall_score": self.overall_score,
            "sustainability_score": self.sustainability_score,
            "carbon_score": self.carbon_score,
            "energy_score": self.energy_score,
        }


@dataclass
class ScoringResult:
    """Every qualified model's scorecard, ranked best-first by overall score."""

    scorecards: list[ModelScoreCard] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {"scorecards": [c.to_dict() for c in self.scorecards]}
