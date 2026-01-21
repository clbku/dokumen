"""
Test configuration and fixtures for Deep-Spec AI testing.

This module provides:
- Mock LLM responses for avoiding API calls during tests
- Sample data for testing agent outputs
- Schema validation helpers
- Integration test helpers
"""

import pytest
import os
import sys
import json
from unittest.mock import MagicMock
from typing import Dict, Any

# Add src to pythonpath
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


# === LLM Mock Fixtures ===

@pytest.fixture
def mock_llm_response(mocker):
    """Mocks the LLM response to avoid API calls."""
    mock = mocker.patch('src.utils.llm_provider.get_agent_llm')
    mock_llm = MagicMock()
    mock.return_value = mock_llm
    return mock_llm


@pytest.fixture
def sample_architect_response() -> str:
    """
    Sample response from Senior System Architect (White Hat).
    Đây là output đúng định dạng mà Architect nên trả về.
    """
    return json.dumps({
        "feature_id": "USER-REG-001",
        "feature_name": "User Registration",
        "description": "Đăng ký người dùng mới với email và password",
        "steps": [
            {
                "step_number": 1,
                "actor": "User",
                "action": "Nhập email và password vào form đăng ký",
                "outcome": "Form validation pass",
                "involved_components": ["frontend", "api-gateway"],
                "error_scenario": None,
                "fallback_step": None,
                "is_critical": False,
                "retry_count": None
            },
            {
                "step_number": 2,
                "actor": "System",
                "action": "Validate email format và password strength",
                "outcome": "Email hợp lệ, password mạnh",
                "involved_components": ["api-gateway", "validation-service"],
                "error_scenario": "Email không hợp lệ hoặc password yếu",
                "fallback_step": None,
                "is_critical": True,
                "retry_count": None
            },
            {
                "step_number": 3,
                "actor": "System",
                "action": "Check email đã tồn tại chưa trong database",
                "outcome": "Email chưa tồn tại",
                "involved_components": ["user-service", "postgres-db"],
                "error_scenario": "Email đã được sử dụng",
                "fallback_step": None,
                "is_critical": True,
                "retry_count": None
            },
            {
                "step_number": 4,
                "actor": "System",
                "action": "Hash password và tạo user record",
                "outcome": "User record created successfully",
                "involved_components": ["user-service", "postgres-db"],
                "error_scenario": "Database connection failed",
                "fallback_step": None,
                "is_critical": True,
                "retry_count": 3
            },
            {
                "step_number": 5,
                "actor": "System",
                "action": "Gửi verification email",
                "outcome": "Email sent queue",
                "involved_components": ["notification-service", "email-queue"],
                "error_scenario": "Email service unavailable",
                "fallback_step": 6,
                "is_critical": False,
                "retry_count": 2
            },
            {
                "step_number": 6,
                "actor": "System",
                "action": "Return success response với user ID",
                "outcome": "201 Created response",
                "involved_components": ["api-gateway"],
                "error_scenario": None,
                "fallback_step": None,
                "is_critical": True,
                "retry_count": None
            }
        ],
        "pre_conditions": [
            "User có email chưa đăng ký",
            "User có password mạnh (ít nhất 8 ký tự, có chữ hoa, số, ký tự đặc biệt)",
            "Database đang hoạt động bình thường"
        ],
        "post_conditions": [
            "User record tồn tại trong database",
            "Password đã được hash",
            "Verification email đã được queue",
            "User ID được trả về cho client"
        ],
        "business_value": "Cho phép người dùng mới đăng ký tài khoản, mở rộng user base"
    }, ensure_ascii=False)


