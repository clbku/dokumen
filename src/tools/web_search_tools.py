"""
Web Search Tools for Deep-Spec AI Agents

Provides tools for searching the web to gather information:
- Web search with multiple providers
- Fetch and parse web pages
- Extract relevant information

These tools help agents research:
- Technology trends and best practices
- Documentation and tutorials
- Similar system architectures
- Security vulnerabilities and solutions
"""

import os
from typing import Optional, List
from datetime import datetime

from crewai.tools import tool


@tool("Web Search - Tìm kiếm Web")
def web_search(
    query: str,
    num_results: int = 5,
    language: str = "vi",
    region: str = "VN",
    time_range: Optional[str] = None
) -> str:
    """
    Tìm kiếm trên web và trả về kết quả với nguồn.

    Args:
        query: Câu truy vấn tìm kiếm
        num_results: Số kết quả tối đa (mặc định: 5)
        language: Ngôn ngữ kết quả (mặc định: "vi" cho tiếng Việt)
        region: Khu vực tìm kiếm (mặc định: "VN" cho Việt Nam)
        time_range: Khoảng thời gian ("d" ngày, "w" tuần, "m" tháng, "y" năm)

    Returns:
        str: Kết quả tìm kiếm với tiêu đề, link, và mô tả

    Examples:
        >>> results = web_search("microservices architecture patterns")
        >>> print(results)
    """
    # Import web search provider
    try:
        from src.tools.search_providers import get_search_provider
        provider = get_search_provider()
        return provider.search(query, num_results, language, region, time_range)
    except ImportError:
        # Fallback to mock results if no provider configured
        return _mock_web_search(query, num_results)


@tool("Search with Sources - Tìm kiếm Có Nguồn")
def search_with_sources(
    query: str,
    sources: List[str],
    num_results: int = 3
) -> str:
    """
    Tìm kiếm trên các nguồn cụ thể.

    Args:
        query: Câu truy vấn tìm kiếm
        sources: Danh sách các nguồn (ví dụ: ["github.com", "stackoverflow.com"])
        num_results: Số kết quả tối đa mỗi nguồn

    Returns:
        str: Kết quả tìm kiếm từ các nguồn cụ thể

    Examples:
        >>> results = search_with_sources(
        ...     "kubernetes deployment",
        ...     ["kubernetes.io", "github.com"]
        ... )
    """
    results = [f"# Tìm kiếm: '{query}'\n"]
    results.append(f"Nguồn: {', '.join(sources)}\n\n")

    for source in sources:
        results.append(f"## Từ {source}\n")
        # Add site: filter to query
        site_query = f"site:{source} {query}"
        try:
            from src.tools.search_providers import get_search_provider
            provider = get_search_provider()
            source_results = provider.search(site_query, num_results, "vi", "VN", None)
            results.append(source_results)
        except ImportError:
            results.append("(Không thể kết nối)\n")
        results.append("\n")

    return "".join(results)


@tool("Fetch Web Page - Lấy Nội dung Web")
def fetch_web_page(url: str, max_length: int = 5000) -> str:
    """
    Lấy nội dung của một trang web.

    Args:
        url: URL của trang web
        max_length: Độ dài tối đa của nội dung (mặc định: 5000 ký tự)

    Returns:
        str: Nội dung trang web đã được xử lý

    Examples:
        >>> content = fetch_web_page("https://example.com/docs")
        >>> print(content)
    """
    try:
        from src.tools.web_fetcher import fetch_and_parse_url
        return fetch_and_parse_url(url, max_length)
    except ImportError:
        return _mock_fetch_web_page(url, max_length)


@tool("Search Documentation - Tìm Kiếm Tài Liệu")
def search_documentation(
    technology: str,
    topic: str,
    doc_sources: Optional[List[str]] = None
) -> str:
    """
    Tìm kiếm tài liệu cho một công nghệ cụ thể.

    Args:
        technology: Tên công nghệ (ví dụ: "react", "kubernetes", "postgresql")
        topic: Chủ đề cần tìm (ví dụ: "authentication", "deployment")
        doc_sources: Nguồn tài liệu (tự động phát hiện nếu None)

    Returns:
        str: Kết quả tài liệu tìm thấy

    Examples:
        >>> docs = search_documentation("kubernetes", "helm charts")
        >>> print(docs)
    """
    # Default documentation sources
    default_sources = {
        "react": ["react.dev", "legacy.reactjs.org"],
        "vue": ["vuejs.org", "v2.vuejs.org"],
        "angular": ["angular.io"],
        "kubernetes": ["kubernetes.io", "kubernetes.io/docs"],
        "docker": ["docs.docker.com"],
        "postgresql": ["postgresql.org/docs"],
        "mysql": ["dev.mysql.com/doc"],
        "mongodb": ["mongodb.com/docs"],
        "redis": ["redis.io/docs"],
        "python": ["docs.python.org"],
        "javascript": ["developer.mozilla.org", "nodejs.org"],
        "typescript": ["typescriptlang.org/docs", "www.typescriptlang.org/docs/handbook"],
        "java": ["docs.oracle.com"],
        "go": ["go.dev/doc", "golang.org/doc"],
        "rust": ["doc.rust-lang.org"],
    }

    sources = doc_sources or default_sources.get(technology.lower(), [])

    if not sources:
        # Generic search
        query = f"{technology} {topic} documentation tutorial"
        return web_search.run(query, num_results=5)

    # Search specific documentation sites
    query = f"{topic}"
    return search_with_sources.run(query, sources, num_results=3)


