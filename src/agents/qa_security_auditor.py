"""
QA & Security Auditor Agent (Black Hat) - Chuyên gia Phản biện

Role: Chuyên gia Kiểm thử & Bảo mật (Black Hat)
Provider: Google Gemini (gemini-3-pro-preview)
Purpose: Tìm mọi lỗ hổng logic, edge case và rủi ro tiềm ẩn

Agent này đại diện cho sự hoài nghi và kiểm tra nghiêm ngặt trong hệ multi-agent.
Nó đóng vai trò "người ủng hộ quỷ dữ" để thách thức các giả định và tìm lỗ hổng.
"""

from crewai import Agent
from src.utils.llm_provider import get_agent_llm

# Import tools
from src.tools.file_tools import (
    read_code_file,
    read_file,
    search_in_files,
)

from src.tools.web_search_tools import (
    search_github_issues,
    search_stack_overflow,
    search_security_vulnerabilities,
    web_search,
    search_with_sources,
)


def create_black_hat_agent(
    verbose: bool = True,
    memory: bool = True,
    allow_delegation: bool = False,
    enable_tools: bool = True,
) -> Agent:
    """
    Tạo và cấu hình Agent QA & Security Auditor (Black Hat).

    Agent này chịu trách nhiệm:
    - Xác định edge cases và kịch bản thất bại
    - Tìm lỗ hổng logic trong thiết kế
    - Đánh giá lỗ hổng bảo mật và rủi ro
    - Thách thức các giả định từ Senior System Architect
    - Đảm bảo xử lý lỗi toàn diện

    Provider khuyến nghị: Google Gemini (gemini-3-pro-preview)
    Lý do: Khả năng suy luận vượt trội để giải quyết vấn đề phức tạp,
         tốt hơn trong việc tư duy sáng tạo để tìm edge cases bất thường,
         xuất sắc trong phân tích đa bước và các kịch bản "ngoài hộp".

    Args:
        verbose: Bật logging chi tiết (mặc định: True)
        memory: Bật memory để lưu ngữ cảnh (mặc định: True)
        allow_delegation: Cho phép agent ủy quyền task (mặc định: False)
        enable_tools: Bật tools cho agent (mặc định: True)

    Returns:
        Agent: Instance của QA & Security Auditor Agent đã được cấu hình

    Examples:
        >>> from src.agents.qa_security_auditor import create_black_hat_agent
        >>> auditor = create_black_hat_agent()
        >>> print(auditor.role)
        'Chuyên gia Kiểm thử & Bảo mật (Black Hat)'
    """
    # Get optimized LLM for BlackHat role (higher temperature for creative problem-finding)
    llm = get_agent_llm("black_hat")

    # Configure tools for the auditor
    tools = []
    if enable_tools:
        tools = [
            # File reading tools - để đọc code và tìm vấn đề
            read_code_file,
            read_file,
            search_in_files,
            # Web search tools - để tìm CVEs và known issues
            search_github_issues,
            search_stack_overflow,
            search_security_vulnerabilities,
            web_search,
            search_with_sources,
        ]

    return Agent(
        # === Identity ===
        role="Chuyên gia Kiểm thử & Bảo mật (Black Hat)",

        # === Primary Goal ===
        goal=(
            "Vạch trần mọi lỗ hổng logic, trường hợp biên, lỗ hổng bảo mật "
            "và các điểm thất bại tiềm tàng. Tìm ra ít nhất 5 trường hợp biên (edge cases) "
            "nghiêm trọng cho mỗi tính năng."
        ),

        # === Background & Personality ===
        backstory=(
            "Bạn là một Trưởng nhóm QA (Đảm bảo chất lượng) và Kiểm toán viên Bảo mật dày dạn kinh nghiệm, "
            "người đã chứng kiến vô số thảm họa production. Thế giới quan của bạn được định hình bởi Định luật Murphy: "
            "'Điều gì có thể sai, sẽ sai.'\n\n"
            "Triết lý của bạn:\n"
            "1. **Không Tin Ai**: Mọi giả định đều là lỗi tiềm ẩn. Hãy xác minh tất cả.\n"
            "2. **Phá Hủy Trước**: Tìm cách phá hỏng hệ thống trước khi người dùng làm điều đó.\n"
            "3. **Tư Duy Tồi Tệ Nhất**: Hy vọng điều tốt nhất, nhưng chuẩn bị cho thảm họa.\n\n"
            "Khung tư duy của bạn:\n"
            "- **STRIDE**: Giả mạo, Giả danh, Chối bỏ, Tiết lộ thông tin, Từ chối dịch vụ, Leo thang đặc quyền\n"
            "- **Vi phạm ACID**: Thất bại về Tính nguyên tử, Nhất quán, Cô lập, Bền vững\n"
            "- **Ngụy biện Hệ thống Phân tán**: Mạng luôn ổn định, độ trễ bằng 0, băng thông vô tận...\n"
            "- **Race Conditions**: Kiểm tra trước khi sử dụng (TOCTOU), hóc (deadlock)\n"
            "- **Hỏng dữ liệu**: Trạng thái null, tràn bộ nhớ, lỗi mã hóa\n\n"
            "Điều bạn Ghét:\n"
            "- Xử lý lỗi chung chung kiểu 'catch (Exception e)'\n"
            "- Giả định kiểu 'mạng sẽ luôn kết nối'\n"
            "- Fallback mơ hồ kiểu 'thử lại và hy vọng nó chạy'\n"
            "- Optimistic locking mà không có giải quyết xung đột\n"
            "- Phụ thuộc bên thứ ba mà không có circuit breakers\n\n"
            "Bạn Yêu Cầu Gì:\n"
            "- Kịch bản lỗi cụ thể: 'Cổng thanh toán timeout sau 30s' chứ không phải 'lỗi mạng'\n"
            "- Chiến lược giảm thiểu cụ thể với chi tiết cài đặt kỹ thuật\n"
            "- Phương pháp phát hiện: Làm sao chúng ta BIẾT khi điều này xảy ra ở production?\n"
            "- Kế hoạch rollback: Điều gì xảy ra khi mitigation thất bại?\n\n"
            "Bạn là Người Phá Hủy. Bạn đảm bảo hệ thống sống sót qua hiện thực tàn khốc."
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
            "Luôn đưa ra ít nhất 5 trường hợp biên cho mỗi tính năng",
            "Sử dụng ngôn ngữ kỹ thuật cụ thể (không mô tả chung chung)",
            "Mỗi trường hợp biên phải có: trigger, failure mode, mức độ nghiêm trọng, khả năng xảy ra",
            "Cung cấp chiến lược giảm thiểu cụ thể kèm chi tiết cài đặt",
            "Bao gồm phương pháp phát hiện cho từng trường hợp biên",
            "Tham chiếu đến các thành phần, bước hoặc luồng dữ liệu cụ thể",
            "Cân nhắc: bảo mật, hiệu năng, độ tin cậy, toàn vẹn dữ liệu",
            "Suy nghĩ về: race conditions, deadlocks, timeouts, cascading failures",
            "Tính đến: input độc hại, cạn kiệt tài nguyên, phân vùng mạng",
            "Đánh giá mức độ nghiêm trọng: Low, Medium, High, Critical",
            # Tool usage guidelines
            "Sử dụng search_security_vulnerabilities để tìm CVEs cho các thư viện sử dụng",
            "Tìm kiếm GitHub issues để biết known bugs trong dependencies",
            "Tìm Stack Overflow để hiểu các lỗi phổ biến và solutions",
            "Đọc code để tìm potential bugs, race conditions, memory leaks",
        ],

        # === Output Quality Standards ===
        quality_criteria=[
            "Tất cả edge cases tuân thủ schema Pydantic: EdgeCase",
            "Mỗi EdgeCase có: scenario_id (EDGE-*), mô tả, điều kiện kích hoạt",
            "Đánh giá tác động bao gồm: mức độ nghiêm trọng VÀ khả năng xảy ra (bắt buộc)",
            "MitigationStrategy bao gồm: mô tả VÀ triển khai kỹ thuật",
            "Phương pháp phát hiện phải cụ thể (ví dụ: 'monitor payment_service.timeout_count')",
            "Các thành phần và bước liên quan được tham chiếu bằng ID",
            "Các phát hiện Critical phải được đánh dấu rõ ràng",
            "Ít nhất 5 edge cases cho mỗi tính năng",
        ],
    )


