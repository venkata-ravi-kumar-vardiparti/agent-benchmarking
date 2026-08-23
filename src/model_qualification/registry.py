"""The organization's approved model registry.

Approval is a governance decision (Organization Decision -> Approved Model)
recorded per catalog entry. This module is the single place that answers
"is this model in the approved registry?" so the qualifier logic doesn't
need to know where approval decisions are sourced from.
"""

from __future__ import annotations

from model_catalog.models import ModelRecord


def approved_model_ids(models: list[ModelRecord]) -> set[str]:
    """Return the catalog ids of models in the organization's approved registry."""
    return {m.id for m in models if m.approved}


def is_approved(model: ModelRecord, models: list[ModelRecord]) -> bool:
    """Check whether `model` is present in the organization's approved model registry."""
    return model.id in approved_model_ids(models)
