import os
from pathlib import Path
from uuid import uuid4

import chromadb
from dotenv import load_dotenv

try:
    from .chunks import chunking
except ImportError:
    from chunks import chunking


load_dotenv()

DOCS_DIR = Path(__file__).resolve().parents[1] / "manim_docs"
COLLECTION_NAME = "manim_source_code"
BATCH_SIZE = 250

MODULE_NAMES = [
    "Camera",
    "Animation",
    "mobject_frame",
    "mobject_geometry_arc",
    "mobject_geometry_boolean_ops",
    "mobject_geometry_labelled",
    "mobject_geometry_line",
    "mobject_geometry_polygram",
    "mobject_geometry_shape_matchers",
    "mobject_geometry_tips",
    "mobject_graph",
    "mobject_graphing_coordinate_systems",
    "mobject_graphing_functions",
    "mobject_graphing_number_line",
    "mobject_graphing_probability",
    "mobject_graphing_scale",
    "mobject_matrix",
    "mobject_table",
    "mobject_text",
    "mobject_three_d_polyhedra",
    "mobject_three_d_three_d_utils",
    "mobject_three_d_three_dimensions",
    "mobject_types_image_mobject",
    "mobject_types_point_cloud_mobject",
    "mobject_types_vectorized_mobject",
    "mobject_value_tracker",
    "mobject_vector_field",
    "scenes_moving_camera_scene",
    "scenes_scene",
    "scenes_three_d_scene",
    "scenes_vector_space_scene",
    "utils_color_core",
    "utils_commands",
    "utils_bezier",
]

files_to_index = [
    (
        str(DOCS_DIR / f"{module_name}.py"),
        f"https://docs.manim.community/en/stable/reference/manim.{module_name}.html",
    )
    for module_name in MODULE_NAMES
]


def _validate_environment() -> None:
    required_vars = ("CHROMA_API_KEY", "CHROMA_TENANT", "CHROMA_DATABASE")
    missing = [name for name in required_vars if not os.getenv(name)]
    if missing:
        raise EnvironmentError(
            "Missing required Chroma environment variables: " + ", ".join(missing)
        )


def _normalize_metadata(metadata: dict) -> dict:
    normalized = dict(metadata)
    children_ids = normalized.get("children_ids")
    if isinstance(children_ids, list):
        normalized["children_ids"] = ",".join(children_ids)
    return normalized


def _iter_batches(items: list, batch_size: int):
    for start in range(0, len(items), batch_size):
        yield items[start : start + batch_size]


def populate_chroma() -> None:
    _validate_environment()

    ids: list[str] = []
    documents: list[str] = []
    metadatas: list[dict] = []

    for file_path, file_url in files_to_index:
        source_path = Path(file_path)
        if not source_path.exists():
            raise FileNotFoundError(f"Missing Manim docs source file: {source_path}")

        parent_chunks, child_chunks = chunking(str(source_path), file_url)
        for chunk in parent_chunks + child_chunks:
            ids.append(str(uuid4()))
            documents.append(chunk["content"])
            metadatas.append(_normalize_metadata(chunk["metadata"]))

    client = chromadb.CloudClient(
        tenant=os.getenv("CHROMA_TENANT"),
        database=os.getenv("CHROMA_DATABASE"),
        api_key=os.getenv("CHROMA_API_KEY"),
    )
    collection = client.get_or_create_collection(name=COLLECTION_NAME)

    batched_ids = list(_iter_batches(ids, BATCH_SIZE))
    batched_documents = list(_iter_batches(documents, BATCH_SIZE))
    batched_metadatas = list(_iter_batches(metadatas, BATCH_SIZE))

    for batch_ids, batch_documents, batch_metadatas in zip(
        batched_ids, batched_documents, batched_metadatas
    ):
        collection.add(
            ids=batch_ids,
            documents=batch_documents,
            metadatas=batch_metadatas,
        )

    print(
        f"Indexed {len(documents)} chunks from {len(files_to_index)} files into "
        f"'{COLLECTION_NAME}'."
    )


if __name__ == "__main__":
    populate_chroma()
