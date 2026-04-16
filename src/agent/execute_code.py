import os
from uuid import uuid4

import requests
from dotenv import load_dotenv

from agent.graph_state import State


load_dotenv()


def execute_code(state: State) -> dict:
    worker_url = os.getenv("MANIM_WORKER_URL", "http://localhost:8080").rstrip("/")
    if not worker_url:
        return {
            "sandbox_error": "MANIM_WORKER_URL is not configured",
            "video_url": "",
        }

    payload = {
        "code": state["code"],
        "scene_name": state["scene_name"],
        "request_id": str(uuid4()),
    }

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
        return {
            "sandbox_error": error_text or str(exc),
            "video_url": "",
        }

    return {
        "sandbox_error": "No error",
        "video_url": data["video_url"],
    }
