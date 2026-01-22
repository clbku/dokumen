"""Quality Gate package for Phase 4 validation."""

from src.quality.gate import (
    QualityThreshold,
    QualityGateReport,
    validate_quality_gate,
    calculate_depth_score,
    check_technical_feasibility,
    find_logic_contradictions,
    detect_ai_speak,
)

__all__ = [
    "QualityThreshold",
    "QualityGateReport",
    "validate_quality_gate",
    "calculate_depth_score",
    "check_technical_feasibility",
    "find_logic_contradictions",
    "detect_ai_speak",
]
