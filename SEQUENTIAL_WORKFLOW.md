# Checklist Sequential Design Workflow

> Mục tiêu: Xây dựng quy trình chạy không mồi với 3 Task chuyên biệt, context linking, và validation logic bên ngoài CrewAI.

## Tổng quan

Sequential Design Workflow chia nhỏ quá trình thiết kế kỹ thuật thành 3 task chuyên biệt để tránh AI "lan man" và đảm bảo output sạch, có cấu trúc.

- **HappyPathTask**: Phân tích luồng chính - chỉ lấy khung xương
- **BusinessExceptionsTask**: Phân tích ngoại lệ nghiệp vụ - tìm lỗi về "luật chơi"
- **TechnicalEdgeCasesTask**: Stress-test kỹ thuật - tìm lỗi về "hệ thống"

---

## 1. Validation vs Testing - Tại sao tách riêng?

### Validation (Runtime Quality Gates)
- **Chạy trong quá trình thực thi** (runtime), không phải test
- Kiểm tra chất lượng output của AI agent ngay khi agent trả về kết quả
- Yêu cầu retry nếu output không đạt chuẩn
- Là **business logic** của hệ thống, cần deploy cùng app

**Ví dụ**:
- Check: Happy path có ít nhất 3 bước không?
- Check: Edge cases có cụ thể không (không "server error" chung chung)?
- Check: Task 2 có trùng lặp với Task 3 không?

### Testing (Code Verification)
- **Unit tests, integration tests** trong thư mục `tests/`
- Verify code hoạt động đúng như expect
- Không chạy trong production
- Mục đích: verify code, không phải verify AI output

**Ví dụ**:
- Test: `DesignValidator.validate_happy_path()` trả về đúng tuple?
- Test: `SequentialOrchestrator` execute tasks theo đúng thứ tự?
- Test: Context được truyền đúng giữa tasks?

**Kết luận**: Validation logic ở `src/validation/` vì nó là runtime business logic. Tests ở `tests/` để verify code.

---

## 2. Sequential Process với Context Linking

### Mục tiêu
- Cấu hình Crew với `process=Process.sequential`
- HappyPathTask chạy trước, output truyền cho BusinessExceptionsTask
- BusinessExceptionsTask chạy trước, output truyền cho TechnicalEdgeCasesTask
- Context từ Task N được truyền sang Task N+1

### Checklist triển khai

- [ ] **Tạo file `src/workflows/sequential_orchestrator.py`**
  ```python
  class SequentialOrchestrator:
      def __init__(self):
          self.crew = None
          self.context = {}

      def create_sequential_crew(self, agents, tasks):
          # Tạo Crew với process=Process.sequential
          pass

      def execute_workflow(self, user_requirement: str):
          # Chạy workflow và trả về kết quả
          pass
  ```

- [ ] **Cấu hình context sharing giữa tasks**
  - BusinessExceptionsTask nhận `happy_path` từ HappyPathTask
  - TechnicalEdgeCasesTask nhận `happy_path` và `business_exceptions` từ 2 tasks trước

- [ ] **Test sequential execution**
  - Verify BusinessExceptionsTask không chạy trước HappyPathTask hoàn thành
  - Verify TechnicalEdgeCasesTask không chạy trước BusinessExceptionsTask hoàn thành

---

## 3. Định nghĩa Task với Output Pydantic

### Mục tiêu
- Mỗi Task có `output_pydantic` rõ ràng
- Ép kiểu dữ liệu ngay tại nguồn
- Tránh AI trả về văn bản thừa ngoài Schema

### Checklist triển khai

