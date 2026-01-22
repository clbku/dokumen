"""
Integration tests for Hierarchical Workflow Entry Point.

These tests verify the complete hierarchical workflow execution including:
- Full workflow execution with multiple agents
- Scaling to multiple auditors
- Integration with orchestrator and task definitions
"""

import pytest
from crewai import Agent

from src.workflows import (
    HierarchicalOrchestrator,
    HierarchicalWorkflowConfig,
)
from src.agents import create_architect_agent, create_auditor_agent
from src.tasks import create_hierarchical_tasks


def test_hierarchical_workflow_full_execution():
    """
    Test complete hierarchical workflow execution with all components.

    This test verifies:
    - HierarchicalWorkflowConfig setup
    - HierarchicalOrchestrator creation
    - Agent creation (architect + auditor)
    - Task creation with create_hierarchical_tasks()
    - Workflow execution
    - Result parsing
    """
    # Setup: Create configuration
    config = HierarchicalWorkflowConfig(
        manager_llm_provider="google",
        manager_llm_model="gemini/gemini-3-pro-preview",
        verbose=True,
        memory=True,
        max_execution_time=300,
    )

    # Create orchestrator
    orchestrator = HierarchicalOrchestrator(config)
    assert orchestrator is not None
    assert orchestrator.manager_agent is not None

    # Create workers (architect + auditor)
    architect = create_architect_agent(
        verbose=True,
        memory=True,
        allow_delegation=False,
    )
    auditor = create_auditor_agent(
        verbose=True,
        memory=True,
        allow_delegation=False,
    )

    assert architect is not None
    assert auditor is not None

    # Create hierarchical crew
    crew = orchestrator.create_hierarchical_crew(
        workers=[architect, auditor],
    )
    assert crew is not None
    assert crew.process == "hierarchical"

    # Create tasks using task definitions
    user_requirement = "User authentication with email and password"
    tasks = create_hierarchical_tasks(
        user_requirement=user_requirement,
        architect_agent=architect,
        auditor_agent=auditor,
    )

    assert len(tasks) == 3
    assert tasks[0].agent == architect
    assert tasks[1].agent == auditor
    assert tasks[2].agent == auditor

    # Execute workflow
    result = orchestrator.execute_workflow(
        user_requirement=user_requirement,
        tasks=tasks,
    )

    # Verify results
    assert result is not None
    assert "raw_output" in result
    assert "final_result" in result


def test_hierarchical_workflow_scale_to_multiple_auditors():
    """
    Test hierarchical workflow scaling to multiple auditor agents.

    This test verifies the system can handle multiple auditors:
    - Create multiple auditor agents (e.g., for different perspectives)
    - All auditors can be added to the hierarchical crew
    - Manager can coordinate between all workers
    - Workflow executes successfully with multiple auditors
    """
    # Setup: Create configuration
    config = HierarchicalWorkflowConfig(
        manager_llm_provider="google",
        verbose=True,
        memory=True,
    )

    # Create orchestrator
    orchestrator = HierarchicalOrchestrator(config)

    # Create architect (single)
    architect = create_architect_agent(
        verbose=True,
        memory=True,
        allow_delegation=False,
    )

    # Create multiple auditors (scale feature)
    num_auditors = 3
    auditors = [
        create_auditor_agent(
            verbose=True,
            memory=True,
            allow_delegation=False,
        )
        for _ in range(num_auditors)
    ]

    # Verify all auditors created
    assert len(auditors) == num_auditors
    for auditor in auditors:
        assert auditor is not None
        assert isinstance(auditor, Agent)

    # Create hierarchical crew with multiple auditors
    all_workers = [architect] + auditors
    crew = orchestrator.create_hierarchical_crew(
        workers=all_workers,
    )

    assert crew is not None
    assert crew.process == "hierarchical"
    # Manager + architect + auditors
    assert len(crew.agents) == 1 + len(all_workers)

    # Create tasks (can assign different auditors to different tasks)
    user_requirement = "Payment processing system with fraud detection"
    tasks = create_hierarchical_tasks(
        user_requirement=user_requirement,
        architect_agent=architect,
        auditor_agent=auditors[0],  # Use first auditor
    )

    assert len(tasks) == 3

    # Optional: Reassign some tasks to other auditors
    # This demonstrates flexibility of multi-auditor setup
    tasks[2].agent = auditors[1]  # Assign technical edge cases to second auditor

    # Execute workflow with multiple auditors
    result = orchestrator.execute_workflow(
        user_requirement=user_requirement,
        tasks=tasks,
    )

    # Verify results
    assert result is not None
    assert "raw_output" in result
    assert "final_result" in result


