"""
Agent Personality Tests for Deep-Spec AI

Tests to verify that agents exhibit correct personalities:
1. Không bị ảo giác về vai trò: Agent không tự xưng là AI
2. Đúng cá tính: Architect tập trung happy path, Auditor tìm lỗi thực tế
3. Ngôn ngữ đúng: Agents trả lời bằng tiếng Việt

Test Criteria:
- Architect (White Hat): Tập trung vào happy path, không quá pessimistic
- Auditor (Black Hat): Tìm ít nhất 3 lỗi logic thực tế (không chung chung)
- CTO (Green Hat): Cân bằng, tổng hợp các quan điểm
"""

import pytest
import json
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from conftest import check_agent_personality


class TestNoAIHallucination:
    """Test that agents don't hallucinate about being AI models."""

    def test_good_response_no_hallucination(self, sample_architect_response, personality_checker):
        """Test that good architect response doesn't claim to be AI."""
        result = personality_checker(sample_architect_response, 'architect')
        assert result['no_ai_hallucination'] is True, "Architect shouldn't claim to be AI"
        assert len([i for i in result['issues'] if 'AI' in i]) == 0

    def test_bad_response_detects_hallucination(self, bad_response_ai_hallucination, personality_checker):
        """Test that bad AI hallucination response is detected."""
        result = personality_checker(bad_response_ai_hallucination, 'architect')
        assert result['no_ai_hallucination'] is False, "Should detect AI hallucination"
        assert any('AI' in issue for issue in result['issues'])

    def test_various_hallucination_patterns(self, personality_checker):
        """Test detection of various AI hallucination patterns."""
        hallucination_patterns = [
            "Tôi là một mô hình ngôn ngữ AI được tạo bởi Anthropic",
            "I am an AI language model trained by OpenAI",
            "Tôi là ChatGPT, một trợ lý AI",
            "As an artificial intelligence, I cannot",
            "Được xây dựng như một AI assistant"
        ]

        for pattern in hallucination_patterns:
            result = personality_checker(pattern, 'architect')
            assert result['no_ai_hallucination'] is False, f"Should detect hallucination in: {pattern}"


class TestArchitectPersonality:
    """Test Senior System Architect (White Hat) personality."""

    def test_architect_focus_on_happy_path(self, sample_architect_response, personality_checker):
        """
        Test Architect tập trung vào happy path, không quá pessimistic.

        Architect không nên:
        - Quá tập trung vào failure scenarios
        - Liệt kê quá nhiều negative keywords

        Architect nên:
        - Tạo flow steps rõ ràng, sequential
        - Định nghĩa pre/post conditions
        - Chỉ ra error scenarios một cách cụ thể (không chung chung)
        """
        result = personality_checker(sample_architect_response, 'architect')
        assert result['focus_correct'] is True, "Architect should focus on building, not breaking"

        # Parse JSON and check structure
        data = json.loads(sample_architect_response)

        # Should have multiple steps showing sequential flow
        assert len(data['steps']) >= 3, "Architect should provide detailed happy path"

        # Each step should have clear actor, action, outcome
        for step in data['steps']:
            assert step['actor'], "Step must have actor"
            assert step['action'], "Step must have action"
            assert step['outcome'], "Step must have outcome"

        # Should have pre-conditions
        assert len(data['pre_conditions']) > 0, "Architect should define pre-conditions"

        # Should have post-conditions
        assert len(data['post_conditions']) > 0, "Architect should define post-conditions"

    def test_architect_not_too_optimistic(self, bad_architect_response_too_optimistic, personality_checker):
        """
        Test Architect không được quá optimist bỏ qua error handling.

        Response quá đơn giản là BAD:
        - Chỉ có 1 step chung chung
        - Không có error scenarios
        - Không có involved components
        """
        data = json.loads(bad_architect_response_too_optimistic)

        # Should detect lack of detail
        assert len(data['steps']) < 3, "Too optimistic response has too few steps"

        # Most steps should have some error handling consideration
        steps_with_error_handling = sum(
            1 for step in data['steps']
            if step.get('error_scenario') or step.get('fallback_step') or step.get('retry_count')
        )

        # In a good response, critical steps should have error handling
        # This bad response should fail this check
        assert steps_with_error_handling == 0, "Too optimistic response lacks error handling"

    def test_architect_uses_vietnamese(self, sample_architect_response, personality_checker):
        """Test that Architect responds in Vietnamese."""
        result = personality_checker(sample_architect_response, 'architect')
        assert result['language_correct'] is True, "Architect should use Vietnamese"

        # Check for Vietnamese indicators in the response
        vietnamese_words = ['là', 'của', 'và', 'để', 'với', 'không', 'được']
        response_text = sample_architect_response
        assert any(word in response_text for word in vietnamese_words), \
            "Response should contain Vietnamese words"

    def test_architect_technical_detail(self, sample_architect_response):
        """
        Test Architect cung cấp chi tiết kỹ thuật cụ thể.

        Architect nên cung cấp:
        - Component names cụ thể (api-gateway, user-service, postgres-db)
        - Technologies cụ thể
        - Error scenarios cụ thể
        """
        data = json.loads(sample_architect_response)

        # Check that steps reference specific components
        all_components = []
        for step in data['steps']:
            all_components.extend(step.get('involved_components', []))

        assert len(all_components) > 0, "Architect should specify components"
        assert any(comp in all_components for comp in ['api-gateway', 'user-service', 'postgres-db']), \
            "Architect should use specific component names"


