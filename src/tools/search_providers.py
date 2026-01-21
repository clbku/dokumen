"""
Web Search Providers for Deep-Spec AI

Supports multiple search providers:
- MCP Web Search Prime
- Google Custom Search API
- Bing Search API
- DuckDuckGo (free, no API key required)
"""

import os
from typing import Optional, List
from abc import ABC, abstractmethod


class SearchProvider(ABC):
    """Base class for search providers."""

    @abstractmethod
    def search(
        self,
        query: str,
        num_results: int = 5,
        language: str = "vi",
        region: str = "VN",
        time_range: Optional[str] = None
    ) -> str:
        """
        Execute search query.

        Args:
            query: Search query
            num_results: Maximum number of results
            language: Result language
            region: Search region
            time_range: Time filter ("d", "w", "m", "y")

        Returns:
            str: Formatted search results
        """
        pass


class WebSearchPrimeProvider(SearchProvider):
    """Sử dụng MCP Web Search Prime provider."""

    def __init__(self):
        try:
            from mcp_web_search_prime import webSearchPrime
            self.client = webSearchPrime
            self.available = True
        except ImportError:
            self.available = False

    def search(
        self,
        query: str,
        num_results: int = 5,
        language: str = "vi",
        region: str = "VN",
        time_range: Optional[str] = None
    ) -> str:
        if not self.available:
            raise ImportError("MCP Web Search Prime not available. Install: pip install mcp-web-search-prime")

        # Map time_range
        recency_map = {
            "d": "oneDay",
            "w": "oneWeek",
            "m": "oneMonth",
            "y": "oneYear",
        }

        recency = recency_map.get(time_range, "noLimit") if time_range else "noLimit"

        try:
            results = self.client.invoke_web_search(
                search_query=query,
                search_recency_filter=recency,
                location=region.lower(),
                content_size="high",
            )

            return self._format_results(results, num_results)
        except Exception as e:
            return f"Lỗi tìm kiếm: {str(e)}"

    def _format_results(self, results: dict, max_results: int) -> str:
        """Format search results."""
        output = f"# Kết quả tìm kiếm\n\n"

        if isinstance(results, dict):
            items = results.get('data', []) if 'data' in results else []
        else:
            items = []

        if not items:
            return output + "Không tìm thấy kết quả."

        for i, item in enumerate(items[:max_results], 1):
            output += f"## Kết quả {i}\n\n"

            if isinstance(item, dict):
                title = item.get('title', 'Không có tiêu đề')
                url = item.get('url', '')
                snippet = item.get('snippet', item.get('summary', ''))
                source = item.get('website_name', item.get('source', ''))
                icon = item.get('website_icon', '')

                output += f"**Tiêu đề**: {title}\n\n"
                output += f"**Nguồn**: {source}\n\n"
                output += f"**Link**: {url}\n\n"
                if snippet:
                    output += f"**Mô tả**: {snippet}\n\n"
            else:
                output += f"{item}\n\n"

            output += "---\n\n"

        return output


class DuckDuckGoProvider(SearchProvider):
    """
    DuckDuckGo search provider (free, không cần API key).
    Sử dụng duckduckgo_search library.
    """

    def __init__(self):
        try:
            from duckduckgo_search import DDGS
            self.client = DDGS()
            self.available = True
        except ImportError:
            self.available = False

    def search(
        self,
        query: str,
        num_results: int = 5,
        language: str = "vi",
        region: str = "VN",
        time_range: Optional[str] = None
    ) -> str:
        if not self.available:
            raise ImportError("DuckDuckGo search not available. Install: pip install duckduckgo-search")

        # Map time_range
        time_map = {
            "d": "d",
            "w": "w",
            "m": "m",
            "y": "y",
        }

        try:
            results = self.client.text(
                query,
                max_results=num_results,
                region=region.lower(),
            )

            return self._format_results(results)
        except Exception as e:
            return f"Lỗi tìm kiếm DuckDuckGo: {str(e)}"

    def _format_results(self, results: List[dict]) -> str:
        """Format DuckDuckGo search results."""
        output = f"# Kết quả tìm kiếm DuckDuckGo\n\n"

        if not results:
            return output + "Không tìm thấy kết quả."

        for i, item in enumerate(results, 1):
            output += f"## Kết quả {i}\n\n"
            output += f"**Tiêu đề**: {item.get('title', 'Không có tiêu đề')}\n\n"
            output += f"**Link**: {item.get('link', '')}\n\n"
            output += f"**Mô tả**: {item.get('body', '')}\n\n"
            output += "---\n\n"

        return output


