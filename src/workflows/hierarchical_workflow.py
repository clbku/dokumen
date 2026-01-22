"""
Hierarchical Workflow Entry Point

Main entry point for the hierarchical workflow execution using CrewAI's
hierarchical process with a Manager Agent coordinating worker agents.

This module provides:
- HierarchicalWorkflowConfig: Complete workflow configuration
- HierarchicalWorkflow: Main workflow class
- execute_hierarchical_workflow(): Convenience function for quick execution
"""

from typing import List, Optional, Dict, Any, Literal
from dataclasses import dataclass
from crewai import Agent, Task

from src.workflows.hierarchical_orchestrator import HierarchicalOrchestrator
from src.agents import create_architect_agent, create_auditor_agent
from src.tasks import create_hierarchical_tasks


# Re-export the config for convenience
from src.workflows.hierarchical_orchestrator import HierarchicalWorkflowConfig


class HierarchicalWorkflow:
    """
    Main entry point for Hierarchical Workflow execution.

    This class orchestrates the complete hierarchical workflow:
    1. Creates HierarchicalOrchestrator with Manager Agent
    2. Creates worker agents (Architect, Auditors)
    3. Creates hierarchical tasks
    4. Executes workflow with Manager coordination
    5. Returns structured results

    The hierarchical process allows:
    - Manager Agent dynamically decides task execution order
    - Easy scaling to multiple auditor agents
    - Better context management between tasks
    - Manager synthesizes final output from all workers

    Example:
        >>> from src.workflows import HierarchicalWorkflow, HierarchicalWorkflowConfig
        >>>
        >>> config = HierarchicalWorkflowConfig(
        ...     manager_llm_provider="google",
        ...     verbose=True,
        ... )
        >>>
        >>> workflow = HierarchicalWorkflow(config)
        >>> result = workflow.execute(
        ...     user_requirement="User authentication system",
        ...     num_auditors=2,
        ... )
    """

    def __init__(self, config: HierarchicalWorkflowConfig):
        """
        Initialize the Hierarchical Workflow.

        Args:
            config: Workflow configuration including LLM providers,
                   verbosity, memory settings, etc.
        """
        self.config = config
        self.orchestrator = HierarchicalOrchestrator(config)
        self.architect: Optional[Agent] = None
        self.auditors: List[Agent] = []

    def create_agents(
        self,
        num_auditors: int = 1,
        architect_verbose: bool = True,
        architect_memory: bool = True,
        auditor_verbose: bool = True,
        auditor_memory: bool = True,
    ) -> tuple[Agent, List[Agent]]:
        """
        Create worker agents for the hierarchical workflow.

        Args:
            num_auditors: Number of auditor agents to create (default: 1)
                         Supports scaling to multiple auditors for different perspectives
            architect_verbose: Enable verbose logging for architect (default: True)
            architect_memory: Enable memory for architect agent (default: True)
            auditor_verbose: Enable verbose logging for auditors (default: True)
            auditor_memory: Enable memory for auditor agents (default: True)

        Returns:
            tuple[Agent, List[Agent]]: (architect_agent, list_of_auditor_agents)
        """
        # Create architect (single)
        self.architect = create_architect_agent(
            verbose=architect_verbose or self.config.verbose,
            memory=architect_memory or self.config.memory,
            allow_delegation=False,  # Architect doesn't delegate
        )

        # Create auditors (multiple for scaling)
        self.auditors = [
            create_auditor_agent(
                verbose=auditor_verbose or self.config.verbose,
                memory=auditor_memory or self.config.memory,
                allow_delegation=False,  # Auditors don't delegate
            )
            for _ in range(num_auditors)
        ]

        return self.architect, self.auditors

    def create_crew(
        self,
        workers: Optional[List[Agent]] = None,
    ):
        """
        Create the hierarchical crew with Manager and workers.

        Args:
            workers: Optional list of worker agents. If None, uses
                    previously created architect and auditors.

        Returns:
            Crew: The hierarchical crew object

        Raises:
            ValueError: If no workers provided and none created yet
        """
        if workers is None:
            if self.architect is None or not self.auditors:
                raise ValueError(
                    "No workers available. Call create_agents() first "
                    "or provide workers parameter."
                )
            workers = [self.architect] + self.auditors

        return self.orchestrator.create_hierarchical_crew(workers=workers)

    def execute(
        self,
        user_requirement: str,
        num_auditors: int = 1,
        create_auditors: bool = True,
        assign_auditors_to_tasks: bool = True,
    ) -> Dict[str, Any]:
        """
        Execute the complete hierarchical workflow.

        This is the main entry point that:
        1. Creates agents (architect + auditors)
        2. Creates hierarchical crew with Manager
        3. Creates tasks with proper dependencies
        4. Executes workflow with Manager coordination
        5. Returns structured results

        Args:
            user_requirement: Feature description from user
            num_auditors: Number of auditor agents to create (default: 1)
            create_auditors: Whether to create new auditors (default: True)
                            Set to False if you want to reuse existing auditors
            assign_auditors_to_tasks: Whether to distribute tasks across auditors (default: True)
                                    If True and multiple auditors, different tasks
                                    may be assigned to different auditors

        Returns:
            Dict[str, Any]: Results containing:
                - manager_output: Output from Manager agent
                - raw_output: Raw output from crew execution
                - final_result: Parsed and structured result
                - num_auditors: Number of auditors used
                - num_tasks: Number of tasks executed
        """
        # Step 1: Create agents if needed
        if create_auditors or self.architect is None or not self.auditors:
            architect, auditors = self.create_agents(num_auditors=num_auditors)
        else:
            architect = self.architect
            auditors = self.auditors

        # Step 2: Create hierarchical crew
        self.create_crew(workers=[architect] + auditors)

        # Step 3: Create tasks
        tasks = create_hierarchical_tasks(
            user_requirement=user_requirement,
            architect_agent=architect,
            auditor_agent=auditors[0],  # Use first auditor as default
        )

        # Step 4: Optionally distribute tasks across multiple auditors
        if assign_auditors_to_tasks and len(auditors) > 1:
            # Distribute auditor tasks across available auditors
            # Task 0: Happy Path (architect) - keep as is
            # Task 1: Business Exceptions (auditor) - assign to first auditor
            # Task 2: Technical Edge Cases (auditor) - assign to second auditor if available
            if len(auditors) >= 2 and len(tasks) >= 3:
                tasks[2].agent = auditors[1]
            # Continue distributing if more auditors and tasks available
            for i in range(3, len(tasks)):
                auditor_idx = (i - 1) % len(auditors)
                tasks[i].agent = auditors[auditor_idx]

        # Step 5: Execute workflow
        result = self.orchestrator.execute_workflow(
            user_requirement=user_requirement,
            tasks=tasks,
        )

        # Step 6: Add metadata to result
        result["num_auditors"] = len(auditors)
        result["num_tasks"] = len(tasks)

        return result

    def reset(self):
        """
        Reset the workflow to allow re-execution with different configuration.

        Clears the orchestrator crew and allows fresh execution.
        """
        self.orchestrator.reset()
        self.architect = None
        self.auditors = []


