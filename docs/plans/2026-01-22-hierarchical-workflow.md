# Hierarchical Workflow Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Xây dựng Hierarchical Process với CrewAI để scale tốt hơn so với Sequential process, sử dụng Manager Agent (LLM hoặc human) để điều phối các worker agents.

**Architecture:** Thay vì chạy tasks theo thứ tự cố định (Task 1 → Task 2 → Task 3), Hierarchical process sử dụng Manager Agent (CTO) để:
- Phân công tasks động cho worker agents (Architect, Auditor)
- Quyết định task nào chạy tiếp theo dựa trên context
- Tổng hợp kết quả từ tất cả agents
- Cho phép thêm/bớt agents mà không cần refactor code

**Tech Stack:** CrewAI hierarchical process, Pydantic schemas, Python 3.13

---

## Overview: Sequential vs Hierarchical

| Aspect | Sequential Process | Hierarchical Process |
|--------|-------------------|---------------------|
| Scale | 2-5 agents | 10+ agents |
| Task Order | Cố định (T1 → T2 → T3) | Động (Manager quyết định) |
| Context Passing | Tự động chain | Qua Manager |
| Use Case | Simple workflows | Complex, adaptive workflows |
| Flexibility | Thấp | Cao |

**Hierarchical Process Flow:**
```
        ┌─────────────────┐
        │  Manager Agent  │ (CTO - gemini-3-pro-preview)
        │  (Dispatcher)   │
        └────────┬────────┘
                 │
       ┌─────────┴─────────┬─────────────┬────────────┐
       ▼                   ▼             ▼            ▼
┌──────────┐        ┌──────────┐  ┌──────────┐  ┌──────────┐
│Architect │        │ Auditor  │  │Auditor 2 │  │  Auditor │
│ (White)  │        │ (Black)  │  │ (Black)  │  │  (Black) │
│Happy Path│        │Business  │  │Technical │  │Security  │
└──────────┘        └──────────┘  └──────────┘  └──────────┘
```

---

## Task 1: Create Hierarchical Orchestrator

**Files:**
- Create: `src/workflows/hierarchical_orchestrator.py`
- Create: `src/workflows/__init__.py`
- Test: `tests/test_hierarchical_orchestrator.py`

**Step 1: Create `src/workflows/__init__.py`**

```python
"""Hierarchical workflow package."""

from src.workflows.hierarchical_orchestrator import (
    HierarchicalOrchestrator,
    HierarchicalWorkflowConfig,
)

__all__ = [
    "HierarchicalOrchestrator",
    "HierarchicalWorkflowConfig",
]
```

**Step 2: Write the failing test**

Create `tests/test_hierarchical_orchestrator.py`:

```python
import pytest
from crewai import Agent, Task
from src.workflows import HierarchicalOrchestrator, HierarchicalWorkflowConfig

def test_hierarchical_orchestrator_init():
    """Test khởi tạo orchestrator với config."""
    config = HierarchicalWorkflowConfig(
        manager_llm_provider="google",
        verbose=True
    )
    orchestrator = HierarchicalOrchestrator(config)

    assert orchestrator.config.manager_llm_provider == "google"
    assert orchestrator.manager_agent is not None
    assert orchestrator.crew is None  # Crew chưa được tạo

def test_create_hierarchical_crew():
    """Test tạo hierarchical crew với manager."""
    config = HierarchicalWorkflowConfig(
        manager_llm_provider="google",
        verbose=True
    )
    orchestrator = HierarchicalOrchestrator(config)

    # Create worker agents
    from src.agents import create_architect_agent, create_auditor_agent
    architect = create_architect_agent()
    auditor = create_auditor_agent()

    # Create hierarchical crew
    crew = orchestrator.create_hierarchical_crew(
        workers=[architect, auditor]
    )

    assert crew is not None
    assert crew.process == "hierarchical"

def test_execute_workflow():
    """Test execute workflow với hierarchical process."""
    config = HierarchicalWorkflowConfig(
        manager_llm_provider="google",
        verbose=True
    )
    orchestrator = HierarchicalOrchestrator(config)

    from src.agents import create_architect_agent, create_auditor_agent
    architect = create_architect_agent()
    auditor = create_auditor_agent()

    # Create tasks
    happy_path_task = Task(
        description="Thiết kế happy path cho: đăng nhập người dùng",
        expected_output="HappyPath object với luồng đăng nhập thành công",
        agent=architect,
    )

    edge_case_task = Task(
        description="Tìm edge cases cho flow đăng nhập",
        expected_output="StressTestReport với 5+ edge cases",
        agent=auditor,
    )

    # Execute
    result = orchestrator.execute_workflow(
        user_requirement="Hệ thống đăng nhập với email và password",
        tasks=[happy_path_task, edge_case_task]
    )

    assert result is not None
    assert "happy_path" in result or "edge_cases" in result
```

