"""
Multi-Agent Role Definitions for Phase 4.

Theo PRODUCT_VISION.md, sử dụng 4 agents với vai trò đối lập:
- White Hat (Optimist): Review content for completeness
- Black Hat (Critic): Challenge và tìm lỗ hổng ⚠️ CRITICAL
- Green Hat (Creative): Format visual components
- Editor (Synthesizer): Tổng hợp thành final output
"""

from crewai import Agent
from src.utils.llm_provider import get_llm


def create_white_hat_agent(
    provider: str = "google",
    verbose: bool = True,
    memory: bool = True,
) -> Agent:
    """
    Create White Hat Agent (Content Reviewer).

    Role: Review tích cực, tìm kiếm good points, flag missing sections.

    Args:
        provider: LLM provider ("google" or "zai")
        verbose: Enable verbose logging
        memory: Enable agent memory

    Returns:
        Agent: White Hat reviewer agent
    """
    llm = get_llm(provider)

    return Agent(
        role="White Hat - Content Reviewer (Optimist)",
        goal=(
            "Review aggregated content for completeness and clarity. "
            "Flag missing sections, identify good points to maintain, "
            "ensure logical flow and clear happy path description."
        ),
        backstory=(
            "Bạn là reviewer tích cực, luôn nhìn vào những điểm tốt. "
            "Bạn đảm bảo tất cả sections có đầy đủ thông tin, content flows logically, "
            "happy path được mô tả rõ ràng. KHÔNG thêm thông tin mới, CHỈ review."
        ),
        llm=llm,
        verbose=verbose,
        memory=memory,
        allow_delegation=False,
    )


def create_black_hat_agent(
    provider: str = "google",
    verbose: bool = True,
    memory: bool = True,
) -> Agent:
    """
    Create Black Hat Agent (Quality Challenger) ⚠️ CRITICAL.

    Role: PHẢN BIỆT và tìm LỖ HỔNG. PHẢI tìm ≥3 issues.

    Args:
        provider: LLM provider
        verbose: Enable verbose logging
        memory: Enable agent memory

    Returns:
        Agent: Black Hat critic agent
    """
    llm = get_llm(provider)

    return Agent(
        role="Black Hat - Quality Challenger (Critic) ⚠️ CRITICAL",
        goal=(
            "PHẢN BIỆT và tìm LỖ HỔNG trong content. "
            "PHẢI tìm ít nhất 3 critical issues. Challenge edge case coverage. "
            "Validate technical feasibility. Reject nếu không qua Quality Gate."
        ),
        backstory=(
            "Bạn là 'Kẻ phá hoại' - Critical Thinking Specialist. "
            "Bạn cực kỳ dị ứng với shallow analysis (chỉ happy path), "
            "missing edge cases, generic solutions không technically feasible, "
            "và AI-speak. NO 'yes-man' attitude. Challenge mọi assumption."
        ),
        llm=llm,
        verbose=verbose,
        memory=memory,
        allow_delegation=False,
    )


def create_green_hat_agent(
    provider: str = "google",
    verbose: bool = True,
    memory: bool = False,
) -> Agent:
    """
    Create Green Hat Agent (Visual Formatter).

    Role: Chuyển đổi text thành visual components (Mermaid, tables).

    Args:
        provider: LLM provider
        verbose: Enable verbose logging
        memory: Enable agent memory

    Returns:
        Agent: Green Hat creative agent
    """
    llm = get_llm(provider)

    return Agent(
        role="Green Hat - Visual Formatter (Creative)",
        goal=(
            "Chuyển đổi text thành visual components. "
            "Generate valid Mermaid diagrams. Format tables properly. "
            "Create visual, readable documentation."
        ),
        backstory=(
            "Bạn là visual storyteller. Biến complex logic thành "
            "Mermaid diagrams (Flowchart, Sequence, State), tables aligned và readable, "
            "code blocks với syntax highlighting. Mermaid code PHẢI valid."
        ),
        llm=llm,
        verbose=verbose,
        memory=memory,
        allow_delegation=False,
    )


def create_editor_agent(
    provider: str = "google",
    verbose: bool = True,
    memory: bool = True,
) -> Agent:
    """
    Create Editor Agent (Final Aggregator/Synthesizer).

    Role: Tổng hợp outputs từ 3 agents trên thành SDD final.

    Args:
        provider: LLM provider
        verbose: Enable verbose logging
        memory: Enable agent memory

    Returns:
        Agent: Editor synthesizer agent
    """
    llm = get_llm(provider)

    return Agent(
        role="Editor - Final Aggregator (Synthesizer)",
        goal=(
            "Tổng hợp outputs từ White, Black, Green Hat agents thành SDD final. "
            "PHẢI address tất cả critical_issues từ Black Hat. "
            "KHÔNG bypass Quality Gate. Reject nếu quality_gate_passed = False."
        ),
        backstory=(
            "Bạn là biên tập viên cuối cùng. Synthesize content từ White Hat, "
            "challenges từ Black Hat (MUST address all), visuals từ Green Hat. "
            "Type dị ứng với AI-speak và redundant content."
        ),
        llm=llm,
        verbose=verbose,
        memory=memory,
        allow_delegation=False,
    )
