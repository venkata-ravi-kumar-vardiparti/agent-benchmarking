"""Agent construction and invocation for LLM capability analysis."""

from agents import Agent, AgentOutputSchema, Runner,trace

from llm_advisor.analyzer_schema import ScenarioEvaluationBlueprint

INSTRUCTIONS = """You are an LLM solution architect for enterprise AI deployments. \
Given a business scenario (industry, business use case, expected monthly request \
volume, and monthly budget ceiling), produce a structured evaluation blueprint that \
downstream tooling will use to select and benchmark candidate LLMs.

You must populate every field of the schema:
- business_context: the industry and a concise restatement of the use case.
- workload_profile: classify the workload family, task type, and complexity, \
  taking into account the reasoning depth and multimodality the use case implies.
- required_capabilities: choose only from the fixed capability list defined by the \
  schema's enum (e.g. Reasoning, Long Context, Structured Output, Function Calling, \
  Tool Calling, RAG Support, PII Handling, Multimodal, OCR, Code Generation, \
  Low Latency, Private Deployment, Fine Tuning, Agent Execution). Never invent a \
  capability name outside this fixed list; if none of the values fit, omit it.
- benchmark_plan: pick relevant evaluation metrics from the schema's fixed metric \
  enum, and assign integer scoring weights across quality, governance, cost, and \
  latency that sum to 100, reflecting the priorities implied by the volume and \
  budget ceiling (e.g. tight budgets or high volume should weight cost/latency \
  more heavily).
- governance_requirements: list applicable regulations and allowed deployment \
  regions using only the enum values defined by the schema, based on the industry's \
  typical compliance obligations and any data residency implications. Use an empty \
  list if nothing applies.
- financial_constraints: set monthly_budget_usd to the provided budget ceiling.

Every enum field must use one of the exact values defined in the schema for that \
field -- never a synonym or a value from a different field's enum."""


def build_agent(model: str) -> Agent:
    return Agent(
        name="LLM Capability Advisor",
        instructions=INSTRUCTIONS,
        model=model,
        output_type=AgentOutputSchema(ScenarioEvaluationBlueprint, strict_json_schema=False),
    )


def analyze(
    industry: str,
    use_case: str,
    volume: float,
    budget: float,
    model: str,
) -> ScenarioEvaluationBlueprint:
    with trace("analyzer_agent"):
        agent = build_agent(model)
        prompt = (
        f"Industry: {industry}\n"
        f"Business use case: {use_case}\n"
        f"Expected monthly request volume: {volume}\n"
        f"Monthly budget ceiling: {budget}\n\n"
        "Analyze this scenario and determine the required capabilities of the LLM."
        )
        result = Runner.run_sync(agent, prompt)
        return result.final_output