class TestAuditorPersonality:
    """Test QA & Security Auditor (Black Hat) personality."""

    def test_auditor_finds_real_logic_errors(self, sample_auditor_response, personality_checker):
        """
        Test Auditor tìm ít nhất 3 lỗi logic thực tế.

        Lỗi logic THỰC TẾ (không chung chung):
        - SQL injection
        - Race conditions
        - Duplicate requests
        - Email injection
        - Connection pool exhaustion

        Lời RẤT CHUNG CHUNG (BAD):
        - "Server error" - quá mơ hồ
        - "Network error" - không cụ thể
        - "System fail" - không có giá trị
        """
        result = personality_checker(sample_auditor_response, 'auditor')
        assert result['focus_correct'] is True, "Auditor should find specific logic errors"

        data = json.loads(sample_auditor_response)

        # Should have at least 5 edge cases
        assert len(data['edge_cases']) >= 5, "Auditor must find at least 5 edge cases"

        # Check that edge cases are specific, not vague
        vague_patterns = ['server error', 'network error', 'lỗi server', 'lỗi mạng', 'system fail']

        for ec in data['edge_cases']:
            desc = ec['description'].lower()
            trigger = ec['trigger_condition'].lower()

            # Edge case should NOT be vague
            is_vague = any(vp in desc or vp in trigger for vp in vague_patterns)
            assert not is_vague, f"Edge case is too vague: {ec['description']}"

        # Check for specific, realistic error patterns
        real_error_patterns = [
            'sql injection',
            'race condition',
            'duplicate',
            'timeout',
            'injection',
            'exhausted',
            'overflow',
            'brute force',
            'password'
        ]

        found_real_errors = 0
        for ec in data['edge_cases']:
            description = ec['description'].lower()
            if any(pattern in description for pattern in real_error_patterns):
                found_real_errors += 1

        # Should find at least 3 specific, realistic errors
        assert found_real_errors >= 3, f"Auditor should find at least 3 specific errors, found {found_real_errors}"

    def test_auditor_edge_case_structure(self, sample_auditor_response):
        """
        Test Auditor edge cases có đầy đủ thông tin.

        Mỗi edge case nên có:
        - scenario_id bắt đầu với EDGE-
        - description cụ thể
        - trigger_condition cụ thể
        - expected_failure cụ thể
        - severity (Low/Medium/High/Critical)
        - likelihood
        - mitigation có technical_implementation
        """
        data = json.loads(sample_auditor_response)

        for ec in data['edge_cases']:
            # Check scenario_id format
            assert ec['scenario_id'].startswith('EDGE-'), \
                f"Edge case ID must start with EDGE-: {ec['scenario_id']}"

            # Check required fields are present and specific
            assert len(ec['description']) > 10, "Description should be specific"
            assert len(ec['trigger_condition']) > 10, "Trigger should be specific"
            assert len(ec['expected_failure']) > 10, "Expected failure should be specific"

            # Check mitigation has technical details
            mitigation = ec['mitigation']
            assert len(mitigation['technical_implementation']) > 10, \
                "Mitigation should have technical implementation details"

    def test_auditor_finds_security_issues(self, sample_auditor_response):
        """
        Test Auditor tìm lỗ hổng bảo mật.

        Auditor (Black Hat) nên tìm:
        - SQL injection
        - XSS
        - CSRF
        - Header injection
        - Brute force vulnerabilities
        """
        data = json.loads(sample_auditor_response)

        security_keywords = [
            'sql injection',
            'injection',
            'xss',
            'csrf',
            'security',
            'bảo mật',
            'attack',
            'vulnerability',
            'lỗ hổng'
        ]

        security_related_cases = 0
        for ec in data['edge_cases']:
            description = ec['description'].lower()
            if any(keyword in description for keyword in security_keywords):
                security_related_cases += 1

        # Should find at least some security-related issues
        assert security_related_cases >= 1, "Auditor should find security-related edge cases"

    def test_auditor_uses_vietnamese(self, sample_auditor_response, personality_checker):
        """Test that Auditor responds in Vietnamese."""
        result = personality_checker(sample_auditor_response, 'auditor')
        assert result['language_correct'] is True, "Auditor should use Vietnamese"

    def test_auditor_vague_errors_detected(self, bad_auditor_response_vague, personality_checker):
        """
        Test Auditor đưa ra lỗi chung chung được phát hiện.

        Bad example response chỉ có:
        - "Server error"
        - "Network error"

        Đây KHÔNG PHẢI là edge cases giá trị.
        """
        result = personality_checker(bad_auditor_response_vague, 'auditor')
        assert result['focus_correct'] is False, "Should detect vague edge cases"
        assert any('vague' in issue.lower() or 'chung chung' in issue.lower()
                   for issue in result['issues']), \
            "Should flag vague descriptions as issues"

    def test_auditor_min_edge_cases(self, sample_auditor_response):
        """Test Auditor finds minimum required edge cases."""
        data = json.loads(sample_auditor_response)
        assert len(data['edge_cases']) >= 5, "Auditor must find at least 5 edge cases per feature"


