import json
from pathlib import Path

from src.application.ai_review.preprocessing_utils.file_handlers import DEFAULT_FILE_HANDLERS
from src.application.ai_review.preprocessing_utils.project_content import path_content
from src.application.ai_review.preprocessing_utils.project_tree import path_tree
from src.constants.preprocessing import IGNORED_DIRECTORIES


def include_without_ignored_directories(p: Path) -> bool:
    return p.name not in IGNORED_DIRECTORIES and not p.name.startswith(".")


def test__path_content__single_text_file(tmp_path):
    file = tmp_path / "main.py"
    file.write_text("print('hello')")

    result = path_content(tmp_path)

    assert "===== FILE: main.py =====" in result
    assert "print('hello')" in result
    assert "===== END FILE =====" in result


def test__path_content__multiple_files(tmp_path):
    (tmp_path / "a.py").write_text("a = 1")
    (tmp_path / "b.py").write_text("b = 2")

    result = path_content(tmp_path)

    assert "a = 1" in result
    assert "b = 2" in result
    assert result.count("===== FILE:") == 2


def test__path_content__notebook_file(tmp_path):
    nb = {
        "cells": [{"cell_type": "code", "source": "x = 1"}],
        "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.9.5"
  }
 },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    (tmp_path / "notebook.ipynb").write_text(json.dumps(nb))

    result = path_content(tmp_path)

    assert "===== FILE: notebook.ipynb =====" in result
    assert "x = 1" in result


def test__path_content__skip_binary(tmp_path):
    (tmp_path / "main.py").write_text("print('hello')")
    (tmp_path / "image.png").write_bytes(b"\x00\x01\x02")

    result = path_content(tmp_path, skip_binary=True)

    assert "main.py" in result
    assert "image.png" not in result


def test__path_content__custom_handler_replaces_default(tmp_path):
    (tmp_path / "notebook.ipynb").write_text("{}")

    custom_handlers = dict(DEFAULT_FILE_HANDLERS)
    custom_handlers[".ipynb"] = lambda p: "CUSTOM_IPYNB"
    result = path_content(tmp_path, file_handlers=custom_handlers)

    assert "CUSTOM_IPYNB" in result


def test__path_content__include_filter(tmp_path):
    (tmp_path / "main.py").write_text("a = 1")
    (tmp_path / "readme.txt").write_text("readme")

    def only_py(p: Path) -> bool:
        return p.suffix == ".py"

    result = path_content(tmp_path, include=only_py)

    assert "a = 1" in result
    assert "readme" not in result


def test__path_content__nested_dirs(tmp_path):
    (tmp_path / "dir").mkdir()
    (tmp_path / "dir" / "inner.py").write_text("inner")

    result = path_content(tmp_path)

    assert "inner" in result


def test__path_content__ignored_directories(tmp_path):
    (tmp_path / "main.py").write_text("main")
    (tmp_path / "__pycache__").mkdir()
    (tmp_path / "__pycache__" / "cache.pyc").write_text("cached")
    (tmp_path / ".venv").mkdir()
    (tmp_path / ".venv" / "script.py").write_text("venv")

    result = path_content(tmp_path, include=include_without_ignored_directories)

    assert "main" in result
    assert "cache" not in result
    assert "venv" not in result


def test__path_tree__simple_tree(tmp_path):
    (tmp_path / "a.py").write_text("a")
    (tmp_path / "b.txt").write_text("b")

    result = path_tree(tmp_path)

    assert "a.py" in result
    assert "b.txt" in result
    assert "├── a.py" in result or "└── a.py" in result


def test__path_tree__directories_first(tmp_path):
    (tmp_path / "file.txt").write_text("f")
    (tmp_path / "dir").mkdir()

    result = path_tree(tmp_path)

    lines = result.split("\n")
    dir_idx = next(i for i, l in enumerate(lines) if "dir" in l)
    file_idx = next(i for i, l in enumerate(lines) if "file.txt" in l)
    assert dir_idx < file_idx


def test__path_tree__nested_dirs(tmp_path):
    (tmp_path / "dir").mkdir()
    (tmp_path / "dir" / "subdir").mkdir()
    (tmp_path / "dir" / "subdir" / "file.py").write_text("x = 1")

    result = path_tree(tmp_path)

    assert "dir" in result
    assert "subdir" in result
    assert "file.py" in result


def test__path_tree__ignored_directories(tmp_path):
    (tmp_path / "main.py").write_text("main")
    (tmp_path / "__pycache__").mkdir()
    (tmp_path / "__pycache__" / "cache.pyc").write_text("cached")

    result = path_tree(tmp_path, include=include_without_ignored_directories)

    assert "main.py" in result
    assert "__pycache__" not in result


def test__path_tree__include_filter(tmp_path):
    (tmp_path / "main.py").write_text("a = 1")
    (tmp_path / "readme.txt").write_text("readme")

    def only_py(p: Path) -> bool:
        return p.suffix == ".py"

    result = path_tree(tmp_path, include=only_py)

    assert "main.py" in result
    assert "readme.txt" not in result
