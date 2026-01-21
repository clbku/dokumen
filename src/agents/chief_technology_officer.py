"""
Chief Technology Officer Agent (Green Hat) - Trọng tài Và Tổng hợp

Role: Giám đốc Kỹ thuật (Green Hat)
Provider: Google Gemini (gemini-3-pro-preview)
Purpose: Trọng tài các tranh luận và đưa ra quyết định cân bằng, trưởng thành

Agent này đại diện cho sự tổng hợp và phán xét trong hệ multi-agent.
Nó cân bằng sự lạc quan của Senior System Architect với sự hoài nghi của QA Auditor
để tạo ra quyết định trưởng thành và khả thi.
"""

from crewai import Agent
from src.utils.llm_provider import get_agent_llm

# Import tools
from src.tools.file_tools import (
    read_file,
    read_markdown_file,
    read_code_file,
)

from src.tools.web_search_tools import (
    web_search,
    search_documentation,
)


def create_green_hat_agent(
    verbose: bool = True,
    memory: bool = True,
    allow_delegation: bool = True,
    enable_tools: bool = True,
) -> Agent:
    """
    Tạo và cấu hình Agent Chief Technology Officer (Green Hat).

    Agent này chịu trách nhiệm:
    - Trọng tài các tranh luận giữa Senior System Architect và QA Auditor
    - Đưa ra quyết định cuối cho các đề xuất xung đột
    - Đánh giá độ trưởng thành và chất lượng của tài liệu
    - Cân bằng chức năng với tính thực tế
    - Ngăn chặn over-engineering trong khi đảm bảo độ mạnh mẽ
    - Chạy quality gates để xác thực output

    Provider khuyến nghị: Google Gemini (gemini-3-pro-preview)
    Lý do: Khả năng suy luận mạnh mẽ cho ra quyết định cân bằng,
         tốt trong việc tổng hợp và đánh giá, xử lý phân tích trade-off phức tạp,
         tạo ra phản hồi có cấu trúc và tinh tế.

    Args:
        verbose: Bật logging chi tiết (mặc định: True)
        memory: Bật memory để lưu ngữ cảnh (mặc định: True)
        allow_delegation: Cho phép agent ủy quyền task lại các agent khác
                          (mặc định: True) - CTO có thể yêu cầu revision
        enable_tools: Bật tools cho agent (mặc định: True)

    Returns:
        Agent: Instance của Chief Technology Officer Agent đã được cấu hình

    Examples:
        >>> from src.agents.chief_technology_officer import create_green_hat_agent
        >>> cto = create_green_hat_agent()
        >>> print(cto.role)
        'Giám đốc Kỹ thuật (Green Hat)'
    """
    # Get optimized LLM for GreenHat role (balanced temperature for judgment)
    llm = get_agent_llm("green_hat")

    # Configure tools for the CTO (minimal tools - focuses on decision making)
    tools = []
    if enable_tools:
        tools = [
            # File reading tools - để review documentation
            read_file,
            read_markdown_file,
            read_code_file,
            # Web search tools - để research alternatives và trade-offs
            web_search,
            search_documentation,
        ]

    return Agent(
        # === Identity ===
        role="Giám đốc Kỹ thuật (Green Hat)",

        # === Primary Goal ===
        goal=(
            "Làm trọng tài cho các cuộc tranh luận giữa Kiến trúc sư và Người phản biện để đưa ra "
            "quyết định cân bằng, trưởng thành. Đảm bảo tài liệu đáp ứng tiêu chuẩn chất lượng "
            "trong khi ngăn chặn việc over-engineering. Chỉ phê duyệt khi giải pháp vừa mạnh mẽ vừa thực tế."
        ),

        # === Background & Personality ===
        backstory=(
            "Bạn là một Giám đốc Kỹ thuật (CTO) dày dạn kinh nghiệm với hơn 15 năm lãnh đạo các tổ chức kỹ thuật. "
            "Bạn đã chứng kiến hàng ngàn thiết kế, từ các giải pháp thanh lịch đến những cơn ác mộng over-engineered. "
            "Siêu năng lực của bạn là 'Sự Phán Đoán'—biết cái gì là 'đủ tốt' so với cái gì cần sự hoàn hảo.\n\n"
            "Triết lý của bạn:\n"
            "1. **Sự Xuất Sắc Thực Dụng**: Hoàn hảo là kẻ thù của cái tốt. Ship giải pháp mạnh mẽ, dễ bảo trì, không phải sự hoàn hảo lý thuyết.\n"
            "2. **Nhận Thức Đánh Đổi**: Mọi quyết định đều có chi phí. Hãy làm rõ chúng.\n"
            "3. **Bối Cảnh Là Quan Trọng**: Một pattern 'tệ' có thể đúng trong một bối cảnh cụ thể.\n\n"
            "Khung ra quyết định của bạn:\n"
            "- **Tính khả thi**: Có thể xây dựng với nguồn lực hiện có không?\n"
            "- **Tính bảo trì**: Dev tương lai có hiểu và sửa đổi được không?\n"
            "- **Tính kiểm thử**: Có thể test đầy đủ không?\n"
            "- **Khả năng mở rộng**: Có chịu được tăng trưởng thực tế (không phải giả định) không?\n"
            "- **Bảo mật**: Các rủi ro chính có được giảm thiểu mà không quá phức tạp không?\n"
            "- **Giá trị kinh doanh**: Đầu tư kỹ thuật có xứng đáng với lợi ích kinh doanh không?\n\n"
            "Điều bạn Từ Chối:\n"
            "- Over-engineering cho 'yêu cầu tương lai' có thể không bao giờ đến\n"
            "- Tối ưu hóa sớm trước khi đo lường điểm nghẽn thực tế\n"
            "- Sự thuần túy học thuật bỏ qua các ràng buộc thực tế\n"
            "- 'Analysis paralysis'—thảo luận quá mức mà không hành động\n"
            "- Các tính năng 'dát vàng' vượt quá nhu cầu người dùng\n\n"
            "Bạn là Người Tổng Hợp. Bạn biến xung đột thành sự rõ ràng."
        ),

        # === Behavioral Configuration ===
        verbose=verbose,
        memory=memory,
        allow_delegation=allow_delegation,
        llm=llm,

        # === Tools ===
        tools=tools if tools else None,

        # === Task-Specific Guidelines ===
        instructions=[
            "LUÔN TRẢ LỜI BẰNG TIẾNG VIỆT.",
            "Luôn xem xét quan điểm của cả Senior System Architect và QA Auditor trước khi quyết định",
            "Ghi lại lý do đằng sau mọi quyết định",
            "Yêu cầu thêm thông tin nếu cuộc tranh luận chưa ngã ngũ",
            "Ủy quyền lại cho các agent nếu đầu vào của họ cần chỉnh sửa",
            "Chấm điểm chất lượng tài liệu bằng các chỉ số cụ thể (0-100)",
            "Phân biệt giữa cải tiến 'bắt buộc' và 'nên có'",
            "Ưu tiên dựa trên giá trị kinh doanh và rủi ro kỹ thuật",
            "Cân nhắc giữa nỗ lực triển khai và lợi ích mang lại",
            "Đánh dấu các quyết định cần sự chấp thuận của các bên liên quan",
            "Đảm bảo tất cả đầu ra tuân thủ Pydantic schemas",
            # Tool usage guidelines
            "Sử dụng tools để đọc và hiểu documentation trước khi ra quyết định",
            "Research alternatives và trade-offs khi có nhiều giải pháp",
            "Đọc code examples để hiểu practical implications",
        ],

        # === Output Quality Standards ===
        quality_criteria=[
            "Các quyết định tuân thủ schema Pydantic: ConsensusDecision",
            "Mỗi quyết định bao gồm: chủ đề, quyết định, lý do, ý kiến bất đồng",
            "QualityGateReport bao gồm: overall_maturity_score, depth_score, completeness_score",
            "MaturityMetric bao gồm: metric_name, điểm số, ngưỡng, trạng thái đạt",
            "Các cải tiến được phân loại 'bắt buộc' vs 'đề xuất'",
            "Lý do phải cụ thể và tham chiếu đến các luận điểm tranh luận",
            "Điểm tin cậy phản ánh độ chắc chắn thực tế (0.0-1.0)",
            "Quyết định phải khả thi và không gây nhầm lẫn",
            "Điểm đạt tối thiểu là 70 cho các quality gates",
        ],
    )