def test_hierarchical_workflow_convenience_function():
    """
    Test the convenience function for executing hierarchical workflow.

    This will be implemented in hierarchical_workflow.py as:
    execute_hierarchical_workflow(user_requirement, config)

    The function should:
    - Create orchestrator
    - Create agents
    - Create tasks
    - Execute workflow
    - Return results
    """
    from src.workflows.hierarchical_workflow import execute_hierarchical_workflow

    # Execute with convenience function
    user_requirement = "Real-time notification system"
    config = HierarchicalWorkflowConfig(
        manager_llm_provider="google",
        verbose=True,
    )

    result = execute_hierarchical_workflow(
        user_requirement=user_requirement,
        config=config,
    )

    # Verify results
    assert result is not None
    assert "raw_output" in result
    assert "final_result" in result


def test_hierarchical_workflow_config_validation():
    """
    Test HierarchicalWorkflowConfig validation and defaults.

    Verify:
    - Default values are appropriate
    - Configuration can be customized
    - Invalid values raise appropriate errors
    """
    # Test with defaults
    config1 = HierarchicalWorkflowConfig()
    assert config1.manager_llm_provider == "google"
    assert config1.verbose is True
    assert config1.memory is True
    assert config1.max_execution_time is None
    assert config1.allow_delegation_to_manager is True

    # Test with custom values
    config2 = HierarchicalWorkflowConfig(
        manager_llm_provider="zai",
        manager_llm_model="glm-4.7",
        verbose=False,
        memory=False,
        max_execution_time=600,
        allow_delegation_to_manager=False,
    )
    assert config2.manager_llm_provider == "zai"
    assert config2.manager_llm_model == "glm-4.7"
    assert config2.verbose is False
    assert config2.memory is False
    assert config2.max_execution_time == 600
    assert config2.allow_delegation_to_manager is False


def test_hierarchical_workflow_error_handling():
    """
    Test error handling in hierarchical workflow.

    Verify:
    - Invalid worker agents raise appropriate errors
    - Missing tasks raise appropriate errors
    - Crew can be reset and reused
    """
    config = HierarchicalWorkflowConfig(
        manager_llm_provider="google",
        verbose=True,
    )

    orchestrator = HierarchicalOrchestrator(config)

    # Test: Execute without creating crew should raise error
    with pytest.raises(ValueError, match="Crew chưa được tạo"):
        orchestrator.execute_workflow(
            user_requirement="Test requirement",
            tasks=[],
        )

    # Test: Create crew, then reset
    architect = create_architect_agent()
    auditor = create_auditor_agent()

    crew = orchestrator.create_hierarchical_crew(
        workers=[architect, auditor],
    )
    assert crew is not None
    assert orchestrator.crew is not None

    # Reset
    orchestrator.reset()
    assert orchestrator.crew is None


__all__ = [
    "test_hierarchical_workflow_full_execution",
    "test_hierarchical_workflow_scale_to_multiple_auditors",
    "test_hierarchical_workflow_convenience_function",
    "test_hierarchical_workflow_config_validation",
    "test_hierarchical_workflow_error_handling",
]
