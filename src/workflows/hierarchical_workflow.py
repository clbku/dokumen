"""
Hierarchical Workflow Entry Point

Main entry point for the hierarchical workflow execution using CrewAI's
hierarchical process with a Manager Agent coordinating worker agents.

This module provides:
- HierarchicalWorkflowConfig: Complete workflow configuration
- HierarchicalWorkflow: Main workflow class
- execute_hierarchical_workflow(): Convenience function for quick execution
"""

from typing import Dict, Any, Literal
from dataclasses import dataclass
from crewai import Agent

from src.workflows.hierarchical_orchestrator import HierarchicalOrchestrator
from src.agents import create_architect_agent, create_auditor_agent
from src.tasks import create_hierarchical_tasks


@dataclass
class HierarchicalWorkflowConfig:
    """Cấu hình complete cho Hierarchical Workflow."""

    # Orchestrator config
    manager_llm_provider: Literal["zai", "google"] = "google"
    verbose: bool = True
    memory: bool = True

    # Agents config
    architect_provider: Literal["zai", "google"] = "zai"
    auditor_provider: Literal["zai", "google"] = "google"

    # Multiple auditors (scale feature)
    use_multiple_auditors: bool = False
    num_auditors: int = 1


class HierarchicalWorkflow:
    """
    High-level Hierarchical Workflow interface.

    Usage:
        config = HierarchicalWorkflowConfig()
        workflow = HierarchicalWorkflow(config)
        result = workflow.execute("Hệ thống đấu giá thời gian thực")
    """

    def __init__(self, config: HierarchicalWorkflowConfig):
        self.config = config
        # Create orchestrator config from workflow config
        from src.workflows.hierarchical_orchestrator import HierarchicalWorkflowConfig as OrchestratorConfig
        orchestrator_config = OrchestratorConfig(
            manager_llm_provider=config.manager_llm_provider,
            verbose=config.verbose,
            memory=config.memory,
        )
        self.orchestrator = HierarchicalOrchestrator(orchestrator_config)
        self.agents: Dict[str, Agent] = {}

    def _create_agents(self):
        """Tạo agents cho workflow."""
        # Architect (White Hat)
        self.agents["architect"] = create_architect_agent(
            verbose=self.config.verbose,
            memory=self.config.memory,
            allow_delegation=False,
        )

        # Auditor(s) (Black Hat)
        if self.config.use_multiple_auditors:
            # Scale: tạo nhiều auditors cho different aspects
            for i in range(self.config.num_auditors):
                self.agents[f"auditor_{i}"] = create_auditor_agent(
                    verbose=self.config.verbose,
                    memory=self.config.memory,
                    allow_delegation=False,
                )
        else:
            # Single auditor cho tất cả phases
            self.agents["auditor"] = create_auditor_agent(
                verbose=self.config.verbose,
                memory=self.config.memory,
                allow_delegation=False,
            )

    def execute(
        self,
        user_requirement: str,
    ) -> Dict[str, Any]:
        """
        Execute hierarchical workflow cho user requirement.

        Args:
            user_requirement: Feature description

        Returns:
            dict: Kết quả với keys:
                - happy_path: HappyPath object (dict)
                - business_exceptions: StressTestReport object (dict)
                - technical_edge_cases: StressTestReport object (dict)
                - manager_summary: Tổng hợp từ manager
        """
        # Create agents
        self._create_agents()

        # Create tasks
        architect = self.agents["architect"]
        auditor = self.agents.get("auditor") or self.agents["auditor_0"]

        tasks = create_hierarchical_tasks(
            user_requirement=user_requirement,
            architect_agent=architect,
            auditor_agent=auditor,
        )

        # Get worker agents
        workers = list(self.agents.values())

        # Execute với hierarchical orchestrator
        result = self.orchestrator.execute_workflow(
            user_requirement=user_requirement,
            tasks=tasks,
            workers=workers,
        )

        # Parse và return structured result
        return self._parse_workflow_result(result)

    def _parse_workflow_result(self, raw_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse raw result từ orchestrator thành structured output.

        Manager agent sẽ tổng hợp kết quả. Parse để extract Pydantic objects.
        """
        # TODO: Implement proper parsing
        # Hiện tại return raw, sau này sẽ extract HappyPath và StressTestReport objects

        return {
            "happy_path": self._extract_happy_path(raw_result),
            "business_exceptions": self._extract_business_exceptions(raw_result),
            "technical_edge_cases": self._extract_technical_edge_cases(raw_result),
            "manager_summary": raw_result.get("manager_output"),
        }

    def _extract_happy_path(self, raw_result: Dict) -> Dict[str, Any]:
        """Extract happy path từ raw result."""
        # TODO: Parse Pydantic object from manager output
        return {"feature_name": "TODO", "steps": []}

    def _extract_business_exceptions(self, raw_result: Dict) -> Dict[str, Any]:
        """Extract business exceptions từ raw result."""
        return {"edge_cases": []}

    def _extract_technical_edge_cases(self, raw_result: Dict) -> Dict[str, Any]:
        """Extract technical edge cases từ raw result."""
        return {"edge_cases": []}


def execute_hierarchical_workflow(
    user_requirement: str,
    manager_provider: Literal["zai", "google"] = "google",
    architect_provider: Literal["zai", "google"] = "zai",
    auditor_provider: Literal["zai", "google"] = "google",
    verbose: bool = True,
    use_multiple_auditors: bool = False,
) -> Dict[str, Any]:
    """
    Convenience function để execute hierarchical workflow.

    Args:
        user_requirement: Feature description
        manager_provider: LLM provider cho Manager Agent
        architect_provider: LLM provider cho Architect
        auditor_provider: LLM provider cho Auditor
        verbose: Enable verbose logging
        use_multiple_auditors: Scale với nhiều auditors

    Returns:
        dict: Workflow results

    Examples:
        >>> result = execute_hierarchical_workflow(
        ...     "Hệ thống đấu giá thời gian thực",
        ...     manager_provider="google",
        ... )
        >>> print(result["happy_path"]["feature_name"])
    """
    config = HierarchicalWorkflowConfig(
        manager_llm_provider=manager_provider,
        architect_provider=architect_provider,
        auditor_provider=auditor_provider,
        verbose=verbose,
        use_multiple_auditors=use_multiple_auditors,
    )

    workflow = HierarchicalWorkflow(config)
    return workflow.execute(user_requirement)


__all__ = [
    "HierarchicalWorkflow",
    "HierarchicalWorkflowConfig",
    "execute_hierarchical_workflow",
]