# === Chief Technology Officer Agent Task Templates ===

GREEN_HAT_TASK_TEMPLATES = {
    "arbitrate_debate": {
        "description": (
            "Review tranh luận giữa các agent Senior System Architect và QA Auditor và đưa ra quyết định cuối.\n\n"
            "Chủ đề tranh luận:\n"
            "{topic}\n\n"
            "Vị trí của Senior System Architect (Kiến trúc sư):\n"
            "{white_hat_position}\n\n"
            "Vị trí của QA & Security Auditor (Người phản biện):\n"
            "{black_hat_position}\n\n"
            "Bối cảnh thiết kế liên quan:\n"
            "{context}\n\n"
            "Nhiệm vụ của bạn:\n"
            "1. Đọc và hiểu tài liệu và context liên quan (nếu có)\n"
            "2. Phân tích cả hai vị trí một cách cẩn thận\n"
            "3. Xác định các điểm đồng ý và bất đồng\n"
            "4. Đánh giá tính hợp lý kỹ thuật của mỗi luận điểm\n"
            "5. Cân nhắc tác động kinh doanh và tính khả thi triển khai\n"
            "6. Đưa ra quyết định rõ ràng với lý do hỗ trợ\n"
            "7. Tài liệu hóa các ý kiến bất đồng bạn đã bác bỏ\n\n"
            "Output phải tuân thủ Pydantic schema: ConsensusDecision"
        ),
        "expected_output": (
            "Một object ConsensusDecision hoàn chỉnh:\n"
            "- decision_id: Định danh duy nhất\n"
            "- topic: Điều đã được tranh luận\n"
            "- decision: Quyết định cuối rõ ràng, khả thi\n"
            "- reasoning: Tại sao quyết định này được đạt (trích dẫn luận điểm cụ thể)\n"
            "- dissenting_opinions: Các điểm chính được xem xét nhưng bác bỏ\n"
            "- participating_agents: [Senior System Architect, QA & Security Auditor, CTO]\n"
            "- confidence_score: 0.0-1.0 (mức độ tin cậy vào quyết định này)\n"
            "- impact_area: Những phần của hệ thống bị ảnh hưởng\n\n"
            "Định dạng: JSON hợp lệ khớp với schema ConsensusDecision"
        ),
    },

    "run_quality_gate": {
        "description": (
            "Đánh giá chất lượng của tài liệu kỹ thuật và chạy quality gates.\n\n"
            "Tài liệu để đánh giá:\n"
            "{document_details}\n\n"
            "Tiêu chí đánh giá:\n"
            "1. **Tính Đầy Đủ** (0-100): Có phải tất cả các phần bắt buộc đều có mặt không?\n"
            "   - Kiến trúc hệ thống với components và interactions\n"
            "   - Happy paths với steps và outcomes\n"
            "   - Edge cases (tối thiểu 5 mỗi feature)\n"
            "   - Agent comments và consensus decisions\n\n"
            "2. **Độ Sâu** (0-100): Có đủ chi tiết kỹ thuật không?\n"
            "   - Công nghệ và patterns cụ thể (không chung chung)\n"
            "   - Chi tiết triển khai cụ thể\n"
            "   - Edge cases thực (không lý thuyết)\n"
            "   - Chiến lược mitigation khả thi\n\n"
            "3. **Tính Đúng Đắn** (0-100): Thiết kế có đúng kỹ thuật không?\n"
            "   - Tuân thủ schemas đã định nghĩa (không thiếu required fields)\n"
            "   - Tính nhất quán logic giữa các components\n"
            "   - Lựa chọn kỹ thuật khả thi\n"
            "   - Không có mâu thuẫn hoặc bất khả thi\n\n"
            "4. **Tính Rõ Ràng** (0-100): Có thể implement mà không mơ hồ không?\n"
            "   - Trách nhiệm component rõ ràng\n"
            "   - Định nghĩa step không mơ hồ\n"
            "   - Protocols và định dạng dữ liệu cụ thể\n"
            "   - Các giả định và ràng buộc rõ ràng\n\n"
            "Nhiệm vụ của bạn:\n"
            "Chấm điểm mỗi tiêu chí và xác định độ trưởng thành tổng thể.\n"
            "Liệt kê các cải tiến bắt buộc nếu score < 70.\n"
            "Liệt kê các cải tiến gợi ý để chất lượng cao hơn.\n\n"
            "Output phải tuân thủ Pydantic schema: QualityGateReport"
        ),
        "expected_output": (
            "Một object QualityGateReport hoàn chỉnh:\n"
            "- report_id: Định danh duy nhất\n"
            "- target_id: Đang đánh giá cái gì\n"
            "- overall_maturity_score: 0-100 (phải >= 70 để pass)\n"
            "- depth_score: 0-100\n"
            "- completeness_score: 0-100\n"
            "- metrics: List[MaturityMetric] với phân tích chi tiết\n"
            "- passed: Boolean (True nếu tất cả metrics quan trọng pass)\n"
            "- required_improvements: Vấn đề bắt buộc fix trước khi publication\n"
            "- suggested_improvements: Cải tiến nice-to-have\n\n"
            "Định dạng: JSON hợp lệ khớp với schema QualityGateReport"
        ),
    },

    "synthesize_feedback": {
        "description": (
            "Tổng hợp phản hồi từ tất cả các agent và tạo tóm tắt gắn kết.\n\n"
            "Agent Comments:\n"
            "{agent_comments}\n\n"
            "Thiết kế gốc:\n"
            "{original_design}\n\n"
            "Nhiệm vụ của bạn:\n"
            "1. Đọc và hiểu tất cả feedback từ các agents\n"
            "2. Xác định các chủ đề chung qua các phản hồi của agent\n"
            "3. Giải quyết mâu thuẫn giữa các agent\n"
            "4. Ưu tiên các vấn đề theo severity và impact\n"
            "5. Tạo tóm tắt khả thi cho team phát triển\n"
            "6. Chỉ định những gì cần làm vs những gì là tùy chọn\n\n"
            "Output nên rõ ràng, có cấu trúc và khả thi."
        ),
        "expected_output": (
            "Một tóm tắt có cấu trúc bao gồm:\n"
            "- Tóm tắt điều hành các phát hiện chính\n"
            "- Các hành động được Ưu tiên (must-have vs nice-to-have)\n"
            "- Các quyết định đã giải quyết với lý do\n"
            "- Các câu hỏi mở cần input từ stakeholder\n"
            "- Các bước tiếp theo cho team phát triển"
        ),
    },

    "review_and_approve": {
        "description": (
            "Review tài liệu thiết kế kỹ thuật cuối cùng và phê duyệt hoặc yêu cầu revision.\n\n"
            "Tài liệu:\n"
            "{document}\n\n"
            "Báo cáo Quality Gate:\n"
            "{quality_gate_report}\n\n"
            "Nhiệm vụ của bạn:\n"
            "1. Review tài liệu thiết kế kỹ thuật hoàn chỉnh\n"
            "2. Kiểm tra rằng các tiêu chí quality gate được đáp ứng\n"
            "3. Xác minh rằng tất cả phản hồi của agent đã được giải quyết\n"
            "4. Đảm bảo tất cả validations của schema pass\n"
            "5. Hoặc phê duyệt tài liệu hoặc chỉ định các revision cần thiết\n\n"
            "Nếu phê duyệt, tài liệu sẵn sàng để implement.\n"
            "Nếu từ chối, nêu rõ những gì cần fix trước khi re-submit."
        ),
        "expected_output": (
            "Quyết định cuối bao gồm:\n"
            "- Decision: APPROVED hoặc REVISIONS_REQUIRED\n"
            "- Tóm tắt chất lượng tài liệu\n"
            "- Các revision bắt buộc (nếu có)\n"
            "- Độ tin cậy vào thiết kế\n"
            "- Đề xuất cho team triển khai"
        ),
    },

    "research_alternatives": {
        "description": (
            "Nghiên cứu các giải pháp thay thế cho một quyết định kỹ thuật.\n\n"
            "Quyết định cần nghiên cứu:\n"
            "{decision_context}\n\n"
            "Giải pháp hiện tại:\n"
            "{current_solution}\n\n"
            "Nhiệm vụ của bạn:\n"
            "1. Tìm kiếm các alternatives đã được đề xuất hoặc đã sử dụng trong industry\n"
            "2. So sánh ưu/nhược điểm của từng alternative\n"
            "3. Đánh giá trade-offs: cost, complexity, performance, maintainability\n"
            "4. Tìm case studies thực tế về các alternatives này\n"
            "5. Đề xuất recommendation có nên thay đổi không, và nếu có thì chọn alternative nào\n"
        ),
        "expected_output": (
            "Báo cáo nghiên cứu bao gồm:\n"
            "- Giới thiệu các alternatives\n"
            "- So sánh chi tiết (trade-offs matrix)\n"
            "- Case studies và examples thực tế\n"
            "- Recommendation với lý do"
        ),
    },
}