@pytest.fixture
def sample_auditor_response() -> str:
    """
    Sample response from QA & Security Auditor (Black Hat).
    Đây là output đúng định dạng với ít nhất 5 edge cases thực tế.
    """
    return json.dumps({
        "report_id": "STRESS-USER-REG-001",
        "happy_path_id": "USER-REG-001",
        "feature_name": "User Registration",
        "edge_cases": [
            {
                "scenario_id": "EDGE-USER-REG-001",
                "description": "Email injection attack - user nhập malicious email header",
                "trigger_condition": "User nhập email chứa '\\r\\n' hoặc 'Cc:' characters",
                "expected_failure": "Email header injection, có thể spam cho người khác",
                "severity": "High",
                "likelihood": "Medium",
                "detection_method": "Test với email payload: 'test@example.com\\r\\nCc:victim@example.com'",
                "related_components": ["notification-service"],
                "related_step": 5,
                "mitigation": {
                    "description": "Validate và sanitize email input trước khi gửi",
                    "technical_implementation": "Sử dụng regex strict email validation, reject emails với special characters",
                    "implementation_complexity": "Low",
                    "estimated_effort": "2 giờ"
                }
            },
            {
                "scenario_id": "EDGE-USER-REG-002",
                "description": "Duplicate registration request - user click register button nhiều lần",
                "trigger_condition": "User spam click register button hoặc network latency",
                "expected_failure": "Tạo nhiều user records với cùng email, race condition",
                "severity": "High",
                "likelihood": "High",
                "detection_method": "Test với concurrent requests cùng email trong 100ms",
                "related_components": ["user-service", "postgres-db", "api-gateway"],
                "related_step": 4,
                "mitigation": {
                    "description": "Implement idempotency key và unique constraint",
                    "technical_implementation": "Add unique index on email column, use idempotency key from client",
                    "implementation_complexity": "Medium",
                    "estimated_effort": "1 ngày"
                }
            },
            {
                "scenario_id": "EDGE-USER-REG-003",
                "description": "SQL Injection trong email check query",
                "trigger_condition": "User nhập email chứa SQL payload: 'test@example.com' OR '1'='1'",
                "expected_failure": "Query return true, bypass email uniqueness check",
                "severity": "Critical",
                "likelihood": "Medium",
                "detection_method": "Test với SQL payloads trong email field",
                "related_components": ["user-service", "postgres-db"],
                "related_step": 3,
                "mitigation": {
                    "description": "Sử dụng parameterized queries",
                    "technical_implementation": "Use prepared statements hoặc ORM with parameter binding",
                    "implementation_complexity": "Low",
                    "estimated_effort": "4 giờ"
                }
            },
            {
                "scenario_id": "EDGE-USER-REG-004",
                "description": "Database connection pool exhausted khi high traffic",
                "trigger_condition": "Nhiều registration requests đồng thời vượt quá pool size",
                "expected_failure": "Requests timeout hoặc fail với connection error",
                "severity": "High",
                "likelihood": "Medium",
                "detection_method": "Load test với 1000+ concurrent requests",
                "related_components": ["user-service", "postgres-db"],
                "related_step": 4,
                "mitigation": {
                    "description": "Configure connection pooling và circuit breaker",
                    "technical_implementation": "Set max_connections=20, connection_timeout=5s, retry with backoff",
                    "implementation_complexity": "Medium",
                    "estimated_effort": "2 ngày"
                }
            },
            {
                "scenario_id": "EDGE-USER-REG-005",
                "description": "Password hash quá chậm khi dùng weak hashing algorithm",
                "trigger_condition": "User tạo password cực dài (1000+ chars) với bcrypt",
                "expected_failure": "Hash operation timeout > 30s",
                "severity": "Medium",
                "likelihood": "Low",
                "detection_method": "Test với password length 1000+ characters",
                "related_components": ["user-service"],
                "related_step": 4,
                "mitigation": {
                    "description": "Limit password length và optimize hash algorithm",
                    "technical_implementation": "Max password length 128 chars, use Argon2id with reasonable memory cost",
                    "implementation_complexity": "Low",
                    "estimated_effort": "3 giờ"
                }
            },
            {
                "scenario_id": "EDGE-USER-REG-006",
                "description": "Email service timeout - verification email không gửi được",
                "trigger_condition": "Email provider down hoặc network partition",
                "expected_failure": "User registration fail dù user record đã tạo",
                "severity": "Medium",
                "likelihood": "Medium",
                "detection_method": "Mock email service timeout trong test",
                "related_components": ["notification-service", "email-queue"],
                "related_step": 5,
                "mitigation": {
                    "description": "Make email sending async với fallback",
                    "technical_implementation": "Use message queue (RabbitMQ/Redis) với retry policy, return success immediately",
                    "implementation_complexity": "High",
                    "estimated_effort": "3 ngày"
                }
            }
        ],
        "resilience_score": 65,
        "coverage_score": 85,
        "review_summary": "Thiết kế có several critical vulnerabilities cần fix: SQL injection, race conditions, và lack of idempotency",
        "critical_findings": [
            "SQL injection vulnerability ở step 3 - CRITICAL",
            "Race condition ở duplicate registration - HIGH",
            "Missing idempotency key cho registration requests - HIGH"
        ],
        "recommendations": [
            "Implement rate limiting cho registration endpoint",
            "Add CAPTCHA để prevent automated registration spam",
            "Implement email verification timeout mechanism"
        ]
    }, ensure_ascii=False)


