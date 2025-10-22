FROM python:3.12-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --no-editable

# Copy the project into the intermediate image
ADD . /app

# Sync the project
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-editable

# FROM python:3.12-slim AS test

# COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# # Copy the environment, but not the source code
# COPY --from=builder --chown=app:app /app/.venv /app/.venv

WORKDIR /app/tests

# Run tests
CMD ["uv", "run", "pytest"]