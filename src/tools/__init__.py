"""
Deep-Spec AI Tools Package

This package provides tools for Deep-Spec AI agents to use.

Available Tools:
- File Reading Tools: Read various file formats (code, docs, configs)
- Web Search Tools: Search the web for information
- Schema Validation Tools: Validate outputs against Pydantic schemas
- Diagram Generation Tools: Generate Mermaid diagrams
"""

from src.tools.file_tools import (
    ReadFileTool,
    read_file,
    read_code_file,
    read_markdown_file,
    read_json_file,
    read_yaml_file,
)

from src.tools.web_search_tools import (
    WebSearchTool,
    web_search,
    search_with_sources,
)

__all__ = [
    # File Tools
    "ReadFileTool",
    "read_file",
    "read_code_file",
    "read_markdown_file",
    "read_json_file",
    "read_yaml_file",
    # Web Search Tools
    "WebSearchTool",
    "web_search",
    "search_with_sources",
]