**Step 3: Run test to verify it fails**

```bash
pytest tests/test_hierarchical_orchestrator.py -v
```

Expected: `ImportError: cannot import name 'HierarchicalOrchestrator'`

**Step 4: Write minimal implementation**

Create `src/workflows/hierarchical_orchestrator.py`:

```python
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

from src.utils.llm_provider import get_llm
from src.schemas import HappyPath, StressTestReport

load_dotenv()


@dataclass
class HierarchicalWorkflowConfig:
    """Cấu hình cho Hierarchical Workflow."""

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

    def __init__(self, config: HierarchicalWorkflowConfig):
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

        self.crew = Crew(
            agents=all_agents,
            tasks=tasks,
            process="hierarchical",
            manager_llm=get_llm(self.config.manager_llm_provider),
            verbose=self.config.verbose,
            memory=self.config.memory,
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
```

**Step 5: Run test to verify it passes**

```bash
pytest tests/test_hierarchical_orchestrator.py::test_hierarchical_orchestrator_init -v
```

Expected: PASS

**Step 6: Commit**

```bash
git add src/workflows/__init__.py src/workflows/hierarchical_orchestrator.py tests/test_hierarchical_orchestrator.py
git commit -m "feat: add hierarchical orchestrator with manager agent"
```

---

## Task 2: Create Hierarchical Task Definitions

**Files:**
- Create: `src/tasks/task_definitions.py`
- Create: `src/tasks/__init__.py`
- Test: `tests/test_hierarchical_tasks.py`

**Step 1: Create `src/tasks/__init__.py`**

```python
"""Task definitions for hierarchical workflow."""

from src.tasks.task_definitions import (
    HappyPathTaskDefinition,
    BusinessExceptionsTaskDefinition,
    TechnicalEdgeCasesTaskDefinition,
    create_hierarchical_tasks,
)

__all__ = [
    "HappyPathTaskDefinition",
    "BusinessExceptionsTaskDefinition",
    "TechnicalEdgeCasesTaskDefinition",
    create_hierarchical_tasks,
]
```

**Step 2: Write the failing test**

Create `tests/test_hierarchical_tasks.py`:

```python
import pytest
from src.tasks import create_hierarchical_tasks
from src.agents import create_architect_agent, create_auditor_agent
from src.schemas import HappyPath, StressTestReport

def test_create_hierarchical_tasks():
    """Test tạo 3 tasks cho hierarchical workflow."""
    architect = create_architect_agent()
    auditor = create_auditor_agent()

    tasks = create_hierarchical_tasks(
        user_requirement="Hệ thống đấu giá thời gian thực",
        architect=architect,
        auditor=auditor,
    )

    assert len(tasks) == 3
    assert tasks[0].agent == architect
    assert tasks[1].agent == auditor
    assert tasks[2].agent == auditor

def test_happy_path_task_has_output_pydantic():
    """Test HappyPathTask có output_pydantic đúng."""
    architect = create_architect_agent()
    auditor = create_auditor_agent()

    tasks = create_hierarchical_tasks(
        user_requirement="User registration",
        architect=architect,
        auditor=auditor,
    )

    assert tasks[0].output_pydantic == HappyPath

def test_business_exceptions_task_context():
    """Test BusinessExceptionsTask nhận context từ HappyPath."""
    architect = create_architect_agent()
    auditor = create_auditor_agent()

    tasks = create_hierarchical_tasks(
        user_requirement="Payment processing",
        architect=architect,
        auditor=auditor,
    )

    # Task 2 should reference happy path from task 1
    assert "happy_path" in tasks[1].description.lower()

def test_technical_edge_cases_task_context():
    """Test TechnicalEdgeCasesTask nhận context từ cả 2 tasks trước."""
    architect = create_architect_agent()
    auditor = create_auditor_agent()

    tasks = create_hierarchical_tasks(
        user_requirement="Real-time chat",
        architect=architect,
        auditor=auditor,
    )

    # Task 3 should reference both happy path và business exceptions
    desc_lower = tasks[2].description.lower()
    assert "happy_path" in desc_lower or "happy path" in desc_lower
    assert "business_exception" in desc_lower or "business exception" in desc_lower
```

