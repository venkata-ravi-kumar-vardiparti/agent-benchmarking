"""Sustainability Engine orchestrator.

Runs after the Scoring Agent and before the Justification Agent: estimates
each qualified model's energy consumption and carbon emissions from Model
Catalog data, then folds a sustainability score into its scorecard.
"""

from __future__ import annotations

from model_catalog.models import ModelRecord
from model_catalog.repository import list_models
from scoring_agent.schema import ScoringResult

CARBON_WEIGHT = 0.50
ENERGY_WEIGHT = 0.50


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
        print(f"record.context_window : {record.context_window}")
        print(f"record.energy_factor : {record.energy_factor}")
        # Step 2: Estimate Carbon Emissions
        co2e_g = energy_wh * record.carbon_intensity
        print(f"record.carbon_intensity :  {record.carbon_intensity}")
        print(f"energy_wh : {energy_wh}")
        print(f"co2e_g : {co2e_g}")
        # Step 3: Quality/Carbon Ratio
        quality_carbon_ratio[card.model_name] = card.overall_score / co2e_g if co2e_g else 0.0
        print(f"quality_carbon_ratio[card.model_name] : {quality_carbon_ratio[card.model_name]}" )
        # Step 5: Quality/Energy Ratio
        quality_energy_ratio[card.model_name] = card.overall_score / energy_wh if energy_wh else 0.0
        print(f"quality_energy_ratio[card.model_name] : {quality_energy_ratio[card.model_name]}" )

    # Step 6 & 7: Compute sustainability_score directly from the absolute
    # ratios (no normalization) and attach it to every scorecard
    for card in scoring_result.scorecards:
        card.carbon_score = quality_carbon_ratio.get(card.model_name, 0.0)
        card.energy_score = quality_energy_ratio.get(card.model_name, 0.0)
        card.sustainability_score = (
            100 * (CARBON_WEIGHT * card.carbon_score + ENERGY_WEIGHT * card.energy_score)
        )
    return scoring_result
