"""
Web Fetcher for Deep-Spec AI

Fetches and parses web pages to extract readable content.
Supports static pages and basic JavaScript-rendered content.
"""

import re
from typing import Optional
from urllib.parse import urlparse, urljoin

from crewai.tools import tool


def fetch_and_parse_url(url: str, max_length: int = 5000) -> str:
    """
    Lấy và parse nội dung từ URL.

    Args:
        url: URL cần fetch
        max_length: Độ dài tối đa của nội dung

    Returns:
        str: Nội dung đã được xử lý

    Examples:
        >>> content = fetch_and_parse_url("https://example.com/docs")
        >>> print(content)
    """
    try:
        import requests
        from bs4 import BeautifulSoup
    except ImportError as e:
        return _error_message(str(e))

    try:
        # Fetch the page
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')

        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()

        # Get title
        title = soup.title.string if soup.title else url

        # Extract main content
        # Try to find main content areas
        main_content = (
            soup.find('main') or
            soup.find('article') or
            soup.find('div', class_=re.compile(r'content|main|article|post', re.I)) or
            soup.body
        )

        if main_content:
            # Get text content
            text = main_content.get_text(separator='\n', strip=True)
        else:
            text = soup.get_text(separator='\n', strip=True)

        # Clean up text
        lines = text.split('\n')
        cleaned_lines = []

        for line in lines:
            line = line.strip()
            # Skip empty lines and very short lines
            if len(line) >= 10 or line == '':
                cleaned_lines.append(line)

        cleaned_text = '\n'.join(cleaned_lines)

        # Truncate if too long
        if len(cleaned_text) > max_length:
            cleaned_text = cleaned_text[:max_length]
            cleaned_text += "\n\n... (nội dung bị cắt bở)"

        # Format output
        result = f"# {title}\n\n"
        result += f"**URL**: {url}\n\n"
        result += f"**Độ dài**: {len(cleaned_text)} ký tự\n\n"
        result += "---\n\n"
        result += cleaned_text

        return result

    except requests.Timeout:
        return f"# Lỗi Timeout\n\nKhông thể tải {url} trong thời gian cho phép."
    except requests.RequestException as e:
        return f"# Lỗi Request\n\nKhông thể tải {url}: {str(e)}"
    except Exception as e:
        return f"# Lỗi\n\nKhông thể parse {url}: {str(e)}"


@tool("Fetch GitHub README - Lấy GitHub README")
def fetch_github_readme(repo_url: str) -> str:
    """
    Lấy README từ GitHub repository.

    Args:
        repo_url: URL của GitHub repository

    Returns:
        str: Nội dung README

    Examples:
        >>> readme = fetch_github_readme.run("https://github.com/facebook/react")
        >>> print(readme)
    """
    try:
        import requests
    except ImportError:
        return _error_message("Cần cài đặt requests")

    # Parse repo URL
    parsed = urlparse(repo_url)
    path_parts = parsed.path.strip('/').split('/')

    if len(path_parts) < 2:
        return f"# Lỗi\n\nURL GitHub không hợp lệ: {repo_url}"

    owner, repo = path_parts[0], path_parts[1]

    # Try different README filenames
    readme_names = ['README.md', 'README.MD', 'readme.md', 'Readme.md']

    for readme_name in readme_names:
        raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/main/{readme_name}"

        try:
            response = requests.get(raw_url, timeout=10)
            if response.status_code == 200:
                content = response.text
                return f"# README: {owner}/{repo}\n\n" + content
        except Exception:
            continue

    # Try master branch if main failed
    for readme_name in readme_names:
        raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/master/{readme_name}"

        try:
            response = requests.get(raw_url, timeout=10)
            if response.status_code == 200:
                content = response.text
                return f"# README: {owner}/{repo}\n\n" + content
        except Exception:
            continue

    return f"# Không tìm thấy README\n\nKhông tìm thấy README trong repository: {repo_url}"


def _error_message(missing_dependency: str) -> str:
    """Helper để tạo error message khi thiếu dependency."""
    return f"""# Lỗi: Thiếu Dependency

Không thể thực hiện thao tác. Cần cài đặt:

```
pip install requests beautifulsoup4
```

Lỗi chi tiết: {missing_dependency}
"""


class WebFetcher:
    """
    Wrapper class cho web fetching tools.

    Examples:
        >>> from src.tools.web_fetcher import WebFetcher
        >>> fetcher = WebFetcher()
        >>> content = fetcher.fetch("https://example.com")
    """

    def __init__(self):
        try:
            import requests
            from bs4 import BeautifulSoup
            self.available = True
        except ImportError:
            self.available = False

    def fetch(self, url: str, max_length: int = 5000) -> str:
        """
        Fetch nội dung từ URL.

        Args:
            url: URL cần fetch
            max_length: Độ dài tối đa

        Returns:
            str: Nội dung đã được xử lý
        """
        return fetch_and_parse_url(url, max_length)

    def fetch_readme(self, repo_url: str) -> str:
        """
        Fetch README từ GitHub repository.

        Args:
            repo_url: URL của GitHub repository

        Returns:
            str: Nội dung README
        """
        return fetch_github_readme(repo_url)