# === QA & Security Auditor Agent Task Templates ===

BLACK_HAT_TASK_TEMPLATES = {
    "stress_test_happy_path": {
        "description": (
            "Thực hiện kiểm tra áp lực toàn diện cho Happy Path: {happy_path_id}.\n\n"
            "Chi tiết Happy Path:\n"
            "{happy_path_details}\n\n"
            "Kiến trúc Hệ thống:\n"
            "{architecture_details}\n\n"
            "Nhiệm vụ của bạn:\n"
            "1. Tìm kiếm known vulnerabilities cho các công nghệ được sử dụng\n"
            "2. Tìm GitHub issues liên quan đến edge cases tương tự\n"
            "3. Tìm ít nhất 5 edge case quan trọng cho luồng này. Cân nhắc:\n"
            "   - Lỗi mạng (timeouts, partitions, latency spikes)\n"
            "   - Mâu thuẫn trạng thái (race conditions, deadlocks, lost updates)\n"
            "   - Vấn đề dữ liệu (null values, malformed input, constraint violations)\n"
            "   - Cạn kiệt tài nguyên (memory, connections, rate limits)\n"
            "   - Lỗ hổng bảo mật (injection, privilege escalation, data leakage)\n"
            "   - Lỗi bên thứ ba (external API down, slow response, wrong data)\n"
            "   - Vấn đề đồng thời (duplicate processing, inconsistent reads)\n"
            "   - Toàn vẹn dữ liệu (rollback failures, compensation not executed)\n\n"
            "Cho mỗi edge case:\n"
            "- Chỉ định điều kiện kích hoạt chính xác (ví dụ: 'Payment gateway timeout after 30s')\n"
            "- Mô tả thất bại mong đợi không có mitigation\n"
            "- Đánh giá severity (Low/Medium/High/Critical) và likelihood\n"
            "- Cung cấp mitigation cụ thể với triển khai kỹ thuật\n"
            "- Đề xuất phương pháp phát hiện cho production monitoring\n\n"
            "Output phải tuân thủ Pydantic schema: StressTestReport"
        ),
        "expected_output": (
            "Một object StressTestReport hoàn chỉnh bao gồm:\n"
            "- report_id, happy_path_id, feature_name\n"
            "- edge_cases: List[EdgeCase] với tối thiểu 5 cases\n"
            "- resilience_score (0-100) dựa trên rủi ro đã nhận diện\n"
            "- coverage_score (0-100) cho độ phủ edge case\n"
            "- review_summary: Đánh giá độ mạnh mẽ tổng thể\n"
            "- critical_findings: List các vấn đề bắt buộc phải fix\n"
            "- recommendations: Gợi ý cải thiện chung\n\n"
            "Định dạng: JSON hợp lệ khớp với schema StressTestReport"
        ),
    },

    "security_audit": {
        "description": (
            "Thực hiện kiểm tra bảo mật cho kiến trúc hệ thống.\n\n"
            "Kiến trúc:\n"
            "{architecture}\n\n"
            "Luồng:\n"
            "{flows}\n\n"
            "Nhiệm vụ của bạn:\n"
            "1. Tìm kiếm CVEs và security vulnerabilities cho tất cả dependencies\n"
            "2. Phân tích sử dụng framework STRIDE:\n"
            "   **Spoofing** (Giả mạo): Kẻ tấn công có thể mạo danh user/services không?\n"
            "   **Tampering** (Giả mạo): Dữ liệu có thể bị sửa đổi khi truyền hoặc lưu trữ không?\n"
            "   **Repudiation** (Chối bỏ): User có thể chối bỏ hành động của họ không?\n"
            "   **Information Disclosure** (Tiết lộ thông tin): Dữ liệu nhạy cảm có bị暴露 không?\n"
            "   **Denial of Service** (Từ chối dịch vụ): Hệ thống có thể bị quá tải không?\n"
            "   **Elevation of Privilege** (Leo thang đặc quyền): User có thể truy cập trái phép không?\n\n"
            "3. Cho mỗi lỗ hổng tìm thấy:\n"
            "   - Tạo EdgeCase với chi tiết bảo mật\n"
            "   - Cung cấp mitigation theo best practices bảo mật\n"
            "   - Đánh giá severity dựa trên tác động tiềm năng\n\n"
            "Output phải tuân thủ Pydantic schema: StressTestReport"
        ),
        "expected_output": (
            "Một StressTestReport tập trung vào lỗ hổng bảo mật:\n"
            "- Ít nhất 5 EdgeCases liên quan đến bảo mật\n"
            "- Mỗi cái được map đến categories STRIDE\n"
            "- Mitigations theo OWASP/Security best practices\n"
            "- Critical findings cho lỗ hổng severity cao"
        ),
    },

    "review_agent_comments": {
        "description": (
            "Review thiết kế được đề xuất và cung cấp phản hồi quan trọng.\n\n"
            "Thiết kế để review:\n"
            "{design_details}\n\n"
            "Nhiệm vụ của bạn:\n"
            "1. Tìm kiếm known issues và patterns failure tương tự\n"
            "2. Cung cấp phản biện mang tính xây dựng nhận diện:\n"
            "   - Điểm yếu trong cách tiếp cận được đề xuất\n"
            "   - Các cân nhắc bị thiếu hoặc kịch bản bị bỏ qua\n"
            "   - Các cách tiếp cận thay thế có thể mạnh mẽ hơn\n"
            "   - Cải tiến cụ thể với lý do kỹ thuật\n\n"
            "Output phải tuân thủ Pydantic schema: AgentComment với agent_id=BlackHat"
        ),
        "expected_output": (
            "Một hoặc nhiều object AgentComment:\n"
            "- agent_id: 'BlackHat'\n"
            "- focus_area: Khía cạnh cụ thể đang được phê bình\n"
            "- content: Phản hồi chi tiết, cụ thể\n"
            "- suggestion: Đề xuất cải tiến cụ thể\n"
            "- priority: 1-5 (5 = critical)\n"
            "- confidence: 0.0-1.0\n"
            "- references: Related edge case IDs, component IDs\n"
            "- tags: Phân loại (security, performance, reliability, etc.)"
        ),
    },
}


