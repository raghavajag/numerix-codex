import logging
import os
from pathlib import Path
from uuid import uuid4

import requests
from dotenv import load_dotenv

from agent.graph_state import State


ROOT_DIR = Path(__file__).resolve().parents[2]
load_dotenv(ROOT_DIR / ".env")
logger = logging.getLogger(__name__)


def execute_code(state: State) -> dict:
    worker_url = os.getenv("MANIM_WORKER_URL", "http://localhost:8080").rstrip("/")
    if not worker_url:
        logger.error("execute_code: MANIM_WORKER_URL is not configured")
        return {
            "sandbox_error": "MANIM_WORKER_URL is not configured",
            "video_url": "",
            "render_failures": state.get("render_failures", 0) + 1,
        }

    request_id = str(uuid4())
    payload = {
        "code": state["code"],
        "scene_name": state["scene_name"],
        "request_id": request_id,
    }
    logger.info(
        "execute_code: sending render request to worker_url=%s scene_name=%s request_id=%s",
        worker_url,
        state["scene_name"],
        request_id,
    )

    try:
        response = requests.post(
            f"{worker_url}/render",
            json=payload,
            timeout=900,
        )
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as exc:
        error_text = ""
        response_obj = getattr(exc, "response", None)
        if response_obj is not None:
            try:
                error_body = response_obj.json()
                error_text = error_body.get("detail", str(error_body))
            except ValueError:
                error_text = response_obj.text
        logger.error(
            "execute_code: worker render failed for scene_name=%s request_id=%s error=%s",
            state["scene_name"],
            request_id,
            error_text or str(exc),
        )
        return {
            "sandbox_error": error_text or str(exc),
            "video_url": "",
            "render_failures": state.get("render_failures", 0) + 1,
        }

    logger.info(
        "execute_code: worker render succeeded for scene_name=%s request_id=%s video_url=%s",
        state["scene_name"],
        request_id,
        data["video_url"],
    )
    return {
        "sandbox_error": "No error",
        "video_url": data["video_url"],
        "render_failures": 0,
    }
