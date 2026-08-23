"""CRUD operations for the model catalog, backed by SQLite."""

import sqlite3
import uuid
from datetime import datetime, timezone

from model_catalog.db import get_connection, init_db
from model_catalog.models import DuplicateModelError, ModelRecord

_COLUMNS = [
    "model_name",
    "provider",
    "version",
    "context_window",
    "multimodal_support",
    "tool_calling",
    "fine_tuning_support",
    "capabilities",
    "approved",
    "input_token_cost_usd_per_million",
    "output_token_cost_usd_per_million",
    "latency_ms",
    "throughput_rps",
    "availability_pct",
    "region_availability",
    "data_residency",
    "certifications",
]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def list_models() -> list[ModelRecord]:
    init_db()
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM models ORDER BY provider, model_name, version").fetchall()
    return [ModelRecord.from_row(dict(row)) for row in rows]


def get_model(model_id: str) -> ModelRecord | None:
    init_db()
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM models WHERE id = ?", (model_id,)).fetchone()
    return ModelRecord.from_row(dict(row)) if row else None


def create_model(record: ModelRecord) -> ModelRecord:
    init_db()
    record.id = uuid.uuid4().hex
    record.created_at = _now()
    record.updated_at = record.created_at
    row = record.to_row()

    columns = ["id", *_COLUMNS, "created_at", "updated_at"]
    placeholders = ", ".join("?" for _ in columns)
    values = [row[col] for col in columns]

    try:
        with get_connection() as conn:
            conn.execute(
                f"INSERT INTO models ({', '.join(columns)}) VALUES ({placeholders})",
                values,
            )
    except sqlite3.IntegrityError as exc:
        raise DuplicateModelError(
            f"A model already exists for provider={record.provider!r}, "
            f"model_name={record.model_name!r}, version={record.version!r}."
        ) from exc

    return record


def update_model(model_id: str, record: ModelRecord) -> ModelRecord:
    init_db()
    existing = get_model(model_id)
    if existing is None:
        raise ValueError(f"No model found with id={model_id!r}")

    record.id = existing.id
    record.created_at = existing.created_at
    record.updated_at = _now()
    row = record.to_row()

    assignments = ", ".join(f"{col} = ?" for col in _COLUMNS)
    values = [row[col] for col in _COLUMNS] + [row["updated_at"], model_id]

    try:
        with get_connection() as conn:
            conn.execute(
                f"UPDATE models SET {assignments}, updated_at = ? WHERE id = ?",
                values,
            )
    except sqlite3.IntegrityError as exc:
        raise DuplicateModelError(
            f"Another model already exists for provider={record.provider!r}, "
            f"model_name={record.model_name!r}, version={record.version!r}."
        ) from exc

    return record
