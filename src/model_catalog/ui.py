"""Streamlit UI for managing the Model Catalog."""

import streamlit as st

from llm_advisor.analyzer_schema import Capability
from model_catalog.models import DuplicateModelError, ModelRecord
from model_catalog.repository import create_model, get_model, list_models, update_model

_CAPABILITY_OPTIONS = [c.value for c in Capability]


def _model_label(m: ModelRecord) -> str:
    return f"{m.provider} / {m.model_name} / {m.version}"


def _render_model_fields(prefix: str, defaults: ModelRecord | None) -> ModelRecord:
    d = defaults

    st.markdown("**Model Details**")
    c1, c2, c3 = st.columns(3)
    model_name = c1.text_input("Model name", value=d.model_name if d else "", key=f"{prefix}_model_name")
    provider = c2.text_input("Provider", value=d.provider if d else "", key=f"{prefix}_provider")
    version = c3.text_input("Version", value=d.version if d else "", key=f"{prefix}_version")

    c1, c2, c3, c4 = st.columns(4)
    context_window = c1.number_input(
        "Context window (tokens)", min_value=0, step=1000,
        value=d.context_window if d else 0, key=f"{prefix}_context_window",
    )
    multimodal_support = c2.checkbox(
        "Multimodal support", value=d.multimodal_support if d else False, key=f"{prefix}_multimodal"
    )
    tool_calling = c3.checkbox(
        "Tool calling", value=d.tool_calling if d else False, key=f"{prefix}_tool_calling"
    )
    fine_tuning_support = c4.checkbox(
        "Fine tuning support", value=d.fine_tuning_support if d else False, key=f"{prefix}_fine_tuning"
    )

    st.markdown("**Model Capabilities**")
    capabilities = st.multiselect(
        "Capabilities",
        options=_CAPABILITY_OPTIONS,
        default=[c.value for c in d.capabilities] if d else [],
        key=f"{prefix}_capabilities",
    )

    st.markdown("**Organization Decision**")
    approved = st.checkbox("Approved model", value=d.approved if d else True, key=f"{prefix}_approved")

    st.markdown("**Commercial Data**")
    c1, c2 = st.columns(2)
    input_token_cost = c1.number_input(
        "Input token cost (USD / 1M tokens)", min_value=0.0, step=0.01,
        value=d.input_token_cost_usd_per_million if d else 0.0, key=f"{prefix}_input_cost",
    )
    output_token_cost = c2.number_input(
        "Output token cost (USD / 1M tokens)", min_value=0.0, step=0.01,
        value=d.output_token_cost_usd_per_million if d else 0.0, key=f"{prefix}_output_cost",
    )

    st.markdown("**Operational Metrics**")
    c1, c2, c3 = st.columns(3)
    latency_ms = c1.number_input(
        "Latency (ms, avg)", min_value=0.0, step=10.0,
        value=d.latency_ms if d else 0.0, key=f"{prefix}_latency",
    )
    throughput_rps = c2.number_input(
        "Throughput (requests/sec)", min_value=0.0, step=1.0,
        value=d.throughput_rps if d else 0.0, key=f"{prefix}_throughput",
    )
    availability_pct = c3.number_input(
        "Availability (%)", min_value=0.0, max_value=100.0, step=0.1,
        value=d.availability_pct if d else 0.0, key=f"{prefix}_availability",
    )

    st.markdown("**Governance Data**")
    region_availability = st.text_input(
        "Region availability (comma-separated, e.g. US, EU, APAC)",
        value=", ".join(d.region_availability) if d else "",
        key=f"{prefix}_regions",
    )
    data_residency = st.text_input(
        "Data residency", value=d.data_residency if d else "", key=f"{prefix}_residency"
    )
    certifications = st.text_input(
        "Certifications (comma-separated, e.g. SOC2, ISO27001, HIPAA)",
        value=", ".join(d.certifications) if d else "",
        key=f"{prefix}_certifications",
    )

    return ModelRecord(
        model_name=model_name.strip(),
        provider=provider.strip(),
        version=version.strip(),
        context_window=int(context_window),
        multimodal_support=multimodal_support,
        tool_calling=tool_calling,
        fine_tuning_support=fine_tuning_support,
        capabilities=[Capability(c) for c in capabilities],
        approved=approved,
        input_token_cost_usd_per_million=input_token_cost,
        output_token_cost_usd_per_million=output_token_cost,
        latency_ms=latency_ms,
        throughput_rps=throughput_rps,
        availability_pct=availability_pct,
        region_availability=[r.strip() for r in region_availability.split(",") if r.strip()],
        data_residency=data_residency.strip(),
        certifications=[c.strip() for c in certifications.split(",") if c.strip()],
    )


def _validate(record: ModelRecord) -> list[str]:
    missing = []
    if not record.model_name:
        missing.append("model name")
    if not record.provider:
        missing.append("provider")
    if not record.version:
        missing.append("version")
    return missing


def _render_catalog_table(models: list[ModelRecord]) -> None:
    if not models:
        st.info("No models in the catalog yet. Add one below.")
        return

    st.dataframe(
        [
            {
                "Provider": m.provider,
                "Model": m.model_name,
                "Version": m.version,
                "Context window": m.context_window,
                "Multimodal": m.multimodal_support,
                "Tool calling": m.tool_calling,
                "Fine tuning": m.fine_tuning_support,
                "Capabilities": ", ".join(c.value for c in m.capabilities),
                "Approved": m.approved,
                "Input $/1M": m.input_token_cost_usd_per_million,
                "Output $/1M": m.output_token_cost_usd_per_million,
                "Latency (ms)": m.latency_ms,
                "Throughput (rps)": m.throughput_rps,
                "Availability %": m.availability_pct,
                "Regions": ", ".join(m.region_availability),
                "Data residency": m.data_residency,
                "Certifications": ", ".join(m.certifications),
            }
            for m in models
        ],
        use_container_width=True,
        hide_index=True,
    )


def render_catalog_tab() -> None:
    st.header("Model Catalog")
    st.caption(
        "Source of truth for every LLM's details, capabilities, commercial terms, "
        "operational metrics, and governance attributes."
    )

    models = list_models()
    _render_catalog_table(models)

    with st.expander("Add new model", expanded=not models):
        with st.form("add_model_form"):
            new_record = _render_model_fields("add", defaults=None)
            submitted = st.form_submit_button("Create model")

        if submitted:
            missing = _validate(new_record)
            if missing:
                st.warning("Please provide: " + ", ".join(missing))
            else:
                try:
                    create_model(new_record)
                    st.success(f"Created {_model_label(new_record)}.")
                    st.rerun()
                except DuplicateModelError as exc:
                    st.error(str(exc))

    with st.expander("Update existing model", expanded=False):
        if not models:
            st.info("No models to update yet.")
            return

        options = {m.id: _model_label(m) for m in models}
        selected_id = st.selectbox(
            "Select a model to edit",
            options=list(options.keys()),
            format_func=lambda model_id: options[model_id],
            key="edit_model_select",
        )
        selected = get_model(selected_id)

        with st.form(f"edit_model_form_{selected_id}"):
            updated_record = _render_model_fields(f"edit_{selected_id}", defaults=selected)
            submitted = st.form_submit_button("Save changes")

        if submitted:
            missing = _validate(updated_record)
            if missing:
                st.warning("Please provide: " + ", ".join(missing))
            else:
                try:
                    update_model(selected_id, updated_record)
                    st.success(f"Updated {_model_label(updated_record)}.")
                    st.rerun()
                except DuplicateModelError as exc:
                    st.error(str(exc))
