"""Agent construction and invocation for the Justification Agent.

Turns a model's per-metric scores (and the rationale already attached to each
one by the Scoring Agent) into one coherent, plain-language explanation of why
it received its overall score.
"""

from __future__ import annotations

from dataclasses import dataclass

from agents import Agent, Runner, set_default_openai_client, trace
from openai import AsyncOpenAI

from llm_advisor.config import get_settings
from scoring_agent.schema import ModelScoreCard

INSTRUCTIONS = """You explain LLM benchmark scores to a business decision-maker who is \
choosing which model to deploy for a specific use case.

You are given one candidate model's overall score and its per-metric scores, each with a \
short rationale already computed by an evaluation pipeline. Do not re-score or contradict \
the given numbers -- synthesize them into a short, clear explanation (2-4 sentences) of why \
this model landed at its overall score: call out its strongest and weakest metrics by name, \
and note any notable cost/quality tradeoff. Write for a business audience, not an ML audience. \
Do not invent facts that are not supported by the given metric rationales."""


@dataclass(frozen=True)
class JustificationAgentSettings:
    """The model name property used to power the Justification Agent."""

    justification_model_name: str

    @classmethod
    def default(cls) -> "JustificationAgentSettings":
        return cls(justification_model_name=get_settings().default_model)


settings = get_settings()
client = AsyncOpenAI(
    api_key=settings.openai_api_key,
    base_url="https://us.api.openai.com/v1",
)

set_default_openai_client(client)


def build_justification_agent(model_name: str) -> Agent:
    return Agent(
        name="Benchmark Score Justifier",
        instructions=INSTRUCTIONS,
        model=model_name,
    )


def _format_score_card(card: ModelScoreCard) -> str:
    metric_lines = "\n".join(
        f"- {ms.metric}: {ms.score:.0f}/100 -- {ms.rationale}" for ms in card.metric_scores
    )
    return (
        f"Model: {card.model_name}\n"
        f"Overall score: {card.overall_score:.0f}/100\n"
        f"Per-metric scores:\n{metric_lines}"
    )


def justify_score(justification_model_name: str, card: ModelScoreCard) -> str:
    """Generate a plain-language explanation for one model's scorecard."""
    if not card.metric_scores:
        return "No metric scores were available to justify this model's ranking."

    prompt = (
        f"{_format_score_card(card)}\n\n"
        "Explain why this model received this overall score."
    )

    with trace("justification_agent"):
        agent = build_justification_agent(justification_model_name)
        result = Runner.run_sync(agent, prompt)
        return result.final_output
