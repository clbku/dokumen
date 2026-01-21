"""
Agent Initialization Tests for Deep-Spec AI

Tests for basic agent creation and configuration.
These are quick unit tests for agent properties.

For comprehensive testing including schema validation,
personality checks, and integration tests, see:
- test_schema_validation.py
- test_agent_personality.py
- test_integration.py
"""

import pytest
from unittest.mock import MagicMock
from src.agents.senior_system_architect import create_white_hat_agent
from src.agents.qa_security_auditor import create_black_hat_agent
from src.agents.chief_technology_officer import create_green_hat_agent
from crewai import Agent


class TestArchitectAgent:
    """Test Senior System Architect (White Hat) agent."""

    def test_initialization(self):
        """Test that Senior System Architect is initialized correctly."""
        agent = create_white_hat_agent(enable_tools=False)
        assert isinstance(agent, Agent)
        assert agent.role == "Kiến trúc sư hệ thống (White Hat)"
        assert "Happy Path" in agent.goal
        assert "Kiến trúc sư hệ thống" in agent.backstory

    def test_no_ai_hallucination_in_backstory(self):
        """Test that agent backstory doesn't claim to be AI."""
        agent = create_white_hat_agent(enable_tools=False)
        # Backstory should describe the role, not claim to be an AI
        assert "mô hình ngôn ngữ" not in agent.backstory.lower()
        assert "language model" not in agent.backstory.lower()

    def test_vietnamese_instructions(self):
        """Test that agent has Vietnamese language instructions."""
        agent = create_white_hat_agent(enable_tools=False)
        # Check backstory and goal for Vietnamese content
        # Vietnamese indicators that should be present
        vietnamese_indicators = ['kiến trúc sư', 'hệ thống', 'thiết kế', 'yêu cầu', 'người dùng']
        combined = agent.backstory + " " + agent.goal

        # At least some Vietnamese indicators should be present
        found = sum(1 for indicator in vietnamese_indicators if indicator in combined.lower())
        assert found >= 2, f"Expected at least 2 Vietnamese indicators, found {found}"

    def test_task_template(self):
        """Test that Architect has valid task templates."""
        from src.agents.senior_system_architect import get_white_hat_task_template
        template = get_white_hat_task_template("design_happy_path")
        assert "description" in template
        assert "expected_output" in template
        assert "Happy Path" in template["description"]

    def test_all_task_templates_exist(self):
        """Test that all expected task templates exist."""
        from src.agents.senior_system_architect import WHITE_HAT_TASK_TEMPLATES

        expected_templates = [
            "design_happy_path",
            "design_system_architecture",
            "create_sequence_diagram",
            "research_technology"
        ]

        for template_name in expected_templates:
            assert template_name in WHITE_HAT_TASK_TEMPLATES
            template = WHITE_HAT_TASK_TEMPLATES[template_name]
            assert "description" in template
            assert "expected_output" in template


class TestAuditorAgent:
    """Test QA & Security Auditor (Black Hat) agent."""

    def test_initialization(self):
        """Test that Auditor is initialized correctly."""
        agent = create_black_hat_agent(enable_tools=False)
        assert isinstance(agent, Agent)
        assert agent.role == "Chuyên gia Kiểm thử & Bảo mật (Black Hat)"
        assert "lỗ hổng" in agent.goal
        assert "Định luật Murphy" in agent.backstory

    def test_min_edge_cases_requirement(self):
        """Test that Auditor is configured to find minimum edge cases."""
        agent = create_black_hat_agent(enable_tools=False)
        # Goal should mention minimum edge cases
        assert "5" in agent.goal or "năm" in agent.goal
        assert "trường hợp biên" in agent.goal or "edge case" in agent.goal.lower()

    def test_security_focus(self):
        """Test that Auditor focuses on security."""
        agent = create_black_hat_agent(enable_tools=False)
        # Should have security-related content in goal or backstory
        combined = agent.goal + " " + agent.backstory
        assert "security" in combined.lower() or "bảo mật" in combined

    def test_task_template(self):
        """Test that Auditor has valid task templates."""
        from src.agents.qa_security_auditor import get_black_hat_task_template
        template = get_black_hat_task_template("stress_test_happy_path")
        assert "description" in template
        assert "expected_output" in template
        assert "edge case" in template["description"].lower() or "biên" in template["description"]

    def test_all_task_templates_exist(self):
        """Test that all expected task templates exist."""
        from src.agents.qa_security_auditor import BLACK_HAT_TASK_TEMPLATES

        expected_templates = [
            "stress_test_happy_path",
            "security_audit",
            "review_agent_comments"
        ]

        for template_name in expected_templates:
            assert template_name in BLACK_HAT_TASK_TEMPLATES
            template = BLACK_HAT_TASK_TEMPLATES[template_name]
            assert "description" in template
            assert "expected_output" in template


