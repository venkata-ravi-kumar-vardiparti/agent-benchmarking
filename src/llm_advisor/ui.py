"""Streamlit chat UI for the LLM Capability Advisor."""

import streamlit as st

from llm_advisor.agent import analyze
from llm_advisor.config import get_settings
from llm_advisor.formatting import format_analysis
from model_catalog.repository import list_models
from model_qualification import qualify_models
from model_qualification.formatting import format_qualification


_INPUT_KEYS = ("advisor_industry", "advisor_use_case", "advisor_volume", "advisor_budget", "advisor_model_name")


def _clear_advisor_state() -> None:
    st.session_state.messages = []
    for key in _INPUT_KEYS:
        st.session_state.pop(key, None)


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
        submitted = st.button("Analyze")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

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
        f"**Budget ceiling:** ${budget:,.2f} / month"
    )
    st.session_state.messages.append({"role": "user", "content": user_summary})
    with st.chat_message("user"):
        st.markdown(user_summary)

    with st.chat_message("assistant"):
        with st.spinner("Analyzing scenario..."):
            try:
                blueprint = analyze(industry, use_case, volume, budget, model_name)
                qualification = qualify_models(blueprint.required_capabilities, list_models())
                response_text = (
                    format_analysis(blueprint) + "\n\n" + format_qualification(qualification)
                )
            except Exception as exc:  # noqa: BLE001
                response_text = f"Analysis failed: {exc}"
        st.markdown(response_text)
    st.session_state.messages.append({"role": "assistant", "content": response_text})