**Step 3: Run test to verify it fails**

```bash
pytest tests/test_hierarchical_tasks.py -v
```

Expected: `ImportError`

**Step 4: Write minimal implementation**

Create `src/tasks/task_definitions.py`:

```python
"""
Task Definitions cho Hierarchical Workflow.

Khác với sequential, hierarchical tasks không cần context linking thủ công
vì Manager Agent sẽ quyết định task nào chạy và truyền context.
Tuy nhiên, tasks vẫn cần description rõ ràng để Manager hiểu dependencies.
"""

from typing import List, Optional
from crewai import Task
from src.agents import create_architect_agent, create_auditor_agent
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


# === Helper Functions ===


def get_task_for_phase(
    phase: Literal["happy_path", "business_exceptions", "technical_edge_cases"],
    user_requirement: str,
    architect_agent,
    auditor_agent,
) -> Task:
    """
    Lấy task cụ thể cho một phase.

    Hữu ích khi muốn chạy riêng lẻ từng phase.
    """
    phase_mapping = {
        "happy_path": HappyPathTaskDefinition,
        "business_exceptions": BusinessExceptionsTaskDefinition,
        "technical_edge_cases": TechnicalEdgeCasesTaskDefinition,
    }

    task_class = phase_mapping.get(phase)
    if not task_class:
        raise ValueError(
            f"Phase không tồn tại: '{phase}'. "
            f"Các phases có sẵn: {list(phase_mapping.keys())}"
        )

    if phase == "happy_path":
        return task_class.create(user_requirement, architect_agent)
    elif phase == "business_exceptions":
        # Cần tạo dummy happy_path_task cho context
        dummy_task = Task(description="Dummy happy path task")
        return task_class.create(user_requirement, auditor_agent, dummy_task)
    else:
        # Cần tạo dummy tasks cho context
        dummy_task1 = Task(description="Dummy happy path task")
        dummy_task2 = Task(description="Dummy business exceptions task")
        return task_class.create(
            user_requirement, auditor_agent, dummy_task1, dummy_task2
        )
```

**Step 5: Run test to verify it passes**

```bash
pytest tests/test_hierarchical_tasks.py -v
```

Expected: PASS cho test_create_hierarchical_tasks

**Step 6: Commit**

```bash
git add src/tasks/__init__.py src/tasks/task_definitions.py tests/test_hierarchical_tasks.py
git commit -m "feat: add hierarchical task definitions with output_pydantic"
```

---

## Task 3: Create Hierarchical Workflow Entry Point

**Files:**
- Create: `src/workflows/hierarchical_workflow.py`
- Modify: `src/main.py` (add CLI option)
- Test: `tests/test_hierarchical_workflow_integration.py`

**Step 1: Write the failing test**

Create `tests/test_hierarchical_workflow_integration.py`:

```python
import pytest
from src.workflows.hierarchical_workflow import HierarchicalWorkflow, HierarchicalWorkflowConfig

def test_hierarchical_workflow_full_execution():
    """Test end-to-end hierarchical workflow."""
    config = HierarchicalWorkflowConfig(
        manager_llm_provider="google",
        verbose=True,
    )

    workflow = HierarchicalWorkflow(config)

    result = workflow.execute(
        user_requirement="Hệ thống đăng nhập với email và password"
    )

    # Verify structure
    assert "happy_path" in result
    assert "business_exceptions" in result
    assert "technical_edge_cases" in result

    # Verify happy path
    assert result["happy_path"]["feature_name"] is not None
    assert len(result["happy_path"]["steps"]) >= 3

    # Verify business exceptions
    assert len(result["business_exceptions"]["edge_cases"]) >= 5

    # Verify technical edge cases
    assert len(result["technical_edge_cases"]["edge_cases"]) >= 5

def test_hierarchical_workflow_scale_to_multiple_auditors():
    """Test hierarchical workflow có thể scale với nhiều auditors."""
    config = HierarchicalWorkflowConfig(
        manager_llm_provider="google",
        verbose=True,
    )

    workflow = HierarchicalWorkflow(config)

    # Add multiple auditors (khác với sequential chỉ có 1)
    result = workflow.execute(
        user_requirement="Hệ thống chat real-time",
        use_multiple_auditors=True,  # Business + Technical + Security auditors
    )

    assert result is not None
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/test_hierarchical_workflow_integration.py::test_hierarchical_workflow_full_execution -v
```

