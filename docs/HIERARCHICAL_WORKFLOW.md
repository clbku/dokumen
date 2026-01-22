# Hierarchical Design Workflow

> **NOTE**: Đây là tài liệu cho **Hierarchical workflow** - approach mới với khả năng scale tốt hơn. Để xem tài liệu gốc cho Sequential workflow, xem [SEQUENTIAL_WORKFLOW.md](./SEQUENTIAL_WORKFLOW.md).
>
> Mục tiêu: Xây dựng quy trình có thể scale lên 10+ agents với Manager Agent điều phối động, context management tốt hơn, và task execution linh hoạt.

## Tổng quan

Hierarchical Design Workflow là kiến trúc thế hệ mới sử dụng CrewAI's **hierarchical process** với một Manager Agent điều phối các Worker Agents. Khác với sequential workflow (task cố định), hierarchical cho phép manager quyết định task nào chạy tiếp dựa trên context và kết quả thực tế.

### Ưu điểm của Hierarchical over Sequential

| Dimension | Sequential Workflow | Hierarchical Workflow |
|-----------|---------------------|----------------------|
| **Scale** | 2-5 agents | 10+ agents |
| **Task Order** | Cố định (hard-coded) | Động (manager quyết định) |
| **Context Management** | Truyền tay liền mạch | Manager tổng hợp và phân phối |
| **Flexibility** | Thêm task = rewrite code | Thêm task = dynamic delegation |
| **Error Recovery** | Linear retry | Manager có thể skip/pivot |
| **Complexity** | Đơn giản | Phức tạp hơn nhưng scalable |

### Architecture Diagram

```
┌────────────────────────────────────────────────────────────────────────┐
│                         HIERARCHICAL WORKFLOW                          │
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │                     MANAGER AGENT (CTO)                          │  │
│  │  - Điều phối task execution                                     │  │
│  │  - Quyết định task nào chạy tiếp                                 │  │
│  │  - Tổng hợp kết quả từ workers                                   │  │
│  │  - Context management & delegation                               │  │
│  └─────────────────────────────────────────────────────────────────┘  │
│                              ↓↓                                       │
│         ┌────────────────────┴────────────────────┐                  │
│         │          Dynamic Task Delegation         │                  │
│         └────────────────────┬────────────────────┘                  │
│                              ↓↓                                       │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │                      WORKER AGENTS                               │  │
│  │                                                                  │  │
│  │  ┌──────────────────┐  ┌──────────────────┐                     │  │
│  │  │   Architect      │  │     Auditor      │                     │  │
│  │  │  (White Hat)     │  │  (Black Hat)     │                     │  │
│  │  │                  │  │                  │                     │  │
│  │  │ - Happy Path     │  │ - Edge Cases     │                     │  │
│  │  │ - Architecture   │  │ - Security       │                     │  │
│  │  │ - Data Models    │  │ - Stress Test    │                     │  │
│  │  └──────────────────┘  └──────────────────┘                     │  │
│  │                                                                  │  │
│  │  [Scale: Thêm nhiều auditors cho different aspects]              │  │
│  └─────────────────────────────────────────────────────────────────┘  │
│                              ↓↓                                       │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │                   HIERARCHICAL VALIDATOR                         │  │
│  │  - Validate task outputs                                         │  │
│  │  - Quality gate enforcement                                      │  │
│  │  - Return structured results                                     │  │
│  └─────────────────────────────────────────────────────────────────┘  │
│                              ↓↓                                       │
│                     FINAL OUTPUT (Pydantic Objects)                   │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 1. Sequential vs Hierarchical - Khi nào dùng gì?

### Sequential Workflow
**Phù hợp cho**:
- Projects nhỏ với 2-5 agents
- Task order cố định, không thay đổi
- Context flow đơn giản (A → B → C)
- Quick prototyping

**Ví dụ**:
```
HappyPathTask → BusinessExceptionsTask → TechnicalEdgeCasesTask
```

### Hierarchical Workflow
**Phù hợp cho**:
- Projects lớn với 10+ agents
- Task order động (có thể skip/bypass)
- Complex context management
- Cần scale linh hoạt

**Ví dụ**:
```
Manager nhận requirement
  ↓
Manager quyết định: Architect chạy trước
  ↓
Architect trả về Happy Path
  ↓
Manager review: "Đủ detail, tiếp tục với Auditor"
  ↓
Auditor chạy Business Exceptions
  ↓
Manager review: "Cần thêm Technical Edge Cases"
  ↓
Auditor chạy Technical Edge Cases
  ↓
