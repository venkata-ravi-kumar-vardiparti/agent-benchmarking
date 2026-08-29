"""Data model for the Justification Agent.

Runs after the Scoring Agent: explains, in plain language, why each qualified
model received the score it did.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ModelJustification:
    """A plain-language explanation of one model's overall score."""

    model_name: str
    overall_score: float
    justification: str

    def to_dict(self) -> dict:
        return {
            "model_name": self.model_name,
            "overall_score": self.overall_score,
            "justification": self.justification,
        }


@dataclass
class JustificationResult:
    """Every qualified model's score justification, in scorecard rank order."""

    justifications: list[ModelJustification] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {"justifications": [j.to_dict() for j in self.justifications]}