class TestCTOAgent:
    """Test Chief Technology Officer (Green Hat) agent."""

    def test_initialization(self):
        """Test that CTO is initialized correctly."""
        agent = create_green_hat_agent(enable_tools=False)
        assert isinstance(agent, Agent)
        assert agent.role == "Giám đốc Kỹ thuật (Green Hat)"

    def test_decision_making_focus(self):
        """Test that CTO focuses on decision making."""
        agent = create_green_hat_agent(enable_tools=False)
        # Should mention decisions, arbitration, or quality gates
        combined = agent.goal + " " + agent.backstory
        assert "quyết định" in combined.lower() or "decision" in combined.lower()
        assert "trọng tài" in combined or "arbitrate" in combined.lower()

    def test_delegation_enabled_by_default(self):
        """Test that CTO has delegation enabled by default."""
        agent = create_green_hat_agent()
        assert agent.allow_delegation is True

    def test_task_template(self):
        """Test that CTO has valid task templates."""
        from src.agents.chief_technology_officer import get_green_hat_task_template
        template = get_green_hat_task_template("arbitrate_debate")
        assert "description" in template
        assert "expected_output" in template

    def test_all_task_templates_exist(self):
        """Test that all expected task templates exist."""
        from src.agents.chief_technology_officer import GREEN_HAT_TASK_TEMPLATES

        expected_templates = [
            "arbitrate_debate",
            "run_quality_gate",
            "synthesize_feedback",
            "review_and_approve",
            "research_alternatives"
        ]

        for template_name in expected_templates:
            assert template_name in GREEN_HAT_TASK_TEMPLATES
            template = GREEN_HAT_TASK_TEMPLATES[template_name]
            assert "description" in template
            assert "expected_output" in template


class TestAgentConfiguration:
    """Test agent configuration options."""

    def test_tools_enable_disable(self):
        """Test that tools can be enabled or disabled."""
        # Without tools
        agent_no_tools = create_white_hat_agent(enable_tools=False)
        # When tools are disabled, tools should be None or empty
        assert agent_no_tools.tools is None or len(agent_no_tools.tools) == 0

        # With tools (only if dependencies are available)
        # Note: Skip this test if dependencies are missing
        try:
            agent_with_tools = create_white_hat_agent(enable_tools=True)
            assert agent_with_tools.tools is not None
            assert len(agent_with_tools.tools) > 0
        except Exception:
            # Tools require additional dependencies, skip if not available
            pass

    def test_verbose_option(self):
        """Test verbose option for agent."""
        agent_verbose = create_white_hat_agent(verbose=True, enable_tools=False)
        agent_quiet = create_white_hat_agent(verbose=False, enable_tools=False)

        # Both should work, just different verbosity
        assert agent_verbose.role == agent_quiet.role

    def test_memory_option(self):
        """Test memory option for agent."""
        agent_with_memory = create_white_hat_agent(memory=True, enable_tools=False)
        agent_no_memory = create_white_hat_agent(memory=False, enable_tools=False)

        # Both should work, just different memory settings
        assert agent_with_memory.role == agent_no_memory.role