Manager tổng hợp final output
```

---

## 2. Hierarchical Process Components

### 2.1 Manager Agent (CTO)

**Role**: Điều phối viên, không làm việc trực tiếp

**Responsibilities**:
- Nhận user requirement
- Quyết định task nào chạy tiếp
- Tổng hợp kết quả từ workers
- Quality gate enforcement
- Context management

**Configuration**:
```python
manager_llm_provider: "google"  # hoặc "zai"
manager_llm_model: "gemini/gemini-3-pro-preview"
verbose: True
memory: True
allow_delegation: True  # Manager có thể delegate lại cho workers
```

### 2.2 Worker Agents

#### Architect (White Hat)
- **Provider**: Z.AI (glm-4.7)
- **Role**: Thiết kế happy path và architecture
- **Tasks**:
  - Design happy path flow
  - Định nghĩa data models
  - Tạo system diagrams

#### Auditor (Black Hat)
- **Provider**: Google Gemini (gemini-3-pro-preview)
- **Role**: Stress test và tìm edge cases
- **Tasks**:
  - Business exceptions
  - Technical edge cases
  - Security vulnerabilities
  - Performance bottlenecks

**Scale Feature**: Có thể tạo nhiều auditors:
- `auditor_0`: Business exceptions
- `auditor_1`: Technical edge cases
- `auditor_2`: Security audit
- `auditor_3`: Performance stress test

### 2.3 Hierarchical Validator

**Role**: External validation logic (runtime quality gates)

**Validates**:
- HappyPath output có ≥ 3 steps
- BusinessExceptions có ≥ 5 edge cases
- TechnicalEdgeCases có ≥ 5 edge cases
- Không trùng lặp giữa tasks
- Edge cases cụ thể, không chung chung

---

## 3. Usage Examples

### 3.1 CLI Usage

**Basic Execution**:
```bash
python src/main.py --hierarchical "Hệ thống đấu giá thời gian thực với 1000 người dùng"
```

**With Custom Configuration**:
```bash
python src/main.py --hierarchical \
  --manager-provider google \
  --architect-provider zai \
  --auditor-provider google \
  --verbose \
  "Hệ thống thanh toán với retries và timeouts"
```

**Scale with Multiple Auditors**:
```bash
python src/main.py --hierarchical \
  --use-multiple-auditors \
  --num-auditors 3 \
  "Hệ thống chat real-time với WebSocket scaling"
```

### 3.2 Python API

**Basic Usage**:
```python
from src.workflows.hierarchical_workflow import execute_hierarchical_workflow

result = execute_hierarchical_workflow(
    user_requirement="Hệ thống đấu giá thời gian thực",
    manager_provider="google",
    architect_provider="zai",
    auditor_provider="google",
    verbose=True,
)

# Access results
print(f"Feature: {result['happy_path']['feature_name']}")
print(f"Happy Path Steps: {len(result['happy_path']['steps'])}")
print(f"Business Exceptions: {len(result['business_exceptions']['edge_cases'])}")
print(f"Technical Edge Cases: {len(result['technical_edge_cases']['edge_cases'])}")
print(f"Validation: {result['validation']['is_valid']}")
```

**Advanced Usage with Configuration**:
```python
from src.workflows.hierarchical_workflow import HierarchicalWorkflow, HierarchicalWorkflowConfig

config = HierarchicalWorkflowConfig(
    manager_llm_provider="google",
    architect_provider="zai",
    auditor_provider="google",
    verbose=True,
    memory=True,
    use_multiple_auditors=True,
    num_auditors=3,
)

workflow = HierarchicalWorkflow(config)
result = workflow.execute("Hệ thống thanh toán với fraud detection")
```

**Scale with Multiple Auditors**:
```python
# Tạo 3 auditors cho different aspects
result = execute_hierarchical_workflow(
    user_requirement="Hệ thống chat real-time",
    use_multiple_auditors=True,
)

# Manager sẽ điều phối 3 auditors:
# - auditor_0: Business exceptions
# - auditor_1: Technical edge cases
# - auditor_2: Security audit
```

---

## 4. File Structure

```
src/
├── agents/
│   ├── __init__.py                      # Agent factory functions
│   ├── senior_system_architect.py       # Architect (White Hat)
│   ├── qa_security_auditor.py           # Auditor (Black Hat)
│   └── chief_technology_officer.py      # CTO (Manager)
│
├── tasks/
│   ├── __init__.py                      # Task exports
│   └── task_definitions.py              # Hierarchical task definitions
│
├── workflows/
│   ├── __init__.py
│   ├── hierarchical_orchestrator.py     # Manager + Crew orchestration
│   └── hierarchical_workflow.py         # Main workflow entry point
│
├── validation/
│   ├── __init__.py
│   └── hierarchical_validator.py        # Validation logic
│
├── schemas/
│   ├── __init__.py                      # Pydantic schemas
│   ├── happy_path.py
│   └── stress_test_report.py
│
├── utils/
│   ├── __init__.py
│   └── llm_provider.py                  # LLM provider factory
│
└── main.py                              # CLI entry point
```

---

## 5. Hierarchical Process Flow

### 5.1 Initialization Phase

```python
# 1. Create configuration
config = HierarchicalWorkflowConfig(
    manager_llm_provider="google",
    verbose=True,
)