def get_green_hat_task_template(template_name: str) -> dict:
    """
    Lấy template task được cấu hình trước cho Chief Technology Officer Agent.

    Args:
        template_name: Tên của template ("arbitrate_debate",
                        "run_quality_gate", "synthesize_feedback", "review_and_approve", "research_alternatives")

    Returns:
        dict: Template với các khóa 'description' và 'expected_output'

    Raises:
        ValueError: Nếu tên template không tồn tại
    """
    template = GREEN_HAT_TASK_TEMPLATES.get(template_name)
    if not template:
        available = ", ".join(GREEN_HAT_TASK_TEMPLATES.keys())
        raise ValueError(
            f"Template không tồn tại: '{template_name}'. "
            f"Các template có sẵn: {available}"
        )
    return template.copy()


# === Quality Gate Scoring Helpers ===

QUALITY_GATE_THRESHOLDS = {
    "completeness": {
        "excellent": 90,
        "good": 75,
        "acceptable": 70,
        "poor": 50,
    },
    "depth": {
        "excellent": 85,
        "good": 70,
        "acceptable": 65,
        "poor": 45,
    },
    "correctness": {
        "excellent": 95,
        "good": 80,
        "acceptable": 70,
        "poor": 50,
    },
    "clarity": {
        "excellent": 90,
        "good": 75,
        "acceptable": 65,
        "poor": 50,
    },
}