def execute_hierarchical_workflow(
    user_requirement: str,
    config: Optional[HierarchicalWorkflowConfig] = None,
    num_auditors: int = 1,
) -> Dict[str, Any]:
    """
    Convenience function to execute hierarchical workflow with minimal setup.

    This is the simplest way to run the hierarchical workflow:
    - Creates default config if not provided
    - Initializes workflow
    - Creates agents and crew
    - Executes workflow
    - Returns results

    Args:
        user_requirement: Feature description from user
        config: Optional workflow configuration. If None, uses defaults.
        num_auditors: Number of auditor agents to create (default: 1)

    Returns:
        Dict[str, Any]: Results containing:
            - manager_output: Output from Manager agent
            - raw_output: Raw output from crew execution
            - final_result: Parsed and structured result
            - num_auditors: Number of auditors used
            - num_tasks: Number of tasks executed

    Example:
        >>> from src.workflows.hierarchical_workflow import execute_hierarchical_workflow
        >>>
        >>> result = execute_hierarchical_workflow(
        ...     user_requirement="Real-time notification system",
        ...     num_auditors=2,
        ... )
        >>>
        >>> print(result["final_result"])
    """
    # Create default config if not provided
    if config is None:
        config = HierarchicalWorkflowConfig()

    # Initialize workflow
    workflow = HierarchicalWorkflow(config)

    # Execute and return results
    return workflow.execute(
        user_requirement=user_requirement,
        num_auditors=num_auditors,
    )


__all__ = [
    "HierarchicalWorkflow",
    "HierarchicalWorkflowConfig",
    "execute_hierarchical_workflow",
]
