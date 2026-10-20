"""Stable interface for replacing the rule engine with an edge model."""
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class VitalFeatures:
    heart_rate: float
    spo2: float
    temperature: float


class RiskModel(Protocol):
    def predict(self, features: VitalFeatures) -> str:
        """Return NORMAL, ATTENTION, or HIGH_RISK."""


class RuleBasedModel:
    def predict(self, features: VitalFeatures) -> str:
        if features.spo2 < 92 or features.heart_rate > 130 or features.heart_rate < 45 or features.temperature > 39:
            return "HIGH_RISK"
        return "NORMAL"
