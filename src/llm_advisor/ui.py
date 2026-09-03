"""Streamlit chat UI for the LLM Capability Advisor."""

import streamlit as st

from benchmark_engine import NoMatchingTestCasesError, run_benchmark_deep_dive
from justification_agent import format_justifications, generate_justifications
from llm_advisor.agent import analyze
from llm_advisor.analyzer_schema import SustainabilityWeightage
from llm_advisor.config import get_settings
from llm_advisor.formatting import format_analysis
from llm_advisor.report_export import build_pdf_report
from model_catalog.repository import list_models
from model_qualification import qualify_models
from model_qualification.formatting import format_qualification
from scoring_agent import (
    build_metric_score_chart,
    build_sustainability_ratio_chart,
    format_scores,
    score_benchmark_results,
)
from scoring_agent.schema import ScoringResult
from sustainability_engine import apply_sustainability_scoring


_INPUT_KEYS = (
    "advisor_industry",
    "advisor_use_case",
    "advisor_volume",
    "advisor_budget",
    "advisor_model_name",
    "advisor_sustainability_weightage",
)


def _clear_advisor_state() -> None:
    st.session_state.messages = []
    st.session_state.pop("last_report", None)
    for key in _INPUT_KEYS:
        st.session_state.pop(key, None)


def _render_score_charts(scoring_result: ScoringResult | None) -> None:
    if not scoring_result or not scoring_result.scorecards:
        return
    metric_chart = build_metric_score_chart(scoring_result)
    if metric_chart is not None:
        st.altair_chart(metric_chart, use_container_width=True)
    ratio_chart = build_sustainability_ratio_chart(scoring_result)
    if ratio_chart is not None:
        st.altair_chart(ratio_chart, use_container_width=True)


def _validate(industry: str, use_case: str, volume: float, budget: float) -> list[str]:
    missing = []
    if not industry.strip():
        missing.append("industry")
    if not use_case.strip():
        missing.append("business use case")
    if not volume or volume <= 0:
        missing.append("volume of requests")
    if not budget or budget <= 0:
        missing.append("budget ceiling")
    return missing


