import pytest
from crewai import Agent
from src.agents.multi_agent_roles import (
    create_white_hat_agent,
    create_black_hat_agent,
    create_green_hat_agent,
    create_editor_agent,
)

def test_white_hat_agent_created():
    """Test White Hat agent has correct role."""
    agent = create_white_hat_agent()

    assert agent is not None
    assert "White Hat" in agent.role or "Optimist" in agent.role
    assert agent.verbose is True

def test_black_hat_agent_created():
    """Test Black Hat agent has critical thinking role."""
    agent = create_black_hat_agent()

    assert agent is not None
    assert "Black Hat" in agent.role or "Critic" in agent.role
    assert agent.verbose is True

def test_green_hat_agent_created():
    """Test Green Hat agent has creative formatting role."""
    agent = create_green_hat_agent()

    assert agent is not None
    assert "Green Hat" in agent.role or "Creative" in agent.role
    assert agent.verbose is True

def test_editor_agent_created():
    """Test Editor agent has synthesizer role."""
    agent = create_editor_agent()

    assert agent is not None
    assert "Editor" in agent.role or "Synthesizer" in agent.role
    assert agent.verbose is True

def test_all_agents_use_llm():
    """Test all agents have LLM configured."""
    from src.utils.llm_provider import get_llm

    white = create_white_hat_agent()
    black = create_black_hat_agent()
    green = create_green_hat_agent()
    editor = create_editor_agent()

    # Verify all agents have llm attribute
    assert white.llm is not None
    assert black.llm is not None
    assert green.llm is not None
    assert editor.llm is not None
