import pytest
from crewai import Agent, Task
from src.workflows import HierarchicalOrchestrator, HierarchicalWorkflowConfig


def test_hierarchical_orchestrator_init():
    """Test khởi tạo orchestrator với config."""
    config = HierarchicalWorkflowConfig(
        manager_llm_provider="google",
        verbose=True
    )
    orchestrator = HierarchicalOrchestrator(config)

    assert orchestrator.config.manager_llm_provider == "google"
    assert orchestrator.manager_agent is not None
    assert orchestrator.crew is None  # Crew chưa được tạo


def test_create_hierarchical_crew():
    """Test tạo hierarchical crew với manager."""
    config = HierarchicalWorkflowConfig(
        manager_llm_provider="google",
        verbose=True
    )
    orchestrator = HierarchicalOrchestrator(config)

    # Create worker agents
    from src.agents import create_architect_agent, create_auditor_agent
    architect = create_architect_agent()
    auditor = create_auditor_agent()

    # Create hierarchical crew
    crew = orchestrator.create_hierarchical_crew(
        workers=[architect, auditor]
    )

    assert crew is not None
    assert crew.process == "hierarchical"


def test_execute_workflow():
    """Test execute workflow với hierarchical process."""
    config = HierarchicalWorkflowConfig(
        manager_llm_provider="google",
        verbose=True
    )
    orchestrator = HierarchicalOrchestrator(config)

    from src.agents import create_architect_agent, create_auditor_agent
    architect = create_architect_agent()
    auditor = create_auditor_agent()

    # Create tasks
    happy_path_task = Task(
        description="Thiết kế happy path cho: đăng nhập người dùng",
        expected_output="HappyPath object với luồng đăng nhập thành công",
        agent=architect,
    )

    edge_case_task = Task(
        description="Tìm edge cases cho flow đăng nhập",
        expected_output="StressTestReport với 5+ edge cases",
        agent=auditor,
    )

    # Execute
    result = orchestrator.execute_workflow(
        user_requirement="Hệ thống đăng nhập với email và password",
        tasks=[happy_path_task, edge_case_task]
    )

    assert result is not None
    assert "happy_path" in result or "edge_cases" in result