# 2. Create workflow
workflow = HierarchicalWorkflow(config)

# 3. Manager agent được tạo
workflow.orchestrator.manager_agent  # CTO Manager
```

### 5.2 Execution Phase

```python
# 4. Execute workflow
result = workflow.execute("Hệ thống đấu giá thời gian thực")

# Internal process:
# 4.1. Create workers (Architect, Auditor)
# 4.2. Create tasks (HappyPath, BusinessExceptions, TechnicalEdgeCases)
# 4.3. Manager reviews tasks và quyết định execution order
# 4.4. Workers execute tasks
# 4.5. Manager tổng hợp kết quả
# 4.6. Validator validates outputs
# 4.7. Return structured result
```

### 5.3 Manager Decision Making

Manager sử dụng LLM để quyết định:
1. **Task prioritization**: Task nào chạy trước?
2. **Dependency resolution**: Task B có phụ thuộc Task A không?
3. **Context sharing**: Context từ Task A có cần cho Task B không?
4. **Quality check**: Task A có đạt chất lượng không?
5. **Pivot decision**: Cần skip task hay retry?

---

## 6. Validation & Quality Gates

### 6.1 HierarchicalValidator

```python
from src.validation.hierarchical_validator import HierarchicalValidator

validator = HierarchicalValidator()

# Validate entire result
is_valid, errors = validator.validate_hierarchical_result(result)

if not is_valid:
    for error in errors:
        print(f"Validation Error: {error}")
```

### 6.2 Validation Rules

**HappyPath Validation**:
```python
- Min 3 steps: len(happy_path.steps) >= 3
- Structured flow: mỗi step có actor, action, outcome
- No edge cases: happy path chỉ chứa success flow
```

**BusinessExceptions Validation**:
```python
- Min 5 edge cases: len(edge_cases) >= 5
- Business rules only: không technical issues
- Specific triggers: không "server error" chung chung
- Mitigation strategy: mỗi edge case có mitigation
```

**TechnicalEdgeCases Validation**:
```python
- Min 5 edge cases: len(edge_cases) >= 5
- Technical issues only: không business rules
- No overlap: không trùng lặp với BusinessExceptions
- Specific scenarios: concrete technical problems
```

### 6.3 Quality Scores

```python
resilience_score >= 70  # Minimum acceptable
coverage_score >= 70    # Minimum acceptable
```

---

## 7. Success Metrics

Hierarchical Workflow hoàn thành khi:

- [ ] **CLI Execution**: Chạy lệnh `python src/main.py --hierarchical "hệ thống..."` thành công
- [ ] **Manager Coordination**: Manager agent điều phối workers đúng
- [ ] **Dynamic Task Order**: Manager quyết định task order dựa trên context
- [ ] **Structured Output**: Return Python objects (Pydantic), không text
- [ ] **Validation Pass**: Tất cả validation rules pass
- [ ] **No Regression**: 103 existing tests vẫn pass
- [ ] **Scale Capability**: Có thể thêm auditors without changing code

### Console Output Checklist

**Manager Agent - PASS nếu**:
- Log hiển thị Manager decisions
- Manager điều phối tasks theo đúng logic
- Manager tổng hợp final output

**Architect Agent - PASS nếu**:
- HappyPath output có ≥ 3 steps
- Steps có actor, action, outcome
- Không có edge cases trong happy path

**Auditor Agent - PASS nếu**:
- BusinessExceptions có ≥ 5 edge cases
- TechnicalEdgeCases có ≥ 5 edge cases
- Không trùng lặp giữa 2 tasks
- Edge cases cụ thể, không chung chung

**Validator - PASS nếu**:
- Tất cả validation rules pass
- Quality scores ≥ 70
- No validation errors

---

## 8. Comparison: Sequential vs Hierarchical

### 8.1 Code Comparison

**Sequential Workflow**:
```python
from src.workflows.sequential_orchestrator import SequentialOrchestrator

orchestrator = SequentialOrchestrator()
result = orchestrator.execute_workflow("Hệ thống đấu giá")

# Tasks chạy theo thứ tự cố định:
# 1. HappyPathTask
# 2. BusinessExceptionsTask (sau HappyPath)
# 3. TechnicalEdgeCasesTask (sau BusinessExceptions)
```

**Hierarchical Workflow**:
```python
from src.workflows.hierarchical_workflow import HierarchicalWorkflow

