"""SQLite connection and schema management for the model catalog."""

import os
import sqlite3
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = Path(os.getenv("MODEL_CATALOG_DB_PATH", str(_REPO_ROOT / "model_catalog.db")))

_SCHEMA = """
CREATE TABLE IF NOT EXISTS models (
    id TEXT PRIMARY KEY,
    model_name TEXT NOT NULL,
    provider TEXT NOT NULL,
    version TEXT NOT NULL,
    context_window INTEGER NOT NULL,
    multimodal_support INTEGER NOT NULL,
    tool_calling INTEGER NOT NULL,
    fine_tuning_support INTEGER NOT NULL,
    capabilities TEXT NOT NULL DEFAULT '',
    approved INTEGER NOT NULL DEFAULT 1,
    input_token_cost_usd_per_million REAL NOT NULL DEFAULT 0,
    output_token_cost_usd_per_million REAL NOT NULL DEFAULT 0,
    latency_ms REAL NOT NULL DEFAULT 0,
    throughput_rps REAL NOT NULL DEFAULT 0,
    availability_pct REAL NOT NULL DEFAULT 0,
    region_availability TEXT NOT NULL DEFAULT '',
    data_residency TEXT NOT NULL DEFAULT '',
    certifications TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    UNIQUE (provider, model_name, version)
);
"""

# Columns that were dropped from the schema and no longer have a home.
_OBSOLETE_COLUMNS = ["max_input_tokens", "max_output_tokens", "hosting_cost_usd_per_month"]


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _migrate(conn: sqlite3.Connection) -> None:
    """Bring an existing `models` table up to the current schema in place,
    preserving any rows that were already stored."""
    existing_columns = {row["name"] for row in conn.execute("PRAGMA table_info(models)")}
    if not existing_columns:
        return

    if "active" in existing_columns and "approved" not in existing_columns:
        conn.execute("ALTER TABLE models RENAME COLUMN active TO approved")
        existing_columns.discard("active")
        existing_columns.add("approved")

    if "capabilities" not in existing_columns:
        conn.execute("ALTER TABLE models ADD COLUMN capabilities TEXT NOT NULL DEFAULT ''")

    for column in _OBSOLETE_COLUMNS:
        if column in existing_columns:
            conn.execute(f"ALTER TABLE models DROP COLUMN {column}")


def init_db() -> None:
    with get_connection() as conn:
        conn.execute(_SCHEMA)
        _migrate(conn)
