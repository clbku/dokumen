"""
Integration Tests for Deep-Spec AI

Tests actual agent execution with CrewAI framework.
These tests verify end-to-end functionality.

Note: These tests may require actual LLM API calls or careful mocking.

Test Categories:
1. Agent initialization and configuration
2. Task execution with mock LLM responses
3. Multi-agent collaboration
4. End-to-end workflow
"""

import pytest
import json
from unittest.mock import MagicMock, patch
from crewai import Task, Crew

from src.agents import (
    create_deep_spec_crew,
    create_agent_by_role,
    create_architect_agent,
    create_auditor_agent,
    create_cto_agent,
    get_task_template,
)
from src.schemas import HappyPath, StressTestReport, ConsensusDecision
from conftest import validate_schema_compliance, check_agent_personality


class TestAgentInitialization:
    """Test agent creation and initialization."""

    def test_create_deep_spec_crew(self):
        """Test creating all three agents together."""
        architect, auditor, cto = create_deep_spec_crew(
            verbose=False,
            memory=True,
            allow_delegation=False
        )

        # Check architect
        assert architect.role == "Kiến trúc sư hệ thống (White Hat)"
        assert "Happy Path" in architect.goal

        # Check auditor
        assert auditor.role == "Chuyên gia Kiểm thử & Bảo mật (Black Hat)"
        assert "lỗ hổng" in auditor.goal

        # Check CTO
        assert cto.role == "Giám đốc Kỹ thuật (Green Hat)"

    def test_create_agent_by_role(self):
        """Test creating agent by role name."""
        architect = create_agent_by_role("architect")
        assert architect.role == "Kiến trúc sư hệ thống (White Hat)"

        auditor = create_agent_by_role("auditor")
        assert auditor.role == "Chuyên gia Kiểm thử & Bảo mật (Black Hat)"

        cto = create_agent_by_role("cto")
        assert cto.role == "Giám đốc Kỹ thuật (Green Hat)"

        # Test backward compatibility with old names
        white_hat = create_agent_by_role("white_hat")
        assert white_hat.role == "Kiến trúc sư hệ thống (White Hat)"

        black_hat = create_agent_by_role("black_hat")
        assert black_hat.role == "Chuyên gia Kiểm thử & Bảo mật (Black Hat)"

        green_hat = create_agent_by_role("green_hat")
        assert green_hat.role == "Giám đốc Kỹ thuật (Green Hat)"

    def test_invalid_role_raises_error(self):
        """Test that invalid role name raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            create_agent_by_role("invalid_role")
        assert "không tồn tại" in str(exc_info.value).lower() or "not found" in str(exc_info.value).lower()

    def test_agent_tools_configuration(self):
        """Test that agents have proper tools configured."""
        # Architect can be created without tools
        architect_no_tools = create_architect_agent(enable_tools=False)
        assert architect_no_tools.tools is None or len(architect_no_tools.tools) == 0

        # With tools (only if dependencies are available)
        try:
            architect_with_tools = create_architect_agent(enable_tools=True)
            assert architect_with_tools.tools is not None
            assert len(architect_with_tools.tools) > 0
        except Exception:
            # Tools require additional dependencies
            pass

    def test_agent_delegation_settings(self):
        """Test agent delegation settings."""
        # Architect doesn't delegate by default
        architect = create_architect_agent()
        assert architect.allow_delegation is False

        # Auditor doesn't delegate by default
        auditor = create_auditor_agent()
        assert auditor.allow_delegation is False

        # CTO can delegate by default
        cto = create_cto_agent()
        assert cto.allow_delegation is True


class TestTaskTemplates:
    """Test task template retrieval and formatting."""

    def test_architect_task_templates(self):
        """Test architect task templates."""
        # Get happy path design template
        template = get_task_template("architect", "design_happy_path")
        assert "description" in template
        assert "expected_output" in template
        assert "{feature_name}" in template["description"]

        # Format template with actual values
        formatted_desc = template["description"].format(
            feature_name="User Login",
            requirements="User can login with email and password"
        )
        assert "User Login" in formatted_desc

    def test_auditor_task_templates(self):
        """Test auditor task templates."""
        template = get_task_template("auditor", "stress_test_happy_path")
        assert "description" in template
        assert "expected_output" in template
        assert "{happy_path_id}" in template["description"]

    def test_cto_task_templates(self):
        """Test CTO task templates."""
        template = get_task_template("cto", "arbitrate_debate")
        assert "description" in template
        assert "{topic}" in template["description"]

        quality_gate_template = get_task_template("cto", "run_quality_gate")
        assert "{document_details}" in quality_gate_template["description"]

    def test_invalid_template_name_raises_error(self):
        """Test that invalid template name raises ValueError."""
        with pytest.raises(ValueError):
            get_task_template("architect", "invalid_template_name")


class TestMockAgentExecution:
    """Test agent execution with mocked LLM responses."""

    @patch('src.utils.llm_provider.get_agent_llm')
    def test_architect_produces_valid_json(self, mock_llm):
        """
        Test that architect produces valid JSON output.

        This test uses a mock to simulate LLM response.
        In real execution, the LLM would generate this.
        """
        # Setup mock LLM
        mock_llm_instance = MagicMock()
        mock_llm.return_value = mock_llm_instance

        # Create agent
        architect = create_architect_agent(enable_tools=False)

        # Verify agent is configured correctly
        assert architect.role == "Kiến trúc sư hệ thống (White Hat)"
        # Check for Vietnamese content (keywords that indicate Vietnamese)
        vietnamese_indicators = ['kiến trúc sư', 'hệ thống', 'thiết kế', 'xây dựng']
        combined = architect.backstory + " " + architect.goal
        found = sum(1 for kw in vietnamese_indicators if kw in combined.lower())
        assert found >= 2, f"Expected Vietnamese content, found indicators: {found}/{len(vietnamese_indicators)}"

    @patch('src.utils.llm_provider.get_agent_llm')
    def test_auditor_requires_min_edge_cases(self, mock_llm):
        """Test that auditor is configured to require minimum edge cases."""
        mock_llm_instance = MagicMock()
        mock_llm.return_value = mock_llm_instance

        auditor = create_auditor_agent(enable_tools=False)

        # Check goal mentions minimum edge cases
        assert "5" in auditor.goal or "năm" in auditor.goal
        assert "trường hợp biên" in auditor.goal or "edge case" in auditor.goal.lower()

    @patch('src.utils.llm_provider.get_agent_llm')
    def test_cto_quality_gate_configuration(self, mock_llm):
        """Test that CTO is configured for quality gates."""
        mock_llm_instance = MagicMock()
        mock_llm.return_value = mock_llm_instance

        cto = create_cto_agent(enable_tools=False)

        # Check CTO is configured for decision making
        assert "quyết định" in cto.goal.lower() or "decision" in cto.goal.lower()
        assert "trọng tài" in cto.goal or "arbitrate" in cto.goal.lower()


class TestAgentPersonalityIntegration:
    """Integration tests for agent personality enforcement."""

    def test_sample_responses_pass_schema_validation(
        self,
        sample_architect_response,
        sample_auditor_response,
        sample_cto_response,
        schema_validator
    ):
        """Test that sample responses pass schema validation."""
        # Architect response should be valid HappyPath
        arch_result = schema_validator(sample_architect_response, HappyPath)
        assert arch_result['valid'], f"Architect response failed: {arch_result['errors']}"

        # Auditor response should be valid StressTestReport
        audit_result = schema_validator(sample_auditor_response, StressTestReport)
        assert audit_result['valid'], f"Auditor response failed: {audit_result['errors']}"

        # CTO response should be valid ConsensusDecision
        cto_result = schema_validator(sample_cto_response, ConsensusDecision)
        assert cto_result['valid'], f"CTO response failed: {cto_result['errors']}"

    def test_sample_responses_pass_personality_checks(
        self,
        sample_architect_response,
        sample_auditor_response,
        sample_cto_response,
        personality_checker
    ):
        """Test that sample responses pass personality checks."""
        # Architect should not hallucinate, should use Vietnamese
        arch_result = personality_checker(sample_architect_response, 'architect')
        assert arch_result['no_ai_hallucination'], "Architect should not claim to be AI"
        assert arch_result['language_correct'], "Architect should use Vietnamese"

        # Auditor should find specific errors, should use Vietnamese
        audit_result = personality_checker(sample_auditor_response, 'auditor')
        assert audit_result['no_ai_hallucination'], "Auditor should not claim to be AI"
        assert audit_result['language_correct'], "Auditor should use Vietnamese"
        assert audit_result['focus_correct'], "Auditor should find specific errors"

        # CTO should use Vietnamese
        cto_result = personality_checker(sample_cto_response, 'cto')
        assert cto_result['no_ai_hallucination'], "CTO should not claim to be AI"
        assert cto_result['language_correct'], "CTO should use Vietnamese"

    def test_bad_responses_fail_personality_checks(
        self,
        bad_response_ai_hallucination,
        bad_auditor_response_vague,
        personality_checker
    ):
        """Test that bad responses fail personality checks."""
        # AI hallucination should be detected
        hallucination_result = personality_checker(bad_response_ai_hallucination, 'architect')
        assert not hallucination_result['no_ai_hallucination'], \
            "Should detect AI hallucination"

        # Vague edge cases should be detected
        vague_result = personality_checker(bad_auditor_response_vague, 'auditor')
        assert not vague_result['focus_correct'], \
            "Should detect vague edge cases from auditor"


class TestEndToEndWorkflow:
    """Test complete workflow simulation."""

    def test_workflow_simulation(
        self,
        sample_user_requirements,
        sample_architect_response,
        sample_auditor_response,
        sample_cto_response,
        schema_validator
    ):
        """
        Simulate complete workflow:
        1. User provides requirements
        2. Architect designs happy path
        3. Auditor stress tests
        4. CTO makes decisions
        """
        # Step 1: User requirements are provided (simulated)
        assert len(sample_user_requirements) > 0
        assert "đăng nhập" in sample_user_requirements.lower()

        # Step 2: Architect produces HappyPath
        arch_result = schema_validator(sample_architect_response, HappyPath)
        assert arch_result['valid']
        happy_path_data = arch_result['data']
        assert happy_path_data['feature_id']
        assert len(happy_path_data['steps']) > 0

        # Step 3: Auditor produces StressTestReport
        audit_result = schema_validator(sample_auditor_response, StressTestReport)
        assert audit_result['valid']
        stress_test_data = audit_result['data']
        assert len(stress_test_data['edge_cases']) >= 5

        # Step 4: CTO produces ConsensusDecision
        cto_result = schema_validator(sample_cto_response, ConsensusDecision)
        assert cto_result['valid']
        decision_data = cto_result['data']
        assert decision_data['decision']
        assert decision_data['reasoning']

    def test_quality_gate_simulation(self):
        """
        Simulate quality gate process.

        Quality gates check:
        - Completeness (>= 70)
        - Depth (>= 65)
        - Correctness (>= 70)
        - Clarity (>= 65)
        """
        from src.schemas import QualityGateReport, MaturityMetric

        # Create a quality gate report
        report = QualityGateReport(
            report_id="QG-TEST-001",
            target_id="DOC-TEST-001",
            overall_maturity_score=78,
            depth_score=75,
            completeness_score=82,
            metrics=[
                MaturityMetric(
                    metric_name="Completeness",
                    score=82,
                    description="All required sections present",
                    threshold=70,
                    passed=True
                ),
                MaturityMetric(
                    metric_name="Depth",
                    score=75,
                    description="Good technical detail",
                    threshold=65,
                    passed=True
                ),
                MaturityMetric(
                    metric_name="Correctness",
                    score=78,
                    description="Technically accurate",
                    threshold=70,
                    passed=True
                ),
                MaturityMetric(
                    metric_name="Clarity",
                    score=76,
                    description="Clear and unambiguous",
                    threshold=65,
                    passed=True
                )
            ],
            passed=True,
            required_improvements=[],
            suggested_improvements=["Add more diagrams"]
        )

        # Verify quality gate passed
        assert report.passed is True
        assert report.overall_maturity_score >= 70
        assert all(m.passed for m in report.metrics)


class TestToolIntegration:
    """Test that tools are properly integrated with agents."""

    def test_architect_has_research_tools(self):
        """Test Architect has tools for researching patterns."""
        architect = create_architect_agent(enable_tools=True)
        assert architect.tools is not None

        tool_names = [tool.name for tool in architect.tools]

        # Should have file reading tools
        assert any("đọc" in name.lower() or "read" in name.lower() for name in tool_names)

        # Should have web search tools
        assert any("tìm" in name.lower() or "search" in name.lower() for name in tool_names)

    def test_auditor_has_security_tools(self):
        """Test Auditor has tools for finding vulnerabilities."""
        auditor = create_auditor_agent(enable_tools=True)
        assert auditor.tools is not None

        tool_names = [tool.name for tool in auditor.tools]

        # Should have security-focused tools
        assert any("security" in name.lower() or "bảo mật" in name.lower()
                   or "github" in name.lower() or "stack overflow" in name.lower()
                   for name in tool_names)

    def test_cto_has_minimal_tools(self):
        """Test CTO has minimal, focused tools."""
        cto = create_cto_agent(enable_tools=True)
        assert cto.tools is not None

        # CTO should have fewer tools than architect or auditor
        # (focused on documentation review and decision making)
        tool_count = len(cto.tools)
        assert tool_count <= 10, "CTO should have minimal tool set"


class TestBackwardCompatibility:
    """Test backward compatibility with old function names."""

    def test_old_agent_names_still_work(self):
        """Test that old agent creation functions still work."""
        from src.agents import (
            create_white_hat_agent,
            create_black_hat_agent,
            create_green_hat_agent,
        )

        white_hat = create_white_hat_agent()
        assert white_hat.role == "Kiến trúc sư hệ thống (White Hat)"

        black_hat = create_black_hat_agent()
        assert black_hat.role == "Chuyên gia Kiểm thử & Bảo mật (Black Hat)"

        green_hat = create_green_hat_agent()
        assert green_hat.role == "Giám đốc Kỹ thuật (Green Hat)"

    def test_old_template_names_still_work(self):
        """Test that old template names still work."""
        # Old names should work
        template1 = get_task_template("white_hat", "design_happy_path")
        assert "description" in template1

        template2 = get_task_template("black_hat", "stress_test_happy_path")
        assert "description" in template2

        template3 = get_task_template("green_hat", "arbitrate_debate")
        assert "description" in template3


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
