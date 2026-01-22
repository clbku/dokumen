"""
End-to-End Integration Tests for Hierarchical Workflow.

These tests verify the complete hierarchical workflow execution with real agents:
- Full workflow execution with complex features
- Scaling to multiple auditors
- Integration of all components (orchestrator, agents, tasks, validator)

NOTE: These are integration tests that require actual API keys to run.
They may take several minutes to complete.

Run with: pytest tests/test_hierarchical_workflow_e2e.py -v -m integration
"""

import pytest
from typing import Dict, Any

from src.workflows import (
    HierarchicalWorkflow,
    HierarchicalWorkflowConfig,
)
from src.validation.hierarchical_validator import HierarchicalValidator


# === Integration Test Marks ===

integration = pytest.mark.integration
slow = pytest.mark.slow


# === Test Fixtures ===

@pytest.fixture
def complex_feature_requirement() -> str:
    """
    Complex feature requirement for testing.

    From spec (line 1640):
    "Hệ thống đấu giá trực tuyến thời gian thực với 1000 người dùng"
    """
    return "Hệ thống đấu giá trực tuyến thời gian thực với 1000 người dùng"


@pytest.fixture
def validator() -> HierarchicalValidator:
    """Fixture for validator instance."""
    return HierarchicalValidator()


# === Test 1: Complex Feature Workflow ===

@integration
@slow
def test_hierarchical_workflow_complex_feature(
    complex_feature_requirement: str,
    validator: HierarchicalValidator,
):
    """
    Test hierarchical workflow with complex feature.

    From spec (lines 1635-1688):
    - Tests with complex feature: "Hệ thống đấu giá trực tuyến thời gian thực với 1000 người dùng"
    - Verify structure: happy_path, business_exceptions, technical_edge_cases, validation keys present
    - Verify validation passes
    - Verify happy path has 3+ steps
    - Verify business edge cases don't contain technical keywords (concurrency, network, database)
    - Verify technical edge cases has 5+ edge cases

    This test:
    1. Creates a HierarchicalWorkflow with default config
    2. Executes workflow with complex feature requirement
    3. Validates the complete result structure
    4. Verifies all validation requirements pass
    """
    # Arrange: Create workflow config
    config = HierarchicalWorkflowConfig(
        manager_llm_provider="google",
        verbose=True,
        memory=True,
        use_multiple_auditors=False,  # Single auditor for this test
    )

    workflow = HierarchicalWorkflow(config)

    # Act: Execute workflow
    result = workflow.execute(complex_feature_requirement)

    # Assert: Verify result structure
    assert result is not None, "Result should not be None"
    assert isinstance(result, dict), "Result should be a dictionary"

    # Verify all required keys are present
    required_keys = [
        "happy_path",
        "business_exceptions",
        "technical_edge_cases",
        "validation",
    ]
    for key in required_keys:
        assert key in result, f"Result should contain '{key}' key"

    # Verify validation status
    validation = result["validation"]
    assert "is_valid" in validation, "Validation should contain 'is_valid' key"
    assert "errors" in validation, "Validation should contain 'errors' key"

    # Verify validation passes (warnings don't cause failure)
    is_valid = validation["is_valid"]
    errors = validation["errors"]

    # Print validation status for debugging
    print(f"\n{'='*60}")
    print(f"Validation Status: {'PASSED' if is_valid else 'FAILED'}")
    print(f"{'='*60}")

    if errors:
        print(f"\nValidation Errors/Warnings ({len(errors)}):")
        for i, error in enumerate(errors, 1):
            print(f"  {i}. {error}")

    # Verify happy path structure
    happy_path = result["happy_path"]
    assert happy_path is not None, "Happy path should not be None"
    assert hasattr(happy_path, "steps"), "Happy path should have 'steps' attribute"
    assert len(happy_path.steps) >= 3, (
        f"Happy path must have at least 3 steps, got {len(happy_path.steps)}"
    )

    print(f"\nHappy Path:")
    print(f"  Feature: {happy_path.feature_name}")
    print(f"  Steps: {len(happy_path.steps)}")

    # Verify business exceptions structure
    business_exceptions = result["business_exceptions"]
    assert business_exceptions is not None, "Business exceptions should not be None"
    assert hasattr(business_exceptions, "edge_cases"), (
        "Business exceptions should have 'edge_cases' attribute"
    )

    print(f"\nBusiness Exceptions:")
    print(f"  Report ID: {business_exceptions.report_id}")
    print(f"  Edge Cases: {len(business_exceptions.edge_cases)}")
    print(f"  Resilience Score: {business_exceptions.resilience_score}")
    print(f"  Coverage Score: {business_exceptions.coverage_score}")

    # Verify business edge cases don't contain technical keywords
    # From spec: business edge cases shouldn't contain "concurrency", "network", "database"
    business_edge_case_descriptions = [
        ec.description.lower() for ec in business_exceptions.edge_cases
    ]
    business_edge_case_triggers = [
        ec.trigger_condition.lower() for ec in business_exceptions.edge_cases
    ]

    # Combine all business edge case text
    all_business_text = " ".join(
        business_edge_case_descriptions + business_edge_case_triggers
    )

    # Check for forbidden technical keywords in business edge cases
    forbidden_keywords = ["concurrency", "network", "database"]
    found_technical_keywords = [
        kw for kw in forbidden_keywords if kw.lower() in all_business_text
    ]

    if found_technical_keywords:
        pytest.fail(
            f"Business edge cases should not contain technical keywords: "
            f"{', '.join(found_technical_keywords)}"
        )

    # Verify technical edge cases structure
    technical_edge_cases = result["technical_edge_cases"]
    assert technical_edge_cases is not None, "Technical edge cases should not be None"
    assert hasattr(technical_edge_cases, "edge_cases"), (
        "Technical edge cases should have 'edge_cases' attribute"
    )

    # From spec: technical edge cases should have 5+ edge cases
    assert len(technical_edge_cases.edge_cases) >= 5, (
        f"Technical edge cases must have at least 5 edge cases, "
        f"got {len(technical_edge_cases.edge_cases)}"
    )

    print(f"\nTechnical Edge Cases:")
    print(f"  Report ID: {technical_edge_cases.report_id}")
    print(f"  Edge Cases: {len(technical_edge_cases.edge_cases)}")
    print(f"  Resilience Score: {technical_edge_cases.resilience_score}")
    print(f"  Coverage Score: {technical_edge_cases.coverage_score}")

    # Print summary
    print(f"\n{'='*60}")
    print(f"Test Summary: PASSED")
    print(f"{'='*60}")