@pytest.fixture
def sample_cto_response() -> str:
    """
    Sample response from Chief Technology Officer (Green Hat).
    Đây là output đúng định dạng với consensus decisions.
    """
    return json.dumps({
        "decision_id": "DECISION-001",
        "topic": "User Registration - Duplicate Prevention Strategy",
        "target_id": "USER-REG-001",
        "decision": "Implement idempotency key + database unique constraint on email",
        "reasoning": "Architect đề xuất application-level check, Auditor chỉ ra race condition vulnerability. Kết hợp cả database-level unique constraint (đảm bảo data integrity) với application-level idempotency key (để client retry) là solution cân bằng và robust.",
        "dissenting_opinions": [
            "Architect đề xuất chỉ dùng application check với mutex lock - đã bác bỏ vì không scale across instances",
            "Auditor đề xuất only unique constraint - đã bác bỏ vì không cho phép client retry khi network error"
        ],
        "participating_agents": ["WhiteHat", "BlackHat", "GreenHat"],
        "confidence_score": 0.9,
        "impact_area": ["user-service", "postgres-db", "api-gateway"]
    }, ensure_ascii=False)


# === Bad Response Examples for Testing Personality ===

@pytest.fixture
def bad_architect_response_too_optimistic() -> str:
    """
    Bad example: Architect không đề cập error handling,
    tập trung quá nhiều vào happy path mà bỏ qua edge cases.
    Đây là VÍ DỆT KHÔNG NÊN CÓ nhưng hữu ích để test.
    """
    return json.dumps({
        "feature_id": "USER-REG-001",
        "feature_name": "User Registration",
        "description": "Đăng ký người dùng mới",
        "steps": [
            {
                "step_number": 1,
                "actor": "User",
                "action": "Đăng ký",
                "outcome": "Thành công",
                "involved_components": [],
                "error_scenario": None,
                "fallback_step": None,
                "is_critical": False,
                "retry_count": None
            }
        ],
        "pre_conditions": ["User có email"],
        "post_conditions": ["User created"],
        "business_value": "Grow user base"
    }, ensure_ascii=False)


@pytest.fixture
def bad_auditor_response_vague() -> str:
    """
    Bad example: Auditor chỉ đưa ra lỗi chung chung,
    không tìm được lỗi logic thực tế.
    Đây là VÍ DỆT KHÔNG NÊN CÓ nhưng hữu ích để test.
    """
    return json.dumps({
        "report_id": "STRESS-USER-REG-001",
        "happy_path_id": "USER-REG-001",
        "feature_name": "User Registration",
        "edge_cases": [
            {
                "scenario_id": "EDGE-001",
                "description": "Server error",
                "trigger_condition": "Server bị lỗi",
                "expected_failure": "System crash",
                "severity": "High",
                "likelihood": "Medium",
                "detection_method": "Test",
                "related_components": ["server"],
                "related_step": 1,
                "mitigation": {
                    "description": "Fix server",
                    "technical_implementation": "Debug và fix",
                    "implementation_complexity": "Medium",
                    "estimated_effort": "1 tuần"
                }
            },
            {
                "scenario_id": "EDGE-002",
                "description": "Network error",
                "trigger_condition": "Mất mạng",
                "expected_failure": "Cannot connect",
                "severity": "High",
                "likelihood": "Medium",
                "detection_method": "Test",
                "related_components": ["network"],
                "related_step": 2,
                "mitigation": {
                    "description": "Check network",
                    "technical_implementation": "Verify connection",
                    "implementation_complexity": "Low",
                    "estimated_effort": "1 ngày"
                }
            }
        ],
        "resilience_score": 50,
        "coverage_score": 40,
        "review_summary": "Có nhiều lỗi tiềm ẩn",
        "critical_findings": ["Server có thể lỗi", "Network có thể mất"],
        "recommendations": ["Test kỹ hơn"]
    }, ensure_ascii=False)


@pytest.fixture
def bad_response_ai_hallucination() -> str:
    """
    Bad example: Agent tự xưng là AI model.
    Đây là VÍ DỆT KHÔNG NÊN CÓ nhưng hữu ích để test.
    """
    return "Tôi là một mô hình ngôn ngữ AI được训练 bởi Anthropic. Tôi có thể giúp bạn thiết kế hệ thống..."


# === Helper Functions ===