def render_advisor_tab() -> None:
    settings = get_settings()

    header_col, clear_col = st.columns([5, 1])
    with header_col:
        st.header("LLM Capability Advisor")
    with clear_col:
        st.button(
            "Clear",
            on_click=_clear_advisor_state,
            use_container_width=True,
            help="Clear the conversation history and reset all inputs on this tab.",
        )
    st.caption(
        "Provide the industry, business use case, expected request volume, and "
        "budget ceiling in the sidebar. The agent will analyze what capabilities "
        "an LLM needs for that scenario."
    )

    if "messages" not in st.session_state:
        st.session_state.messages = []

    with st.sidebar:
        st.header("Scenario details")
        industry = st.text_input("Industry", key="advisor_industry")
        use_case = st.text_area("Business use case", key="advisor_use_case")
        volume = st.number_input(
            "Volume of requests (per month)", min_value=0, step=100, key="advisor_volume"
        )
        budget = st.number_input(
            "Budget ceiling (USD/month)", min_value=0.0, step=100.0, key="advisor_budget"
        )
        model_name = st.text_input(
            "Model", value=settings.default_model, key="advisor_model_name"
        )
        sustainability_weightage = st.selectbox(
            "Sustainability weightage",
            options=list(SustainabilityWeightage),
            format_func=lambda level: level.value,
            index=1,
            key="advisor_sustainability_weightage",
            help="How heavily energy/carbon impact should factor into each model's final score.",
        )
        submitted = st.button("Analyze")

    for index, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            is_last_message = index == len(st.session_state.messages) - 1
            if is_last_message and message["role"] == "assistant" and st.session_state.get("last_report"):
                _render_score_charts(st.session_state.last_report.get("scoring_result"))
                st.download_button(
                    "📄 Export report as PDF",
                    data=build_pdf_report(**st.session_state.last_report),
                    file_name="llm_capability_advisor_report.pdf",
                    mime="application/pdf",
                    key=f"download_pdf_history_{index}",
                )

    if not submitted:
        return

    missing = _validate(industry, use_case, volume, budget)
    if missing:
        st.warning(
            "Please provide the following before analysis can start: "
            + ", ".join(missing)
        )
        return

    if not settings.openai_api_key:
        st.error(
            "OPENAI_API_KEY is not set. Add it to a .env file or your "
            "environment before running an analysis."
        )
        return

    user_summary = (
        f"**Industry:** {industry}\n\n"
        f"**Business use case:** {use_case}\n\n"
        f"**Volume of requests:** {volume} / month\n\n"
        f"**Budget ceiling:** ${budget:,.2f} / month\n\n"
        f"**Sustainability weightage:** {sustainability_weightage.value}"
    )
    st.session_state.messages.append({"role": "user", "content": user_summary})
    with st.chat_message("user"):
        st.markdown(user_summary)

    with st.chat_message("assistant"):
        response_text = ""
        scoring_result = None
        justification_result = None
        with st.status("Step 1/5 — Analyzing scenario...", expanded=True) as status:
            try:
                blueprint = analyze(
                    industry, use_case, volume, budget, model_name, sustainability_weightage
                )
                status.write("Scenario analysis complete.")

                status.update(label="Step 2/5 — Qualifying models against the catalog...")
                qualification = qualify_models(
                    blueprint.required_capabilities,
                    list_models(),
                    blueprint.workload_profile.context_window,
                    blueprint.business_context.monthly_request_volume,
                    blueprint.financial_constraints.monthly_budget_usd,
                )
                status.write(f"{len(qualification.qualified_models)} model(s) qualified.")

                response_text = (
                    format_analysis(blueprint) + "\n\n" + format_qualification(qualification)
                )
                st.session_state.last_report = {
                    "blueprint": blueprint,
                    "qualification": qualification,
                    "scoring_result": None,
                    "justification_result": None,
                }

                if qualification.qualified_models:
                    status.update(label="Step 3/5 — Running Benchmark Engine Deep Dive...")
                    try:
                        benchmark_results = run_benchmark_deep_dive(blueprint, qualification)
                    except NoMatchingTestCasesError as exc:
                        status.write(f"⚠️ {exc}")
                        status.update(
                            label="Pipeline complete (no test data for this use case).",
                            state="complete",
                            expanded=True,
                        )
                        response_text += (
                            "\n\n**⚠️ Benchmark Engine Deep Dive skipped:** "
                            f"{exc} Add a test case markdown file for this industry to "
                            "`src/test_cases/` to enable benchmarking and scoring for it."
                        )
                    else:
                        status.write(f"Ran {len(benchmark_results)} benchmark test case(s).")

                        status.update(label="Step 4/5 — Scoring qualified models...")
                        scoring_result = score_benchmark_results(
                            blueprint, qualification, benchmark_results
                        )
                        scoring_result = apply_sustainability_scoring(scoring_result)
                        status.write("Scoring complete.")

                        response_text += "\n\n" + format_scores(scoring_result)
                        st.session_state.last_report["scoring_result"] = scoring_result

                        status.update(label="Step 5/5 — Justifying model scores...")
                        justification_result = generate_justifications(
                            scoring_result, blueprint.sustainability_weightage
                        )
                        status.write("Justifications complete.")

                        response_text += "\n\n" + format_justifications(justification_result)
                        st.session_state.last_report["justification_result"] = justification_result

                        status.update(label="Pipeline complete.", state="complete", expanded=False)
                else:
                    status.write("No models qualified — skipping benchmarking, scoring, and justification.")
                    status.update(label="Pipeline complete.", state="complete", expanded=False)
            except Exception as exc:  # noqa: BLE001
                response_text = f"Analysis failed: {exc}"
                status.update(label="Pipeline failed.", state="error", expanded=True)
        st.markdown(response_text)
        _render_score_charts(scoring_result)
        if st.session_state.get("last_report"):
            st.download_button(
                "📄 Export report as PDF",
                data=build_pdf_report(**st.session_state.last_report),
                file_name="llm_capability_advisor_report.pdf",
                mime="application/pdf",
                key="download_pdf_fresh",
            )
    st.session_state.messages.append({"role": "assistant", "content": response_text})
