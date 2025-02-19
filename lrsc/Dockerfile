FROM python:3.10-slim-bullseye

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY README.md pyproject.toml requirements.lock ./

RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.lock \
    && pip install --no-cache /app/wheels/* \
    && rm -rf /app/wheels

COPY src/main.py ./src/
