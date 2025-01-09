# Global Argument
ARG WORK_DIR="/app"

# Build stage
FROM python:3.10@sha256:c970ff53939772f47b0672e380328afb50d8fd1c0568ed4f82c22effc54244fc as builder
ARG WORK_DIR

ENV PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.8.0

RUN apt-get update && apt-get install -y --no-install-recommends \
    musl-dev \
    && apt-get clean

WORKDIR ${WORK_DIR}

COPY ./pyproject.toml ${WORK_DIR}
COPY ./poetry.lock ${WORK_DIR}

RUN pip install "poetry==$POETRY_VERSION" \
    && poetry config virtualenvs.in-project true \
    && poetry install --no-interaction --no-ansi --no-cache --only main --no-root --no-directory

COPY . ${WORK_DIR}

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

RUN poetry install --no-interaction --no-ansi --no-cache --only main

# Final stage
FROM python:3.10-alpine@sha256:1cf0c63d9f573d17be9200c9940a4ce3b18971674b8bf1a596ffe5441802f647 as final

ARG WORK_DIR

WORKDIR ${WORK_DIR}

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

COPY --from=builder ${WORK_DIR} ${WORK_DIR}
