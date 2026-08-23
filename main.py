import pprint

from llm_advisor.agent import analyze
from llm_advisor.config import get_settings
from llm_advisor.formatting import format_analysis
from model_catalog.repository import list_models
from model_qualification import qualify_models
from model_qualification.formatting import format_qualification


def main():
    print("Hello from agent-benchmarking!")
    industry="insurance"
    use_case="enrollment file validations"
    volume="100"
    budget="100"
    model_name="gpt-4o-mini"
    try:
        blueprint = analyze(industry, use_case, volume, budget, model_name)
        qualification = qualify_models(blueprint.required_capabilities, list_models())
        response_text = (
                format_analysis(blueprint) + "\n\n" + format_qualification(qualification)
        )
        pprint.pprint(response_text)
    except Exception as exc:  # noqa: BLE001
        response_text = f"Analysis failed: {exc}"


if __name__ == "__main__":
    main()
