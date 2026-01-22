"""
Task Definitions cho Hierarchical Workflow.

Khác với sequential, hierarchical tasks không cần context linking thủ công
vì Manager Agent sẽ quyết định task nào chạy và truyền context.
Tuy nhiên, tasks vẫn cần description rõ ràng để Manager hiểu dependencies.
"""

from typing import List
from crewai import Task
from src.schemas import HappyPath, StressTestReport


class HappyPathTaskDefinition:
    """
    Task definition cho Happy Path Analysis.

    Trong hierarchical process, Manager sẽ:
    1. Gọi task này trước vì "happy path" là foundation
    2. Truyền kết quả cho các tasks sau
    """

    @staticmethod
    def create(
        user_requirement: str,
        architect_agent,
    ) -> Task:
        """
        Tạo HappyPath task.

        Args:
            user_requirement: Feature description từ user
            architect_agent: Architect agent (White Hat)

        Returns:
            Task: CrewAI Task với output_pydantic=HappyPath
        """
        return Task(
            description=f"""
            PHASE 1: Thiết kế Happy Path cho feature:
            {user_requirement}

            Yêu cầu:
            - Tạo luồng thành công rõ ràng (3+ steps)
            - Mỗi step có: actor, action, outcome
            - Định nghĩa pre-conditions và post-conditions
            - KHÔNG nhắc đến edge cases, errors, hoặc failures

            Output format: HappyPath Pydantic object
            """,
            expected_output=(
                "HappyPath object với: feature_id, feature_name, description, "
                "steps (list of FlowStep), pre_conditions, post_conditions, business_value"
            ),
            agent=architect_agent,
            output_pydantic=HappyPath,
        )


class BusinessExceptionsTaskDefinition:
    """
    Task definition cho Business Exceptions Analysis.

    Manager sẽ chạy task này SAU HappyPathTask và truyền kết quả happy path.
    """

    @staticmethod
    def create(
        user_requirement: str,
        auditor_agent,
        happy_path_task: Task,
    ) -> Task:
        """
        Tạo Business Exceptions task.

        Args:
            user_requirement: Feature description
            auditor_agent: Auditor agent (Black Hat)
            happy_path_task: HappyPath task để reference context

        Returns:
            Task: CrewAI Task với output_pydantic=StressTestReport
        """
        return Task(
            description=f"""
            PHASE 2: Phân tích Business Rule Exceptions cho feature:
            {user_requirement}

            Context từ Phase 1 (HappyPathTask):
            - Sử dụng happy path đã thiết kế để tìm business rule violations
            - Mỗi step trong happy path có thể bị block bởi business logic gì?

            Yêu cầu:
            - Tìm 5+ edge cases về BUSINESS RULES (không technical)
            - Ví dụ: số dư không đủ, chưa đủ cấp độ, hết hạn thời gian, không đủ quyền
            - KHÔNG tìm technical issues (network, database, concurrency)
            - Mỗi edge case có: trigger, severity, mitigation
            - QUAN TRỌNG: ID phải bắt đầu bằng "EDGE-", ví dụ: EDGE-BIZ-001

            Output format: StressTestReport Pydantic object (business exceptions only)
            """,
            expected_output=(
                "StressTestReport object với: report_id, happy_path_id, feature_name, "
                "edge_cases (5+ EdgeCase về business rules), resilience_score, coverage_score"
            ),
            agent=auditor_agent,
            output_pydantic=StressTestReport,
            context=[happy_path_task],  # Hierarchical: Manager sẽ truyền context
        )


class TechnicalEdgeCasesTaskDefinition:
    """
    Task definition cho Technical Edge Cases Analysis.

    Manager sẽ chạy task này SAU cả 2 tasks trước và truyền kết quả cả hai.
    """

    @staticmethod
    def create(
        user_requirement: str,
        auditor_agent,
        happy_path_task: Task,
        business_exceptions_task: Task,
    ) -> Task:
        """
        Tạo Technical Edge Cases task.

        Args:
            user_requirement: Feature description
            auditor_agent: Auditor agent (Black Hat) - có thể dùng cùng agent
            happy_path_task: HappyPath task để reference
            business_exceptions_task: Business exceptions task để reference

        Returns:
            Task: CrewAI Task với output_pydantic=StressTestReport
        """
        return Task(
            description=f"""
            PHASE 3: Stress Test Kỹ Thuật cho feature:
            {user_requirement}

            Context từ Phase 1 & 2:
            - Happy path: dùng để tìm technical failure points
            - Business exceptions: TRÁCH lặp lại các business rules đã tìm

            Yêu cầu:
            - Tìm 5+ TECHNICAL edge cases
            - Ví dụ: race conditions, network timeouts, database deadlocks, concurrent writes
            - KHÔNG lặp lại business exceptions từ Phase 2
            - Mỗi edge case có: trigger, severity, mitigation
            - QUAN TRỌNG: ID phải bắt đầu bằng "EDGE-", ví dụ: EDGE-TECH-001

            Output format: StressTestReport Pydantic object (technical edge cases only)
            """,
            expected_output=(
                "StressTestReport object với: report_id, happy_path_id, feature_name, "
                "edge_cases (5+ EdgeCase về technical issues), resilience_score, coverage_score"
            ),
            agent=auditor_agent,
            output_pydantic=StressTestReport,
            context=[happy_path_task, business_exceptions_task],
        )


def create_hierarchical_tasks(
    user_requirement: str,
    architect_agent,
    auditor_agent,
) -> List[Task]:
    """
    Factory function để tạo tất cả tasks cho hierarchical workflow.

    Trong hierarchical process, Manager Agent sẽ:
    - Quyết định thứ tự chạy tasks
    - Truyền context giữa tasks (không cần chain thủ công như sequential)
    - Tổng hợp kết quả cuối cùng

    Args:
        user_requirement: Feature description từ user
        architect_agent: Architect agent (White Hat)
        auditor_agent: Auditor agent (Black Hat)

    Returns:
        List[Task]: 3 tasks theo thứ tự recommended execution
    """
    # Task 1: Happy Path (Foundation)
    happy_path_task = HappyPathTaskDefinition.create(
        user_requirement=user_requirement,
        architect_agent=architect_agent,
    )

    # Task 2: Business Exceptions (depends on Task 1)
    business_exceptions_task = BusinessExceptionsTaskDefinition.create(
        user_requirement=user_requirement,
        auditor_agent=auditor_agent,
        happy_path_task=happy_path_task,
    )

    # Task 3: Technical Edge Cases (depends on Task 1 & 2)
    technical_edge_cases_task = TechnicalEdgeCasesTaskDefinition.create(
        user_requirement=user_requirement,
        auditor_agent=auditor_agent,
        happy_path_task=happy_path_task,
        business_exceptions_task=business_exceptions_task,
    )

    return [
        happy_path_task,
        business_exceptions_task,
        technical_edge_cases_task,
    ]


__all__ = [
    "HappyPathTaskDefinition",
    "BusinessExceptionsTaskDefinition",
    "TechnicalEdgeCasesTaskDefinition",
    "create_hierarchical_tasks",
]
