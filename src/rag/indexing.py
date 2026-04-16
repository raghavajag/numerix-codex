from __future__ import annotations

import json
import os
from pathlib import Path

from dotenv import load_dotenv

from rag.chunks import chunking
from rag.example_chunks import extract_example_chunks
from rag.synthetic_chunks import build_synthetic_symbol_chunks

try:
    import chromadb
except ImportError as exc:  # pragma: no cover - runtime utility script
    raise RuntimeError("chromadb must be installed to run indexing") from exc


load_dotenv()

DOCS_DIR = Path(__file__).resolve().parents[1] / "manim_docs"
API_COLLECTION_NAME = "manim_source_code"
EXAMPLE_COLLECTION_NAME = "manim_example_chunks"
BATCH_SIZE = 250


def _doc_url(module_name: str) -> str:
    return f"https://docs.manim.community/en/stable/reference/manim.{module_name}.html"


def _iter_batches(items: list, batch_size: int):
    for start in range(0, len(items), batch_size):
        yield items[start : start + batch_size]


def _validate_environment() -> None:
    required = ("CHROMA_API_KEY", "CHROMA_TENANT", "CHROMA_DATABASE")
    missing = [name for name in required if not os.getenv(name)]
    if missing:
        raise EnvironmentError(
            "Missing required Chroma environment variables: " + ", ".join(missing)
        )


def _normalize_metadata(metadata: dict) -> dict:
    normalized = dict(metadata)
    for key in (
        "children_symbols",
        "imports_hint",
        "keywords",
        "aliases",
        "domain_tags",
        "visual_patterns",
        "symbols_used",
        "layout_patterns",
        "animation_patterns",
        "teaching_patterns",
    ):
        value = normalized.get(key)
        if isinstance(value, list):
            normalized[key] = json.dumps(value, ensure_ascii=False)
    return normalized


def _api_chunks() -> list[dict]:
    chunks: list[dict] = []
    for source_path in sorted(DOCS_DIR.glob("*.py")):
        parent_chunks, child_chunks = chunking(str(source_path), _doc_url(source_path.stem))
        chunks.extend(parent_chunks)
        chunks.extend(child_chunks)
    chunks.extend(build_synthetic_symbol_chunks(DOCS_DIR))
    return chunks


def _example_chunks() -> list[dict]:
    chunks: list[dict] = []
    for source_path in sorted(DOCS_DIR.glob("*.py")):
        chunks.extend(extract_example_chunks(str(source_path)))
    return chunks


def _collection_id(chunk: dict) -> str:
    prefix = chunk["metadata"].get("source_type", "chunk")
    return f"{prefix}:{chunk['id']}"


def _upload_collection(collection, chunks: list[dict]) -> None:
    ids = [_collection_id(chunk) for chunk in chunks]
    documents = [chunk["content"] for chunk in chunks]
    metadatas = [_normalize_metadata(chunk["metadata"]) for chunk in chunks]

    for batch_ids, batch_docs, batch_meta in zip(
        _iter_batches(ids, BATCH_SIZE),
        _iter_batches(documents, BATCH_SIZE),
        _iter_batches(metadatas, BATCH_SIZE),
    ):
        collection.upsert(ids=batch_ids, documents=batch_docs, metadatas=batch_meta)


def populate_chroma() -> None:
    _validate_environment()
    client = chromadb.CloudClient(
        tenant=os.getenv("CHROMA_TENANT"),
        database=os.getenv("CHROMA_DATABASE"),
        api_key=os.getenv("CHROMA_API_KEY"),
    )

    api_collection = client.get_or_create_collection(name=API_COLLECTION_NAME)
    example_collection = client.get_or_create_collection(name=EXAMPLE_COLLECTION_NAME)

    api_chunks = _api_chunks()
    example_chunks = _example_chunks()

    _upload_collection(api_collection, api_chunks)
    _upload_collection(example_collection, example_chunks)

    print(
        f"Indexed {len(api_chunks)} API chunks into '{API_COLLECTION_NAME}' and "
        f"{len(example_chunks)} example chunks into '{EXAMPLE_COLLECTION_NAME}'."
    )


if __name__ == "__main__":  # pragma: no cover - utility script
    populate_chroma()
