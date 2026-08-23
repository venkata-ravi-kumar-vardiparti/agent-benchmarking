"""Presentation helpers for turning agent output into chat-friendly text."""

from llm_advisor.analyzer_schema import ScenarioEvaluationBlueprint


def format_analysis(blueprint: ScenarioEvaluationBlueprint) -> str:
    ctx = blueprint.business_context
    workload = blueprint.workload_profile
    benchmark = blueprint.benchmark_plan
    governance = blueprint.governance_requirements
    financial = blueprint.financial_constraints

    capabilities = (
        "\n".join(f"- {c.value}" for c in blueprint.required_capabilities)
        or "- None specified"
    )
    metrics = (
        "\n".join(f"- {m.value}" for m in benchmark.evaluation_metrics)
        or "- None specified"
    )
    weights = (
        "\n".join(f"- {k}: {v}%" for k, v in benchmark.weights.items())
        or "- None specified"
    )
    regulations = ", ".join(r.value for r in governance.regulations) or "None"
    allowed_regions = ", ".join(r.value for r in governance.allowed_regions) or "Any"

    parts = [
        "**Business context**",
        f"- Industry: {ctx.industry.value}",
        f"- Use case: {ctx.use_case}",
        "\n**Workload profile**",
        f"- Workload family: {workload.workload_family.value}",
        f"- Task type: {workload.task_type.value}",
        f"- Complexity: {workload.complexity.value}",
        f"- Context window: {workload.context_window}",
        "\n**Required LLM capabilities**",
        capabilities,
        "\n**Benchmark plan**",
        "Evaluation metrics:",
        metrics,
        "Scoring weights:",
        weights,
        "\n**Governance requirements**",
        f"- Regulations: {regulations}",
        f"- Allowed regions: {allowed_regions}",
        "\n**Financial constraints**",
        f"- Monthly budget: ${financial.monthly_budget_usd:,.2f}",
    ]
    return "\n".join(parts)
