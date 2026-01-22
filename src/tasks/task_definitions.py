"""
Hierarchical Task Definitions for Deep-Spec AI Workflow.

This module provides task definition classes for creating CrewAI tasks
with proper output_pydantic schemas and context linking for the
hierarchical workflow process.

Task Flow:
1. HappyPathTaskDefinition - Creates happy path analysis task (Architect)
2. BusinessExceptionsTaskDefinition - Analyzes business exceptions (Auditor)
3. TechnicalEdgeCasesTaskDefinition - Identifies technical edge cases (Auditor)
"""

from typing import List, Optional, Union, Literal
from crewai import Task, Agent
from src.schemas import HappyPath, StressTestReport


class HappyPathTaskDefinition:
    """
    Task definition for creating Happy Path analysis tasks.

    This task is assigned to the Senior System Architect (White Hat)
    and outputs a structured HappyPath Pydantic schema.

    Attributes:
        None (uses factory pattern)

    Example:
        >>> from src.agents import create_architect_agent
        >>> from src.tasks import HappyPathTaskDefinition
        >>>
        >>> architect = create_architect_agent()
        >>> task_def = HappyPathTaskDefinition()
        >>> task = task_def.create_task(
        ...     user_requirement="User login with email and password",
        ...     agent=architect
        ... )
    """

    def create_task(
        self,
        user_requirement: str,
        agent: Agent,
    ) -> Task:
        """
        Create a Happy Path analysis task with output_pydantic schema.

        Args:
            user_requirement: The user's feature requirement description
            agent: The CrewAI Agent (typically Senior System Architect)

        Returns:
            Task: CrewAI Task configured with HappyPath output_pydantic

        Task Configuration:
            - description: Detailed prompt for creating happy path flow
            - expected_output: Clear description of expected HappyPath object
            - output_pydantic: HappyPath schema for structured output
            - agent: Senior System Architect (White Hat)
        """
        description = f"""Analyze the following requirement and create a comprehensive Happy Path flow:

Requirement: {user_requirement}

Your task:
1. Break down the requirement into clear, sequential steps
2. Identify all actors involved (User, System, External services)
3. Define pre-conditions required before execution
4. Define post-conditions expected after successful execution
5. Identify the business value this feature provides

For each step, specify:
- Step number (sequential)
- Actor performing the action
- Action description
- Expected outcome
- Components involved

Output a HappyPath object with:
- feature_id: Unique identifier (e.g., "feat-001")
- feature_name: Clear name for this feature
- description: Brief description of what this feature does
- steps: List of FlowStep objects (minimum 3 steps)
- pre_conditions: List of required states before execution
- post_conditions: List of expected states after success
- business_value: Business value this feature provides

Ensure all steps are realistic and technically feasible.
"""

        expected_output = (
            "A HappyPath Pydantic object containing the complete happy path flow "
            "with sequential steps, actors, pre/post conditions, and business value."
        )

        return Task(
            description=description,
            expected_output=expected_output,
            output_pydantic=HappyPath,
            agent=agent,
        )


class BusinessExceptionsTaskDefinition:
    """
    Task definition for analyzing business exceptions and rule violations.

    This task is assigned to the QA & Security Auditor (Black Hat)
    and focuses on finding business logic failures and rule violations.

    Context Linking:
        This task requires context from the HappyPath task to analyze
        business exceptions based on the defined happy path flow.

    Attributes:
        None (uses factory pattern)

    Example:
        >>> from src.agents import create_auditor_agent
        >>> from src.tasks import BusinessExceptionsTaskDefinition
        >>>
        >>> auditor = create_auditor_agent()
        >>> task_def = BusinessExceptionsTaskDefinition()
        >>> task = task_def.create_task(
        ...     user_requirement="User login with email and password",
        ...     agent=auditor,
        ...     context=happy_path_task  # Link to happy path output
        ... )
    """

    def create_task(
        self,
        user_requirement: str,
        agent: Agent,
        context: Optional[Union[Task, List[Task]]] = None,
    ) -> Task:
        """
        Create a Business Exceptions analysis task with context linking.

        Args:
            user_requirement: The user's feature requirement description
            agent: The CrewAI Agent (typically QA & Security Auditor)
            context: HappyPath task for context linking (optional but recommended)

        Returns:
            Task: CrewAI Task configured with business exceptions focus

        Task Configuration:
            - description: Detailed prompt for finding business exceptions
            - expected_output: Description of business exception analysis
            - context: Linked to HappyPath task output
            - agent: QA & Security Auditor (Black Hat)
        """
        context_prompt = ""
        if context:
            context_prompt = (
                "\n\nIMPORTANT: Review the Happy Path context provided. "
                "Focus on business exceptions that can occur at each step of the happy path. "
                "Identify scenarios where business rules are violated or business logic fails."
            )

        description = f"""Analyze the following requirement for business exceptions and rule violations:

Requirement: {user_requirement}{context_prompt}

Your task (Business Exceptions Focus):
1. Review each step in the happy path flow
2. Identify business rule violations (e.g., invalid states, unauthorized actions)
3. Find business logic failures (e.g., constraint violations, validation failures)
4. Consider domain-specific exceptions (e.g., payment failures, inventory shortages)
5. Identify data validation failures at business layer

For each business exception:
- Which happy path step does it relate to?
- What business rule or constraint is violated?
- What are the business impacts?
- How should the system handle this exception?

Categories to explore:
- Validation failures (invalid input, missing required fields)
- Authorization failures (permission denied, role restrictions)
- Business rule violations (e.g., duplicate orders, insufficient funds)
- State inconsistencies (e.g., conflicting statuses)
- External service failures (e.g., payment gateway down)

Provide a detailed analysis of business exceptions that can occur during execution.
"""

        expected_output = (
            "A comprehensive analysis of business exceptions and rule violations, "
            "organized by happy path steps, with handling strategies for each exception."
        )

        # Normalize context to list for CrewAI
        context_list = [context] if isinstance(context, Task) else (context or [])

        return Task(
            description=description,
            expected_output=expected_output,
            context=context_list,
            agent=agent,
        )


