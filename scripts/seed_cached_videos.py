from __future__ import annotations

import hashlib
import os
import sys
from pathlib import Path

import chromadb
from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

load_dotenv(ROOT_DIR / ".env")

CACHE_COLLECTION_NAME = "manim_cached_video_url"

SEED_CACHED_VIDEOS = [
    {
        "prompt": "Draw the equation of SHM",
        "video_url": "https://pub-b215a097b7b243dc86da838a88d50339.r2.dev/media/videos/SimpleHarmonicMotionGraph/480p15/SimpleHarmonicMotionGraph.mp4",
    },
    {
        "prompt": "Plot a 3D Spiral Curve expanding along the Z-Axis",
        "video_url": "https://pub-b215a097b7b243dc86da838a88d50339.r2.dev/media/videos/Spiral3DScene/480p15/Spiral3DScene.mp4",
    },
    {
        "prompt": "Explain Binary Search in an Array",
        "video_url": "https://pub-b215a097b7b243dc86da838a88d50339.r2.dev/media/videos/BinarySearchTutorial/480p15/BinarySearchTutorial.mp4",
    },
    {
        "prompt": "Draw y = x^3 Plot",
        "video_url": "https://pub-b215a097b7b243dc86da838a88d50339.r2.dev/media/videos/CubicFunctionPlot/480p15/CubicFunctionPlot.mp4",
    },
    {
        "prompt": "Visualize Electron Orbits in a Hydrogen Atom",
        "video_url": "https://pub-b215a097b7b243dc86da838a88d50339.r2.dev/media/videos/HydrogenAtomOrbits/480p15/HydrogenAtomOrbits.mp4",
    },
    {
        "prompt": "Draw y = sin(x) from -π to π",
        "video_url": "https://pub-b215a097b7b243dc86da838a88d50339.r2.dev/media/videos/SineCurveWithKeyPoints/480p15/SineCurveWithKeyPoints.mp4",
    },
]


def _seed_id(prompt: str) -> str:
    normalized = prompt.strip().lower().encode("utf-8")
    digest = hashlib.sha256(normalized).hexdigest()
    return f"cached-video-{digest}"


def _get_collection():
    required_vars = ("CHROMA_API_KEY", "CHROMA_DATABASE", "CHROMA_TENANT")
    missing = [name for name in required_vars if not os.getenv(name)]
    if missing:
        raise RuntimeError(
            "Missing required Chroma environment variables: " + ", ".join(missing)
        )

    client = chromadb.CloudClient(
        api_key=os.getenv("CHROMA_API_KEY"),
        database=os.getenv("CHROMA_DATABASE"),
        tenant=os.getenv("CHROMA_TENANT"),
    )
    return client.get_or_create_collection(name=CACHE_COLLECTION_NAME)


def seed_cached_videos() -> None:
    collection = _get_collection()
    ids = [_seed_id(item["prompt"]) for item in SEED_CACHED_VIDEOS]
    documents = [item["prompt"] for item in SEED_CACHED_VIDEOS]
    metadatas = [
        {
            "video_url": item["video_url"],
            "title": item["prompt"],
            "seed_source": "manual_seed_script",
        }
        for item in SEED_CACHED_VIDEOS
    ]

    collection.upsert(ids=ids, documents=documents, metadatas=metadatas)

    print(
        f"Seeded {len(SEED_CACHED_VIDEOS)} cached video records into "
        f"'{CACHE_COLLECTION_NAME}'."
    )


if __name__ == "__main__":
    seed_cached_videos()