class GoogleCustomSearchProvider(SearchProvider):
    """
    Google Custom Search API provider.
    Cần API key và Custom Search Engine ID.
    """

    def __init__(self, api_key: Optional[str] = None, cse_id: Optional[str] = None):
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        self.cse_id = cse_id or os.getenv("GOOGLE_CSE_ID")
        self.available = bool(self.api_key and self.cse_id)

    def search(
        self,
        query: str,
        num_results: int = 5,
        language: str = "vi",
        region: str = "VN",
        time_range: Optional[str] = None
    ) -> str:
        if not self.available:
            raise ValueError("Google CSE requires GOOGLE_API_KEY and GOOGLE_CSE_ID environment variables")

        try:
            import requests

            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                "key": self.api_key,
                "cx": self.cse_id,
                "q": query,
                "num": min(num_results, 10),  # Google max is 10 per request
                "lr": language,
                "gl": region,
            }

            if time_range:
                time_map = {"d": "d1", "w": "w1", "m": "m1", "y": "y1"}
                params["dateRestrict"] = time_map.get(time_range, "")

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            return self._format_results(data)

        except Exception as e:
            return f"Lỗi tìm kiếm Google: {str(e)}"

    def _format_results(self, data: dict) -> str:
        """Format Google CSE results."""
        output = f"# Kết quả tìm kiếm Google\n\n"

        items = data.get("items", [])

        if not items:
            return output + "Không tìm thấy kết quả."

        for i, item in enumerate(items, 1):
            output += f"## Kết quả {i}\n\n"
            output += f"**Tiêu đề**: {item.get('title', 'Không có tiêu đề')}\n\n"
            output += f"**Link**: {item.get('link', '')}\n\n"
            output += f"**Mô tả**: {item.get('snippet', '')}\n\n"
            output += "---\n\n"

        return output


def get_search_provider(provider_name: Optional[str] = None) -> SearchProvider:
    """
    Lấy search provider. Tự động phát hiện nếu không chỉ định.

    Args:
        provider_name: Tên provider ("web_search_prime", "duckduckgo", "google")

    Returns:
        SearchProvider: Instance của search provider

    Raises:
        ValueError: Nếu không có provider nào available
    """
    # Try specified provider first
    if provider_name:
        providers = {
            "web_search_prime": WebSearchPrimeProvider,
            "duckduckgo": DuckDuckGoProvider,
            "google": GoogleCustomSearchProvider,
        }

        provider_class = providers.get(provider_name.lower())
        if provider_class:
            instance = provider_class()
            if instance.available:
                return instance
            else:
                raise ValueError(f"Provider '{provider_name}' không available. Kiểm tra dependencies/API keys.")

    # Auto-detect: try in order of preference
    providers_to_try = [
        WebSearchPrimeProvider,
        DuckDuckGoProvider,
        GoogleCustomSearchProvider,
    ]

    for provider_class in providers_to_try:
        try:
            instance = provider_class()
            if instance.available:
                print(f"Đang sử dụng search provider: {provider_class.__name__}")
                return instance
        except Exception:
            continue

    # If all fail, raise error
    raise ValueError(
        "Không có search provider nào available. "
        "Cài đặt ít nhất một trong các options sau:\n"
        "1. pip install mcp-web-search-prime (khuyên dùng)\n"
        "2. pip install duckduckgo-search (miễn phí)\n"
        "3. Cấu hình Google API key và CSE ID"
    )
