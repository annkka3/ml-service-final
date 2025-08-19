
FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# системные зависимости (для pandas/matplotlib)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    tzdata \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

ENV TZ=Europe/Berlin
WORKDIR /app

# зависимости
COPY pyproject.toml /app/
RUN python -m venv /opt/venv && . /opt/venv/bin/activate && \
    pip install --upgrade pip && \
    pip install -e .

# --- Runtime image ---
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TZ=Europe/Berlin

WORKDIR /app

COPY --from=base /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# копируем только исходники и .env.example
COPY src /app/src
COPY .env.example /app/.env.example

# создаем директорию для данных
RUN mkdir -p /data && touch /data/subscribers.txt

CMD ["python", "-m", "src.bot_main"]