- [ ] **Tạo file `src/tasks/task_definitions.py`**

  **HappyPathTask**
  ```python
  from crewai import Task
  from src.schemas import HappyPath

  happy_path_task = Task(
      description="Phân tích luồng chính cho: {requirement}",
      expected_output="Output là HappyPath object với workflow tối thiểu 3 bước",
      agent=architect,
      output_pydantic=HappyPath,
      context={"requirement": str},
      instructions=[
          "CHỈ tập trung vào luồng thành công.",
          "KHÔNG được liệt kê lỗi kỹ thuật.",
          "Nếu thấy lỗi tiềm ẩn, BỎ QUA.",
          "Output phải đúng schema HappyPath."
      ]
  )
  ```

  **BusinessExceptionsTask**
  ```python
  from src.schemas import StressTestReport

  business_exceptions_task = Task(
      description="Phân tích ngoại lệ nghiệp vụ dựa trên: {happy_path}",
      expected_output="Output là StressTestReport với business rule edge cases",
      agent=auditor,
      output_pydantic=StressTestReport,
      context={"happy_path": HappyPath},
      instructions=[
          "Dựa trên các bước happy_path từ HappyPathTask.",
          "Tìm các bước có thể bị chặn bởi logic nghiệp vụ.",
          "Ví dụ: không đủ số dư, chưa đủ cấp độ, giới hạn thời gian.",
          "KHÔNG tìm lỗi kỹ thuật (concurrency, network, database).",
          "Output phải đúng schema StressTestReport."
      ]
  )
  ```

  **TechnicalEdgeCasesTask**
  ```python
  technical_edge_cases_task = Task(
      description="Stress-test kỹ thuật dựa trên: {happy_path} và {business_exceptions}",
      expected_output="Output là StressTestReport với technical edge cases",
      agent=auditor,
      output_pydantic=StressTestReport,
      context={"happy_path": HappyPath, "business_exceptions": StressTestReport},
      instructions=[
          "Dựa trên happy_path và business_exceptions đã phân tích.",
          "Tìm các vấn đề kỹ thuật: concurrency, race conditions, data integrity.",
          "Tìm vấn đề infrastructure: network, database, timeouts.",
          "KHÔNG lặp lại các business exceptions từ BusinessExceptionsTask.",
          "Output phải đúng schema StressTestReport."
      ]
  )
  ```

- [ ] **Tạo `src/tasks/task_factory.py`**
  ```python
  class TaskFactory:
      def create_sequential_tasks(self, user_requirement: str):
          """Tạo 3 tasks cho sequential workflow."""
          pass

      def get_task_with_context(self, task_template: str, **context):
          """Tạo task với context variables đã fill."""
          pass
  ```

- [ ] **Test output_pydantic validation**
  - Verify HappyPathTask trả về HappyPath object
  - Verify BusinessExceptionsTask trả về StressTestReport object
  - Verify TechnicalEdgeCasesTask trả về StressTestReport object

---

## 4. Validation Logic Bên Ngoài CrewAI

### Mục tiêu
- "Người gác cổng" bằng code Python thuần túy
- Kiểm tra chất lượng output của mỗi Task
- Yêu cầu làm lại nếu không đạt chất lượng

### Checklist triển khai

- [ ] **Tạo file `src/validation/design_validator.py`**
  ```python
  class DesignValidator:
      def __init__(self):
          self.validation_rules = {
              "min_workflow_steps": 3,
              "min_edge_cases_per_task": 3,
              "no_overlap_check": True
          }

      def validate_happy_path(self, result: HappyPath) -> tuple[bool, str]:
          """Validate HappyPathTask output."""
          if len(result.steps) < 3:
              return False, "Luồng chính quá sơ sài, cần ít nhất 3 bước."
          # Check không có edge case trong happy path
          return True, "PASS"

      def validate_business_exceptions(self, result: StressTestReport, happy_path: HappyPath) -> tuple[bool, str]:
          """Validate BusinessExceptionsTask output."""
          if len(result.edge_cases) < 3:
              return False, "Cần ít nhất 3 business exceptions."
          # Check edge cases là business rules, not technical
          technical_keywords = ['concurrency', 'race condition', 'network', 'database']
          for ec in result.edge_cases:
              if any(kw in ec.description.lower() for kw in technical_keywords):
                  return False, f"BusinessExceptionsTask không được chứa technical issues: {ec.description}"
          return True, "PASS"

      def validate_technical_edge_cases(self, result: StressTestReport, previous_reports: list) -> tuple[bool, str]:
          """Validate TechnicalEdgeCasesTask output."""
          if len(result.edge_cases) < 3:
              return False, "Cần ít nhất 3 technical edge cases."
          # Check không trùng lặp với BusinessExceptionsTask
          return True, "PASS"

      def validate_final_output(self, final_result) -> dict:
          """Validate final output và trả về report."""
          pass
  ```

