"""
File Reading Tools for Deep-Spec AI Agents

Provides tools for reading various file formats including:
- Source code files
- Documentation files (Markdown)
- Configuration files (JSON, YAML)
- Plain text files

These tools help agents understand existing codebases, documentation,
and configuration when designing system architectures.
"""

import os
from typing import Optional, List
from pathlib import Path

from crewai.tools import tool


@tool("Read File - Đọc File")
def read_file(file_path: str, encoding: str = "utf-8") -> str:
    """
    Đọc nội dung của một file văn bản.

    Args:
        file_path: Đường dẫn đến file (có thể tuyệt đối hoặc tương đối)
        encoding: Encoding của file (mặc định: utf-8)

    Returns:
        str: Nội dung của file

    Raises:
        FileNotFoundError: Nếu file không tồn tại
        UnicodeDecodeError: Nếu encoding không đúng

    Examples:
        >>> content = read_file("/path/to/file.txt")
        >>> print(content)
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File không tồn tại: {file_path}")

    if not path.is_file():
        raise ValueError(f"Đường dẫn không phải là file: {file_path}")

    try:
        with open(path, 'r', encoding=encoding) as f:
            content = f.read()
        return f"# Nội dung của file: {file_path}\n\n{content}"
    except UnicodeDecodeError as e:
        raise UnicodeDecodeError(
            f"Không thể đọc file với encoding '{encoding}'. "
            f"Thử encoding khác như 'latin-1' hoặc 'utf-16'."
        ) from e


@tool("Read Code File - Đọc File Code")
def read_code_file(file_path: str, language: Optional[str] = None) -> str:
    """
    Đọc file code với highlight thông tin ngôn ngữ.

    Hỗ trợ các phần mở rộng:
    - Python: .py
    - JavaScript/TypeScript: .js, .ts, .jsx, .tsx
    - Java: .java
    - Go: .go
    - Rust: .rs
    - C/C++: .c, .cpp, .h, .hpp
    - HTML/CSS: .html, .css, .scss
    - SQL: .sql
    - Shell: .sh, .bash

    Args:
        file_path: Đường dẫn đến file code
        language: Ngôn ngữ lập trình (tự động phát hiện nếu None)

    Returns:
        str: Nội dung file code với thông tin ngôn ngữ

    Examples:
        >>> code = read_code_file("/path/to/app.py")
        >>> print(code)
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File code không tồn tại: {file_path}")

    # Auto-detect language from extension
    if language is None:
        extension_map = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.jsx': 'JavaScript JSX',
            '.tsx': 'TypeScript JSX',
            '.java': 'Java',
            '.go': 'Go',
            '.rs': 'Rust',
            '.c': 'C',
            '.cpp': 'C++',
            '.h': 'C/C++ Header',
            '.hpp': 'C++ Header',
            '.html': 'HTML',
            '.css': 'CSS',
            '.scss': 'SCSS',
            '.sql': 'SQL',
            '.sh': 'Shell',
            '.bash': 'Bash',
            '.yaml': 'YAML',
            '.yml': 'YAML',
            '.json': 'JSON',
            '.xml': 'XML',
            '.md': 'Markdown',
        }
        language = extension_map.get(path.suffix, 'Unknown')

    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        return f"""# File Code: {file_path}
Ngôn ngữ: {language}
Kích thước: {len(content)} ký tự

```{language.lower()}
{content}
```"""
    except UnicodeDecodeError:
        # Try with latin-1 as fallback
        with open(path, 'r', encoding='latin-1') as f:
            content = f.read()
        return f"""# File Code: {file_path}
Ngôn ngữ: {language} (đã dùng encoding latin-1)

```{language.lower()}
{content}
```"""


