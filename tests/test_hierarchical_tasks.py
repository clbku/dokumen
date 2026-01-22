import pytest
from src.tasks import create_hierarchical_tasks
from src.agents import create_architect_agent, create_auditor_agent
from src.schemas import HappyPath, StressTestReport

def test_create_hierarchical_tasks():
    """Test tạo 3 tasks cho hierarchical workflow."""
    architect = create_architect_agent()
    auditor = create_auditor_agent()

    tasks = create_hierarchical_tasks(
        user_requirement="Hệ thống đấu giá thời gian thực",
        architect_agent=architect,
        auditor_agent=auditor,
    )

    assert len(tasks) == 3
    assert tasks[0].agent == architect
    assert tasks[1].agent == auditor
    assert tasks[2].agent == auditor

def test_happy_path_task_has_output_pydantic():
    """Test HappyPathTask có output_pydantic đúng."""
    architect = create_architect_agent()
    auditor = create_auditor_agent()

    tasks = create_hierarchical_tasks(
        user_requirement="User registration",
        architect_agent=architect,
        auditor_agent=auditor,
    )

    assert tasks[0].output_pydantic == HappyPath

def test_business_exceptions_task_context():
    """Test BusinessExceptionsTask nhận context từ HappyPath."""
    architect = create_architect_agent()
    auditor = create_auditor_agent()

    tasks = create_hierarchical_tasks(
        user_requirement="Payment processing",
        architect_agent=architect,
        auditor_agent=auditor,
    )

    # Task 2 should reference happy path from task 1
    assert "happy path" in tasks[1].description.lower()

def test_technical_edge_cases_task_context():
    """Test TechnicalEdgeCasesTask nhận context từ cả 2 tasks trước."""
    architect = create_architect_agent()
    auditor = create_auditor_agent()

    tasks = create_hierarchical_tasks(
        user_requirement="Real-time chat",
        architect_agent=architect,
        auditor_agent=auditor,
    )

    # Task 3 should reference both happy path và business exceptions
    desc_lower = tasks[2].description.lower()
    assert "happy_path" in desc_lower or "happy path" in desc_lower
    assert "business_exception" in desc_lower or "business exception" in desc_lower
