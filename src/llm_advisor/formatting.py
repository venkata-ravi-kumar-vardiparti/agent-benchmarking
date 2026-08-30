"""Presentation helpers for turning agent output into chat-friendly text."""

from llm_advisor.analyzer_schema import ScenarioEvaluationBlueprint


def format_analysis(blueprint: ScenarioEvaluationBlueprint) -> str:
    ctx = blueprint.business_context
    workload = blueprint.workload_profile
    benchmark = blueprint.benchmark_plan
    governance = blueprint.governance_requirements
    financial = blueprint.financial_constraints

    capabilities = ", ".join(c.value for c in blueprint.required_capabilities) or "None specified"
    metrics = ", ".join(m.value for m in benchmark.evaluation_metrics) or "None specified"
    weights = ", ".join(f"{k}: {v}%" for k, v in benchmark.weights.items()) or "None specified"
    regulations = ", ".join(r.value for r in governance.regulations) or "None"
    allowed_regions = ", ".join(r.value for r in governance.allowed_regions) or "Any"

    rows = [
        ("Industry", ctx.industry.value),
        ("Use case", ctx.use_case),
        ("Volume of requests (per month)", ctx.monthly_request_volume),
        ("Workload family", workload.workload_family.value),
        ("Task type", workload.task_type.value),
        ("Complexity", workload.complexity.value),
        ("Context window", workload.context_window),
        ("Required capabilities", capabilities),
        ("Evaluation metrics", metrics),
        ("Scoring weights", weights),
        ("Regulations", regulations),
        ("Allowed regions", allowed_regions),
        ("Monthly budget", f"${financial.monthly_budget_usd:,.2f}"),
        ("Sustainability weightage", blueprint.sustainability_weightage.value),
    ]

    table_lines = ["| Field | Value |", "| --- | --- |"]
    table_lines += [f"| {field} | {value} |" for field, value in rows]

    parts = ["**Scenario Evaluation Blueprint**", "\n".join(table_lines)]
    return "\n\n".join(parts)
