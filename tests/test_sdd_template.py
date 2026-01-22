import pytest
from src.templates import SDD_TEMPLATE, get_mermaid_style_guide, format_sdd

def test_sdd_template_has_required_sections():
    """Test SDD template contains all required sections."""
    required = [
        "## 1. OVERVIEW",
        "## 2. SYSTEM WORKFLOW",
        "## 3. FUNCTIONAL SPECIFICATIONS",
        "## 4. RESILIENCE & EDGE CASES",
        "## 5. TECHNICAL RECOMMENDATIONS",
    ]

    for section in required:
        assert section in SDD_TEMPLATE

def test_sdd_template_has_placeholders():
    """Test SDD template has correct placeholders."""
    placeholders = [
        "{feature_name}",
        "{version}",
        "{business_context}",
        "{mermaid_code}",
        "{workflow_table}",
    ]

    for placeholder in placeholders:
        assert placeholder in SDD_TEMPLATE

def test_get_mermaid_style_guide():
    """Test Mermaid style guide returns string."""
    guide = get_mermaid_style_guide()

    assert isinstance(guide, str)
    assert "graph TD" in guide or "sequenceDiagram" in guide
    assert "PascalCase" in guide

def test_format_sdd_basic():
    """Test format_sdd fills template with data."""
    data = {
        "feature_name": "Test Feature",
        "version": "1.0",
        "date": "2024-01-22",
        "author": "Test",
        "business_context": "Test context",
        "mermaid_code": "graph TD\nA[Test]",
        "workflow_table": "| Step | Action |\n| 1 | Test |",
    }

    result = format_sdd(data)

    assert "Test Feature" in result
    assert "1.0" in result
    assert "Test context" in result
    assert "graph TD" in result