class TechnicalEdgeCasesTaskDefinition:
    """
    Task definition for identifying technical edge cases and stress testing.

    This task is assigned to the QA & Security Auditor (Black Hat)
    and outputs a structured StressTestReport Pydantic schema.

    Context Linking:
        This task requires dual context from both HappyPath and
        BusinessExceptions tasks to provide comprehensive edge case analysis.

    Attributes:
        None (uses factory pattern)

    Example:
        >>> from src.agents import create_auditor_agent
        >>> from src.tasks import TechnicalEdgeCasesTaskDefinition
        >>>
        >>> auditor = create_auditor_agent()
        >>> task_def = TechnicalEdgeCasesTaskDefinition()
        >>> task = task_def.create_task(
        ...     user_requirement="User login with email and password",
        ...     agent=auditor,
        ...     context=[happy_path_task, business_exceptions_task]
        ... )
    """

    def create_task(
        self,
        user_requirement: str,
        agent: Agent,
        context: Optional[Union[Task, List[Task]]] = None,
    ) -> Task:
        """
        Create a Technical Edge Cases analysis task with output_pydantic schema.

        Args:
            user_requirement: The user's feature requirement description
            agent: The CrewAI Agent (typically QA & Security Auditor)
            context: List of tasks [HappyPath, BusinessExceptions] for dual context

        Returns:
            Task: CrewAI Task configured with StressTestReport output_pydantic

        Task Configuration:
            - description: Detailed prompt for finding technical edge cases
            - expected_output: Description of edge case analysis
            - output_pydantic: StressTestReport schema for structured output
            - context: Linked to HappyPath and BusinessExceptions tasks
            - agent: QA & Security Auditor (Black Hat)
        """
        context_prompt = ""
        if context:
            context_prompt = (
                "\n\nIMPORTANT: Review both the Happy Path and Business Exceptions context. "
                "Build upon these analyses to identify technical edge cases and stress scenarios. "
                "Consider how business exceptions might manifest as technical failures."
            )

        description = f"""Perform comprehensive stress testing and identify technical edge cases for:

Requirement: {user_requirement}{context_prompt}

Your task (Technical Edge Cases Focus):
1. Analyze the system under stress conditions (high load, concurrent requests)
2. Identify race conditions and timing issues
3. Find network-related failures (timeouts, connection drops)
4. Discover data consistency issues (concurrent updates, orphaned records)
5. Identify security vulnerabilities (injection attacks, authentication bypass)
6. Find resource exhaustion scenarios (memory leaks, connection pool exhaustion)

For EACH edge case, provide:
- scenario_id: Unique identifier (e.g., "EDGE-LOGIN-001")
- description: Clear description of the failure scenario
- trigger_condition: What triggers this edge case
- expected_failure: How the system would fail without mitigation
- severity: Impact level (Low, Medium, High, Critical)
- likelihood: How likely this is to occur
- detection_method: How to detect this in testing/production
- related_components: Which components are affected
- related_step: Which flow step this relates to
- mitigation: MitigationStrategy with:
  - description: How to mitigate
  - technical_implementation: Specific technical details
  - implementation_complexity: Complexity level
  - estimated_effort: Effort estimate (optional)

MINIMUM REQUIREMENTS:
- Identify at least 5 edge cases
- Cover multiple categories (network, concurrency, security, data, resources)
- Provide concrete, actionable mitigation strategies

After identifying all edge cases, provide:
- resilience_score: Estimated resilience (0-100)
- coverage_score: Edge case coverage percentage
- review_summary: Overall assessment
- critical_findings: Must-address issues
- recommendations: General recommendations

Output a StressTestReport Pydantic object with all edge cases and metrics.
"""

        expected_output = (
            "A StressTestReport Pydantic object containing at least 5 edge cases "
            "with detailed analysis, mitigation strategies, and quality metrics."
        )

        # Normalize context to list for CrewAI
        context_list = [context] if isinstance(context, Task) else (context or [])

        return Task(
            description=description,
            expected_output=expected_output,
            output_pydantic=StressTestReport,
            context=context_list,
            agent=agent,
        )