Expected: `ImportError`

**Step 3: Write minimal implementation**

Create `src/workflows/hierarchical_workflow.py`:

```python
"""
Hierarchical Workflow - Main Entry Point

End-to-end workflow sử dụng CrewAI hierarchical process.
Manager Agent (CTO) điều phối các worker agents để hoàn thành technical design.
"""

from typing import List, Dict, Any, Optional, Literal
from dataclasses import dataclass
from crewai import Agent, Task

from src.workflows.hierarchical_orchestrator import (
    HierarchicalOrchestrator,
    HierarchicalWorkflowConfig as OrchestratorConfig,
)
from src.tasks.task_definitions import create_hierarchical_tasks
from src.agents import create_architect_agent, create_auditor_agent
from src.schemas import HappyPath, StressTestReport


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
        self.orchestrator = HierarchicalOrchestrator(
            OrchestratorConfig(
                manager_llm_provider=config.manager_llm_provider,
                verbose=config.verbose,
                memory=config.memory,
            )
        )
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


# === CLI Interface ===


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
```

**Step 4: Update `src/main.py`**

Add hierarchical workflow option:

```python
# ... existing imports ...
import argparse

# ... existing code ...

def run_hierarchical_workflow(requirement: str):
    """Run hierarchical workflow."""
    from src.workflows.hierarchical_workflow import execute_hierarchical_workflow

    print("\n" + "="*60)
    print("HIERARCHICAL WORKFLOW - Manager Agent Mode")
    print("="*60)

    result = execute_hierarchical_workflow(
        user_requirement=requirement,
        manager_provider="google",
        verbose=True,
    )

    print("\n" + "="*60)
    print("HIERARCHICAL WORKFLOW RESULTS")
    print("="*60)

    # Print happy path
    if "happy_path" in result:
        print("\n[Happy Path]")
        hp = result["happy_path"]
        print(f"Feature: {hp.get('feature_name', 'N/A')}")
        print(f"Steps: {len(hp.get('steps', []))}")

    # Print business exceptions
    if "business_exceptions" in result:
        print("\n[Business Exceptions]")
        be = result["business_exceptions"]
        print(f"Edge Cases: {len(be.get('edge_cases', []))}")

    # Print technical edge cases
    if "technical_edge_cases" in result:
        print("\n[Technical Edge Cases]")
        te = result["technical_edge_cases"]
        print(f"Edge Cases: {len(te.get('edge_cases', []))}")

    return result


def main():
    parser = argparse.ArgumentParser(description="Deep-Spec AI - Technical Design Assistant")
    parser.add_argument(
        "--mode",
        choices=["sequential", "hierarchical"],
        default="hierarchical",
        help="Workflow mode: sequential (old) or hierarchical (new, scalable)",
    )
    parser.add_argument(
        "requirement",
        help="Feature requirement to analyze",
    )

    args = parser.parse_args()

    if args.mode == "hierarchical":
        run_hierarchical_workflow(args.requirement)
    else:
        # Original sequential workflow
        run_original_sequential(args.requirement)


def run_original_sequential(requirement: str):
    """Original sequential workflow (for backward compatibility)."""
    # ... existing code from current main.py ...
    try:
        print("Initializing Agents with different providers...")

        llm_openai = get_llm("zai")
        llm_google = get_llm("google")

        agent_a = Agent(
            role='OpenAI Representative',
            goal='Introduce yourself and your underlying model',
            backstory='You are an AI assistant powered by OpenAI.',
            verbose=True,
            memory=False,
            llm=llm_openai
        )

        agent_b = Agent(
            role='Google Gemini Representative',
            goal='Introduce yourself and your underlying model',
            backstory='You are an AI assistant powered by Google Gemini.',
            verbose=True,
            memory=False,
            llm=llm_google
        )

        task_a = Task(
            description='Say hello and state which model provider you are using.',
            expected_output='A greeting from the OpenAI agent.',
            agent=agent_a,
        )

        task_b = Task(
            description='Say hello and state which model provider you are using. Also compliment the other agent.',
            expected_output='A greeting from the Google agent.',
            agent=agent_b,
        )

        crew = Crew(
            agents=[agent_a, agent_b],
            tasks=[task_a, task_b],
            process='sequential'
        )

        result = crew.kickoff()
        print("\n########################\n")
        print("Crew Execution Result:")
        print(result)
        print("\n########################\n")

    except Exception as e:
        print(f"Error during execution: {e}")


if __name__ == "__main__":
    main()
```

