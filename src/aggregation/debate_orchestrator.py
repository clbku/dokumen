"""
Multi-Agent Debate Orchestrator cho Phase 4.

Quản lý 4 agents (White/Black/Green/Editor) chạy theo debate protocol.
"""

from dataclasses import dataclass, field
from typing import Dict, Optional, Any
from crewai import Agent, Task

from src.quality import validate_quality_gate, QualityGateReport


@dataclass
class DebateConfig:
    """Cấu hình cho Multi-Agent Debate."""

    max_retries: int = 3
    enforce_quality_gate: bool = True
    verbose: bool = True

    # Agent providers
    white_provider: str = "google"
    black_provider: str = "google"
    green_provider: str = "google"
    editor_provider: str = "google"


class DebateOrchestrator:
    """
    Orchestrator cho Multi-Agent Debate System.

    Manages 4 agents:
    - Round 1: White Hat reviews content
    - Round 2: Black Hat challenges quality ⚠️ CRITICAL
    - Round 3: Green Hat formats visuals
    - Round 4: Editor synthesizes final output
    """

    REQUIRED_AGENTS = ["white", "black", "green", "editor"]

    def __init__(self, config: DebateConfig):
        self.config = config
        self.agents: Dict[str, Agent] = {}

    def register_agent(self, name: str, agent: Agent):
        """Register an agent with a name."""
        self.agents[name] = agent

    def has_required_agents(self) -> bool:
        """Check if all required agents are registered."""
        return all(name in self.agents for name in self.REQUIRED_AGENTS)

    def run_debate(
        self,
        aggregated_data: Dict[str, Any],
        template: str,
    ) -> Dict[str, Any]:
        """
        Run multi-agent debate cycle.

        Args:
            aggregated_data: Data from Phase 3 aggregation
            template: SDD template string

        Returns:
            dict: {
                "white_review": {...},
                "black_challenge": {...},
                "green_visuals": {...},
                "final_output": {
                    "markdown": str,
                    "quality_report": QualityGateReport,
                    "passed": bool
                }
            }
        """
        if not self.has_required_agents():
            raise ValueError(
                f"Missing required agents. Need: {self.REQUIRED_AGENTS}, "
                f"Have: {list(self.agents.keys())}"
            )

        # TODO: Implement actual debate with LLM calls
        # Hiện tại return mock structure

        mock_quality_report = validate_quality_gate(
            content="Mock content",
            extracted_data=aggregated_data,
        )

        return {
            "white_review": {
                "missing_sections": [],
                "good_points": ["Content structure"],
                "completeness_score": 8.0,
            },
            "black_challenge": {
                "critical_issues": [],
                "edge_case_gaps": [],
                "feasibility_warnings": [],
                "quality_gate_passed": True,
            },
            "green_visuals": {
                "mermaid_diagrams": ["graph TD\nA[Start]"],
                "formatted_tables": [],
                "visual_score": 8.0,
            },
            "final_output": {
                "markdown": "# Mock SDD\n\nContent placeholder",
                "quality_report": mock_quality_report,
                "passed": mock_quality_report.passed_quality_gate,
            },
        }