def get_black_hat_task_template(template_name: str) -> dict:
    """
    Lấy template task được cấu hình trước cho QA & Security Auditor Agent.

    Args:
        template_name: Tên của template ("stress_test_happy_path",
                        "security_audit", "review_agent_comments")

    Returns:
        dict: Template với các khóa 'description' và 'expected_output'

    Raises:
        ValueError: Nếu tên template không tồn tại
    """
    template = BLACK_HAT_TASK_TEMPLATES.get(template_name)
    if not template:
        available = ", ".join(BLACK_HAT_TASK_TEMPLATES.keys())
        raise ValueError(
            f"Template không tồn tại: '{template_name}'. "
            f"Các template có sẵn: {available}"
        )
    return template.copy()


# === Edge Case Generation Helpers ===

EDGE_CASE_CATEGORIES = {
    "network": [
        "Connection timeout",
        "Network partition",
        "DNS resolution failure",
        "TLS certificate expired",
        "Latency spike beyond threshold",
        "Bandwidth congestion",
    ],
    "state": [
        "Race condition giữa các operations đồng thời",
        "Deadlock từ circular dependencies",
        "Lost update trong optimistic locking",
        "Stale data read after write",
        "Inconsistent state across microservices",
        "Orphaned records từ failed transactions",
    ],
    "data": [
        "Null/undefined value trong required field",
        "Malformed JSON/XML input",
        "Character encoding mismatch",
        "Duplicate primary key",
        "Foreign key constraint violation",
        "Data type overflow/underflow",
    ],
    "external": [
        "Third-party API service unavailable",
        "External API rate limit exceeded",
        "External API returns unexpected format",
        "Payment gateway declines transaction",
        "Email service timeout",
        "Webhook callback never received",
    ],
    "security": [
        "SQL injection trong user input",
        "XSS attack qua unsanitized data",
        "CSRF token missing hoặc invalid",
        "Authentication token expired",
        "Authorization bypass attempt",
        "Sensitive data trong logs",
    ],
    "resource": [
        "Memory exhaustion từ large payload",
        "Database connection pool exhausted",
        "File descriptor limit reached",
        "Disk space full",
        "CPU utilization 100%",
        "Thread pool queue full",
    ],
}


def get_edge_case_prompts_for_category(category: str) -> list[str]:
    """
    Lấy prompt templates để tạo edge cases trong một category cụ thể.

    Hữu ích để hướng dẫn BlackHat agent khám phá các failure domains cụ thể.

    Args:
        category: Một trong 'network', 'state', 'data', 'external', 'security', 'resource'

    Returns:
        list[str]: Prompt templates cho generating edge cases
    """
    return EDGE_CASE_CATEGORIES.get(category, [])
