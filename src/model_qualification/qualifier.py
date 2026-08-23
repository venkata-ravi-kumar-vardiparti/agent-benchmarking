"""Model Qualification step.

Runs after the Scenario Intelligence Agent and before the Benchmark Engine:
filters the Model Catalog down to models that are approved by the
organization and support every capability the scenario requires.
"""

from __future__ import annotations

from llm_advisor.analyzer_schema import Capability
from model_catalog.models import ModelRecord

from model_qualification.registry import approved_model_ids
from model_qualification.schema import DisqualifiedModel, ModelQualificationResult, QualifiedModel


def qualify_models(
    required_capabilities: list[Capability],
    catalog_models: list[ModelRecord],
) -> ModelQualificationResult:
    """Classify every model in the catalog as qualified or disqualified.

    A model is qualified only if it is present in the organization's approved
    model registry AND supports every capability in `required_capabilities`.
    """
    approved_ids = approved_model_ids(catalog_models)
    result = ModelQualificationResult()

    for model in catalog_models:
        reasons: list[str] = []

        if model.id not in approved_ids:
            reasons.append("Model is not present in approved model registry")

        missing_capabilities = [c for c in required_capabilities if c not in model.capabilities]
        reasons.extend(f"Missing capability: {c.value}" for c in missing_capabilities)

        if reasons:
            result.disqualified_models.append(
                DisqualifiedModel(model_name=model.model_name, reasons=reasons)
            )
        else:
            result.qualified_models.append(QualifiedModel(model_name=model.model_name))

    return result
