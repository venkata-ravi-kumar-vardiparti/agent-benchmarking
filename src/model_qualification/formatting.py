"""Presentation helpers for rendering Model Qualification results."""

import json

from model_qualification.schema import ModelQualificationResult


def format_qualification(result: ModelQualificationResult) -> str:
    qualified = (
        "\n".join(f"- {m.model_name}" for m in result.qualified_models)
        or "- None"
    )
    disqualified = (
        "\n".join(
            f"- {m.model_name}\n" + "\n".join(f"  - {reason}" for reason in m.reasons)
            for m in result.disqualified_models
        )
        or "- None"
    )

    parts = [
        "**Model Qualification Analysis**",
        "\nQualified Models:",
        qualified,
        "\nDisqualified Models:",
        disqualified,
        "\n```json",
        json.dumps(result.to_dict(), indent=2),
        "```",
    ]
    return "\n".join(parts)
