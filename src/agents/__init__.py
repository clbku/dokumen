"""
Deep-Spec AI Agents Package

This package provides the three core agents for the Deep-Spec AI system:
- Senior System Architect (White Hat): Designs Happy Paths
- QA & Security Auditor (Black Hat): Finds edge cases
- Chief Technology Officer (Green Hat): Makes decisions and runs quality gates

Usage:
    from src.agents import create_deep_spec_crew

    # Create all three agents
    architect, auditor, cto = create_deep_spec_crew()

    # Or create individually
    from src.agents import create_architect_agent, create_auditor_agent, create_cto_agent

    architect = create_architect_agent()
    auditor = create_auditor_agent()
    cto = create_cto_agent()
"""

from typing import Literal
from crewai import Agent

from src.agents.senior_system_architect import (
    create_white_hat_agent as create_architect_agent,
    get_white_hat_task_template as get_architect_task_template,
    WHITE_HAT_TASK_TEMPLATES as ARCHITECT_TASK_TEMPLATES,
)
from src.agents.qa_security_auditor import (
    create_black_hat_agent as create_auditor_agent,
    get_black_hat_task_template as get_auditor_task_template,
    BLACK_HAT_TASK_TEMPLATES as AUDITOR_TASK_TEMPLATES,
    EDGE_CASE_CATEGORIES,
    get_edge_case_prompts_for_category,
)
from src.agents.chief_technology_officer import (
    create_green_hat_agent as create_cto_agent,
    get_green_hat_task_template as get_cto_task_template,
    GREEN_HAT_TASK_TEMPLATES as CTO_TASK_TEMPLATES,
    QUALITY_GATE_THRESHOLDS,
    get_quality_threshold,
    get_minimum_acceptable_score,
)

# Backward compatibility aliases
create_white_hat_agent = create_architect_agent
create_black_hat_agent = create_auditor_agent
create_green_hat_agent = create_cto_agent

get_white_hat_task_template = get_architect_task_template
get_black_hat_task_template = get_auditor_task_template
get_green_hat_task_template = get_cto_task_template

WHITE_HAT_TASK_TEMPLATES = ARCHITECT_TASK_TEMPLATES
BLACK_HAT_TASK_TEMPLATES = AUDITOR_TASK_TEMPLATES
GREEN_HAT_TASK_TEMPLATES = CTO_TASK_TEMPLATES


# === Agent Factory Functions ===


def create_deep_spec_crew(
    verbose: bool = True,
    memory: bool = True,
    allow_delegation: bool = True,
) -> tuple[Agent, Agent, Agent]:
    """
    Tạo và cấu hình cả ba agent Deep-Spec AI.

    Đây là cách được khuyến nghị để khởi tạo agent crew cho một phiên Deep-Spec.
    Trả về agents theo thứ tự: Architect, Auditor, CTO

    Args:
        verbose: Bật logging chi tiết cho tất cả agents (mặc định: True)
        memory: Bật agent memory để lưu ngữ cảnh (mặc định: True)
        allow_delegation: Cho phép agents ủy quyền tasks (mặc định: True)
                       Lưu ý: Architect và Auditor có tắt delegation mặc định

    Returns:
        tuple[Agent, Agent, Agent]: (architect, auditor, cto)

    Examples:
        >>> from src.agents import create_deep_spec_crew
        >>> architect, auditor, cto = create_deep_spec_crew()

        >>> # Use in a Crew
        >>> from crewai import Crew
        >>> crew = Crew(
        ...     agents=[architect, auditor, cto],
        ...     tasks=[...],
        ...     process="sequential"
        ... )
    """
    architect = create_architect_agent(
        verbose=verbose,
        memory=memory,
        allow_delegation=False,  # Architect doesn't delegate
    )

    auditor = create_auditor_agent(
        verbose=verbose,
        memory=memory,
        allow_delegation=False,  # Auditor doesn't delegate
    )

    cto = create_cto_agent(
        verbose=verbose,
        memory=memory,
        allow_delegation=allow_delegation,  # CTO may delegate back
    )

    return architect, auditor, cto


