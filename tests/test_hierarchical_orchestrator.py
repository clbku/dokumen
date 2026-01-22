import pytest
from unittest.mock import MagicMock, patch
from src.workflows import HierarchicalOrchestrator, HierarchicalWorkflowConfig


@pytest.fixture
def mock_llm():
    """Mock LLM for testing without API calls."""
    mock = MagicMock()
    mock.model = "test-model"
    mock.temperature = 0.5
    return mock


@pytest.fixture
def mock_get_llm(mock_llm):
    """Mock get_llm function."""
    with patch('src.utils.llm_provider.get_llm', return_value=mock_llm):
        yield


def test_hierarchical_orchestrator_init(mock_get_llm):
    """Test khởi tạo orchestrator với config."""
    config = HierarchicalWorkflowConfig(
        manager_llm_provider="google",
        verbose=True
    )
    orchestrator = HierarchicalOrchestrator(config)

    assert orchestrator.config.manager_llm_provider == "google"
    assert orchestrator.manager_agent is not None
    assert orchestrator.crew is None  # Crew chưa được tạo


def test_create_hierarchical_crew(mock_get_llm):
    """Test tạo hierarchical crew với manager."""
    config = HierarchicalWorkflowConfig(
        manager_llm_provider="google",
        verbose=True
    )
    orchestrator = HierarchicalOrchestrator(config)

    # Test that manager agent was created with correct config
    assert orchestrator.manager_agent is not None
    assert orchestrator.manager_agent.role == "Manager Agent - CTO"

    # Test that crew is initially None
    assert orchestrator.crew is None

    # Test that reset method works
    orchestrator.reset()
    assert orchestrator.crew is None

    # Note: Actual Crew creation is tested in integration tests
    # as it requires proper Agent setup with LLMs
