import os
import subprocess
from datetime import date
from pathlib import Path
from typing import Any
from uuid import uuid4

from fastapi import FastAPI, HTTPException


app = FastAPI(title="AnimAI Manim Worker")

TMP_DIR = Path("/tmp")
MEDIA_DIR = TMP_DIR / "media"


def _validate_render_payload(payload: dict[str, Any]) -> tuple[str, str, str]:
    code = payload.get("code")
    scene_name = payload.get("scene_name")
    request_id = payload.get("request_id")

    if not isinstance(code, str) or not code.strip():
        raise HTTPException(status_code=400, detail="code and scene_name are required")
    if not isinstance(scene_name, str) or not scene_name.strip():
        raise HTTPException(status_code=400, detail="code and scene_name are required")

    normalized_request_id = (
        request_id.strip()
        if isinstance(request_id, str) and request_id.strip()
        else str(uuid4())
    )
    return code, scene_name.strip(), normalized_request_id


def _render_video(code: str, scene_name: str, request_id: str) -> Path:
    source_file = TMP_DIR / f"{request_id}.py"
    source_file.write_text(code, encoding="utf-8")
    MEDIA_DIR.mkdir(parents=True, exist_ok=True)

    command = [
        "manim",
        "-ql",
        str(source_file),
        scene_name,
        "--media_dir",
        str(MEDIA_DIR),
    ]

    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as exc:
        error_output = (exc.stderr or exc.stdout or str(exc)).strip()
        raise HTTPException(status_code=500, detail=f"Manim failed: {error_output}") from exc

    video_path = MEDIA_DIR / "videos" / request_id / "480p15" / f"{scene_name}.mp4"
    if not video_path.exists():
        raise HTTPException(status_code=500, detail="Video not generated")

    return video_path


def _upload_to_r2(video_path: Path, scene_name: str, request_id: str, today: str) -> str:
    if os.getenv("SKIP_UPLOAD") == "1":
        return video_path.resolve().as_uri()

    account_id = os.getenv("R2_ACCOUNT_ID")
    access_key_id = os.getenv("R2_ACCESS_KEY_ID")
    secret_access_key = os.getenv("R2_SECRET_ACCESS_KEY")
    bucket = os.getenv("R2_BUCKET")

    missing = [
        name
        for name, value in (
            ("R2_ACCOUNT_ID", account_id),
            ("R2_ACCESS_KEY_ID", access_key_id),
            ("R2_SECRET_ACCESS_KEY", secret_access_key),
            ("R2_BUCKET", bucket),
        )
        if not value
    ]
    if missing:
        raise HTTPException(
            status_code=500,
            detail="Missing required R2 environment variables: " + ", ".join(missing),
        )

    import boto3

    key = f"manim/{today}/{scene_name}/{request_id}.mp4"
    endpoint_url = f"https://{account_id}.r2.cloudflarestorage.com"

    client = boto3.client(
        "s3",
        endpoint_url=endpoint_url,
        aws_access_key_id=access_key_id,
        aws_secret_access_key=secret_access_key,
        region_name="auto",
    )

    try:
        client.upload_file(
            str(video_path),
            bucket,
            key,
            ExtraArgs={"ContentType": "video/mp4"},
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Upload failed: {exc}") from exc

    return f"https://pub-{account_id}.r2.dev/{key}"


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/render")
def render(payload: dict[str, Any]) -> dict[str, str]:
    code, scene_name, request_id = _validate_render_payload(payload)
    today = date.today().isoformat()
    video_path = _render_video(code, scene_name, request_id)
    video_url = _upload_to_r2(video_path, scene_name, request_id, today)

    return {
        "video_url": video_url,
        "scene_name": scene_name,
        "request_id": request_id,
    }
