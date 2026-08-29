import pprint

from benchmark_engine import NoMatchingTestCasesError, run_benchmark_deep_dive
from justification_agent import format_justifications, generate_justifications
from llm_advisor.agent import analyze
from llm_advisor.config import get_settings
from llm_advisor.formatting import format_analysis
from model_catalog.repository import list_models
from model_qualification import qualify_models
from model_qualification.formatting import format_qualification
from scoring_agent import format_scores, score_benchmark_results


def main():
    print("Hello from agent-benchmarking!")
    industry="insurance"
    use_case="enrollment file validations"
    volume="100"
    budget="100"
    model_name="gpt-4o-mini"
    try:
        blueprint = analyze(industry, use_case, volume, budget, model_name)
        qualification = qualify_models(
            blueprint.required_capabilities,
            list_models(),
            blueprint.workload_profile.context_window,
            blueprint.business_context.monthly_request_volume,
            blueprint.financial_constraints.monthly_budget_usd,
        )
        response_text = (
                format_analysis(blueprint) + "\n\n" + format_qualification(qualification)
        )

        if qualification.qualified_models:
            try:
                benchmark_results = run_benchmark_deep_dive(blueprint, qualification)
            except NoMatchingTestCasesError as exc:
                response_text += (
                    f"\n\n**Benchmark Engine Deep Dive skipped:** {exc} Add a test case "
                    "markdown file for this industry to `src/test_cases/` to enable it."
                )
            else:
                scoring_result = score_benchmark_results(blueprint, qualification, benchmark_results)
                response_text += "\n\n" + format_scores(scoring_result)

                justification_result = generate_justifications(scoring_result)
                response_text += "\n\n" + format_justifications(justification_result)

        pprint.pprint(response_text)
    except Exception as exc:  # noqa: BLE001
        response_text = f"Analysis failed: {exc}"


if __name__ == "__main__":
    main()
