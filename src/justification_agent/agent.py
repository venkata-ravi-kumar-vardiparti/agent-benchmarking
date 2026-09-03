"""Agent construction and invocation for the Justification Agent.

Turns a model's per-metric scores (and the rationale already attached to each
one by the Scoring Agent) into one coherent, plain-language explanation of why
it received its overall score.
"""

from __future__ import annotations

from dataclasses import dataclass

from agents import Agent, Runner, set_default_openai_client, trace
from openai import AsyncOpenAI

from llm_advisor.analyzer_schema import SustainabilityWeightage
from llm_advisor.config import get_settings
from scoring_agent.schema import ModelScoreCard

INSTRUCTIONS = """You explain LLM benchmark scores to a business decision-maker who is \
choosing which model to deploy for a specific use case.

You are given one candidate model's overall score, its per-metric scores (each with a short \
rationale already computed by an evaluation pipeline), its carbon ratio and energy ratio \
(quality delivered per unit of carbon emitted / energy consumed -- higher is more sustainable), \
and the user's chosen sustainability weightage (Low, Medium, High, or Very High). Do not \
re-score or contradict the given numbers -- synthesize them into a short, clear explanation \
(2-4 sentences) of why this model landed at its overall score: call out its strongest and \
weakest metrics by name, note any notable cost/quality tradeoff, and factor in the carbon and \
energy ratios in proportion to the sustainability weightage (mention sustainability more \
prominently the higher the weightage, and de-emphasize it when the weightage is Low). Write \
for a business audience, not an ML audience. Do not invent facts that are not supported by the \
given metric rationales."""


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


def _format_score_card(card: ModelScoreCard, sustainability_weightage: SustainabilityWeightage) -> str:
    metric_lines = "\n".join(
        f"- {ms.metric}: {ms.score:.0f}/100 -- {ms.rationale}" for ms in card.metric_scores
    )
    return (
        f"Model: {card.model_name}\n"
        f"Overall score: {card.overall_score:.0f}/100\n"
        f"Per-metric scores:\n{metric_lines}\n"
        f"Carbon ratio: {card.carbon_score:.2f}\n"
        f"Energy ratio: {card.energy_score:.2f}\n"
        f"Sustainability weightage: {sustainability_weightage.value}"
    )


def justify_score(
    justification_model_name: str,
    card: ModelScoreCard,
    sustainability_weightage: SustainabilityWeightage = SustainabilityWeightage.MEDIUM,
) -> str:
    """Generate a plain-language explanation for one model's scorecard."""
    if not card.metric_scores:
        return "No metric scores were available to justify this model's ranking."

    prompt = (
        f"{_format_score_card(card, sustainability_weightage)}\n\n"
        "Explain why this model received this overall score."
    )

    with trace("justification_agent"):
        agent = build_justification_agent(justification_model_name)
        result = Runner.run_sync(agent, prompt)
        return result.final_output
