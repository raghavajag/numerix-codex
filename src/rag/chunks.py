import ast
from pathlib import Path
from typing import Any


def get_source_segment(source_code: str, start_line: int, end_line: int) -> str:
    lines = source_code.splitlines()
    return "\n".join(lines[start_line - 1 : end_line - 1])


def create_hierarchy_chunks(
    source_code: str, file_path: str
) -> list[list[dict[str, Any]]]:
    try:
        tree = ast.parse(source_code)
    except SyntaxError as exc:
        raise ValueError(f"Failed to parse Python source for {file_path}") from exc

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
        init_method = next((method for method in methods if method.name == "__init__"), None)
        child_method_ids = [
            f"{node.name}.{method.name}"
            for method in methods
            if method.name != "__init__"
        ]

        if init_method is not None and init_method.end_lineno is not None:
            parent_content = get_source_segment(
                source_code, node.lineno, init_method.end_lineno + 1
            )
        else:
            first_body_line = node.body[0].lineno if node.body else node.lineno + 1
            parent_content = get_source_segment(source_code, node.lineno, first_body_line)

        parent_chunks.append(
            {
                "id": node.name,
                "content": parent_content,
                "metadata": {
                    "type": "Class",
                    "file_path": file_path,
                    "children_ids": child_method_ids,
                },
            }
        )

        for method in methods:
            if method.name == "__init__":
                continue
            if method.end_lineno is None:
                continue

            child_chunks.append(
                {
                    "id": f"{node.name}.{method.name}",
                    "content": get_source_segment(
                        source_code, method.lineno, method.end_lineno + 1
                    ),
                    "metadata": {
                        "type": "Method",
                        "file_path": file_path,
                        "method_name": method.name,
                        "parent_id": node.name,
                    },
                }
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