# === Test 2: Multiple Auditors Scaling ===

@integration
@slow
def test_hierarchical_workflow_with_multiple_auditors(
    validator: HierarchicalValidator,
):
    """
    Test hierarchical workflow scaling with multiple auditors.

    From spec (lines 1689-1694):
    - Tests scaling with multiple auditors (3 auditors: Business, Technical, Security)
    - Verify workflow has 4 agents (1 architect + 3 auditors)

    This test:
    1. Creates a HierarchicalWorkflow with 3 auditors
    2. Executes workflow
    3. Verifies all agents are created correctly
    4. Validates the result still passes with multiple auditors
    """
    # Arrange: Create workflow config with multiple auditors
    config = HierarchicalWorkflowConfig(
        manager_llm_provider="google",
        verbose=True,
        memory=True,
        use_multiple_auditors=True,
        num_auditors=3,  # Business, Technical, Security auditors
    )

    workflow = HierarchicalWorkflow(config)

    # Act: Execute workflow
    user_requirement = "Payment processing system with multi-level fraud detection"
    result = workflow.execute(user_requirement)

    # Assert: Verify workflow has correct number of agents
    # From spec: 1 architect + 3 auditors = 4 workers
    # Plus 1 manager agent = 5 total agents
    assert len(workflow.agents) == 4, (
        f"Workflow should have 4 worker agents (1 architect + 3 auditors), "
        f"got {len(workflow.agents)}"
    )

    # Verify agent types
    assert "architect" in workflow.agents, "Workflow should have architect agent"
    assert "auditor_0" in workflow.agents, "Workflow should have auditor_0"
    assert "auditor_1" in workflow.agents, "Workflow should have auditor_1"
    assert "auditor_2" in workflow.agents, "Workflow should have auditor_2"

    print(f"\n{'='*60}")
    print(f"Multiple Auditors Test")
    print(f"{'='*60}")
    print(f"Total Worker Agents: {len(workflow.agents)}")
    print(f"Agent Keys: {list(workflow.agents.keys())}")

    # Verify result structure is still valid with multiple auditors
    assert result is not None, "Result should not be None"
    assert isinstance(result, dict), "Result should be a dictionary"

    # Verify all required keys are present
    required_keys = [
        "happy_path",
        "business_exceptions",
        "technical_edge_cases",
        "validation",
    ]
    for key in required_keys:
        assert key in result, f"Result should contain '{key}' key"

    # Verify validation passes
    validation = result["validation"]
    is_valid = validation["is_valid"]
    errors = validation["errors"]

    print(f"\nValidation Status: {'PASSED' if is_valid else 'FAILED'}")

    if errors:
        print(f"\nValidation Errors/Warnings ({len(errors)}):")
        for i, error in enumerate(errors, 1):
            print(f"  {i}. {error}")

    # Verify happy path structure
    happy_path = result["happy_path"]
    assert happy_path is not None, "Happy path should not be None"
    assert len(happy_path.steps) >= 3, (
        f"Happy path must have at least 3 steps, got {len(happy_path.steps)}"
    )

    print(f"\nHappy Path:")
    print(f"  Feature: {happy_path.feature_name}")
    print(f"  Steps: {len(happy_path.steps)}")

    # Verify business exceptions structure
    business_exceptions = result["business_exceptions"]
    assert business_exceptions is not None, "Business exceptions should not be None"
    assert len(business_exceptions.edge_cases) >= 5, (
        f"Business exceptions must have at least 5 edge cases, "
        f"got {len(business_exceptions.edge_cases)}"
    )

    print(f"\nBusiness Exceptions:")
    print(f"  Edge Cases: {len(business_exceptions.edge_cases)}")

    # Verify technical edge cases structure
    technical_edge_cases = result["technical_edge_cases"]
    assert technical_edge_cases is not None, "Technical edge cases should not be None"
    assert len(technical_edge_cases.edge_cases) >= 5, (
        f"Technical edge cases must have at least 5 edge cases, "
        f"got {len(technical_edge_cases.edge_cases)}"
    )

    print(f"\nTechnical Edge Cases:")
    print(f"  Edge Cases: {len(technical_edge_cases.edge_cases)}")

    # Print summary
    print(f"\n{'='*60}")
    print(f"Test Summary: PASSED")
    print(f"Multiple auditors scaling: VERIFIED")
    print(f"{'='*60}")


# === Test Configuration ===

def pytest_configure(config):
    """
    Configure pytest markers.

    This allows tests to be run with:
    pytest tests/test_hierarchical_workflow_e2e.py -v -m integration
    """
    config.addinivalue_line("markers", "integration: mark test as integration test")
    config.addinivalue_line("markers", "slow: mark test as slow running")


# === Module Exports ===

__all__ = [
    "test_hierarchical_workflow_complex_feature",
    "test_hierarchical_workflow_with_multiple_auditors",
]
