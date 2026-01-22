"""
Quality Gate Scoring System for Phase 4.

Theo PRODUCT_VISION.md, mọi tài liệu PHẢI vượt qua Quality Gate thresholds:
- depth_score: ≥ 8.0/10
- edge_case_coverage: ≥ 5 scenarios
- technical_feasibility: 100%
- logic_consistency: 0 contradictions
- no_ai_speak: 0 instances
"""

from pydantic import BaseModel, Field, model_validator
from typing import List, Dict
from enum import Enum


class QualityThreshold(Enum):
    """Product Vision Quality Metrics."""
    DEPTH_SCORE_MIN = 8.0  # /10
    EDGE_CASE_MIN = 5     # scenarios
    TECHNICAL_FEASIBILITY = 100.0  # %
    LOGIC_CONSISTENCY = 0  # contradictions allowed
    NO_AI_SPEAK = 0  # instances allowed


class QualityGateReport(BaseModel):
    """Báo cáo chất lượng SDD."""
    depth_score: float = Field(..., ge=0, le=10, description="Độ sâu phân tích (0-10)")
    edge_case_coverage: int = Field(..., ge=0, description="Số edge cases được cover")
    technical_feasibility: float = Field(..., ge=0, le=100, description="% feasible solutions")
    logic_consistency: float = Field(..., ge=0, description="Số contradictions tìm thấy")
    ai_speak_instances: int = Field(..., ge=0, description="Số lần AI-speak detected")
    maturity_score: float = Field(0, ge=0, le=10, description="Overall maturity score")

    @model_validator(mode='before')
    @classmethod
    def calculate_maturity_score(cls, data: Dict) -> Dict:
        """
        Calculate overall maturity score based on Product Vision metrics.

        Formula:
        - Depth Score: 40% weight
        - Edge Case Coverage: 25% weight (normalized to 0-10)
        - Technical Feasibility: 20% weight
        - Logic Consistency: 10% weight (inverted)
        - No AI-Speak: 5% weight (inverted)
        """
        depth = data.get('depth_score', 0)
        edge_cases = data.get('edge_case_coverage', 0)
        feasibility = data.get('technical_feasibility', 0)
        contradictions = data.get('logic_consistency', 0)
        ai_speak = data.get('ai_speak_instances', 0)

        # Normalize edge cases to 0-10 scale (5+ cases = 10 points)
        edge_score = min(edge_cases / 5 * 10, 10)

        # Invert contradictions (0 = 10 points, 5+ = 0 points)
        consistency_score = max(10 - contradictions * 2, 0)

        # Invert AI-speak (0 = 5 points, 5+ = 0 points)
        clarity_score = max(5 - ai_speak, 0)

        # Calculate weighted score
        maturity = (
            depth * 0.40 +
            edge_score * 0.25 +
            feasibility / 10 * 0.20 +
            consistency_score * 0.10 +
            clarity_score * 0.05
        )

        data['maturity_score'] = round(maturity, 2)
        return data

    @property
    def passed_quality_gate(self) -> bool:
        """Check if document passes Quality Gate thresholds."""
        return (
            self.depth_score >= QualityThreshold.DEPTH_SCORE_MIN.value and
            self.edge_case_coverage >= QualityThreshold.EDGE_CASE_MIN.value and
            self.technical_feasibility >= QualityThreshold.TECHNICAL_FEASIBILITY.value and
            self.logic_consistency == QualityThreshold.LOGIC_CONSISTENCY.value and
            self.ai_speak_instances == QualityThreshold.NO_AI_SPEAK.value
        )

    @property
    def failure_reasons(self) -> List[str]:
        """Get list of quality gate failures."""
        reasons = []

        if self.depth_score < QualityThreshold.DEPTH_SCORE_MIN.value:
            reasons.append(f"depth_score {self.depth_score} < {QualityThreshold.DEPTH_SCORE_MIN.value}")

        if self.edge_case_coverage < QualityThreshold.EDGE_CASE_MIN.value:
            reasons.append(f"edge_cases {self.edge_case_coverage} < {QualityThreshold.EDGE_CASE_MIN.value}")

        if self.technical_feasibility < QualityThreshold.TECHNICAL_FEASIBILITY.value:
            reasons.append(f"Technical feasibility {self.technical_feasibility}% < 100%")

        if self.logic_consistency > QualityThreshold.LOGIC_CONSISTENCY.value:
            reasons.append(f"Found {self.logic_consistency} logic contradictions")

        if self.ai_speak_instances > QualityThreshold.NO_AI_SPEAK.value:
            reasons.append(f"Found {self.ai_speak_instances} AI-speak instances")

        return reasons


