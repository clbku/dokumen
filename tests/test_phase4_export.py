import pytest
from pathlib import Path
from src.aggregation import export_sdd, QualityGateError

def test_export_sdd_basic(tmp_path):
    """Test basic export function."""
    data = {
        "feature_name": "Test Feature",
        "happy_path": [{"action": "Test"}],
        "edge_cases": [
            {"scenario": f"Case {i}", "mitigation": "Fix"} for i in range(5)
        ],
        "tech_stack": {"FastAPI": {"rationale": "Async"}},
    }

    result = export_sdd(
        aggregated_data=data,
        template="# {feature_name}\n\nHappy Path: {happy_path}\nEdge Cases: {edge_cases}",
        output_path=str(tmp_path),
        enforce_quality_gate=False,  # Bypass for test
    )

    # With enforce_quality_gate=False, export succeeds even if QG fails
    assert "file_path" in result
    assert Path(result["file_path"]).exists()
    assert "quality_report" in result

def test_export_sdd_quality_gate_enforcement():
    """Test export enforces quality gate by default."""
    # Low quality data - should fail
    data = {
        "feature_name": "Low Quality",
        "happy_path": [],  # Empty - fails depth score
        "edge_cases": [],  # Empty - fails edge case count
        "tech_stack": {},
    }

    with pytest.raises(QualityGateError):
        export_sdd(
            aggregated_data=data,
            template="# {feature_name}",
            enforce_quality_gate=True,
        )

def test_export_sdd_creates_quality_report_json(tmp_path):
    """Test export creates quality report JSON."""
    data = {
        "feature_name": "Test",
        "happy_path": [{"action": "A", "description": "Test"}] * 5,
        "edge_cases": [{"scenario": f"C{i}", "mitigation": "F"} for i in range(5)],
        "tech_stack": {"A": {"rationale": "R"}},
    }

    result = export_sdd(
        aggregated_data=data,
        template="# {feature_name}",
        output_path=str(tmp_path),
        enforce_quality_gate=False,
    )

    # Check for quality report JSON
    output_dir = Path(tmp_path)
    json_files = list(output_dir.glob("*_quality_report.json"))

    assert len(json_files) >= 1
