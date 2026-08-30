"""Sustainability Engine orchestrator.

Runs after the Scoring Agent and before the Justification Agent: estimates
each qualified model's energy consumption and carbon emissions from Model
Catalog data, then folds a sustainability score into its scorecard.
"""

from __future__ import annotations

from model_catalog.models import ModelRecord
from model_catalog.repository import list_models
from scoring_agent.schema import ScoringResult

SUSTAINABILITY_WEIGHT = 0.35


def _normalize(raw_values: dict[str, float]) -> dict[str, float]:
    """Min-max normalize raw values across models to a 0-100 score (higher is better)."""
    if not raw_values:
        return {}

    lo, hi = min(raw_values.values()), max(raw_values.values())
    if hi == lo:
        return {name: 100.0 for name in raw_values}

    return {name: 100.0 * (value - lo) / (hi - lo) for name, value in raw_values.items()}


def apply_sustainability_scoring(
    scoring_result: ScoringResult,
    catalog_models: list[ModelRecord] | None = None,
) -> ScoringResult:
    """Estimate energy consumption and carbon emissions for every scored model,
    and attach a 0-100 sustainability_score to each scorecard in place."""
    models_by_name = {m.model_name: m for m in (catalog_models or list_models())}

    quality_carbon_ratio: dict[str, float] = {}
    quality_energy_ratio: dict[str, float] = {}

    for card in scoring_result.scorecards:
        record = models_by_name.get(card.model_name)
        if record is None:
            continue

        # Step 1: Estimate Energy Consumption
        energy_wh = record.context_window * record.energy_factor
        # Step 2: Estimate Carbon Emissions
        co2e_g = energy_wh * record.carbon_intensity

        # Step 3: Quality/Carbon Ratio
        quality_carbon_ratio[card.model_name] = card.overall_score / co2e_g if co2e_g else 0.0
        # Step 5: Quality/Energy Ratio
        quality_energy_ratio[card.model_name] = card.overall_score / energy_wh if energy_wh else 0.0

    # Step 6: Normalize both ratios to 0-100 across the qualified models
    normalized_carbon_ratio = _normalize(quality_carbon_ratio)
    normalized_energy_ratio = _normalize(quality_energy_ratio)

    # Step 7 & 8: Compute sustainability_score and attach it to every scorecard
    for card in scoring_result.scorecards:
        carbon_score = normalized_carbon_ratio.get(card.model_name, 0.0)
        energy_score = normalized_energy_ratio.get(card.model_name, 0.0)
        card.sustainability_score = (
            SUSTAINABILITY_WEIGHT * carbon_score + SUSTAINABILITY_WEIGHT * energy_score
        )

    return scoring_result
