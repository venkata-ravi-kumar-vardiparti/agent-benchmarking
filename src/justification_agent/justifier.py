"""Justification Agent orchestrator.

Runs after the Scoring Agent: generates a plain-language justification for
every qualified model's overall score.
"""

from __future__ import annotations

from scoring_agent.schema import ScoringResult

from justification_agent.agent import JustificationAgentSettings, justify_score
from justification_agent.schema import JustificationResult, ModelJustification


def generate_justifications(
    scoring_result: ScoringResult,
    justification_settings: JustificationAgentSettings | None = None,
) -> JustificationResult:
    settings = justification_settings or JustificationAgentSettings.default()

    justifications = [
        ModelJustification(
            model_name=card.model_name,
            overall_score=card.overall_score,
            justification=justify_score(settings.justification_model_name, card),
        )
        for card in scoring_result.scorecards
    ]

    return JustificationResult(justifications=justifications)
