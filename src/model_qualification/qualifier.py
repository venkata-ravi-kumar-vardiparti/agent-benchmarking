"""Model Qualification step.

Runs after the Scenario Intelligence Agent and before the Benchmark Engine:
filters the Model Catalog down to models that are approved by the
organization and support every capability the scenario requires.
"""

from __future__ import annotations

import re

from llm_advisor.analyzer_schema import Capability
from model_catalog.models import ModelRecord

from model_qualification.registry import approved_model_ids
from model_qualification.schema import DisqualifiedModel, ModelQualificationResult, QualifiedModel

_CONTEXT_WINDOW_PATTERN = re.compile(r"([\d,]+(?:\.\d+)?)\s*(k|m)?", re.IGNORECASE)


def _parse_context_window_tokens(value: str) -> int | None:
    """Parse a free-text context window requirement (e.g. "128k tokens") into a token count.

    The Scenario Intelligence Agent emits `context_window` as free text, so this
    tolerates plain numbers, thousands separators, and k/m suffixes. Returns
    None if no number can be found.
    """
    match = _CONTEXT_WINDOW_PATTERN.search(value)
    if not match:
        return None

    number = float(match.group(1).replace(",", ""))
    suffix = (match.group(2) or "").lower()
    if suffix == "k":
        number *= 1_000
    elif suffix == "m":
        number *= 1_000_000

    return int(number)


def qualify_models(
    required_capabilities: list[Capability],
    catalog_models: list[ModelRecord],
    context_window_need: str,
) -> ModelQualificationResult:
    """Classify every model in the catalog as qualified or disqualified.

    A model is qualified only if it is present in the organization's approved
    model registry, supports every capability in `required_capabilities`, AND
    has a context window at least as large as `context_window_need`.
    """
    approved_ids = approved_model_ids(catalog_models)
    required_context_window = _parse_context_window_tokens(context_window_need)
    result = ModelQualificationResult()

    for model in catalog_models:
        reasons: list[str] = []

        if model.id not in approved_ids:
            reasons.append("Model is not present in approved model registry")

        missing_capabilities = [c for c in required_capabilities if c not in model.capabilities]
        reasons.extend(f"Missing capability: {c.value}" for c in missing_capabilities)

        if required_context_window is not None and model.context_window < required_context_window:
            reasons.append(
                "Context window too small: requires at least "
                f"{required_context_window} tokens, has {model.context_window}"
            )

        if reasons:
            result.disqualified_models.append(
                DisqualifiedModel(model_name=model.model_name, reasons=reasons)
            )
        else:
            result.qualified_models.append(QualifiedModel(model_name=model.model_name))

    return result