def create_agent_by_role(
    role: Literal["white_hat", "black_hat", "green_hat", "architect", "auditor", "cto"],
    verbose: bool = True,
    memory: bool = True,
    allow_delegation: bool = False,
) -> Agent:
    """
    Tạo một agent duy nhất theo tên role.

    Hữu ích khi bạn chỉ cần các agent cụ thể thay vì cả crew.

    Args:
        role: Role của agent ("white_hat"/"architect", "black_hat"/"auditor", "green_hat"/"cto")
        verbose: Bật logging chi tiết (mặc định: True)
        memory: Bật agent memory (mặc định: True)
        allow_delegation: Cho phép task delegation (mặc định: False)

    Returns:
        Agent: Agent đã được cấu hình cho role được chỉ định

    Raises:
        ValueError: Nếu role không tồn tại

    Examples:
        >>> from src.agents import create_agent_by_role
        >>> auditor = create_agent_by_role("auditor")
        >>> cto = create_agent_by_role("cto", allow_delegation=True)
    """
    role_mapping = {
        "white_hat": create_architect_agent,
        "architect": create_architect_agent,
        "black_hat": create_auditor_agent,
        "auditor": create_auditor_agent,
        "green_hat": create_cto_agent,
        "cto": create_cto_agent,
    }

    agent_func = role_mapping.get(role)
    if not agent_func:
        raise ValueError(
            f"Role không tồn tại: '{role}'. "
            f"Các roles có sẵn: {list(role_mapping.keys())}"
        )

    return agent_func(verbose, memory, allow_delegation)


# === Task Template Factory ===


def get_task_template(
    agent_role: Literal["white_hat", "black_hat", "green_hat", "architect", "auditor", "cto"],
    template_name: str,
) -> dict:
    """
    Lấy task template cho một agent role cụ thể.

    Task templates cung cấp descriptions và expected outputs được cấu hình trước
    cho các tasks của agent. Templates dùng Python format strings để tùy chỉnh.

    Args:
        agent_role: Role của agent ("white_hat"/"architect", "black_hat"/"auditor", "green_hat"/"cto")
        template_name: Tên của template cần lấy

    Returns:
        dict: Template với các khóa 'description' và 'expected_output'

    Raises:
        ValueError: Nếu agent_role hoặc template_name không tồn tại

    Examples:
        >>> from src.agents import get_task_template
        >>> template = get_task_template("architect", "design_happy_path")
        >>> description = template["description"].format(
        ...     feature_name="User Registration",
        ...     requirements="..."
        ... )
    """
    role_mapping = {
        "white_hat": get_architect_task_template,
        "architect": get_architect_task_template,
        "black_hat": get_auditor_task_template,
        "auditor": get_auditor_task_template,
        "green_hat": get_cto_task_template,
        "cto": get_cto_task_template,
    }

    template_func = role_mapping.get(agent_role)
    if not template_func:
        raise ValueError(
            f"Role không tồn tại: '{agent_role}'. "
            f"Các roles có sẵn: {list(role_mapping.keys())}"
        )

    return template_func(template_name)


# === Agent Information ===

