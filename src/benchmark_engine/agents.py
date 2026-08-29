"""Agent construction and invocation for the Benchmark Engine Deep Dive.

For every qualified model, a dedicated OpenAI Agent SDK agent is built using
that model's name and run against each test case question.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from agents import Agent, Runner, set_default_openai_client, trace
from openai import AsyncOpenAI

from benchmark_engine.schema import BenchmarkResult, TestCase
from llm_advisor.config import get_settings
from model_qualification.schema import QualifiedModel

INSTRUCTIONS = """You are the candidate LLM being evaluated in a benchmark test. \
Answer the question directly and concisely, exactly as you would in a real \
production deployment for this use case. Do not mention that you are being \
benchmarked."""


settings = get_settings()
client = AsyncOpenAI(
    api_key=settings.openai_api_key,
    base_url="https://us.api.openai.com/v1",
)

set_default_openai_client(client)


@dataclass(frozen=True)
class BenchmarkModelRoster:
    """The qualified model names the Benchmark Engine will build agents for."""

    model_names: list[str] = field(default_factory=list)

    @classmethod
    def from_qualified_models(cls, qualified_models: list[QualifiedModel]) -> "BenchmarkModelRoster":
        return cls(model_names=[m.model_name for m in qualified_models])


def build_agent(model_name: str) -> Agent:
    return Agent(
        name=f"Benchmark Candidate ({model_name})",
        instructions=INSTRUCTIONS,
        model=model_name,
    )


def run_test_case(model_name: str, test_case: TestCase) -> BenchmarkResult:
    with trace("benchmark_engine_agent"):
        agent = build_agent(model_name)
        result = Runner.run_sync(agent, test_case.question)

    return BenchmarkResult(
        model_name=model_name,
        test_question=test_case.question,
        original_test_response=test_case.expected_answer,
        model_response=result.final_output,
    )