- [ ] **Implement kiểm tra trùng lặp**
  - BusinessExceptionsTask không được chứa edge cases về concurrency, network, database
  - TechnicalEdgeCasesTask chỉ được chứa technical issues, không business logic issues

- [ ] **Implement kiểm tra độ chi tiết**
  - Happy path phải có tối thiểu 3 bước
  - Mỗi task phải có ít nhất 3 edge cases
  - Edge cases phải cụ thể, không chung chung ("server error", "network error")

---

## 5. Feedback Loop Mechanism

### Mục tiêu
- Yêu cầu Agent làm lại nếu output không đạt chất lượng
- Tự động retry với giới hạn số lần
- Trả về kết quả cuối cùng khi đạt chất lượng

### Checklist triển khai

- [ ] **Tạo file `src/workflows/feedback_loop.py`**
  ```python
  class FeedbackLoop:
      def __init__(self, max_retries: int = 3):
          self.max_retries = max_retries
          self.validator = DesignValidator()

      def execute_with_retry(self, task, context: dict) -> dict:
          """Execute task với retry logic."""
          for attempt in range(self.max_retries):
              result = task.execute(context)
              is_valid, message = self.validator.validate_task_result(result)

              if is_valid:
                  return result

              # Update context với feedback
              context["feedback"] = message
              context["attempt"] = attempt + 1

          raise Exception(f"Task failed after {self.max_retries} attempts")
  ```

- [ ] **Test feedback loop**
  - Test khi HappyPathTask trả về kết quả kém -> tự động retry
  - Test giới hạn retry (max 3 lần)
  - Test feedback được truyền đúng cho Agent

---

## 6. File Structure Cần Tạo

```
src/
├── tasks/
│   ├── __init__.py
│   ├── task_definitions.py      # 3 Task definitions với output_pydantic
│   └── task_factory.py           # Factory để tạo tasks
├── workflows/
│   ├── __init__.py
│   ├── sequential_orchestrator.py # Sequential process
│   ├── feedback_loop.py          # Feedback loop mechanism
│   └── sequential_workflow.py    # Main sequential workflow entry point
├── validation/
│   ├── __init__.py
│   ├── design_validator.py       # External validation logic (runtime quality gates)
│   └── validation_rules.py        # Validation rules configuration
└── config/
    ├── __init__.py
    ├── task_config.py             # Task configuration
    └── validation_config.py       # Validation thresholds
```

---

## 7. Files Cần Cập Nhật

- [ ] **Cập nhật `src/main.py`**
  - Thêm sequential workflow execution option
  - Add command line interface để chọn workflow mode

- [ ] **Cập nhật `src/workflows/__init__.py`**
  - Export SequentialOrchestrator
  - Export FeedbackLoop

---

## 8. Testing Checklist

### Unit Tests

- [ ] **Test Task definitions**
  - Verify output_pydantic ép đúng schema
  - Verify context được truyền đúng

- [ ] **Test SequentialOrchestrator**
  - Verify sequential execution order
  - Verify context linking works correctly

- [ ] **Test DesignValidator**
  - Verify validate_happy_path() reject thiếu bước
  - Verify validate_business_exceptions() reject thiếu edge cases
  - Verify validate_technical_edge_cases() detect trùng lặp

- [ ] **Test FeedbackLoop**
  - Verify retry mechanism hoạt động
  - Verify feedback được truyền đúng

### Integration Tests

- [ ] **Test end-to-end sequential workflow**
  ```python
  def test_sequential_workflow_complex_feature():
      orchestrator = SequentialOrchestrator()
      result = orchestrator.execute_workflow(
          "Hệ thống đấu giá thời gian thực với 1000 người dùng đồng thời"
      )

      # Verify HappyPathTask: Happy path has success flow
      assert result.happy_path.steps[0].action == "Đấu giá"

      # Verify BusinessExceptionsTask: Business exceptions (số dư, giới hạn)
      business_cases = result.business_exceptions.edge_cases
      assert any("số dư" in case.description for case in business_cases)

      # Verify TechnicalEdgeCasesTask: Technical edge cases (race conditions)
      tech_cases = result.technical_edge_cases.edge_cases
      assert any("race condition" in case.description for case in tech_cases)
  ```

