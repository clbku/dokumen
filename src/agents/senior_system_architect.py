"""
Senior System Architect Agent (White Hat) - Kiến trúc sư Tối ưu

Role: Kiến trúc sư hệ thống (White Hat)
Provider: Z.AI (glm-4.7)
Purpose: Thiết kế luồng nghiệp vụ tối ưu, súc tích và khả thi (Happy Path)

Agent này đại diện cho sự lạc quan và xây dựng trong hệ multi-agent.
Nó tập trung vào việc xây dựng các giải pháp vững chắc hoạt động trong điều kiện lý tưởng.
"""

from crewai import Agent
from src.utils.llm_provider import get_agent_llm

# Import tools
from src.tools.file_tools import (
    read_file,
    read_code_file,
    read_markdown_file,
    list_directory,
    search_in_files,
)

from src.tools.web_search_tools import (
    web_search,
    search_documentation,
    fetch_web_page,
)

from src.tools.web_fetcher import (
    fetch_github_readme,
)


def create_white_hat_agent(
    verbose: bool = True,
    memory: bool = True,
    allow_delegation: bool = False,
    enable_tools: bool = True,
) -> Agent:
    """
    Tạo và cấu hình Agent Senior System Architect (White Hat).

    Agent này chịu trách nhiệm:
    - Thiết kế Happy Path (kịch bản luồng lý tưởng)
    - Tạo đề xuất kiến trúc hệ thống
    - Định nghĩa cấu trúc dữ liệu và logic nghiệp vụ
    - Đảm bảo tính khả thi về kỹ thuật của giải pháp

    Provider khuyến nghị: Z.AI (glm-4.7)
    Lý do: Xuất sắc trong việc tạo output có cấu trúc, chi tiết kỹ thuật chính xác,
         và duy trì tính nhất quán trong thiết kế kiến trúc.

    Args:
        verbose: Bật logging chi tiết (mặc định: True)
        memory: Bật memory để lưu ngữ cảnh (mặc định: True)
        allow_delegation: Cho phép agent ủy quyền task (mặc định: False)
        enable_tools: Bật tools cho agent (mặc định: True)

    Returns:
        Agent: Instance của Senior System Architect Agent đã được cấu hình

    Examples:
        >>> from src.agents.senior_system_architect import create_white_hat_agent
        >>> architect = create_white_hat_agent()
        >>> print(architect.role)
        'Kiến trúc sư hệ thống (White Hat)'
    """
    # Get optimized LLM for WhiteHat role
    llm = get_agent_llm("white_hat")

    # Configure tools for the architect
    tools = []
    if enable_tools:
        tools = [
            # File reading tools - để đọc codebase hiện tại
            read_file,
            read_code_file,
            read_markdown_file,
            list_directory,
            search_in_files,
            # Web search tools - để research patterns và best practices
            web_search,
            search_documentation,
            fetch_web_page,
            # GitHub tools - để đọc README và examples
            fetch_github_readme,
        ]

    return Agent(
        # === Identity ===
        role="Kiến trúc sư hệ thống (White Hat)",

        # === Primary Goal ===
        goal=(
            "Thiết kế luồng nghiệp vụ tối ưu, súc tích và khả thi (Happy Path) "
            "dựa trên yêu cầu của người dùng, đảm bảo tính xuất sắc về kỹ thuật "
            "vào tránh việc kỹ thuật hóa quá mức (over-engineering)."
        ),

        # === Background & Personality ===
        backstory=(
            "Bạn là một Kiến trúc sư hệ thống cấp cao với hơn 20 năm kinh nghiệm xây dựng "
            "các hệ thống quy mô lớn. Bạn không chấp nhận sự rườm rà và 'chém gió' kỹ thuật. "
            "Triết lý của bạn dựa trên 3 nguyên tắc cốt lõi:\n\n"
            "1. **Tính Đúng Đắn Là Tiên Quyết**: Một hệ thống phải hoạt động hoàn hảo trong điều kiện lý tưởng "
            "trước khi xử lý các ngoại lệ. Happy Path là nền móng.\n\n"
            "2. **Chính Xác Hơn Phức Tạp**: Mọi quyết định thiết kế phải có lý do kỹ thuật rõ ràng. "
            "Bạn ưu tiên các pattern đã được kiểm chứng hơn là các giải pháp thử nghiệm.\n\n"
            "3. **Tư Duy Hướng Dữ Liệu**: Cấu trúc dữ liệu tốt và logic nghiệp vụ quan trọng hơn "
            "việc chọn framework hay chi tiết cài đặt.\n\n"
            "Danh tiếng của bạn:\n"
            "- Bạn từ chối các tính năng 'có thì vui' (nice-to-have) làm tăng độ phức tạp không cần thiết\n"
            "- Bạn thách thức các yêu cầu mơ hồ và đòi hỏi sự cụ thể\n"
            "- Thiết kế của bạn nổi tiếng là 'nhàm chán nhưng chống đạn'\n"
            "- Bạn tin rằng over-engineering là một dạng nợ kỹ thuật\n\n"
            "Khi thiết kế hệ thống:\n"
            "- Bắt đầu với giá trị cốt lõi và suy luận ngược lại\n"
            "- Định nghĩa rõ ràng mô hình dữ liệu với schema có kiểu (Pydantic)\n"
            "- Quy định chính xác các hợp đồng API và luồng dữ liệu\n"
            "- Chọn công nghệ dựa trên yêu cầu thực tế, không chạy theo xu hướng\n"
            "- Ghi rõ các giả định và ràng buộc\n\n"
            "Bạn là Người Xây Dựng. Bạn tạo ra nền móng để người khác kiểm tra và tinh chỉnh."
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
            "Luôn tạo ra output có cấu trúc, tuân thủ schema",
            "Định nghĩa Happy Path là một chuỗi các bước rõ ràng, có thể kiểm thử",
            "Xác định chính xác cấu trúc dữ liệu sử dụng typed schemas (kiểu Pydantic)",
            "Bao gồm điều kiện tiên quyết (pre-conditions) và hậu điều kiện (post-conditions) cho mỗi luồng",
            "Liệt kê rõ ràng tất cả các thành phần hệ thống và tương tác của chúng",
            "Tránh các phát biểu chung chung; phải cụ thể về công nghệ và pattern",
            "Khi không chắc chắn, hãy nêu rõ các giả định thay vì đoán mò",
            "Ưu tiên sự chính xác và rõ ràng hơn là sự thông minh hay tối ưu hóa sớm",
            "Mọi yếu tố thiết kế đều phải phục vụ một mục đích nghiệp vụ rõ ràng",
            "Output phải sẵn sàng để code mà không gây hiểu nhầm",
            # Tool usage guidelines
            "Sử dụng tools để đọc codebase hiện tại trước khi đề xuất kiến trúc mới",
            "Tìm kiếm documentation và examples để hiểu best practices",
            "Research patterns và frameworks trước khi chọn công nghệ",
            "Đọc README của các thư viện opensource để hiểu usage patterns",
        ],

        # === Output Quality Standards ===
        quality_criteria=[
            "Tất cả các luồng tuân thủ cấu trúc Pydantic schema trong src/schemas.py",
            "Mỗi bước có: tác nhân (actor), hành động (action), kết quả (outcome), thành phần liên quan",
            "Định nghĩa thành phần bao gồm: ID, tên, loại, công nghệ",
            "Các tương tác chỉ rõ: nguồn, đích, giao thức, đồng bộ/bất đồng bộ",
            "Happy path phải hoàn chỉnh và có thể thực thi từ đầu đến cuối",
            "Không dùng văn bản giữ chỗ (placeholder) hoặc mô tả mơ hồ",
            "Các lựa chọn kỹ thuật được biện giải bằng lý do cụ thể",
        ],
    )


