"""
Hierarchical Workflow Orchestrator

Sử dụng CrewAI's hierarchical process với Manager Agent điều phối worker agents.
Manager có thể là LLM hoặc human để điều phối task động.
"""

from typing import List, Optional, Dict, Any, Literal
from dataclasses import dataclass, field
from crewai import Agent, Task, Crew, LLM
from dotenv import load_dotenv
import os

from src.utils.llm_provider import get_llm, get_google_gemini_embedder_config
from src.schemas import HappyPath, StressTestReport

load_dotenv()


@dataclass
class HierarchicalOrchestratorConfig:
    """Cấu hình cho Hierarchical Orchestrator."""

    # Manager LLM config
    manager_llm_provider: Literal["zai", "google"] = "google"
    manager_llm_model: str = "gemini/gemini-3-pro-preview"

    # Workflow config
    verbose: bool = True
    memory: bool = True

    # Execution config
    max_execution_time: Optional[int] = None  # seconds
    allow_delegation_to_manager: bool = True

    # Hierarchical-specific config
    manager_role: str = (
        "Technical Project Manager - Điều phối tasks cho team, "
        "quyết định task nào chạy tiếp, tổng hợp kết quả"
    )
    manager_goal: str = (
        "Điều phối hiệu quả worker agents để hoàn thành technical design, "
        "đảm bảo tất cả aspects được cover (happy path, edge cases, security)"
    )
    manager_backstory: str = (
        "Bạn là CTO với 15 năm kinh nghiệm. Bạn biết cách phân công tasks, "
        "đánh giá kết quả, và quyết định hướng đi tiếp theo dựa trên context. "
        "Bạn không làm việc trực tiếp, chỉ điều phối và tổng hợp."
    )


class HierarchicalOrchestrator:
    """
    Orchestrator cho Hierarchical Process workflow.

    Trong hierarchical process:
    - Manager Agent (CTO) điều phối worker agents
    - Workers thực hiện tasks cụ thể
    - Manager quyết định task nào chạy tiếp dựa trên kết quả
    - Manager tổng hợp final output

    Advantages over Sequential:
    - Có thể scale lên 10+ agents
    - Task order động (manager quyết định)
    - Dễ thêm/bớt agents
    - Context management tốt hơn
    """

    def __init__(self, config: HierarchicalOrchestratorConfig):
        self.config = config
        self.manager_agent: Optional[Agent] = None
        self.crew: Optional[Crew] = None
        self._create_manager_agent()

    def _create_manager_agent(self) -> Agent:
        """Tạo Manager Agent để điều phối workflow."""
        manager_llm = get_llm(self.config.manager_llm_provider)

        self.manager_agent = Agent(
            role="Manager Agent - CTO",
            goal=self.config.manager_goal,
            backstory=self.config.manager_backstory,
            llm=manager_llm,
            verbose=self.config.verbose,
            memory=self.config.memory,
            allow_delegation=self.config.allow_delegation_to_manager,
            # Manager không làm task cụ thể, chỉ điều phối
            instructions=[
                "LUÔN TRẢ LỜI BẰNG TIẾNG VIỆT.",
                "Điều phối worker agents để hoàn thành technical design",
                "Đánh giá kết quả từ từng worker trước khi quyết định bước tiếp theo",
                "Tổng hợp output từ tất cả workers thành final document",
                "Đảm bảo tất cả aspects được cover: happy path, edge cases, security",
                "Ra quyết định dựa trên context và chất lượng output của workers",
                "Phân công task phù hợp cho từng worker dựa trên khả năng của họ",
            ],
        )
        return self.manager_agent

    def create_hierarchical_crew(
        self,
        workers: List[Agent],
        tasks: Optional[List[Task]] = None,
    ) -> Crew:
        """
        Tạo Hierarchical Crew với Manager điều phối Workers.

        Args:
            workers: Danh sách worker agents (Architect, Auditors, etc.)
            tasks: Optional list of tasks (có thể add sau)

        Returns:
            Crew: Hierarchical crew object
        """
        if tasks is None:
            tasks = []

        all_agents = [self.manager_agent] + workers

        # Configure Google Gemini embeddings for memory/RAG
        embedder_config = get_google_gemini_embedder_config()

        self.crew = Crew(
            agents=all_agents,
            tasks=tasks,
            process="hierarchical",
            manager_llm=get_llm(self.config.manager_llm_provider),
            verbose=self.config.verbose,
            memory=self.config.memory,
            embedder=embedder_config,
        )

        return self.crew

    def execute_workflow(
        self,
        user_requirement: str,
        tasks: List[Task],
        workers: Optional[List[Agent]] = None,
    ) -> Dict[str, Any]:
        """
        Execute hierarchical workflow với manager điều phối.

        Args:
            user_requirement: Yêu cầu từ user (feature description)
            tasks: Danh sách tasks cần thực hiện
            workers: Optional worker agents (nếu chưa tạo crew)

        Returns:
            dict: Kết quả workflow với các keys:
                - manager_output: Kết quả từ manager
                - task_results: Kết quả từng task
                - final_result: Kết quả tổng hợp
        """
        if workers is not None and self.crew is None:
            # Create crew nếu chưa có
            self.create_hierarchical_crew(workers=workers, tasks=tasks)
        elif self.crew is None:
            raise ValueError(
                "Crew chưa được tạo. Provide workers hoặc gọi create_hierarchical_crew() trước."
            )
        else:
            # Add tasks nếu crew đã tồn tại
            self.crew.tasks = tasks

        # Execute
        result = self.crew.kickoff()

        return {
            "manager_output": getattr(self.manager_agent, "output", None),
            "raw_output": result,
            "final_result": self._parse_hierarchical_result(result),
        }

    def _parse_hierarchical_result(self, raw_result: str) -> Dict[str, Any]:
        """
        Parse kết quả từ hierarchical execution.

        Manager sẽ tổng hợp kết quả từ tất cả workers.
        Parse để trích xuất structured data.
        """
        # TODO: Implement proper parsing dựa trên output format
        # Hiện tại return raw, sau này sẽ parse Pydantic objects
        return {
            "raw": raw_result,
            "parsed": False,
        }

    def reset(self):
        """Reset crew để có thể tạo mới."""
        self.crew = None
