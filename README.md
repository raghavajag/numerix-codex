# Numerix

**Prompt in. Clear visual explanations out.**

Numerix is a two-service system that turns a natural-language learning prompt into a rendered animation video.
It does more than generate raw code: it classifies the request, researches the topic when needed, plans the video shot-by-shot, retrieves Manim evidence, writes the scene, renders it in an isolated worker, and falls back to simpler code when reliability matters more than detail.

---

## Why This Exists

Most "text to animation" demos stop at code generation.
Numerix tries to go one step further:

- keep non-animation prompts out of the expensive path
- ground real-world topics before visualizing them
- retrieve actual Manim API patterns before writing code
- render inside a dedicated worker instead of inside the API
- recover from render failures with repair and simplification loops

The goal is simple: **make educational videos that are useful, legible, and actually render.**

---

## The Flow

```text
User Prompt
   |
   v
FastAPI /run
   |
   v
LangGraph agent
   |
   +--> Prompt classifier
   +--> Grounding router
   +--> Topic brief builder
   +--> Scene + shot planner
   +--> Manim RAG retrieval
   +--> Code outline
   +--> Final code generation
   +--> Render execution
           |
           v
      Manim worker
           |
           +--> local file URL (SKIP_UPLOAD=1)
           +--> Cloudflare R2 URL
```

### What actually happens on `/run`

1. The API checks a semantic cache in Chroma.
2. The prompt is classified to decide whether it should even become an animation.
3. The graph decides whether the topic needs factual grounding.
4. A topic brief is created from either internal reasoning or external web evidence.
5. A single scene is planned as 4-8 connected shots.
6. Each shot retrieves relevant Manim API chunks and example patterns.
7. The model creates a code outline, then final Manim code.
8. The worker renders the video.
9. If rendering fails, Numerix first repairs the code, then simplifies it aggressively to prioritize availability.

---

## Services

### `api`

The API is a FastAPI app on port `8000`.

It is responsible for:

- `/run`
- `/health`
- rate limiting with SlowAPI
- semantic caching in Chroma
- LangGraph orchestration
- language normalization

Main file:
- [src/api/main.py](/Users/pushpitkamboj/PersonalProjects/codex_hackathon/numerix-codex/src/api/main.py)

### `manim-worker`

The worker is a separate FastAPI service on port `8080`.

It is responsible for:

- `/render`
- validating render payloads
- running the `manim` subprocess
- enforcing render limits and timeouts
- returning either a local file URL or an uploaded R2 URL

Main file:
- [src/manim-worker/app.py](/Users/pushpitkamboj/PersonalProjects/codex_hackathon/numerix-codex/src/manim-worker/app.py)

---

## Core Architecture

### 1. LangGraph agent

The graph is wired in:
- [src/agent/graph.py](/Users/pushpitkamboj/PersonalProjects/codex_hackathon/numerix-codex/src/agent/graph.py)

Important stages:

- `analyze_user_prompt`
- `route_prompt_for_grounding`
- `build_topic_brief`
- `plan_video`
- `get_chunks`
- `generate_code_outline`
- `generate_code`
- `execute_code`
- `correct_code`
- `simplify_code`

State lives in:
- [src/agent/graph_state.py](/Users/pushpitkamboj/PersonalProjects/codex_hackathon/numerix-codex/src/agent/graph_state.py)

That state holds:

- prompt and language
- route info and topic brief
- scene spec and shot plan
- retrieval evidence
- code outline and final code
- render result and recovery counters

### 2. Research + planning

This is where Numerix becomes more than a one-shot code generator.

- [src/agent/research_router.py](/Users/pushpitkamboj/PersonalProjects/codex_hackathon/numerix-codex/src/agent/research_router.py) decides whether the topic needs external grounding.
- [src/agent/research_topic.py](/Users/pushpitkamboj/PersonalProjects/codex_hackathon/numerix-codex/src/agent/research_topic.py) builds a factual topic brief.
- [src/agent/plan_video.py](/Users/pushpitkamboj/PersonalProjects/codex_hackathon/numerix-codex/src/agent/plan_video.py) turns that brief into one coherent scene with dependent shots.

### 3. RAG for Manim

Numerix retrieves Manim-specific evidence before writing code.

- [src/rag/chunks.py](/Users/pushpitkamboj/PersonalProjects/codex_hackathon/numerix-codex/src/rag/chunks.py) chunks Manim source files
- [src/rag/indexing.py](/Users/pushpitkamboj/PersonalProjects/codex_hackathon/numerix-codex/src/rag/indexing.py) indexes them into Chroma
- [src/rag/retriever.py](/Users/pushpitkamboj/PersonalProjects/codex_hackathon/numerix-codex/src/rag/retriever.py) combines lexical, optional dense, synthetic, and example-based retrieval

The raw Manim source used for indexing lives in:
- [src/manim_docs](/Users/pushpitkamboj/PersonalProjects/codex_hackathon/numerix-codex/src/manim_docs)

### 4. Code generation

Code generation is split into two steps:

- an outline pass
- a final code pass

Main file:
- [src/agent/generate_code.py](/Users/pushpitkamboj/PersonalProjects/codex_hackathon/numerix-codex/src/agent/generate_code.py)

Current model family used in the agent stack:
- `openai:gpt-5.4`

### 5. Recovery over perfection

If render fails:

1. try targeted repair
2. if failures keep happening, switch to a simpler scene
3. stop after the configured max instead of looping forever

This behavior lives in:
- [src/agent/regenerate_code.py](/Users/pushpitkamboj/PersonalProjects/codex_hackathon/numerix-codex/src/agent/regenerate_code.py)

---

## Quick Start

### 1. Create env file

```bash
cp .env.example .env
```

Minimum useful values:

- `OPENAI_API_KEY`
- `MANIM_WORKER_URL=http://manim-worker:8080` in Docker
- `SKIP_UPLOAD=1` for local testing

If you want dense retrieval and caching:

- `CHROMA_API_KEY`
- `CHROMA_TENANT`
- `CHROMA_DATABASE`

If you want upload instead of local file URLs:

- `R2_ACCOUNT_ID`
- `R2_ACCESS_KEY_ID`
- `R2_SECRET_ACCESS_KEY`
- `R2_BUCKET`
- `R2_PUBLIC_BASE_URL`

### 2. Run the stack

```bash
docker compose up --build
```

This starts:

- API on `http://localhost:8000`
- worker on `http://localhost:8080`

### 3. Health checks

```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8080/health
```

### 4. Smoke test the worker

```bash
curl -X POST http://127.0.0.1:8080/render \
  -H "Content-Type: application/json" \
  -d '{
    "scene_name": "TestScene",
    "request_id": "smoke-test-001",
    "code": "from manim import *\nclass TestScene(Scene):\n    def construct(self):\n        c = Circle()\n        self.play(Create(c))\n        self.wait()"
  }'
```

### 5. Run the full pipeline

```bash
curl -X POST http://127.0.0.1:8000/run \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Explain projectile motion with a simple animation",
    "language": "en"
  }'
```

You can also send:

```json
{
  "prompt": "Derive the quadratic formula step by step",
  "lang": "fr"
}
```

The API accepts both `language` and `lang`.

---

## API Reference

### `GET /health`

API health and current worker target.

Example response:

```json
{
  "message": "ok",
  "worker_url": "http://manim-worker:8080"
}
```

### `POST /run`

Runs the full generation pipeline.

Request body:

```json
{
  "prompt": "Explain simple harmonic motion",
  "language": "en"
}
```

Possible responses:

Success:

```json
{
  "result": "file:///tmp/manim-worker/published/2026-04-16/...",
  "status": "success"
}
```

Non-animation:

```json
{
  "result": "Ask me for a concrete educational animation and I can help.",
  "status": "non_animation"
}
```

Pipeline failure:

```json
{
  "result": "Video generation failed after multiple attempts",
  "status": "error"
}
```

### `GET /health` on worker

```json
{
  "status": "ok",
  "quality": "-ql"
}
```

### `POST /render`

Render-only endpoint for direct worker testing.

Request body:

```json
{
  "scene_name": "TestScene",
  "request_id": "debug-001",
  "code": "..."
}
```

---

## Frontend

There is also a small Next.js chat frontend in:
- [src/fe](/Users/pushpitkamboj/PersonalProjects/codex_hackathon/numerix-codex/src/fe)

It gives you:

- a single-page chat UI
- loading/error states
- local message persistence
- a simple proxy route at `src/fe/app/api/generate/route.ts`

Run it separately:

```bash
cd src/fe
npm install
ANIMAI_API_URL=http://localhost:8000 npm run dev
```

Then open:

```text
http://localhost:3000
```

---

## Project Map

```text
src/
  agent/         LangGraph nodes, planning, codegen, recovery
  api/           FastAPI entrypoint, caching, language normalization
  rag/           Chunking, indexing, retrieval, reranking
  manim-worker/  Isolated render service
  manim_docs/    Local Manim source used to build retrieval corpus
  fe/            Next.js chat frontend
tests/           Worker, retrieval, language, recovery, integration tests
terraform/       Cloud Run + Artifact Registry infrastructure
```

---

## Tests

Useful tests already in the repo:

- [tests/test_manim_worker.py](/Users/pushpitkamboj/PersonalProjects/codex_hackathon/numerix-codex/tests/test_manim_worker.py)
- [tests/test_language_registry.py](/Users/pushpitkamboj/PersonalProjects/codex_hackathon/numerix-codex/tests/test_language_registry.py)
- [tests/test_recovery_logic.py](/Users/pushpitkamboj/PersonalProjects/codex_hackathon/numerix-codex/tests/test_recovery_logic.py)
- [tests/test_pipeline_integration.py](/Users/pushpitkamboj/PersonalProjects/codex_hackathon/numerix-codex/tests/test_pipeline_integration.py)

You also have a `Makefile` with common commands:
- [Makefile](/Users/pushpitkamboj/PersonalProjects/codex_hackathon/numerix-codex/Makefile)

Examples:

```bash
make test-local
make test-local-run
make docker-build
make lint
```

---

## Important Tradeoffs

This version is practical and debuggable, but not magic.

- `/run` is still synchronous end-to-end, so long renders block the request.
- Dense retrieval depends on Chroma credentials and indexed docs.
- The frontend currently defaults to English unless you wire language choice into the UI.
- Long, complex videos are possible, but reliability improves a lot when prompts are specific.
- The worker is Dockerized and isolated on purpose, because Manim and voiceover dependencies are heavy.

If you want to push this further, the natural next step is a job-based async render system with per-shot rendering and final video assembly.

---

## Deployment

This repo already includes:

- Docker multi-stage builds: [Dockerfile](/Users/pushpitkamboj/PersonalProjects/codex_hackathon/numerix-codex/Dockerfile)
- Compose setup: [compose.yml](/Users/pushpitkamboj/PersonalProjects/codex_hackathon/numerix-codex/compose.yml)
- LangGraph config: [langgraph.json](/Users/pushpitkamboj/PersonalProjects/codex_hackathon/numerix-codex/langgraph.json)
- Terraform for Cloud Run: [terraform](/Users/pushpitkamboj/PersonalProjects/codex_hackathon/numerix-codex/terraform)

---

## One-Line Mental Model

**Numerix is a research-aware LangGraph planner that writes Manim, hands rendering to a worker, and cares more about producing a working educational video than winning a prompt beauty contest.**