@tool("Read Markdown File - Đọc File Markdown")
def read_markdown_file(file_path: str) -> str:
    """
    Đọc file Markdown và trả về nội dung với metadata.

    Args:
        file_path: Đường dẫn đến file Markdown (.md)

    Returns:
        str: Nội dung Markdown với thông tin metadata

    Examples:
        >>> doc = read_markdown_file("/path/to/README.md")
        >>> print(doc)
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File Markdown không tồn tại: {file_path}")

    if path.suffix not in ['.md', '.markdown']:
        raise ValueError(f"File không phải là Markdown: {file_path}")

    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract title if exists (first # heading)
    title = "Không có tiêu đề"
    for line in content.split('\n'):
        line = line.strip()
        if line.startswith('# '):
            title = line[2:].strip()
            break
        elif line.startswith('## '):
            title = line[3:].strip()
            break

    lines_count = len(content.split('\n'))
    words_count = len(content.split())

    return f"""# Markdown File: {file_path}

Tiêu đề: {title}
Số dòng: {lines_count}
Số từ: {words_count}

---
{content}
---"""


@tool("Read JSON File - Đọc File JSON")
def read_json_file(file_path: str, pretty: bool = True) -> str:
    """
    Đọc file JSON và trả về nội dung đã format.

    Args:
        file_path: Đường dẫn đến file JSON
        pretty: Có format đẹp không (mặc định: True)

    Returns:
        str: Nội dung JSON đã format

    Examples:
        >>> data = read_json_file("/path/to/config.json")
        >>> print(data)
    """
    import json

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File JSON không tồn tại: {file_path}")

    if path.suffix != '.json':
        raise ValueError(f"File không phải là JSON: {file_path}")

    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    formatted = json.dumps(data, indent=2 if pretty else None, ensure_ascii=False)

    return f"""# JSON File: {file_path}

```json
{formatted}
```"""


@tool("Read YAML File - Đọc File YAML")
def read_yaml_file(file_path: str) -> str:
    """
    Đọc file YAML và trả về nội dung.

    Args:
        file_path: Đường dẫn đến file YAML (.yaml, .yml)

    Returns:
        str: Nội dung YAML

    Examples:
        >>> config = read_yaml_file("/path/to/config.yaml")
        >>> print(config)
    """
    try:
        import yaml
    except ImportError:
        return "Lỗi: Cần cài đặt PyYAML. Chạy: pip install pyyaml"

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File YAML không tồn tại: {file_path}")

    if path.suffix not in ['.yaml', '.yml']:
        raise ValueError(f"File không phải là YAML: {file_path}")

    with open(path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    # Convert to formatted string
    import json
    formatted = json.dumps(data, indent=2, ensure_ascii=False)

    return f"""# YAML File: {file_path}

