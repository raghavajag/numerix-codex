import logging
import os
import sys
from pathlib import Path
from uuid import uuid4

import chromadb
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from langgraph.errors import GraphRecursionError
from pydantic import AliasChoices, BaseModel, Field
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address


SRC_DIR = Path(__file__).resolve().parents[1]
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

ROOT_DIR = Path(__file__).resolve().parents[2]
load_dotenv(ROOT_DIR / ".env")

from api.language_registry import normalize_language
from agent.graph import workflow_app

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger(__name__)

THRESHOLD = 1 - 0.2
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="AnimAI API")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)


class InstructionInput(BaseModel):
    prompt: str
    language: str = Field(default="en", validation_alias=AliasChoices("language", "lang"))


def _get_cache_collection():
    required_vars = ("CHROMA_API_KEY", "CHROMA_DATABASE", "CHROMA_TENANT")
    missing = [name for name in required_vars if not os.getenv(name)]
    if missing:
        logger.info(
            "Chroma cache disabled because required environment variables are missing: %s",
            ", ".join(missing),
        )
        return None

    client = chromadb.CloudClient(
        api_key=os.getenv("CHROMA_API_KEY"),
        database=os.getenv("CHROMA_DATABASE"),
        tenant=os.getenv("CHROMA_TENANT"),
    )
    return client.get_or_create_collection(name="manim_cached_video_url")


def _get_cached_video_url(prompt: str) -> str | None:
    collection = _get_cache_collection()
    if collection is None:
        return None
    result = collection.query(query_texts=[prompt], n_results=1)

    distances = result.get("distances", [[]])
    metadatas = result.get("metadatas", [[]])
    if not distances or not distances[0] or not metadatas or not metadatas[0]:
        return None

    distance = distances[0][0]
    metadata = metadatas[0][0] or {}
    if distance is not None and distance <= THRESHOLD:
        return metadata.get("video_url")
    return None


def _cache_video_url(prompt: str, video_url: str) -> None:
    collection = _get_cache_collection()
    if collection is None:
        return
    collection.add(
        ids=[str(uuid4())],
        documents=[prompt],
        metadatas=[{"video_url": video_url}],
    )


@app.get("/health")
async def health() -> dict[str, str]:
    worker_url = os.getenv("MANIM_WORKER_URL", "").rstrip("/")
    return {"message": "ok", "worker_url": worker_url or "unset"}


@app.post("/run")
@limiter.limit("10/minute")
async def run_pipeline(request: Request, data: InstructionInput) -> dict[str, str]:
    _ = request

    try:
        cached_url = _get_cached_video_url(data.prompt)
        if cached_url:
            logger.info("Semantic cache hit for prompt")
            return {"result": cached_url, "status": "success"}

        thread_id = str(uuid4())
        normalized_language = normalize_language(data.language)
        logger.info(
            "Running workflow for thread_id=%s with language=%s",
            thread_id,
            normalized_language,
        )
        result = await workflow_app.ainvoke(
            input={"prompt": data.prompt, "language": normalized_language},
            config={
                "configurable": {"thread_id": thread_id},
                "recursion_limit": 18,
            },
        )

        if not result.get("animation", True):
            return {
                "result": result.get("non_animation_reply", ""),
                "status": "non_animation",
            }

        video_url = result.get("video_url")
        if not video_url:
            sandbox_error = (result.get("sandbox_error") or "").strip()
            return JSONResponse(
                status_code=422,
                content={
                    "result": sandbox_error or "Video generation failed after multiple attempts",
                    "status": "error",
                },
            )

        _cache_video_url(data.prompt, video_url)
        return {"result": video_url, "status": "success"}
    except GraphRecursionError:
        return JSONResponse(
            status_code=422,
            content={
                "result": "Too difficult, give me something easier",
                "status": "error",
            },
        )
    except HTTPException:
        raise
    except Exception:
        logger.exception("Unexpected server error while processing request")
        return JSONResponse(
            status_code=500,
            content={"result": "Unexpected server error", "status": "error"},
        )
