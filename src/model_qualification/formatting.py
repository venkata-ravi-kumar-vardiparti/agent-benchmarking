"""Presentation helpers for rendering Model Qualification results."""

import json

from model_qualification.schema import ModelQualificationResult


def format_qualification(result: ModelQualificationResult) -> str:
    rows = [(m.model_name, "Qualified", "-") for m in result.qualified_models]
    rows += [
        (m.model_name, "Disqualified", "; ".join(m.reasons) or "-")
        for m in result.disqualified_models
    ]

    table_lines = ["| Model | Status | Reasons |", "| --- | --- | --- |"]
    if rows:
        table_lines += [f"| {model} | {status} | {reasons} |" for model, status, reasons in rows]
    else:
        table_lines.append("| - | - | - |")

    parts = [
        "**Model Qualification Analysis**",
        "\n".join(table_lines),
        # "\n```json",
        # json.dumps(result.to_dict(), indent=2),
        # "```",
    ]
    return "\n\n".join(parts)