**Step 5: Run test to verify it passes**

```bash
pytest tests/test_hierarchical_workflow_integration.py::test_hierarchical_workflow_full_execution -v
```

Expected: PASS (hoặc SKIP nếu chưa có API keys)

**Step 6: Commit**

```bash
git add src/workflows/hierarchical_workflow.py src/main.py tests/test_hierarchical_workflow_integration.py
git commit -m "feat: add hierarchical workflow entry point with CLI support"
```

---

## Task 4: Update Validation for Hierarchical

**Files:**
- Create: `src/validation/hierarchical_validator.py`
- Modify: `src/workflows/hierarchical_workflow.py` (integrate validator)
- Test: `tests/test_hierarchical_validator.py`

**Step 1: Write the failing test**

Create `tests/test_hierarchical_validator.py`:

```python
import pytest
from src.validation.hierarchical_validator import HierarchicalValidator
from src.schemas import HappyPath, StressTestReport, EdgeCase, FlowStep, MitigationStrategy, RiskLevel

def test_validate_hierarchical_result_pass():
    """Test validation pass với valid result."""
    validator = HierarchicalValidator()

    # Valid happy path
    happy_path = HappyPath(
        feature_id="TEST-001",
        feature_name="Test Feature",
        description="Test",
        steps=[
            FlowStep(step_number=1, actor="User", action="Login", outcome="Success"),
            FlowStep(step_number=2, actor="System", action="Verify", outcome="Valid"),
            FlowStep(step_number=3, actor="System", action="Redirect", outcome="Dashboard"),
        ],
        post_conditions=["User logged in"],
        business_value="Access control",
    )

    # Valid stress test report
    stress_report = StressTestReport(
        report_id="STR-001",
        happy_path_id="TEST-001",
        feature_name="Test Feature",
        edge_cases=[
            EdgeCase(
                scenario_id="EDGE-001",
                description="Invalid password",
                trigger_condition="Wrong password",
                expected_failure="Login fails",
                severity=RiskLevel.LOW,
                likelihood=RiskLevel.HIGH,
                mitigation=MitigationStrategy(
                    description="Show error",
                    technical_implementation="Return 401",
                    implementation_complexity=RiskLevel.LOW,
                ),
            )
        ] * 5,  # 5 edge cases
        resilience_score=80,
        coverage_score=85,
        review_summary="Good",
    )

    result = {
        "happy_path": happy_path,
        "business_exceptions": stress_report,
        "technical_edge_cases": stress_report,
    }

    is_valid, errors = validator.validate_hierarchical_result(result)

    assert is_valid
    assert len(errors) == 0

def test_validate_hierarchical_result_fail_not_enough_steps():
    """Test validation fail khi happy path thiếu steps."""
    validator = HierarchicalValidator()

    happy_path = HappyPath(
        feature_id="TEST-002",
        feature_name="Test Feature 2",
        description="Test",
        steps=[
            FlowStep(step_number=1, actor="User", action="Login", outcome="Success"),
            # Chỉ 2 steps - không đủ
        ],
        post_conditions=["Done"],
        business_value="Test",
    )

    stress_report = StressTestReport(
        report_id="STR-002",
        happy_path_id="TEST-002",
        feature_name="Test Feature 2",
        edge_cases=[
            EdgeCase(
                scenario_id="EDGE-002",
                description="Test",
                trigger_condition="Test",
                expected_failure="Test",
                severity=RiskLevel.LOW,
                likelihood=RiskLevel.LOW,
                mitigation=MitigationStrategy(
                    description="Test",
                    technical_implementation="Test",
                    implementation_complexity=RiskLevel.LOW,
                ),
            )
        ] * 5,
        resilience_score=70,
        coverage_score=70,
        review_summary="Test",
    )

    result = {
        "happy_path": happy_path,
        "business_exceptions": stress_report,
        "technical_edge_cases": stress_report,
    }

    is_valid, errors = validator.validate_hierarchical_result(result)

    assert not is_valid
    assert any("happy path" in err.lower() for err in errors)
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/test_hierarchical_validator.py -v
```

Expected: `ImportError`

**Step 3: Write minimal implementation**

Create `src/validation/hierarchical_validator.py`:

