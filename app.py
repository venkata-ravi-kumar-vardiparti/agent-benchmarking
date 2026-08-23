"""Entry point for `streamlit run app.py`."""

import streamlit as st

from llm_advisor.ui import render_advisor_tab
from model_catalog.ui import render_catalog_tab

st.set_page_config(page_title="LLM Advisor & Model Catalog", page_icon="🤖", layout="wide")

advisor_tab, catalog_tab = st.tabs(["Capability Advisor", "Model Catalog"])

with advisor_tab:
    render_advisor_tab()

with catalog_tab:
    render_catalog_tab()