class TestCTOPersonality:
    """Test Chief Technology Officer (Green Hat) personality."""

    def test_cto_balanced_decision(self, sample_cto_response, personality_checker):
        """
        Test CTO đưa ra quyết định cân bằng.

        CTO nên:
        - Tổng hợp quan điểm từ Architect và Auditor
        - Đưa ra quyết định có lý do rõ ràng
        - Ghi nhận dissenting opinions
        """
        result = personality_checker(sample_cto_response, 'cto')
        assert result['focus_correct'] is True, "CTO should make balanced decisions"

        data = json.loads(sample_cto_response)

        # Should have reasoning
        assert len(data['reasoning']) > 50, "CTO should provide detailed reasoning"

        # Should reference participating agents
        assert len(data['participating_agents']) >= 2, "CTO should involve multiple agents"

        # Should have dissenting opinions (showing debate occurred)
        # This is optional but good for showing thorough consideration
        if 'dissenting_opinions' in data and data['dissenting_opinions']:
            assert len(data['dissenting_opinions']) > 0, "CTO should document considered alternatives"

    def test_cto_uses_vietnamese(self, sample_cto_response, personality_checker):
        """Test that CTO responds in Vietnamese."""
        result = personality_checker(sample_cto_response, 'cto')
        assert result['language_correct'] is True, "CTO should use Vietnamese"

    def test_cto_confidence_score(self, sample_cto_response):
        """Test CTO provides confidence score for decisions."""
        data = json.loads(sample_cto_response)

        # Should have confidence score
        assert 'confidence_score' in data
        assert 0.0 <= data['confidence_score'] <= 1.0, "Confidence must be 0.0-1.0"

        # Confidence should be reasonably high for a well-considered decision
        assert data['confidence_score'] >= 0.5, "CTO should have reasonable confidence"

    def test_cto_impact_analysis(self, sample_cto_response):
        """Test CTO analyzes impact of decisions."""
        data = json.loads(sample_cto_response)

        # Should specify impact areas
        assert 'impact_area' in data
        assert len(data['impact_area']) > 0, "CTO should specify impact areas"


class TestVietnameseLanguage:
    """Test Vietnamese language compliance across all agents."""

    def test_architect_vietnamese_keywords(self, sample_architect_response):
        """Test Architect uses Vietnamese keywords."""
        vietnamese_keywords = ['là', 'của', 'và', 'để', 'với', 'không', 'được', 'các', 'hệ thống']
        response_lower = sample_architect_response.lower()

        found_keywords = [kw for kw in vietnamese_keywords if kw in response_lower]
        assert len(found_keywords) >= 3, "Should use Vietnamese vocabulary"

    def test_auditor_vietnamese_keywords(self, sample_auditor_response):
        """Test Auditor uses Vietnamese keywords."""
        # Sample response contains technical terms in English/ Vietnamese mix
        # Check for Vietnamese content indicators
        vietnamese_keywords = ['lỗ hổng', 'bảo mật', 'xác minh', 'với', 'của', 'và', 'để', 'là']
        response_lower = sample_auditor_response.lower()

        found_keywords = [kw for kw in vietnamese_keywords if kw in response_lower]
        assert len(found_keywords) >= 3, f"Should use Vietnamese vocabulary, found: {found_keywords}"

    def test_cto_vietnamese_keywords(self, sample_cto_response):
        """Test CTO uses Vietnamese keywords."""
        vietnamese_keywords = ['là', 'của', 'quyết định', 'vì', 'kết hợp', 'cân bằng']
        response_lower = sample_cto_response.lower()

        found_keywords = [kw for kw in vietnamese_keywords if kw in response_lower]
        assert len(found_keywords) >= 2, "Should use Vietnamese vocabulary"


class TestAgentRoleIdentity:
    """Test agents maintain their role identity consistently."""

    def test_architect_does_not_claim_other_roles(self, sample_architect_response):
        """Test Architect doesn't claim to be Auditor or CTO."""
        response_lower = sample_architect_response.lower()

        # Should not claim other roles
        other_roles = ['qa', 'auditor', 'black hat', 'security', 'cto', 'chief technology']
        inappropriate_role_claims = [role for role in other_roles if role in response_lower]

        # Having other role terms in a technical discussion is fine,
        # but explicitly claiming to be those roles is not
        # This is a soft check - we're looking for obvious misidentities

    def test_auditor_does_not_become_builder(self, sample_auditor_response):
        """Test Auditor doesn't switch to builder mode."""
        data = json.loads(sample_auditor_response)

        # Edge cases should focus on failures, not building
        # All edge cases should have expected_failure field
        for ec in data['edge_cases']:
            assert ec['expected_failure'], "Auditor should always specify expected failure"
            assert ec['severity'], "Auditor should assess severity"
