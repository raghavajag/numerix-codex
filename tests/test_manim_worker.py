from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient
import pytest


ROOT_DIR = Path(__file__).resolve().parents[1]
WORKER_APP_PATH = ROOT_DIR / "src" / "manim-worker" / "app.py"


def _load_worker_module():
    spec = importlib.util.spec_from_file_location("manim_worker_app", WORKER_APP_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules["manim_worker_app"] = module
    spec.loader.exec_module(module)
    return module


def test_validate_render_payload_accepts_valid_scene_name() -> None:
    worker = _load_worker_module()

    code, scene_name, request_id = worker._validate_render_payload(
        {"code": "from manim import *", "scene_name": "TestScene"}
    )

    assert code == "from manim import *"
    assert scene_name == "TestScene"
    assert request_id


def test_validate_render_payload_rejects_invalid_scene_name() -> None:
    worker = _load_worker_module()

    with pytest.raises(worker.HTTPException) as exc_info:
        worker._validate_render_payload(
            {"code": "from manim import *", "scene_name": "../bad-scene"}
        )

    assert exc_info.value.status_code == 400
    assert "valid Python class identifier" in exc_info.value.detail


def test_build_manim_command_uses_configured_quality_flag(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MANIM_QUALITY_FLAG", "-qm")
    worker = _load_worker_module()

    command = worker._build_manim_command(
        Path("/tmp/manim-worker/test/scene.py"),
        "TestScene",
        Path("/tmp/manim-worker/test/media"),
    )

    assert command[:3] == ["manim", "-qm", "/tmp/manim-worker/test/scene.py"]
    assert "--disable_caching" in command


def test_upload_to_r2_skip_upload_publishes_local_copy(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("SKIP_UPLOAD", "1")
    worker = _load_worker_module()
    monkeypatch.setattr(worker, "PUBLISHED_DIR", tmp_path / "published")

    source = tmp_path / "source.mp4"
    source.write_bytes(b"video")

    video_url = worker._upload_to_r2(source, "TestScene", "req-123", "2026-04-16")

    published_path = tmp_path / "published" / "2026-04-16" / "TestScene" / "req-123.mp4"
    assert published_path.exists()
    assert video_url == published_path.resolve().as_uri()


def test_render_endpoint_returns_video_url(monkeypatch: pytest.MonkeyPatch) -> None:
    worker = _load_worker_module()
    client = TestClient(worker.app)

    fake_video = ROOT_DIR / "tests" / "fixtures" / "fake.mp4"
    fake_video.parent.mkdir(parents=True, exist_ok=True)
    fake_video.write_bytes(b"video")

    with patch.object(worker, "_render_video", return_value=fake_video), patch.object(
        worker, "_upload_to_r2", return_value="file:///tmp/fake.mp4"
    ):
        response = client.post(
            "/render",
            json={
                "scene_name": "TestScene",
                "code": "from manim import *\nclass TestScene(Scene):\n    pass",
                "request_id": "req-001",
            },
        )

    assert response.status_code == 200
    body = response.json()
    assert body["video_url"] == "file:///tmp/fake.mp4"
    assert body["scene_name"] == "TestScene"
    assert body["request_id"] == "req-001"