config = HierarchicalWorkflowConfig(manager_llm_provider="google")
workflow = HierarchicalWorkflow(config)
result = workflow.execute("Hệ thống đấu giá")

# Manager quyết định task order:
# - Có thể skip tasks nếu không cần
# - Có thể chạy parallel nếu không phụ thuộc
# - Có thể retry tasks nếu quality thấp
```

### 8.2 Feature Comparison

| Feature | Sequential | Hierarchical |
|---------|-----------|--------------|
| **Max Agents** | 2-5 | 10+ |
| **Task Order** | Fixed | Dynamic |
| **Context Management** | Linear | Manager-controlled |
| **Error Handling** | Retry same task | Manager can pivot |
| **Scalability** | Limited | High |
| **Complexity** | Simple | Moderate |
| **Use Case** | Small projects | Large projects |

---

## 9. Migration Guide: Sequential → Hierarchical

### Step 1: Update Import
```python
# Old (Sequential)
from src.workflows.sequential_orchestrator import SequentialOrchestrator

# New (Hierarchical)
from src.workflows.hierarchical_workflow import HierarchicalWorkflow, HierarchicalWorkflowConfig
```

### Step 2: Update Configuration
```python
# Old
orchestrator = SequentialOrchestrator()

# New
config = HierarchicalWorkflowConfig(
    manager_llm_provider="google",
    verbose=True,
)
workflow = HierarchicalWorkflow(config)
```

### Step 3: Update Execution
```python
# Old
result = orchestrator.execute_workflow(requirement)

# New
result = workflow.execute(requirement)
```

### Step 4: Update Result Access
```python
# Old - Sequential results
result.happy_path.steps
result.business_exceptions.edge_cases

# New - Hierarchical results (same structure)
result['happy_path']['steps']
result['business_exceptions']['edge_cases']
```

---

## 10. Troubleshooting

### Issue: Manager không điều phối đúng

**Symptoms**:
- Tasks chạy theo顺序 lạ
- Manager skip important tasks

**Solutions**:
1. Check manager LLM provider (nên dùng Google Gemini)
2. Review manager backstory và goal
3. Tăng verbose để xem manager decisions

### Issue: Workers không nhận tasks

**Symptoms**:
- Workers idle
- No worker output

**Solutions**:
1. Verify workers được create đúng
2. Check crew process="hierarchical"
3. Verify tasks được assign đúng agents

### Issue: Validation fail

**Symptoms**:
- Validation errors
- Low quality scores

**Solutions**:
1. Review task descriptions và expected outputs
2. Check LLM provider cho từng agent
3. Tăng retry count cho tasks
4. Review validation thresholds

---

## 11. Best Practices

### 11.1 Manager Configuration

```python
# Recommended: Use Google Gemini cho Manager
config = HierarchicalWorkflowConfig(
    manager_llm_provider="google",  # Best cho decision-making
    verbose=True,  # Enable logs để debug
    memory=True,  # Enable context memory
    allow_delegation=True,  # Manager có thể delegate
)
```

### 11.2 Worker Configuration

```python
# Architect: Use Z.AI cho creative design
architect = create_architect_agent(
    provider="zai",
    verbose=True,
    allow_delegation=False,  # Không delegate
)

# Auditor: Use Google Gemini cho critical thinking
auditor = create_auditor_agent(
    provider="google",
    verbose=True,
    allow_delegation=False,  # Không delegate
)
```

### 11.3 Scale Configuration

```python
# Multi-auditor setup cho complex features
config = HierarchicalWorkflowConfig(
    use_multiple_auditors=True,
    num_auditors=3,  # Business, Technical, Security
)
```

---

## 12. Dependencies

### requirements.txt
```
crewai==0.80.0
pydantic==2.0.0
python-dotenv==1.0.0
google-generativeai==0.8.0  # Cho Google Gemini
zai-sdk==1.0.0               # Cho Z.AI (hypothetical)
```

### Environment Variables
```bash
# .env file
GOOGLE_API_KEY=your_google_api_key
ZAI_API_KEY=your_zai_api_key
OPENAI_API_KEY=your_openai_api_key  # Optional
```

---

## 13. References

- [CrewAI Documentation - Hierarchical Process](https://docs.crewai.com/concepts/processes/hierarchical)
- [SEQUENTIAL_WORKFLOW.md](./SEQUENTIAL_WORKFLOW.md) - Original sequential approach
- [PRODUCT_VISION.md](./PRODUCT_VISION.md) - Product vision and architecture

---

*Document Version: 1.0*
*Last Updated: January 2026*
*Workflow Owner: Deep-Spec AI Team*
