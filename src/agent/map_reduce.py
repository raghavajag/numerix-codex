import os
from typing import Any

import chromadb
from dotenv import load_dotenv
from langgraph.types import Send
from typing_extensions import TypedDict

from agent.graph_state import State


load_dotenv()

COLLECTION_NAME = "manim_source_code"


class InstructionState(TypedDict):
    instruction: str


def _get_collection():
    required_vars = ("CHROMA_API_KEY", "CHROMA_DATABASE", "CHROMA_TENANT")
    missing = [name for name in required_vars if not os.getenv(name)]
    if missing:
        raise EnvironmentError(
            "Missing required Chroma environment variables: " + ", ".join(missing)
        )

    client = chromadb.CloudClient(
        api_key=os.getenv("CHROMA_API_KEY"),
        database=os.getenv("CHROMA_DATABASE"),
        tenant=os.getenv("CHROMA_TENANT"),
    )
    return client.get_collection(name=COLLECTION_NAME)


def continue_instructions(state: State) -> list[Send]:
    return [Send("get_chunks", {"instruction": instr}) for instr in state["instructions"]]


def get_chunks(state: InstructionState) -> dict[str, list[dict[str, Any]]]:
    instruction = state["instruction"]
    collection = _get_collection()
    result = collection.query(query_texts=[instruction], n_results=1)

    ids = result.get("ids", [[]])
    documents = result.get("documents", [[]])
    metadatas = result.get("metadatas", [[]])

    chunk_ids = ids[0] if ids else []
    chunk_documents = documents[0] if documents else []
    chunk_metadatas = metadatas[0] if metadatas else []

    chunks = [
        {
            "id": chunk_id,
            "text": document,
            "metadata": metadata or {},
        }
        for chunk_id, document, metadata in zip(
            chunk_ids, chunk_documents, chunk_metadatas
        )
    ]

    return {"mapped_chunks": [{"instruction": instruction, "chunks": chunks}]}
