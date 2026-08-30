"""Data model for a catalog entry."""

from __future__ import annotations

from dataclasses import dataclass, field

from llm_advisor.analyzer_schema import Capability


class DuplicateModelError(Exception):
    """Raised when a (provider, model_name, version) combination already exists."""


def _split_list(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def _join_list(values: list[str]) -> str:
    return ", ".join(values)


@dataclass
class ModelRecord:
    # Model Details
    model_name: str
    provider: str
    version: str
    context_window: int
    multimodal_support: bool
    tool_calling: bool
    fine_tuning_support: bool

    # Model Capabilities
    capabilities: list[Capability] = field(default_factory=list)

    # Organization Decision
    approved: bool = True

    # Commercial Data
    input_token_cost_usd_per_million: float = 0.0
    output_token_cost_usd_per_million: float = 0.0

    # Operational Metrics
    latency_ms: float = 0.0
    throughput_rps: float = 0.0
    availability_pct: float = 0.0

    # Governance Data
    region_availability: list[str] = field(default_factory=list)
    data_residency: str = ""
    certifications: list[str] = field(default_factory=list)

    # Sustainability Data
    energy_factor: float = 0.0
    carbon_intensity: float = 0.0

    # Bookkeeping
    id: str = ""
    created_at: str = ""
    updated_at: str = ""

    def to_row(self) -> dict:
        return {
            "id": self.id,
            "model_name": self.model_name,
            "provider": self.provider,
            "version": self.version,
            "context_window": self.context_window,
            "multimodal_support": int(self.multimodal_support),
            "tool_calling": int(self.tool_calling),
            "fine_tuning_support": int(self.fine_tuning_support),
            "capabilities": _join_list([c.value for c in self.capabilities]),
            "approved": int(self.approved),
            "input_token_cost_usd_per_million": self.input_token_cost_usd_per_million,
            "output_token_cost_usd_per_million": self.output_token_cost_usd_per_million,
            "latency_ms": self.latency_ms,
            "throughput_rps": self.throughput_rps,
            "availability_pct": self.availability_pct,
            "region_availability": _join_list(self.region_availability),
            "data_residency": self.data_residency,
            "certifications": _join_list(self.certifications),
            "energy_factor": self.energy_factor,
            "carbon_intensity": self.carbon_intensity,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_row(cls, row: dict) -> "ModelRecord":
        return cls(
            id=row["id"],
            model_name=row["model_name"],
            provider=row["provider"],
            version=row["version"],
            context_window=row["context_window"],
            multimodal_support=bool(row["multimodal_support"]),
            tool_calling=bool(row["tool_calling"]),
            fine_tuning_support=bool(row["fine_tuning_support"]),
            capabilities=[Capability(v) for v in _split_list(row["capabilities"])],
            approved=bool(row["approved"]),
            input_token_cost_usd_per_million=row["input_token_cost_usd_per_million"],
            output_token_cost_usd_per_million=row["output_token_cost_usd_per_million"],
            latency_ms=row["latency_ms"],
            throughput_rps=row["throughput_rps"],
            availability_pct=row["availability_pct"],
            region_availability=_split_list(row["region_availability"]),
            data_residency=row["data_residency"],
            certifications=_split_list(row["certifications"]),
            energy_factor=row["energy_factor"],
            carbon_intensity=row["carbon_intensity"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )
