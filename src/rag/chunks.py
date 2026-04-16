from __future__ import annotations

import ast
import re
from pathlib import Path
from typing import Any


def get_source_segment(source_code: str, start_line: int, end_line: int) -> str:
    lines = source_code.splitlines()
    return "\n".join(lines[start_line - 1 : end_line - 1]).strip()


def _first_sentence(text: str) -> str:
    cleaned = " ".join((text or "").strip().split())
    if not cleaned:
        return ""
    match = re.split(r"(?<=[.!?])\s+", cleaned, maxsplit=1)
    return match[0][:300]


def _extract_keywords(*values: str) -> list[str]:
    terms: set[str] = set()
    for value in values:
        for token in re.findall(r"[A-Za-z_][A-Za-z0-9_]{2,}", value or ""):
            lowered = token.lower()
            if lowered in {"self", "true", "false", "none", "return", "class", "def"}:
                continue
            terms.add(token)
    return sorted(terms)[:40]


def _build_aliases(symbol: str, module_name: str) -> list[str]:
    aliases = {
        symbol,
        symbol.lower(),
        module_name,
        module_name.replace("_", "."),
        symbol.replace("_", ""),
    }
    return sorted(alias for alias in aliases if alias)


def _module_name_from_path(file_path: str) -> str:
    return Path(file_path).stem


def _class_chunk(
    source_code: str,
    file_path: str,
    module_name: str,
    node: ast.ClassDef,
    methods: list[ast.FunctionDef | ast.AsyncFunctionDef],
) -> dict[str, Any]:
    init_method = next((method for method in methods if method.name == "__init__"), None)
    child_symbols = [f"{node.name}.{method.name}" for method in methods if method.name != "__init__"]
    class_docstring = ast.get_docstring(node) or ""

    if init_method is not None and init_method.end_lineno is not None:
        end_line = init_method.end_lineno + 1
    else:
        end_line = node.body[0].lineno if node.body else (node.end_lineno or node.lineno + 1)

    content = get_source_segment(source_code, node.lineno, end_line)
    summary = _first_sentence(class_docstring)
    keywords = _extract_keywords(node.name, class_docstring, content)

    return {
        "id": node.name,
        "content": content,
        "metadata": {
            "source_type": "api",
            "chunk_kind": "class",
            "symbol": node.name,
            "module": module_name,
            "file_path": file_path,
            "parent_symbol": None,
            "children_symbols": child_symbols,
            "imports_hint": [module_name],
            "keywords": keywords,
            "aliases": _build_aliases(node.name, module_name),
            "doc_summary": summary,
        },
    }


def _method_chunk(
    source_code: str,
    file_path: str,
    module_name: str,
    class_name: str,
    class_summary: str,
    method: ast.FunctionDef | ast.AsyncFunctionDef,
) -> dict[str, Any]:
    method_docstring = ast.get_docstring(method) or ""
    method_content = get_source_segment(source_code, method.lineno, (method.end_lineno or method.lineno) + 1)
    method_symbol = f"{class_name}.{method.name}"
    header = f"# Parent class: {class_name}\n# Parent summary: {class_summary}\n"
    content = f"{header}{method_content}".strip()
    summary = _first_sentence(method_docstring) or _first_sentence(method_content)
    keywords = _extract_keywords(class_name, method.name, method_docstring, method_content)

    return {
        "id": method_symbol,
        "content": content,
        "metadata": {
            "source_type": "api",
            "chunk_kind": "method",
            "symbol": method_symbol,
            "module": module_name,
            "file_path": file_path,
            "parent_symbol": class_name,
            "children_symbols": [],
            "imports_hint": [module_name, class_name],
            "keywords": keywords,
            "aliases": _build_aliases(method_symbol, module_name),
            "doc_summary": summary,
            "method_name": method.name,
        },
    }


def create_hierarchy_chunks(source_code: str, file_path: str) -> list[list[dict[str, Any]]]:
    try:
        tree = ast.parse(source_code)
    except SyntaxError as exc:
        raise ValueError(f"Failed to parse Python source for {file_path}") from exc

    module_name = _module_name_from_path(file_path)
    parent_chunks: list[dict[str, Any]] = []
    child_chunks: list[dict[str, Any]] = []

    for node in tree.body:
        if not isinstance(node, ast.ClassDef):
            continue

        methods = [
            child
            for child in node.body
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]
        class_chunk = _class_chunk(source_code, file_path, module_name, node, methods)
        parent_chunks.append(class_chunk)

        class_summary = class_chunk["metadata"].get("doc_summary", "")
        for method in methods:
            if method.name == "__init__":
                continue
            child_chunks.append(
                _method_chunk(
                    source_code,
                    file_path,
                    module_name,
                    node.name,
                    class_summary,
                    method,
                )
            )

    return [parent_chunks, child_chunks]


def chunking(file_path: str, file_url: str) -> list[list[dict[str, Any]]]:
    source_path = Path(file_path)
    source_code = source_path.read_text(encoding="utf-8")
    parent_chunks, child_chunks = create_hierarchy_chunks(source_code, str(source_path))

    for chunk_group in (parent_chunks, child_chunks):
        for chunk in chunk_group:
            chunk["metadata"]["source_url"] = file_url

    return [parent_chunks, child_chunks]
