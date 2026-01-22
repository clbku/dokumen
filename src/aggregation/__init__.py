"""Aggregation package for Multi-Agent Debate."""

from src.aggregation.debate_orchestrator import (
    DebateConfig,
    DebateOrchestrator,
)
from src.aggregation.export import (
    export_sdd,
    QualityGateError,
)

__all__ = [
    "DebateConfig",
    "DebateOrchestrator",
    "export_sdd",
    "QualityGateError",
]
