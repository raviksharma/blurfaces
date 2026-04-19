FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
        python3 python3-dev python3-pip python3-venv \
        ffmpeg build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app
COPY pyproject.toml .python-version README.md blurfaces.py ./

RUN uv sync --no-dev

ENTRYPOINT ["uv", "run", "blurfaces"]
