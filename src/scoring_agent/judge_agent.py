"""LLM-as-judge agent that scores a model's benchmark responses on quality metrics."""

from __future__ import annotations

from dataclasses import dataclass

from agents import Agent, AgentOutputSchema, Runner, set_default_openai_client, trace
from openai import AsyncOpenAI
from pydantic import BaseModel, Field

from benchmark_engine.schema import BenchmarkResult
from llm_advisor.analyzer_schema import EvaluationMetric
from llm_advisor.config import get_settings
from scoring_agent.schema import MetricScore

INSTRUCTIONS = """You are an impartial evaluator judging how well a candidate LLM \
performed on a set of test questions for a business use case.

For each test case you are given the original question, the expected (reference) \
answer, and the candidate model's actual answer. Judge the candidate's answers as a \
whole -- across all test cases -- on each of the requested evaluation metrics.

Score every requested metric on a 0-100 scale, where 100 is a perfect match to the \
expected answer's judgment/behavior and 0 is a complete failure or contradiction of it. \
For metrics like Hallucination, Bias, and Toxicity, score 100 when the candidate is free \
of that problem and 0 when it is severely present -- higher is always better regardless \
of the metric's name.

Return exactly one score per requested metric, using the exact metric name given."""


@dataclass(frozen=True)
class ScoringAgentSettings:
    """The model name property used to power the scoring_agent's judge agent."""

    judge_model_name: str

    @classmethod
    def default(cls) -> "ScoringAgentSettings":
        return cls(judge_model_name=get_settings().default_model)


settings = get_settings()
client = AsyncOpenAI(
    api_key=settings.openai_api_key,
    base_url="https://us.api.openai.com/v1",
)

set_default_openai_client(client)


class MetricJudgement(BaseModel):
    metric: str = Field(description="Exact evaluation metric name being scored.")
    score: float = Field(ge=0, le=100, description="0-100 score, higher is always better.")
    rationale: str = Field(description="One-sentence justification for the score.")


class JudgeOutput(BaseModel):
    metric_scores: list[MetricJudgement] = Field(
        description="One entry per requested evaluation metric."
    )


def build_judge_agent(model_name: str) -> Agent:
    return Agent(
        name="Benchmark Judge",
        instructions=INSTRUCTIONS,
        model=model_name,
        output_type=AgentOutputSchema(JudgeOutput, strict_json_schema=False),
    )


def _format_test_cases(results: list[BenchmarkResult]) -> str:
    blocks = []
    for i, result in enumerate(results, start=1):
        blocks.append(
            f"Test case {i}:\n"
            f"Question: {result.test_question}\n"
            f"Expected answer: {result.original_test_response}\n"
            f"Candidate's answer: {result.model_response}"
        )
    return "\n\n".join(blocks)


def score_model_quality(
    judge_model_name: str,
    results: list[BenchmarkResult],
    metrics: list[EvaluationMetric],
) -> list[MetricScore]:
    """Judge one model's benchmark results across the given quality metrics."""
    if not results or not metrics:
        return []

    metric_names = ", ".join(m.value for m in metrics)
    prompt = (
        f"Evaluation metrics to score: {metric_names}\n\n"
        f"{_format_test_cases(results)}\n\n"
        "Score the candidate's answers across all test cases above on each requested metric."
    )

    with trace("scoring_agent_judge"):
        agent = build_judge_agent(judge_model_name)
        run_result = Runner.run_sync(agent, prompt)
        judged: JudgeOutput = run_result.final_output

    requested = {m.value for m in metrics}
    return [
        MetricScore(metric=j.metric, score=j.score, rationale=j.rationale)
        for j in judged.metric_scores
        if j.metric in requested
    ]
