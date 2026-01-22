import pytest
from src.aggregation import DebateOrchestrator, DebateConfig
from src.agents import create_white_hat_agent, create_black_hat_agent

def test_debate_config_creation():
    """Test DebateConfig dataclass."""
    config = DebateConfig(
        max_retries=3,
        enforce_quality_gate=True,
    )

    assert config.max_retries == 3
    assert config.enforce_quality_gate is True

def test_orchestrator_init():
    """Test DebateOrchestrator initialization."""
    config = DebateConfig()
    orchestrator = DebateOrchestrator(config)

    assert orchestrator.config is not None
    assert orchestrator.agents == {}

def test_orchestrator_register_agents():
    """Test registering agents."""
    orchestrator = DebateOrchestrator(DebateConfig())

    white = create_white_hat_agent()
    black = create_black_hat_agent()

    orchestrator.register_agent("white", white)
    orchestrator.register_agent("black", black)

    assert "white" in orchestrator.agents
    assert "black" in orchestrator.agents
    assert len(orchestrator.agents) == 2

def test_orchestrator_has_required_agents():
    """Test check for required agents."""
    orchestrator = DebateOrchestrator(DebateConfig())

    # Missing agents
    assert orchestrator.has_required_agents() is False

    # Add all required
    for name in ["white", "black", "green", "editor"]:
        from src.agents import (
            create_white_hat_agent,
            create_black_hat_agent,
            create_green_hat_agent,
            create_editor_agent,
        )
        agents = {
            "white": create_white_hat_agent(),
            "black": create_black_hat_agent(),
            "green": create_green_hat_agent(),
            "editor": create_editor_agent(),
        }
        orchestrator.agents = agents

    assert orchestrator.has_required_agents() is True