@tool("Search GitHub Issues - Tìm Kiếm GitHub Issues")
def search_github_issues(
    repository: str,
    issue_type: str = "issues",
    state: str = "open",
    keywords: Optional[str] = None
) -> str:
    """
    Tìm kiếm GitHub issues/PRs cho một repository.

    Args:
        repository: Tên repository (format: "owner/repo")
        issue_type: Loại ("issues", "prs", hoặc "both")
        state: Trạng thái ("open", "closed", "all")
        keywords: Từ khóa tìm kiếm

    Returns:
        str: Kết quả GitHub issues/PRs

    Examples:
        >>> issues = search_github_issues("facebook/react", "issues", "open", "performance")
        >>> print(issues)
    """
    query = f"repo:{repository} "

    if issue_type == "prs":
        query += "is:pr "
    elif issue_type == "issues":
        query += "is:issue "
    else:
        query += "is:pr OR is:issue "

    if state == "open":
        query += "is:open "
    elif state == "closed":
        query += "is:closed "
    else:
        query += " "

    if keywords:
        query += keywords

    # Search on GitHub
    return search_with_sources.run(
        query.strip(),
        ["github.com"],
        num_results=5
    )


@tool("Search Stack Overflow - Tìm Kiếm Stack Overflow")
def search_stack_overflow(
    question: str,
    tags: Optional[List[str]] = None,
    min_score: int = 5
) -> str:
    """
    Tìm kiếm câu hỏi trên Stack Overflow.

    Args:
        question: Câu hỏi hoặc vấn đề
        tags: Danh sách tags để filter (ví dụ: ["python", "django"])
        min_score: Số điểm tối thiểu (mặc định: 5)

    Returns:
        str: Kết quả từ Stack Overflow

    Examples:
        >>> answers = search_stack_overflow("how to deploy react app", ["react", "deployment"])
        >>> print(answers)
    """
    query = question

    if tags:
        query += " " + " ".join([f"[{tag}]" for tag in tags])

    return search_with_sources.run(
        query,
        ["stackoverflow.com"],
        num_results=5
    )


@tool("Search Security Vulnerabilities - Tìm Kiếm Lỗ Hổng Bảo mật")
def search_security_vulnerabilities(
    technology: str,
    cve_id: Optional[str] = None
) -> str:
    """
    Tìm kiếm lỗ hổng bảo mật cho một công nghệ.

    Args:
        technology: Tên công nghệ hoặc package
        cve_id: CVE ID cụ thể (nếu có)

    Returns:
        str: Thông tin lỗ hổng bảo mật

    Examples:
        >>> vulns = search_security_vulnerabilities("log4j")
        >>> print(vulns)
    """
    if cve_id:
        query = f"{cve_id} vulnerability"
    else:
        query = f"{technology} security vulnerabilities CVE"

    # Search in security databases
    sources = [
        "cve.mitre.org",
        "nvd.nist.gov",
        "github.com/advisories"
    ]

    return search_with_sources.run(query, sources, num_results=5)


# Mock functions for testing/fallback

def _mock_web_search(query: str, num_results: int = 5) -> str:
    """Mock web search khi không có provider."""
    results = f"# Kết quả tìm kiếm cho: '{query}'\n\n"
    results += f"Lưu ý: Đây là kết quả giả lập. Cần cấu hình provider thực tế.\n\n"

    for i in range(min(num_results, 3)):
        results += f"## Kết quả {i+1}\n"
        results += f"- **Tiêu đề**: Kết quả mẫu cho '{query}'\n"
        results += f"- **Link**: https://example.com/search?q={query.replace(' ', '+')}\n"
        results += f"- **Mô tả**: Đây là kết quả giả lập. Cần cấu hình web search provider.\n"
        results += "\n"

    return results


def _mock_fetch_web_page(url: str, max_length: int = 5000) -> str:
    """Mock fetch web page khi không có provider."""
    return f"""
# Nội dung từ: {url}

Lưu ý: Đây là nội dung giả lập. Cần cấu hình web fetcher provider.

Để fetch nội dung web thực tế, cần:
1. Cài đặt dependencies: `pip install beautifulsoup4 requests`
2. Cấu hình user agent và headers
3. Xử lý các trang web động (JavaScript-rendered)

URL: {url}
Max Length: {max_length}
"""


class WebSearchTool:
    """
    Wrapper class cho web search tools để sử dụng với CrewAI.

    Examples:
        >>> from src.tools.web_search_tools import WebSearchTool
        >>> tool = WebSearchTool()
        >>> results = tool.run("kubernetes architecture")
    """

    def __init__(self, provider: Optional[str] = None):
        """
        Khởi tạo WebSearchTool.

        Args:
            provider: Tên provider ("google", "bing", hoặc None để auto-detect)
        """
        self.provider = provider
        self.tools = [
            web_search,
            search_with_sources,
            fetch_web_page,
            search_documentation,
            search_github_issues,
            search_stack_overflow,
            search_security_vulnerabilities,
        ]

    def run(self, query: str, **kwargs) -> str:
        """
        Chạy web search.

        Args:
            query: Câu truy vấn tìm kiếm
            **kwargs: Tham số bổ sung (num_results, language, etc.)

        Returns:
            str: Kết quả tìm kiếm
        """
        return web_search.run(query, **kwargs)
