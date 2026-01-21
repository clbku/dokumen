import pytest
import os
from src.tools.file_tools import read_file, list_directory, search_in_files

def test_read_file_success(tmp_path):
    # Create a temporary file
    d = tmp_path / "subdir"
    d.mkdir()
    p = d / "hello.txt"
    p.write_text("Hello World", encoding="utf-8")
    
    content = read_file.run(str(p))
    assert "Hello World" in content
    assert "hello.txt" in content

def test_read_file_not_found():
    with pytest.raises(FileNotFoundError):
        read_file.run("/path/to/non/existent/file.txt")

def test_list_directory(tmp_path):
    d = tmp_path / "subdir"
    d.mkdir()
    (d / "file1.txt").write_text("content")
    (d / "file2.py").write_text("print('hello')")
    
    result = list_directory.run(str(d))
    assert "file1.txt" in result
    assert "file2.py" in result

def test_search_in_files(tmp_path):
    d = tmp_path / "subdir"
    d.mkdir()
    (d / "file1.txt").write_text("Hello there")
    (d / "file2.txt").write_text("General Kenobi")
    
    result = search_in_files.run(str(d), "Kenobi")
    assert "file2.txt" in result
    assert "General Kenobi" in result
    assert "file1.txt" not in result
