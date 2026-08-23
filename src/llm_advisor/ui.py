"""Streamlit chat UI for the LLM Capability Advisor."""

import streamlit as st

from llm_advisor.agent import analyze
from llm_advisor.config import get_settings
from llm_advisor.formatting import format_analysis


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

    st.header("LLM Capability Advisor")
    st.caption(
        "Provide the industry, business use case, expected request volume, and "
        "budget ceiling in the sidebar. The agent will analyze what capabilities "
        "an LLM needs for that scenario."
    )

    if "messages" not in st.session_state:
        st.session_state.messages = []

    with st.sidebar:
        st.header("Scenario details")
        industry = st.text_input("Industry")
        use_case = st.text_area("Business use case")
        volume = st.number_input("Volume of requests (per month)", min_value=0, step=100)
        budget = st.number_input("Budget ceiling (USD/month)", min_value=0.0, step=100.0)
        model_name = st.text_input("Model", value=settings.default_model)
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
                response_text = format_analysis(blueprint)
            except Exception as exc:  # noqa: BLE001
                response_text = f"Analysis failed: {exc}"
        st.markdown(response_text)
    st.session_state.messages.append({"role": "assistant", "content": response_text})
