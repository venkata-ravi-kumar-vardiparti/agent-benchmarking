# LLM Capability Advisor & Model Catalog

A Streamlit app with two tabs:

- **Capability Advisor** — collects a business scenario (industry, business
  use case, expected request volume, and budget ceiling) and uses an
  [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/) agent to
  determine the required capabilities of the LLM for that scenario. The agent
  only runs once all four inputs are provided.
- **Model Catalog** — the source of truth for LLM model metadata (model
  details, commercial data, operational metrics, and governance data), backed
  by a local SQLite file. Lets you add new models and update existing ones.

## Setup

```bash
uv sync
```

Create a `.env` file in the project root with:

```
OPENAI_API_KEY=your-key-here
OPENAI_MODEL=gpt-4o-mini
```

`OPENAI_MODEL` is optional and just sets the default shown in the sidebar's
model field; it can also be changed per-session in the UI.

## Run

```bash
uv run streamlit run app.py
```

On the **Capability Advisor** tab, fill in the industry, business use case,
volume of requests, and budget ceiling in the sidebar, then click **Analyze**.
The agent's capability analysis is shown in the chat window.

On the **Model Catalog** tab, add new models or edit existing ones via the
forms; the catalog is listed in a table above them. Data is stored in a local
SQLite file, `model_catalog.db`, created at the repo root on first use
(override the location with the `MODEL_CATALOG_DB_PATH` env var). This file
is git-ignored — it's a local runtime data store, not source-controlled
content.

## Project structure

```
app.py                          # entry point for `streamlit run app.py`; owns
                                 # st.set_page_config and the two-tab layout
src/llm_advisor/                # Capability Advisor
    config.py                   # env/config loading (.env, defaults)
    analyzer_schema.py          # pydantic output schema (ScenarioEvaluationBlueprint)
    agent.py                    # Agents SDK agent definition + analyze()
    formatting.py               # renders agent output as chat markdown
    ui.py                       # sidebar form, chat, gating logic
src/model_catalog/              # Model Catalog & Metadata Repository
    models.py                   # ModelRecord dataclass
    db.py                       # SQLite connection + schema
    repository.py                # create/get/list/update CRUD functions
    ui.py                        # catalog table + add/update forms
```

Both packages are installed as editable packages (`uv sync` handles this via
the `[build-system]`/`[tool.hatch.build]` config in `pyproject.toml`), so
their modules can be imported normally from `app.py` or elsewhere.