```python
"""
Validation Logic cho Hierarchical Workflow.

Giống DesignValidator nhưng optimized cho hierarchical process:
- Manager agent đã filter, validator chỉ verify quality
- Focus trên completeness và consistency
"""

from typing import Dict, Any, List, Tuple
from src.schemas import HappyPath, StressTestReport


class HierarchicalValidator:
    """
    Validator cho Hierarchical Workflow results.

    Validation rules:
    - Happy path phải có tối thiểu 3 steps
    - Business exceptions phải có tối thiểu 5 edge cases
    - Technical edge cases phải có tối thiểu 5 edge cases
    - Không có trùng lặp giữa business và technical edge cases
    """

    def __init__(self):
        self.validation_rules = {
            "min_happy_path_steps": 3,
            "min_edge_cases": 5,
            "min_resilience_score": 70,
            "min_coverage_score": 70,
        }

    def validate_hierarchical_result(
        self,
        result: Dict[str, Any],
    ) -> Tuple[bool, List[str]]:
        """
        Validate toàn bộ hierarchical workflow result.

        Args:
            result: Dict với keys:
                - happy_path: HappyPath object
                - business_exceptions: StressTestReport object
                - technical_edge_cases: StressTestReport object

        Returns:
            Tuple[bool, List[str]]: (is_valid, list of errors)
        """
        errors = []

        # Validate happy path
        happy_path = result.get("happy_path")
        if happy_path is None:
            errors.append("Missing happy_path in result")
        else:
            hp_errors = self._validate_happy_path(happy_path)
            errors.extend(hp_errors)

        # Validate business exceptions
        be = result.get("business_exceptions")
        if be is None:
            errors.append("Missing business_exceptions in result")
        else:
            be_errors = self._validate_stress_report(be, "business exceptions")
            errors.extend(be_errors)

        # Validate technical edge cases
        te = result.get("technical_edge_cases")
        if te is None:
            errors.append("Missing technical_edge_cases in result")
        else:
            te_errors = self._validate_stress_report(te, "technical edge cases")
            errors.extend(te_errors)

        # Validate no overlap
        if be and te:
            overlap_errors = self._validate_no_overlap(be, te)
            errors.extend(overlap_errors)

        is_valid = len(errors) == 0
        return is_valid, errors

    def _validate_happy_path(self, happy_path: HappyPath) -> List[str]:
        """Validate happy path object."""
        errors = []

        if len(happy_path.steps) < self.validation_rules["min_happy_path_steps"]:
            errors.append(
                f"Happy path must have at least {self.validation_rules['min_happy_path_steps']} steps, "
                f"got {len(happy_path.steps)}"
            )

        return errors

    def _validate_stress_report(
        self,
        report: StressTestReport,
        report_type: str,
    ) -> List[str]:
        """Validate stress test report object."""
        errors = []

        # Check edge cases count
        if len(report.edge_cases) < self.validation_rules["min_edge_cases"]:
            errors.append(
                f"{report_type} must have at least {self.validation_rules['min_edge_cases']} edge cases, "
                f"got {len(report.edge_cases)}"
            )

        # Check scores
        if report.resilience_score < self.validation_rules["min_resilience_score"]:
            errors.append(
                f"{report_type} resilience score too low: {report.resilience_score}"
            )

        if report.coverage_score < self.validation_rules["min_coverage_score"]:
            errors.append(
                f"{report_type} coverage score too low: {report.coverage_score}"
            )

        return errors

    def _validate_no_overlap(
        self,
        business_report: StressTestReport,
        technical_report: StressTestReport,
    ) -> List[str]:
        """
        Validate không có trùng lặp giữa business và technical edge cases.

        Business edge cases nên về rules, logic
        Technical edge cases nên về infrastructure, concurrency, network
        """
        errors = []

        # Get descriptions
        business_desc = set(ec.description.lower() for ec in business_report.edge_cases)
        technical_desc = set(ec.description.lower() for ec in technical_report.edge_cases)

        # Check exact duplicates
        duplicates = business_desc & technical_desc
        if duplicates:
            errors.append(
                f"Found duplicate edge cases between business and technical: {duplicates}"
            )

        # Check business edge cases không chứa technical keywords
        technical_keywords = [
            "concurrency", "race condition", "network", "database",
            "timeout", "deadlock", "websocket", "tcp", "http",
        ]

        for ec in business_report.edge_cases:
            desc_lower = ec.description.lower()
            for keyword in technical_keywords:
                if keyword in desc_lower:
                    errors.append(
                        f"Business edge case should not contain technical keyword '{keyword}': "
                        f"{ec.description}"
                    )
                    break

        return errors
```