def create_hierarchical_tasks(
    user_requirement: str,
    architect: Agent,
    auditor: Agent,
) -> List[Task]:
    """
    Factory function to create all three hierarchical tasks.

    This is the recommended way to create tasks for the hierarchical workflow.
    It creates tasks with proper context linking and output_pydantic schemas.

    Args:
        user_requirement: The user's feature requirement description
        architect: Senior System Architect agent (White Hat)
        auditor: QA & Security Auditor agent (Black Hat)

    Returns:
        List[Task]: A list of 3 tasks in execution order:
            1. HappyPathTaskDefinition (assigned to architect)
            2. BusinessExceptionsTaskDefinition (assigned to auditor, linked to happy path)
            3. TechnicalEdgeCasesTaskDefinition (assigned to auditor, linked to both)

    Task Flow:
        The tasks are designed to be executed sequentially with context chaining:
        - Happy Path creates the baseline flow
        - Business Exceptions analyzes business logic failures
        - Technical Edge Cases performs comprehensive stress testing

    Example:
        >>> from src.agents import create_architect_agent, create_auditor_agent
        >>> from src.tasks import create_hierarchical_tasks
        >>>
        >>> architect = create_architect_agent()
        >>> auditor = create_auditor_agent()
        >>>
        >>> tasks = create_hierarchical_tasks(
        ...     user_requirement="User login with email and password",
        ...     architect=architect,
        ...     auditor=auditor
        ... )
        >>>
        >>> # Use in hierarchical workflow
        >>> from src.workflows import HierarchicalOrchestrator
        >>> orchestrator = HierarchicalOrchestrator(config)
        >>> result = orchestrator.execute_workflow(
        ...     user_requirement="User login with email and password",
        ...     tasks=tasks
        ... )
    """
    # Task 1: Happy Path Analysis (Architect)
    happy_path_task_def = HappyPathTaskDefinition()
    happy_path_task = happy_path_task_def.create_task(
        user_requirement=user_requirement,
        agent=architect,
    )

    # Task 2: Business Exceptions (Auditor, linked to Happy Path)
    business_exceptions_task_def = BusinessExceptionsTaskDefinition()
    business_exceptions_task = business_exceptions_task_def.create_task(
        user_requirement=user_requirement,
        agent=auditor,
        context=happy_path_task,  # Context linking
    )

    # Task 3: Technical Edge Cases (Auditor, linked to both previous tasks)
    technical_edge_cases_task_def = TechnicalEdgeCasesTaskDefinition()
    technical_edge_cases_task = technical_edge_cases_task_def.create_task(
        user_requirement=user_requirement,
        agent=auditor,
        context=[happy_path_task, business_exceptions_task],  # Dual context
    )

    return [
        happy_path_task,
        business_exceptions_task,
        technical_edge_cases_task,
    ]


def get_task_for_phase(
    phase: Literal["happy_path", "business_exceptions", "technical_edge_cases"],
    user_requirement: str,
    agent: Agent,
    context: Optional[Union[Task, List[Task]]] = None,
) -> Task:
    """
    Helper function to get a specific task by phase.

    Useful for creating individual tasks without creating the full hierarchy.

    Args:
        phase: The phase identifier ("happy_path", "business_exceptions", "technical_edge_cases")
        user_requirement: The user's feature requirement description
        agent: The CrewAI Agent to assign this task to
        context: Optional context task(s) for linking (recommended for phases 2 and 3)

    Returns:
        Task: CrewAI Task configured for the specified phase

    Raises:
        ValueError: If phase is not one of the valid options

    Example:
        >>> from src.agents import create_architect_agent
        >>> from src.tasks import get_task_for_phase
        >>>
        >>> architect = create_architect_agent()
        >>> happy_path_task = get_task_for_phase(
        ...     phase="happy_path",
        ...     user_requirement="User login",
        ...     agent=architect
        ... )
    """
    task_definition_classes = {
        "happy_path": HappyPathTaskDefinition,
        "business_exceptions": BusinessExceptionsTaskDefinition,
        "technical_edge_cases": TechnicalEdgeCasesTaskDefinition,
    }

    if phase not in task_definition_classes:
        valid_phases = list(task_definition_classes.keys())
        raise ValueError(
            f"Invalid phase: '{phase}'. Must be one of: {valid_phases}"
        )

    task_def_class = task_definition_classes[phase]
    task_def = task_def_class()

    return task_def.create_task(
        user_requirement=user_requirement,
        agent=agent,
        context=context,
    )


__all__ = [
    "HappyPathTaskDefinition",
    "BusinessExceptionsTaskDefinition",
    "TechnicalEdgeCasesTaskDefinition",
    "create_hierarchical_tasks",
    "get_task_for_phase",
]