# === Senior System Architect Agent Task Templates ===

WHITE_HAT_TASK_TEMPLATES = {
    "design_happy_path": {
        "description": (
            "Thiết kế Happy Path hoàn chỉnh cho tính năng: {feature_name}.\n\n"
            "Yêu cầu tính năng:\n"
            "{requirements}\n\n"
            "Nhiệm vụ của bạn:\n"
            "1. Phân tích yêu cầu và trích xuất luồng nghiệp vụ cốt lõi\n"
            "2. Đọc codebase hiện tại (nếu có) để hiểu context\n"
            "3. Định nghĩa kiến trúc hệ thống (các thành phần và tương tác)\n"
            "4. Tạo Happy Path từng bước\n"
            "5. Quy định cấu trúc dữ liệu và hợp đồng API\n"
            "6. Tài liệu hóa điều kiện tiên quyết và hậu điều kiện\n\n"
            "Output phải tuân thủ Pydantic schema: HappyPath"
        ),
        "expected_output": (
            "Một object HappyPath hoàn chỉnh bao gồm:\n"
            "- feature_id (định danh duy nhất)\n"
            "- feature_name và description\n"
            "- steps: List[FlowStep] với tất cả các trường bắt buộc\n"
            "- pre_conditions và post_conditions\n"
            "- business_value statement\n\n"
            "Định dạng: JSON hợp lệ khớp với schema HappyPath"
        ),
    },

    "design_system_architecture": {
        "description": (
            "Thiết kế kiến trúc hệ thống cho: {project_name}.\n\n"
            "Bối cảnh dự án:\n"
            "{context}\n\n"
            "Yêu cầu:\n"
            "{requirements}\n\n"
            "Nhiệm vụ của bạn:\n"
            "1. Đọc codebase hiện tại nếu có (sử dụng list_directory, read_code_file)\n"
            "2. Tìm kiếm best practices và architecture patterns (sử dụng web_search, search_documentation)\n"
            "3. Xác định tất cả các thành phần hệ thống (services, databases, queues, etc.)\n"
            "4. Định nghĩa loại thành phần và công nghệ\n"
            "5. Quy định tất cả các tương tác giữa các thành phần\n"
            "6. Đánh dấu các thành phần quan trọng để đảm bảo độ tin cậy\n\n"
            "Output phải tuân thủ Pydantic schema: SystemArchitecture"
        ),
        "expected_output": (
            "Một object SystemArchitecture hoàn chỉnh bao gồm:\n"
            "- components: List[SystemComponent] với tất cả các trường\n"
            "- interactions: List[Interaction] với protocols và sync/async\n\n"
            "Định dạng: JSON hợp lệ khớp với schema SystemArchitecture"
        ),
    },

    "create_sequence_diagram": {
        "description": (
            "Tạo sơ đồ sequence Mermaid cho luồng: {flow_name}.\n\n"
            "Bối cảnh luồng:\n"
            "{context}\n\n"
            "Nhiệm vụ của bạn:\n"
            "1. Xác định tất cả các actors và components liên quan\n"
            "2. Ánh xạ chuỗi các tương tác\n"
            "3. Sử dụng cú pháp Mermaid đúng với sequenceDiagram\n"
            "4. Bao gồm các khối alt/opt cho các luồng có điều kiện\n\n"
            "Output phải tuân thủ Pydantic schema: SystemDiagram"
        ),
        "expected_output": (
            "Một object SystemDiagram với:\n"
            "- diagram_type: 'sequence'\n"
            "- mermaid_code: Cú pháp Mermaid sequenceDiagram hợp lệ\n"
            "- title và description\n"
            "- related_components list"
        ),
    },

    "research_technology": {
        "description": (
            "Nghiên cứu công nghệ cho dự án: {technology_name}.\n\n"
            "Bối cảnh:\n"
            "{context}\n\n"
            "Yêu cầu:\n"
            "{requirements}\n\n"
            "Nhiệm vụ của bạn:\n"
            "1. Tìm kiếm documentation chính thức của {technology_name}\n"
            "2. Tìm hiểu best practices và architecture patterns\n"
            "3. Tìm các ví dụ thực tế và case studies\n"
            "4. Đánh giá ưu/nhược điểm và use cases phù hợp\n"
            "5. Đề xuất kết luận có nên sử dụng công nghệ này không"
        ),
        "expected_output": (
            "Báo cáo nghiên cứu bao gồm:\n"
            "- Giới thiệu về công nghệ\n"
            "- Các features chính\n"
            "- Architecture patterns phổ biến\n"
            "- Ưu điểm và nhược điểm\n"
            "- Use cases phù hợp\n"
            "- Kết luận và đề xuất"
        ),
    },
}


def get_white_hat_task_template(template_name: str) -> dict:
    """
    Lấy template task được cấu hình trước cho Senior System Architect Agent.

    Args:
        template_name: Tên của template ("design_happy_path",
                        "design_system_architecture", "create_sequence_diagram", "research_technology")

    Returns:
        dict: Template với các khóa 'description' và 'expected_output'

    Raises:
        ValueError: Nếu tên template không tồn tại
    """
    template = WHITE_HAT_TASK_TEMPLATES.get(template_name)
    if not template:
        available = ", ".join(WHITE_HAT_TASK_TEMPLATES.keys())
        raise ValueError(
            f"Template không tồn tại: '{template_name}'. "
            f"Các template có sẵn: {available}"
        )
    return template.copy()
