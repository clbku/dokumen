"""
Integration tests for Hierarchical Workflow Entry Point.

These tests verify the complete hierarchical workflow execution including:
- Full workflow execution with multiple agents
- Scaling to multiple auditors
- Integration with orchestrator and task definitions
"""

from crewai import Agent

from src.workflows import (
    HierarchicalOrchestrator,
)
from src.workflows.hierarchical_orchestrator import HierarchicalOrchestratorConfig as OrchestratorConfig
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
    config = OrchestratorConfig(
        manager_llm_provider="google",
        verbose=True,
        memory=True,
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
    config = OrchestratorConfig(
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


__all__ = [
    "test_hierarchical_workflow_full_execution",
    "test_hierarchical_workflow_scale_to_multiple_auditors",
]