def validate_schema_compliance(json_str: str, schema_class: type) -> Dict[str, Any]:
    """
    Validate JSON string against a Pydantic schema.

    Args:
        json_str: JSON string to validate
        schema_class: Pydantic schema class

    Returns:
        Dict with keys: 'valid' (bool), 'data' (dict), 'errors' (list)

    Examples:
        >>> from src.schemas import HappyPath
        >>> result = validate_schema_compliance(sample_json, HappyPath)
        >>> assert result['valid'] == True
    """
    try:
        data = json.loads(json_str)
        instance = schema_class(**data)
        return {
            'valid': True,
            'data': instance.model_dump(),
            'errors': []
        }
    except json.JSONDecodeError as e:
        return {
            'valid': False,
            'data': None,
            'errors': [f"JSON parsing error: {str(e)}"]
        }
    except Exception as e:
        return {
            'valid': False,
            'data': None,
            'errors': [f"Schema validation error: {str(e)}"]
        }


def check_agent_personality(response_text: str, agent_role: str) -> Dict[str, Any]:
    """
    Check if agent response matches expected personality.

    Args:
        response_text: Agent's response text
        agent_role: One of 'architect', 'auditor', 'cto'

    Returns:
        Dict with personality check results
    """
    from src.schemas import RiskLevel

    result = {
        'role_correct': True,
        'no_ai_hallucination': True,
        'language_correct': True,  # Vietnamese
        'focus_correct': True,
        'issues': []
    }

    # Check for AI hallucination patterns
    ai_patterns = [
        'tôi là một mô hình ngôn ngữ',
        'i am an ai language model',
        'i am an artificial intelligence',
        'as an artificial intelligence',
        'as an ai',
        'là một ai',
        'là chatgpt',
        'là claude',
        'là anthropic',
        'được tạo bởi',
        'được xây dựng như',
        'được xây dựng như một',
        'built as an ai',
    ]
    response_lower = response_text.lower()
    for pattern in ai_patterns:
        if pattern in response_lower:
            result['no_ai_hallucination'] = False
            result['issues'].append(f"Agent tự xưng là AI: '{pattern}'")
            break

    # Role-specific checks
    if agent_role == 'architect':
        # Architect nên tập trung vào happy path, không nên quá pessimistic
        negative_keywords = ['fail', 'error', 'vấn đề', 'lỗi', 'risk', 'hỏng']
        negative_count = sum(1 for kw in negative_keywords if kw in response_lower)
        if negative_count > 20:  # Arbitrary threshold
            result['focus_correct'] = False
            result['issues'].append(f"Architect quá pessimistic: {negative_count} negative keywords")

    elif agent_role == 'auditor':
        # Auditor nên tìm edge cases cụ thể, không chung chung
        try:
            data = json.loads(response_text)
            if 'edge_cases' in data:
                edge_cases = data['edge_cases']

                # Check minimum edge cases
                if len(edge_cases) < 5:
                    result['focus_correct'] = False
                    result['issues'].append(f"Auditor chỉ tìm {len(edge_cases)} edge cases, cần ít nhất 5")

                # Check for vague descriptions
                vague_patterns = ['server error', 'network error', 'lỗi server', 'lỗi mạng', 'system fail']
                for ec in edge_cases:
                    desc = ec.get('description', '').lower()
                    trigger = ec.get('trigger_condition', '').lower()
                    if any(vp in desc or vp in trigger for vp in vague_patterns):
                        result['focus_correct'] = False
                        result['issues'].append(f"Auditor đưa ra edge case vague: {ec.get('description', '')}")
                        break
        except json.JSONDecodeError:
            pass

    # Check language (Vietnamese)
    vietnamese_indicators = ['là', 'của', 'và', 'để', 'với', 'không', 'có', 'được']
    if not any(indicator in response_text for indicator in vietnamese_indicators):
        result['language_correct'] = False
        result['issues'].append("Response không có dấu hiệu tiếng Việt")

    return result


@pytest.fixture
def schema_validator():
    """Fixture for schema validation function."""
    return validate_schema_compliance


@pytest.fixture
def personality_checker():
    """Fixture for personality checking function."""
    return check_agent_personality


# === Integration Test Helpers ===

@pytest.fixture
def sample_user_requirements() -> str:
    """Sample user requirements for testing."""
    return """
    # Yêu cầu: Hệ thống Đăng nhập Người dùng

    ## Functional Requirements
    1. User có thể đăng nhập với email và password
    2. System kiểm tra email và password có đúng không
    3. Nếu đúng, trả về JWT token
    4. Nếu sai, trả về lỗi 401

    ## Non-Functional Requirements
    - Response time < 500ms
    - Support 1000 concurrent users
    - Password phải được hash trước khi lưu
    """


@pytest.fixture
def temp_test_dir(tmp_path):
    """Create a temporary directory for test files."""
    test_dir = tmp_path / "test_files"
    test_dir.mkdir()
    return test_dir