AGENT_DESCRIPTIONS = {
    "white_hat": {
        "name": "Kiến trúc sư hệ thống (White Hat)",
        "provider": "Z.AI (glm-4.7)",
        "personality": "Lạc quan, chính xác, tập trung xây dựng",
        "strengths": [
            "Thiết kế kiến trúc sạch, khả thi",
            "Tạo Happy Paths có cấu trúc",
            "Định nghĩa cấu trúc dữ liệu chính xác",
            "Tránh over-engineering",
        ],
        "responsibilities": [
            "Thiết kế kiến trúc hệ thống (components, interactions)",
            "Tạo luồng Happy Path với logic từng bước",
            "Định nghĩa data models và API contracts",
            "Tạo system diagrams (Mermaid)",
        ],
    },
    "black_hat": {
        "name": "Chuyên gia Kiểm thử & Bảo mật (Black Hat)",
        "provider": "Google Gemini (gemini-3-pro-preview)",
        "personality": "Hoài nghi, tỉ mỉ, tập trung phá vỡ",
        "strengths": [
            "Tìm edge cases khó phát hiện",
            "Nhận diện lỗ hổng bảo mật",
            "Thách thức các giả định lạc quan",
            "Suy nghĩ về kịch bản tồi tệ nhất",
        ],
        "responsibilities": [
            "Stress test Happy Paths (tối thiểu 5 edge cases mỗi feature)",
            "Thực hiện security audit dùng framework STRIDE",
            "Nhận diện race conditions và mâu thuẫn trạng thái",
            "Cung cấp chiến lược giảm thiểu cụ thể",
        ],
    },
    "green_hat": {
        "name": "Giám đốc Kỹ thuật (Green Hat)",
        "provider": "Google Gemini (gemini-3-pro-preview)",
        "personality": "Cân bằng, quyết đoán, tập trung tổng hợp",
        "strengths": [
            "Trọng tài các tranh luận giữa agents",
            "Đưa ra quyết định kỹ thuật cân bằng",
            "Chạy quality gates và chấm điểm trưởng thành",
            "Ngăn chặn over-engineering",
        ],
        "responsibilities": [
            "Review và tổng hợp phản hồi từ agents",
            "Đưa ra quyết định đồng thuận với lý do rõ ràng",
            "Chạy quality gates (completeness, depth, correctness, clarity)",
            "Phê duyệt hoặc yêu cầu revision cho tài liệu",
        ],
    },
}


def get_agent_info(role: Literal["white_hat", "black_hat", "green_hat"]) -> dict:
    """
    Lấy thông tin chi tiết về một agent role.

    Hữu ích cho documentation, UI display, hoặc hiểu capabilities của agent.

    Args:
        role: Role của agent ("white_hat", "black_hat", "green_hat")

    Returns:
        dict: Thông tin agent bao gồm name, provider, personality, strengths, responsibilities

    Raises:
        ValueError: Nếu role không tồn tại

    Examples:
        >>> from src.agents import get_agent_info
        >>> info = get_agent_info("black_hat")
        >>> print(info["provider"])
        'Google Gemini (gemini-3-pro-preview)'
    """
    info = AGENT_DESCRIPTIONS.get(role)
    if not info:
        raise ValueError(
            f"Role không tồn tại: '{role}'. "
            f"Các roles có sẵn: {list(AGENT_DESCRIPTIONS.keys())}"
        )
    return info.copy()


def list_all_agents() -> dict[str, dict]:
    """
    Lấy thông tin về tất cả Deep-Spec AI agents.

    Returns:
        dict: Mapping từ role names sang thông tin agent

    Examples:
        >>> from src.agents import list_all_agents
        >>> agents = list_all_agents()
        >>> for role, info in agents.items():
        ...     print(f"{role}: {info['name']}")
    """
    return {
        role: get_agent_info(role) for role in ["white_hat", "black_hat", "green_hat"]
    }


# === Public API ===

__all__ = [
    # Agent creation functions (new names)
    "create_architect_agent",
    "create_auditor_agent",
    "create_cto_agent",
    # Agent creation functions (backward compatibility)
    "create_white_hat_agent",
    "create_black_hat_agent",
    "create_green_hat_agent",
    "create_deep_spec_crew",
    "create_agent_by_role",
    # Task template functions (new names)
    "get_architect_task_template",
    "get_auditor_task_template",
    "get_cto_task_template",
    # Task template functions (backward compatibility)
    "get_white_hat_task_template",
    "get_black_hat_task_template",
    "get_green_hat_task_template",
    "get_task_template",
    # Agent info functions
    "get_agent_info",
    "list_all_agents",
    # Constants (new names)
    "ARCHITECT_TASK_TEMPLATES",
    "AUDITOR_TASK_TEMPLATES",
    "CTO_TASK_TEMPLATES",
    # Constants (backward compatibility)
    "AGENT_DESCRIPTIONS",
    "WHITE_HAT_TASK_TEMPLATES",
    "BLACK_HAT_TASK_TEMPLATES",
    "GREEN_HAT_TASK_TEMPLATES",
    "EDGE_CASE_CATEGORIES",
    "QUALITY_GATE_THRESHOLDS",
    # Helper functions
    "get_edge_case_prompts_for_category",
    "get_quality_threshold",
    "get_minimum_acceptable_score",
]