- [ ] **Test complex input**
  - "Hệ thống thanh toán với retries, timeouts, và fraud detection"
  - "Hệ thống chat real-time với WebSocket scaling"

---

## 9. Validation Criteria - Khi nào Sequential Workflow Hoàn Thành?

### Chạy thử nghiệm với tính năng phức tạp

**Input example**: "Hệ thống đấu giá trực tuyến thời gian thực với 1000 người dùng"

### Kiểm tra Console Output:

**HappyPathTask - PASS nếu:**
- Chỉ chứa các bước thành công: "Người A đặt giá 100", "Người B đặt giá 110", "Hệ thống ghép đôi lệnh"
- KHÔNG nhắc đến: "race condition", "network timeout", "database deadlock"

**BusinessExceptionsTask - PASS nếu:**
- Chỉ chứa business rule violations:
  - "Số dư không đủ để thực hiện lệnh"
  - "Giá đặt quá chênh lệ so với giá thị"
  - "Người dùng chưa được xác thực"
- KHÔNG nhắc đến: "WebSocket disconnect", "database connection pool"

**TechnicalEdgeCasesTask - PASS nếu:**
- Chỉ chứa technical issues:
  - "Hai người cùng bấm giá trong cùng 1ms" (race condition)
  - "WebSocket connection dropped midway"
  - "Database transaction timeout"
- KHÔNG nhắc lại: "số dư không đủ", "chưa xác thực"

### Kiểm tra Final Output:

- [ ] **Output đúng cấu trúc**
  - File JSON/Python object hoàn chỉnh
  - Truy xuất được kiểu: `result.happy_path.steps[0].action`

- [ ] **Không có văn bản thừa**
  - Không có "tôi là AI", "dưới đây là kết quả", v.v.
  - Chỉ có dữ liệu theo Schema

- [ ] **Validation pass**
  - `validator.validate_final_output()` trả về success
  - Tất cả 3 tasks pass validation riêng

---

## 10. Dependencies Cần Thêm

### requirements.txt
```
crewai==0.80.0  # Hoặc phiên bản mới hơn
pydantic==2.0.0
python-dotenv==1.0.0
```

---

## 11. Priority Order

### Cao nhất (Must Have)
1. Task definitions với output_pydantic
2. Sequential process với context linking
3. Validation logic bên ngoài (DesignValidator)
4. Update main.py cho sequential workflow

### Trung bình (Should Have)
5. Feedback loop mechanism
6. Comprehensive integration tests
7. Error handling và recovery

### Thấp (Nice to Have)
8. Progress tracking cho workflow execution
9. Logging chi tiết từng step
10. Web UI để monitor workflow execution

---

## 12. Files cần tạo/cập nhật (tóm tắt)

| File | Action | Priority |
|------|--------|----------|
| `src/tasks/task_definitions.py` | Tạo mới | Cao nhất |
| `src/workflows/sequential_orchestrator.py` | Tạo mới | Cao nhất |
| `src/validation/design_validator.py` | Tạo mới | Cao nhất |
| `src/main.py` | Cập nhật | Cao nhất |
| `src/tasks/task_factory.py` | Tạo mới | Trung bình |
| `src/workflows/feedback_loop.py` | Tạo mới | Trung bình |
| `tests/test_sequential_workflow.py` | Tạo mới | Trung bình |

---

## 13. Success Metrics

Sequential Workflow hoàn thành khi:

1. ✅ Chạy 1 lệnh: `python src/main.py --sequential "hệ thống đấu giá..."`
2. ✅ Console log hiển thị HappyPathTask → BusinessExceptionsTask → TechnicalEdgeCasesTask
3. ✅ Final output là Python object (không phải text cần parse)
4. ✅ Validation pass: không có lỗi chung chung, không trùng lặp, đủ chi tiết
5. ✅ 103 existing tests vẫn pass (không break existing code)