class TestAgentFactory:
    """Test agent factory functions from __init__."""

    def test_create_deep_spec_crew(self):
        """Test creating all three agents via factory."""
        from src.agents import create_deep_spec_crew

        architect, auditor, cto = create_deep_spec_crew()

        assert architect.role == "Kiến trúc sư hệ thống (White Hat)"
        assert auditor.role == "Chuyên gia Kiểm thử & Bảo mật (Black Hat)"
        assert cto.role == "Giám đốc Kỹ thuật (Green Hat)"

    def test_create_agent_by_role(self):
        """Test creating agent by role name."""
        from src.agents import create_agent_by_role

        # Test new names - note: create_agent_by_role has enable_tools parameter with default False
        architect = create_agent_by_role("architect")
        assert architect.role == "Kiến trúc sư hệ thống (White Hat)"

        auditor = create_agent_by_role("auditor")
        assert auditor.role == "Chuyên gia Kiểm thử & Bảo mật (Black Hat)"

        cto = create_agent_by_role("cto")
        assert cto.role == "Giám đốc Kỹ thuật (Green Hat)"

    def test_create_agent_by_role_backward_compatibility(self):
        """Test backward compatibility with old role names."""
        from src.agents import create_agent_by_role

        # Old names should still work
        white_hat = create_agent_by_role("white_hat")
        assert white_hat.role == "Kiến trúc sư hệ thống (White Hat)"

        black_hat = create_agent_by_role("black_hat")
        assert black_hat.role == "Chuyên gia Kiểm thử & Bảo mật (Black Hat)"

        green_hat = create_agent_by_role("green_hat")
        assert green_hat.role == "Giám đốc Kỹ thuật (Green Hat)"

    def test_invalid_role_raises_error(self):
        """Test that invalid role raises ValueError."""
        from src.agents import create_agent_by_role

        with pytest.raises(ValueError) as exc_info:
            create_agent_by_role("invalid_role")
        assert "không tồn tại" in str(exc_info.value).lower() or "not found" in str(exc_info.value).lower()


class TestTaskTemplateFactory:
    """Test task template factory function."""

    def test_get_task_template(self):
        """Test getting task template via factory."""
        from src.agents import get_task_template

        # Test with new role names
        template1 = get_task_template("architect", "design_happy_path")
        assert "description" in template1

        template2 = get_task_template("auditor", "stress_test_happy_path")
        assert "description" in template2

        template3 = get_task_template("cto", "arbitrate_debate")
        assert "description" in template3

    def test_get_task_template_backward_compatibility(self):
        """Test backward compatibility with old role names."""
        from src.agents import get_task_template

        # Old names should still work
        template1 = get_task_template("white_hat", "design_happy_path")
        assert "description" in template1

        template2 = get_task_template("black_hat", "stress_test_happy_path")
        assert "description" in template2

        template3 = get_task_template("green_hat", "arbitrate_debate")
        assert "description" in template3

    def test_get_task_template_invalid_inputs(self):
        """Test that invalid inputs raise ValueError."""
        from src.agents import get_task_template

        # Invalid role
        with pytest.raises(ValueError):
            get_task_template("invalid_role", "design_happy_path")

        # Invalid template name
        with pytest.raises(ValueError):
            get_task_template("architect", "invalid_template")


class TestAgentInfo:
    """Test agent information retrieval."""

    def test_get_agent_info(self):
        """Test getting information about specific agent."""
        from src.agents import get_agent_info

        white_hat_info = get_agent_info("white_hat")
        assert white_hat_info["name"] == "Kiến trúc sư hệ thống (White Hat)"
        assert "provider" in white_hat_info
        assert "personality" in white_hat_info
        assert "responsibilities" in white_hat_info

    def test_list_all_agents(self):
        """Test listing all agents."""
        from src.agents import list_all_agents

        all_agents = list_all_agents()
        assert "white_hat" in all_agents
        assert "black_hat" in all_agents
        assert "green_hat" in all_agents

        # Each agent should have required fields
        for role, info in all_agents.items():
            assert "name" in info
            assert "provider" in info
            assert "personality" in info
            assert "responsibilities" in info

    def test_invalid_agent_info(self):
        """Test that invalid agent role raises ValueError."""
        from src.agents import get_agent_info

        with pytest.raises(ValueError):
            get_agent_info("invalid_role")
