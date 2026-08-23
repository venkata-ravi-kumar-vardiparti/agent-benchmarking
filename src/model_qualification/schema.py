"""Result types produced by the Model Qualification step.

The Model Qualification step runs after the Scenario Intelligence Agent and
before the Benchmark Engine: it narrows the full Model Catalog down to the
models that are actually eligible to be benchmarked for a given scenario.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class QualifiedModel:
    model_name: str

    def to_dict(self) -> dict:
        return {"model_name": self.model_name}


@dataclass
class DisqualifiedModel:
    model_name: str
    reasons: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {"model_name": self.model_name, "reasons": list(self.reasons)}


@dataclass
class ModelQualificationResult:
    qualified_models: list[QualifiedModel] = field(default_factory=list)
    disqualified_models: list[DisqualifiedModel] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "qualified_models": [m.to_dict() for m in self.qualified_models],
            "disqualified_models": [m.to_dict() for m in self.disqualified_models],
        }
