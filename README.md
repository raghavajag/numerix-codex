# Numeric

`numeric` now uses a plain Docker-backed worker model for Manim rendering.

The API generates code and sends it to a dedicated worker service over HTTP.
The worker renders the video with Manim and either:

- uploads the result to Cloudflare R2, or
- returns a local `file://` URL when `SKIP_UPLOAD=1`.

## Services

- `api`: LangGraph pipeline and `/run` endpoint on port `8000`
- `manim-worker`: render service and `/render` endpoint on port `8080`

## Local Setup

1. Copy `.env.example` to `.env`
2. Set `OPENAI_API_KEY`
3. Set the R2 variables, or keep `SKIP_UPLOAD=1` for local testing

## Run With Docker Compose

Build and run both services:

```bash
docker compose up --build
```

Only run the render worker:

```bash
docker compose up --build manim-worker
```

## Worker Smoke Test

Once the worker is up on `localhost:8080`, run:

```bash
curl -X POST http://localhost:8080/render \
  -H "Content-Type: application/json" \
  -d '{
    "scene_name": "TestScene",
    "code": "from manim import *\nclass TestScene(Scene):\n    def construct(self):\n        c = Circle()\n        self.play(Create(c))\n        self.wait()"
  }'
```

## Full Pipeline Test

Once both services are up, run:

```bash
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "I want to understand and visualize how the recent Artemis II moon voyage was done, like from Earth to Moon the trajectory, the ship voyage etc!",
    "language": "en"
  }'
```

## Docker Targets

Build the API image only:

```bash
docker build --target api -t numeric-api .
```

Build the Manim worker image only:

```bash
docker build --target worker -t numeric-manim-worker .
```
