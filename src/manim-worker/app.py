import os
import re
import shutil
import subprocess
from datetime import date
from pathlib import Path
from typing import Any
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv


app = FastAPI(title="AnimAI Manim Worker")

ROOT_DIR = Path(__file__).resolve().parents[2]
load_dotenv(ROOT_DIR / ".env")

TMP_DIR = Path(os.getenv("MANIM_TMP_DIR", "/tmp/manim-worker"))
PUBLISHED_DIR = TMP_DIR / "published"
MAX_CODE_BYTES = int(os.getenv("MANIM_MAX_CODE_BYTES", "300000"))
RENDER_TIMEOUT_SECONDS = int(os.getenv("MANIM_RENDER_TIMEOUT_SECONDS", "900"))
QUALITY_FLAG = os.getenv("MANIM_QUALITY_FLAG", "-ql").strip() or "-ql"
SCENE_NAME_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
REQUEST_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{1,80}$")


def _validate_render_payload(payload: dict[str, Any]) -> tuple[str, str, str]:
    code = payload.get("code")
    scene_name = payload.get("scene_name")
    request_id = payload.get("request_id")

    if not isinstance(code, str) or not code.strip():
        raise HTTPException(status_code=400, detail="code and scene_name are required")
    if not isinstance(scene_name, str) or not scene_name.strip():
        raise HTTPException(status_code=400, detail="code and scene_name are required")
    if len(code.encode("utf-8")) > MAX_CODE_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"code exceeds the maximum allowed size of {MAX_CODE_BYTES} bytes",
        )

    normalized_scene_name = scene_name.strip()
    if not SCENE_NAME_PATTERN.fullmatch(normalized_scene_name):
        raise HTTPException(
            status_code=400,
            detail="scene_name must be a valid Python class identifier",
        )

    normalized_request_id = (
        request_id.strip()
        if isinstance(request_id, str) and request_id.strip()
        else str(uuid4())
    )
    if not REQUEST_ID_PATTERN.fullmatch(normalized_request_id):
        raise HTTPException(
            status_code=400,
            detail="request_id may only contain letters, numbers, hyphens, and underscores",
        )

    return code, normalized_scene_name, normalized_request_id


def _request_dir(request_id: str) -> Path:
    return TMP_DIR / request_id


def _build_manim_command(source_file: Path, scene_name: str, media_dir: Path) -> list[str]:
    return [
        "manim",
        QUALITY_FLAG,
        str(source_file),
        scene_name,
        "--media_dir",
        str(media_dir),
        "--disable_caching",
    ]


def _find_video_path(media_dir: Path, scene_name: str) -> Path | None:
    matches = sorted(media_dir.glob(f"videos/**/{scene_name}.mp4"))
    if matches:
        return matches[-1]

    fallback_matches = sorted(media_dir.rglob(f"{scene_name}.mp4"))
    if fallback_matches:
        return fallback_matches[-1]
    return None


def _render_video(code: str, scene_name: str, request_id: str) -> Path:
    request_dir = _request_dir(request_id)
    if request_dir.exists():
        shutil.rmtree(request_dir, ignore_errors=True)
    request_dir.mkdir(parents=True, exist_ok=True)

    source_file = request_dir / "scene.py"
    source_file.write_text(code, encoding="utf-8")
    media_dir = request_dir / "media"
    media_dir.mkdir(parents=True, exist_ok=True)

    command = _build_manim_command(source_file, scene_name, media_dir)

    try:
        subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
            timeout=RENDER_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired as exc:
        raise HTTPException(
            status_code=504,
            detail=f"Manim render timed out after {RENDER_TIMEOUT_SECONDS} seconds",
        ) from exc
    except subprocess.CalledProcessError as exc:
        error_output = (exc.stderr or exc.stdout or str(exc)).strip()
        raise HTTPException(status_code=500, detail=f"Manim failed: {error_output}") from exc

    video_path = _find_video_path(media_dir, scene_name)
    if video_path is None or not video_path.exists():
        raise HTTPException(status_code=500, detail="Video not generated")

    return video_path


def _upload_to_r2(video_path: Path, scene_name: str, request_id: str, today: str) -> str:
    if os.getenv("SKIP_UPLOAD") == "1":
        target_dir = PUBLISHED_DIR / today / scene_name
        target_dir.mkdir(parents=True, exist_ok=True)
        published_path = target_dir / f"{request_id}.mp4"
        shutil.copy2(video_path, published_path)
        return published_path.resolve().as_uri()

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
    public_base_url = os.getenv("R2_PUBLIC_BASE_URL", "").rstrip("/")

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

    if public_base_url:
        return f"{public_base_url}/{key}"

    return f"https://pub-{account_id}.r2.dev/{key}"


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "quality": QUALITY_FLAG}


@app.post("/render")
def render(payload: dict[str, Any]) -> dict[str, str]:
    code, scene_name, request_id = _validate_render_payload(payload)
    today = date.today().isoformat()
    request_dir = _request_dir(request_id)

    try:
        video_path = _render_video(code, scene_name, request_id)
        video_url = _upload_to_r2(video_path, scene_name, request_id, today)
    finally:
        if os.getenv("KEEP_RENDER_ARTIFACTS") != "1":
            shutil.rmtree(request_dir, ignore_errors=True)

    return {
        "video_url": video_url,
        "scene_name": scene_name,
        "request_id": request_id,
    }