**Step 4: Update `src/workflows/hierarchical_workflow.py`**

Integrate validator:

```python
# Add import
from src.validation.hierarchical_validator import HierarchicalValidator

# In HierarchicalWorkflow class:
class HierarchicalWorkflow:
    def __init__(self, config: HierarchicalWorkflowConfig):
        # ... existing code ...
        self.validator = HierarchicalValidator()

    # In execute method, after parsing:
    def execute(self, user_requirement: str) -> Dict[str, Any]:
        # ... existing code ...

        parsed_result = self._parse_workflow_result(result)

        # Validate
        is_valid, errors = self.validator.validate_hierarchical_result(parsed_result)

        if not is_valid:
            print("\n⚠️  Validation Errors:")
            for error in errors:
                print(f"  - {error}")

        parsed_result["validation"] = {
            "is_valid": is_valid,
            "errors": errors,
        }

        return parsed_result
```

**Step 5: Run test to verify it passes**

```bash
pytest tests/test_hierarchical_validator.py -v
```

Expected: PASS

**Step 6: Commit**

```bash
git add src/validation/hierarchical_validator.py tests/test_hierarchical_validator.py
git commit -m "feat: add hierarchical validator with overlap detection"
```

---

## Task 5: Update SEQUENTIAL_WORKFLOW.md Documentation

**Files:**
- Modify: `SEQUENTIAL_WORKFLOW.md` (rename/update to HIERARCHICAL_WORKFLOW.md)
- Create: `HIERARCHICAL_WORKFLOW.md`

**Step 1: Create new documentation**

Create `HIERARCHICAL_WORKFLOW.md`:

```markdown
# Hierarchical Design Workflow

> Mục tiêu: Xây dựng quy trình có khả năng scale với Manager Agent điều phối worker agents động.

## Tổng quan

Hierarchical Design Workflow sử dụng CrewAI's **hierarchical process** để:
- Manager Agent (CTO) điều phối worker agents
- Task execution order linh hoạt (manager quyết định)
- Có thể scale lên 10+ agents
- Context management qua Manager thay vì chain

### Sequential vs Hierarchical

| Aspect | Sequential | Hierarchical |
|--------|-----------|--------------|
| Agent Scale | 2-5 agents | 10+ agents |
| Task Order | Cố định (T1 → T2 → T3) | Động (Manager quyết định) |
| Context Passing | Tự động chain | Qua Manager |
| Flexibility | Thấp | Cao |
| Use Case | Simple workflows | Complex, adaptive workflows |

## Architecture

```
        ┌─────────────────┐
        │  Manager Agent  │ (CTO - gemini-3-pro-preview)
        │  (Dispatcher)   │
        └────────┬────────┘
                 │
       ┌─────────┴─────────┬─────────────┬────────────┐
       ▼                   ▼             ▼            ▼
┌──────────┐        ┌──────────┐  ┌──────────┐  ┌──────────┐
│Architect │        │ Auditor  │  │Auditor 2 │  │  Auditor │
│ (White)  │        │ (Black)  │  │ (Black)  │  │  (Black) │
│Happy Path│        │Business  │  │Technical │  │Security  │
└──────────┘        └──────────┘  └──────────┘  └──────────┘
```

## Usage

```bash
# Run hierarchical workflow
python src/main.py --mode hierarchical "hệ thống đấu giá thời gian thực"
```

```python
from src.workflows.hierarchical_workflow import execute_hierarchical_workflow

result = execute_hierarchical_workflow(
    user_requirement="Hệ thống đấu giá thời gian thực",
    manager_provider="google",
)

print(result["happy_path"]["feature_name"])
print(len(result["business_exceptions"]["edge_cases"]))
```

## File Structure

```
src/
├── workflows/
│   ├── hierarchical_orchestrator.py  # Manager + Crew setup
│   └── hierarchical_workflow.py      # Main entry point
├── tasks/
│   └── task_definitions.py           # Task definitions
├── validation/
│   └── hierarchical_validator.py     # Validation logic
└── agents/                           # Existing agents
```

## Success Metrics

Hierarchical Workflow hoàn thành khi:

1. ✅ Chạy 1 lệnh: `python src/main.py --mode hierarchical "hệ thống..."`
2. ✅ Manager Agent điều phối tasks động
3. ✅ Có thể scale lên nhiều auditors (Business, Technical, Security)
4. ✅ Validation pass với HierarchicalValidator
5. ✅ Existing tests vẫn pass
```

