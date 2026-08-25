# syntax=docker/dockerfile:1.7

# The container is the dev environment: it provides pyenv + poetry so the
# existing build.sh / run_petl_dev.sh flow works unchanged. You keep uv on
# the host.

FROM debian:bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Build deps needed for pyenv to compile CPython, plus curl+git for pyenv.run.
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        ca-certificates \
        curl \
        git \
        libbz2-dev \
        libffi-dev \
        liblzma-dev \
        libncursesw5-dev \
        libreadline-dev \
        libsqlite3-dev \
        libssl-dev \
        libxml2-dev \
        libxmlsec1-dev \
        tk-dev \
        xz-utils \
        zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Install pyenv (same tool build.sh expects to already be present locally).
ENV PYENV_ROOT=/root/.pyenv
ENV PATH="$PYENV_ROOT/shims:$PYENV_ROOT/bin:/root/.local/bin:$PATH"
RUN curl -fsSL https://pyenv.run | bash

WORKDIR /app

# Install the pinned CPython. Mirrors: `pyenv install $(head -n 1 .python-version)`
COPY .python-version ./
RUN pyenv install "$(cat .python-version)" \
 && pyenv global  "$(cat .python-version)" \
 && python -V

# pip -> pipx -> poetry, matching build.sh dev.
RUN pip install --upgrade pip \
 && pip install pipx \
 && pipx ensurepath \
 && pipx install poetry

# Keep the venv inside the project so `poetry run` works from /app and you can
# poke at .venv/ if you shell into the container.
ENV POETRY_VIRTUALENVS_IN_PROJECT=1

# `poetry sync` = install exactly what's in the lockfile, matching build.sh.
COPY pyproject.toml poetry.lock README.md ./
COPY src ./src
RUN poetry sync

# Bring in the runtime scripts last so edits to them don't bust the deps layer.
COPY run_petl_dev.sh run_petl_prod.sh build.sh ./
RUN chmod +x run_petl_dev.sh run_petl_prod.sh build.sh

# run_petl_dev.sh sources ./.env and runs `poetry run petl` for each group.
# Mount your .env at /app/.env when you `docker run` (see README/command below).
ENTRYPOINT ["./run_petl_dev.sh"]