```yaml
{yaml.dump(data, allow_unicode=True, default_flow_style=False)}
```"""


@tool("List Directory - Liệt kê Thư mục")
def list_directory(directory_path: str, pattern: Optional[str] = None, recursive: bool = False) -> str:
    """
    Liệt kê các file trong một thư mục.

    Args:
        directory_path: Đường dẫn đến thư mục
        pattern: Filter theo pattern (ví dụ: "*.py", "*.md")
        recursive: Liệt kê cả thư mục con (mặc định: False)

    Returns:
        str: Danh sách các file tìm thấy

    Examples:
        >>> files = list_directory("/path/to/project", pattern="*.py", recursive=True)
        >>> print(files)
    """
    path = Path(directory_path)

    if not path.exists():
        raise FileNotFoundError(f"Thư mục không tồn tại: {directory_path}")

    if not path.is_dir():
        raise ValueError(f"Đường dẫn không phải là thư mục: {directory_path}")

    if recursive:
        files = list(path.rglob(pattern if pattern else "*"))
    else:
        files = list(path.glob(pattern if pattern else "*"))

    # Filter only files, not directories
    files = [f for f in files if f.is_file()]

    if not files:
        return f"# Thư mục: {directory_path}\n\nKhông tìm thấy file nào."

    result = f"# Thư mục: {directory_path}"
    if pattern:
        result += f" (Pattern: {pattern})"
    result += f"\n\nTìm thấy {len(files)} file:\n\n"

    # Group by extension
    by_extension = {}
    for file in sorted(files):
        ext = file.suffix or 'no_extension'
        if ext not in by_extension:
            by_extension[ext] = []
        by_extension[ext].append(str(file))

    for ext, file_list in sorted(by_extension.items()):
        result += f"## {ext or 'Không có phần mở rộng'} ({len(file_list)} files)\n\n"
        for file_path in file_list:
            rel_path = os.path.relpath(file_path, directory_path)
            result += f"- `{rel_path}`\n"
        result += "\n"

    return result


@tool("Search in Files - Tìm trong Files")
def search_in_files(
    directory_path: str,
    search_term: str,
    pattern: Optional[str] = None,
    case_sensitive: bool = False
) -> str:
    """
    Tìm kiếm một chuỗi trong các file.

    Args:
        directory_path: Đường dẫn đến thư mục
        search_term: Chuỗi cần tìm
        pattern: Filter theo pattern (ví dụ: "*.py")
        case_sensitive: Phân biệt hoa thường (mặc định: False)

    Returns:
        str: Kết quả tìm kiếm

    Examples:
        >>> results = search_in_files("/path/to/project", "import", pattern="*.py")
        >>> print(results)
    """
    path = Path(directory_path)

    if not path.exists():
        raise FileNotFoundError(f"Thư mục không tồn tại: {directory_path}")

    search_term_cmp = search_term if case_sensitive else search_term.lower()

    results = []
    files_searched = 0

    for file_path in path.rglob(pattern if pattern else "*"):
        if not file_path.is_file():
            continue

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            content_cmp = content if case_sensitive else content.lower()

            if search_term_cmp in content_cmp:
                files_searched += 1
                lines = content.split('\n')
                matches = []

                for i, line in enumerate(lines, 1):
                    line_cmp = line if case_sensitive else line.lower()
                    if search_term_cmp in line_cmp:
                        # Truncate line if too long
                        display_line = line.strip()
                        if len(display_line) > 100:
                            display_line = display_line[:97] + "..."
                        matches.append(f"  Line {i}: {display_line}")

                if matches:
                    rel_path = os.path.relpath(file_path, directory_path)
                    results.append(f"## File: {rel_path}\n")
                    results.append(f"Tìm thấy {len(matches)} kết quả:\n")
                    results.extend(matches[:10])  # Max 10 matches per file
                    if len(matches) > 10:
                        results.append(f"  ... và {len(matches) - 10} kết quả khác")
                    results.append("\n")

        except Exception as e:
            continue

    if not results:
        return f"# Tìm kiếm: '{search_term}' trong {directory_path}\n\nKhông tìm thấy kết quả."

    output = f"# Tìm kiếm: '{search_term}' trong {directory_path}"
    if pattern:
        output += f" (Pattern: {pattern})"
    output += f"\n\nTìm thấy trong {files_searched} file:\n\n"
    output += "".join(results)

    return output


# CrewAI Tool class for backward compatibility
class ReadFileTool:
    """
    Wrapper class cho file reading tools để sử dụng với CrewAI.

    Examples:
        >>> from src.tools.file_tools import ReadFileTool
        >>> tool = ReadFileTool()
        >>> result = tool.run("/path/to/file.txt")
    """

    def __init__(self):
        self.tools = [
            read_file,
            read_code_file,
            read_markdown_file,
            read_json_file,
            read_yaml_file,
            list_directory,
            search_in_files,
        ]

    def run(self, file_path: str, file_type: str = "auto") -> str:
        """
        Chạy tool phù hợp dựa trên loại file.

        Args:
            file_path: Đường dẫn đến file
            file_type: Loại file ("auto", "code", "markdown", "json", "yaml")

        Returns:
            str: Nội dung file
        """
        if file_type == "auto":
            suffix = Path(file_path).suffix
            if suffix == '.md':
                file_type = "markdown"
            elif suffix == '.json':
                file_type = "json"
            elif suffix in ['.yaml', '.yml']:
                file_type = "yaml"
            elif suffix in ['.py', '.js', '.ts', '.java', '.go', '.rs', '.c', '.cpp']:
                file_type = "code"

        if file_type == "markdown":
            return read_markdown_file.run(file_path)
        elif file_type == "json":
            return read_json_file.run(file_path)
        elif file_type == "yaml":
            return read_yaml_file.run(file_path)
        elif file_type == "code":
            return read_code_file.run(file_path)
        else:
            return read_file.run(file_path)