def get_quality_threshold(metric_name: str, level: str = "acceptable") -> int:
    """
    Lấy ngưỡng chất lượng cho một metric và level cụ thể.

    Args:
        metric_name: Một trong 'completeness', 'depth', 'correctness', 'clarity'
        level: Một trong 'excellent', 'good', 'acceptable', 'poor'

    Returns:
        int: Threshold score (0-100)

    Raises:
        ValueError: Nếu metric_name hoặc level không tồn tại
    """
    thresholds = QUALITY_GATE_THRESHOLDS.get(metric_name)
    if not thresholds:
        raise ValueError(
            f"Metric không tồn tại: '{metric_name}'. "
            f"Có sẵn: {list(QUALITY_GATE_THRESHOLDS.keys())}"
        )

    threshold = thresholds.get(level)
    if threshold is None:
        raise ValueError(
            f"Level không tồn tại: '{level}'. "
            f"Có sẵn: {list(thresholds.keys())}"
        )

    return threshold


def get_minimum_acceptable_score(metric_name: str) -> int:
    """
    Lấy điểm chấp nhận tối thiểu để metric pass quality gates.

    Args:
        metric_name: Một trong 'completeness', 'depth', 'correctness', 'clarity'

    Returns:
        int: Điểm pass tối thiểu (thường là 65-70)
    """
    return get_quality_threshold(metric_name, "acceptable")
