"""Presentation helpers for rendering Justification Agent results."""

from justification_agent.schema import JustificationResult


def format_justifications(result: JustificationResult) -> str:
    if not result.justifications:
        return "**Score Justifications**\n\nNo qualified models were available to justify."

    sections = ["**Score Justifications**"]
    for j in result.justifications:
        sections.append(f"**{j.model_name}** (Overall: {j.overall_score:.0f}/100)\n\n{j.justification}")

    return "\n\n".join(sections)