def validate_quality_gate(content: str, extracted_data: dict) -> QualityGateReport:
    """
    Validate SDD content against Quality Gate thresholds.

    Args:
        content: Markdown content to validate
        extracted_data: Extracted structured data from document

    Returns:
        QualityGateReport with detailed scoring
    """
    depth_score = calculate_depth_score(extracted_data)

    edge_cases = extracted_data.get('edge_cases', [])
    edge_case_count = len(edge_cases)

    feasibility = check_technical_feasibility(extracted_data)

    contradictions = find_logic_contradictions(content, extracted_data)

    ai_speak = detect_ai_speak(content)

    report = QualityGateReport(
        depth_score=depth_score,
        edge_case_coverage=edge_case_count,
        technical_feasibility=feasibility,
        logic_consistency=contradictions,
        ai_speak_instances=ai_speak,
        maturity_score=0,  # Will be calculated by validator
    )

    return report


def calculate_depth_score(data: dict) -> float:
    """
    Calculate depth score based on:
    - Detail level in happy path (0-3 points)
    - Edge case quality (0-3 points)
    - Technical specificity (0-4 points)
    """
    score = 0.0

    # Happy path detail (0-3)
    happy_path = data.get('happy_path', [])
    if len(happy_path) >= 5:
        score += 1.0
    if any(step.get('description', '').count(' ') > 10 for step in happy_path):
        score += 1.0
    if any('validation' in str(step).lower() for step in happy_path):
        score += 1.0

    # Edge case quality (0-3)
    edge_cases = data.get('edge_cases', [])
    if len(edge_cases) >= 5:
        score += 1.0
    if any(case.get('mitigation') for case in edge_cases):
        score += 1.0
    if any(case.get('scenario', '').count(' ') > 5 for case in edge_cases):
        score += 1.0

    # Technical specificity (0-4)
    tech_stack = data.get('tech_stack', {})
    if len(tech_stack) >= 3:
        score += 1.0
    if any('rationale' in str(v).lower() for v in tech_stack.values()):
        score += 1.0
    if data.get('data_models'):
        score += 1.0
    if data.get('api_spec'):
        score += 1.0

    return min(score, 10.0)


def check_technical_feasibility(data: dict) -> float:
    """
    Check if solutions are technically feasible.
    Returns percentage of feasible solutions.
    """
    total = 0
    feasible = 0

    # Check tech stack choices
    tech_stack = data.get('tech_stack', {})
    for tech, details in tech_stack.items():
        total += 1
        if isinstance(details, dict) and details.get('rationale'):
            feasible += 1

    # Check if edge cases have mitigations
    edge_cases = data.get('edge_cases', [])
    for case in edge_cases:
        total += 1
        if case.get('mitigation'):
            feasible += 1

    return round((feasible / total * 100) if total > 0 else 0, 2)


def find_logic_contradictions(content: str, data: dict) -> int:
    """
    Find logical contradictions in the document.
    """
    contradictions = []

    happy_path = data.get('happy_path', [])
    edge_cases = data.get('edge_cases', [])

    happy_actions = [step.get('action', '').lower() for step in happy_path]
    for case in edge_cases:
        scenario = case.get('scenario', '').lower()
        if 'fail' in scenario and any('success' in action for action in happy_actions):
            contradictions.append(f"Contradiction: {case.get('scenario')}")

    return len(contradictions)


def detect_ai_speak(content: str) -> int:
    """
    Detect AI-speak patterns in content.
    """
    ai_speak_patterns = [
        "Dưới đây là",
        "Tôi hy vọng",
        "Như đã đề cập",
        "Trong tài liệu này",
        "Tôi sẽ",
        "Hãy để tôi",
        "Chúng ta hãy"
    ]

    count = 0
    content_lower = content.lower()

    for pattern in ai_speak_patterns:
        count += content_lower.count(pattern.lower())

    return count