**Step 2: Update original SEQUENTIAL_WORKFLOW.md**

Add note at top:

```markdown
> **NOTE**: This document describes the original sequential workflow approach.
> For the new, scalable hierarchical approach, see [HIERARCHICAL_WORKFLOW.md](./HIERARCHICAL_WORKFLOW.md).

# Checklist Sequential Design Workflow (Legacy)
...
```

**Step 3: Commit**

```bash
git add HIERARCHICAL_WORKFLOW.md SEQUENTIAL_WORKFLOW.md
git commit -m "docs: add hierarchical workflow documentation"
```

---

## Task 6: Final Integration Test

**Files:**
- Test: `tests/test_hierarchical_workflow_e2e.py`

**Step 1: Write comprehensive E2E test**

Create `tests/test_hierarchical_workflow_e2e.py`:

```python
import pytest
from src.workflows.hierarchical_workflow import execute_hierarchical_workflow

@pytest.mark.integration
def test_hierarchical_workflow_complex_feature():
    """Test hierarchical workflow với complex feature."""
    result = execute_hierarchical_workflow(
        user_requirement="Hệ thống đấu giá trực tuyến thời gian thực với 1000 người dùng",
        manager_provider="google",
        verbose=True,
    )

    # Verify structure
    assert "happy_path" in result
    assert "business_exceptions" in result
    assert "technical_edge_cases" in result
    assert "validation" in result

    # Verify validation
    assert result["validation"]["is_valid"], result["validation"]["errors"]

    # Verify happy path
    hp = result["happy_path"]
    assert len(hp["steps"]) >= 3
    assert hp["feature_name"] is not None

    # Verify business exceptions (no technical issues)
    be = result["business_exceptions"]
    assert len(be["edge_cases"]) >= 5
    for ec in be["edge_cases"]:
        desc = ec.get("description", "").lower()
        # Business edge cases không được chứa technical keywords
        assert "concurrency" not in desc
        assert "network" not in desc
        assert "database" not in desc

    # Verify technical edge cases (no business rules)
    te = result["technical_edge_cases"]
    assert len(te["edge_cases"]) >= 5

@pytest.mark.integration
def test_hierarchical_workflow_with_multiple_auditors():
    """Test hierarchical workflow scale với nhiều auditors."""
    from src.workflows.hierarchical_workflow import HierarchicalWorkflow, HierarchicalWorkflowConfig

    config = HierarchicalWorkflowConfig(
        manager_llm_provider="google",
        use_multiple_auditors=True,
        num_auditors=3,  # Business, Technical, Security
    )

    workflow = HierarchicalWorkflow(config)
    result = workflow.execute("Hệ thống chat real-time với WebSocket")

    assert result is not None
    assert len(workflow.agents) == 4  # 1 architect + 3 auditors
```

**Step 2: Run E2E test**

```bash
pytest tests/test_hierarchical_workflow_e2e.py -v -m integration
```

Expected: PASS (nếu có API keys)

**Step 3: Commit**

```bash
git add tests/test_hierarchical_workflow_e2e.py
git commit -m "test: add E2E integration test for hierarchical workflow"
```

---

## Summary

### Files Created

| File | Purpose |
|------|---------|
| `src/workflows/hierarchical_orchestrator.py` | Manager + Crew setup |
| `src/workflows/hierarchical_workflow.py` | Main entry point |
| `src/tasks/task_definitions.py` | Task definitions with output_pydantic |
| `src/validation/hierarchical_validator.py` | Validation logic |
| `tests/test_hierarchical_*.py` | Comprehensive tests |
| `HIERARCHICAL_WORKFLOW.md` | Documentation |

### Files Modified

| File | Changes |
|------|---------|
| `src/main.py` | Add CLI option `--mode hierarchical` |
| `SEQUENTIAL_WORKFLOW.md` | Add legacy note |

### Key Improvements over Sequential

1. **Scalability**: Thêm auditors không cần refactor code
2. **Flexibility**: Manager quyết định task order động
3. **Context Management**: Qua Manager thay vì chain
4. **Maintainability**: Tách biệt orchestrator, workflow, validator

### Usage

```bash
# Run hierarchical workflow
python src/main.py --mode hierarchical "hệ thống đấu giá thời gian thực"

# Or use in code
from src.workflows.hierarchical_workflow import execute_hierarchical_workflow
result = execute_hierarchical_workflow("your feature description")
```
