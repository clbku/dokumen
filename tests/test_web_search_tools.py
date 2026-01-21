import pytest
from unittest.mock import MagicMock, patch
from src.tools.web_search_tools import web_search, search_documentation, fetch_web_page

@patch('src.tools.search_providers.get_search_provider')
def test_web_search(mock_get_provider):
    mock_provider = MagicMock()
    mock_provider.search.return_value = "Mocked search result"
    mock_get_provider.return_value = mock_provider
    
    result = web_search.run("test query")
    assert "Mocked search result" in result

@patch('src.tools.search_providers.get_search_provider')
def test_search_documentation(mock_get_provider):
    mock_provider = MagicMock()
    mock_provider.search.return_value = "Docs result"
    mock_get_provider.return_value = mock_provider
    
    result = search_documentation.run("python", "langchain")
    # Verified implicitly by success
    assert "Docs result" in result

@patch('src.tools.web_fetcher.fetch_and_parse_url')
def test_fetch_web_page(mock_fetch):
    mock_fetch.return_value = "Page Content"
    
    result = fetch_web_page.run("http://example.com")
    assert "Page Content" in result
