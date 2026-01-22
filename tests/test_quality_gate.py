import pytest
from src.quality import QualityThreshold, QualityGateReport, validate_quality_gate
from pydantic import ValidationError

def test_quality_threshold_enum():
    """Test QualityThreshold enum values."""
    assert QualityThreshold.DEPTH_SCORE_MIN.value == 8.0
    assert QualityThreshold.EDGE_CASE_MIN.value == 5
    assert QualityThreshold.TECHNICAL_FEASIBILITY.value == 100.0

def test_quality_gate_report_validation():
    """Test QualityGateReport Pydantic validation."""
    # Valid report
    report = QualityGateReport(
        depth_score=8.5,
        edge_case_coverage=6,
        technical_feasibility=95.0,
        logic_consistency=0,
        ai_speak_instances=0,
        maturity_score=0,  # Will be calculated
    )

    assert report.maturity_score > 0
    assert report.maturity_score <= 10

def test_quality_gate_report_invalid_depth():
    """Test validation rejects depth_score out of range."""
    with pytest.raises(ValidationError):
        QualityGateReport(
            depth_score=11.0,  # Invalid: > 10
            edge_case_coverage=5,
            technical_feasibility=100.0,
            logic_consistency=0,
            ai_speak_instances=0,
        )

def test_passed_quality_gate_true():
    """Test passed_quality_gate property when all thresholds met."""
    report = QualityGateReport(
        depth_score=8.0,
        edge_case_coverage=5,
        technical_feasibility=100.0,
        logic_consistency=0,
        ai_speak_instances=0,
    )

    assert report.passed_quality_gate is True
    assert len(report.failure_reasons) == 0

def test_passed_quality_gate_false_depth_too_low():
    """Test passed_quality_gate false when depth score too low."""
    report = QualityGateReport(
        depth_score=7.5,  # Below threshold
        edge_case_coverage=5,
        technical_feasibility=100.0,
        logic_consistency=0,
        ai_speak_instances=0,
    )

    assert report.passed_quality_gate is False
    assert any("depth_score" in reason for reason in report.failure_reasons)

def test_passed_quality_gate_false_edge_cases_too_few():
    """Test passed_quality_gate false when edge cases too few."""
    report = QualityGateReport(
        depth_score=8.0,
        edge_case_coverage=3,  # Below threshold
        technical_feasibility=100.0,
        logic_consistency=0,
        ai_speak_instances=0,
    )

    assert report.passed_quality_gate is False
    assert any("edge_cases" in reason for reason in report.failure_reasons)

def test_maturity_score_calculation():
    """Test maturity score is calculated correctly."""
    # High quality
    report = QualityGateReport(
        depth_score=9.0,
        edge_case_coverage=7,
        technical_feasibility=100.0,
        logic_consistency=0,
        ai_speak_instances=0,
    )

    assert report.maturity_score >= 8.0

def test_validate_quality_gate_function():
    """Test validate_quality_gate function with mock data."""
    mock_data = {
        "happy_path": [
            {"action": "Login", "description": "User enters credentials"},
            {"action": "Validate", "description": "System validates input format and length"},
            {"action": "Verify", "description": "Check against database"},
        ],
        "edge_cases": [
            {"scenario": "Invalid email", "mitigation": "Show error"},
            {"scenario": "Wrong password", "mitigation": "Return 401"},
            {"scenario": "Database timeout", "mitigation": "Retry with circuit breaker"},
            {"scenario": "Concurrent login", "mitigation": "Use distributed lock"},
            {"scenario": "Account locked", "mitigation": "Return 403"},
        ],
        "tech_stack": {
            "FastAPI": {"rationale": "Async support"},
            "PostgreSQL": {"rationale": "ACID compliant"},
        },
    }

    mock_content = """
    # System Design Document
    ## Happy Path
    User logs in with email and password.
    ## Edge Cases
    Database timeout causes failure.
    """

    report = validate_quality_gate(mock_content, mock_data)

    assert report.depth_score >= 0
    assert report.edge_case_coverage == 5
    assert isinstance(report.maturity_score, float)

def test_detect_ai_speak():
    """Test AI-speak detection function."""
    from src.quality import detect_ai_speak

    # Clean content
    clean = "This is a system design document."
    assert detect_ai_speak(clean) == 0

    # Content with AI-speak
    ai_speak = "Dưới đây là phân tích. Tôi hy vọng tài liệu này giúp ích."
    assert detect_ai_speak(ai_speak) >= 2

def test_calculate_depth_score():
    """Test depth score calculation."""
    from src.quality import calculate_depth_score

    # Minimal data
    minimal = {"happy_path": []}
    assert calculate_depth_score(minimal) >= 0

    # Rich data
    rich = {
        "happy_path": [
            {"action": "A", "description": "This is a very detailed description with many words"},
            {"action": "B", "description": "Another detailed description"},
            {"action": "C", "description": "Third detailed step"},
            {"action": "D", "description": "Fourth step"},
            {"action": "E", "description": "Fifth step with validation"},
        ],
        "edge_cases": [
            {"scenario": "Case 1", "mitigation": "Fix 1"},
            {"scenario": "Case 2", "mitigation": "Fix 2"},
            {"scenario": "Case 3", "mitigation": "Fix 3"},
            {"scenario": "Case 4", "mitigation": "Fix 4"},
            {"scenario": "Case 5", "mitigation": "Fix 5"},
        ],
        "tech_stack": {
            "FastAPI": {"rationale": "Async"},
            "PostgreSQL": {"rationale": "Reliable"},
            "Redis": {"rationale": "Cache"},
        },
        "data_models": {"User": "id, email"},
        "api_spec": {"/login": "POST"},
    }

    score = calculate_depth_score(rich)
    assert score >= 7.0
