FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src

WORKDIR /app


FROM base AS api

COPY requirements.api.txt /app/requirements.api.txt
RUN pip install --no-cache-dir -r /app/requirements.api.txt

COPY . /app

EXPOSE 8000

CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]


FROM base AS worker

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ffmpeg \
    fonts-dejavu \
    libffi-dev \
    libgdk-pixbuf-2.0-0 \
    libcairo2-dev \
    libpango1.0-dev \
    pkg-config \
    shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.worker.txt /app/requirements.worker.txt
RUN pip install --no-cache-dir -r /app/requirements.worker.txt

COPY . /app

RUN useradd --create-home appuser \
    && mkdir -p /tmp/manim-worker \
    && chown -R appuser:appuser /app /tmp/manim-worker

USER appuser

EXPOSE 8080

CMD ["uvicorn", "app:app", "--app-dir", "src/manim-worker", "--host", "0.0.0.0", "--port", "8080"]


FROM api AS final
