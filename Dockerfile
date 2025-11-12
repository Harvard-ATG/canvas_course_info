# syntax=docker/dockerfile:1

FROM python:3.10-slim-bookworm AS build
COPY --from=ghcr.io/astral-sh/uv:0.8.12 /uv /uvx /bin/
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=0 UV_INDEX_PRIVATE_REGISTRY_USERNAME=aws

RUN apt-get update; apt-get install -y --no-install-recommends git libpq-dev build-essential
WORKDIR /code
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=secret,id=UV_INDEX_PRIVATE_REGISTRY_PASSWORD,env=UV_INDEX_PRIVATE_REGISTRY_PASSWORD \
    uv sync --locked --no-install-project --group aws --no-dev --keyring-provider disabled
COPY . /code
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=secret,id=UV_INDEX_PRIVATE_REGISTRY_PASSWORD,env=UV_INDEX_PRIVATE_REGISTRY_PASSWORD \
    uv sync --locked --no-dev --group aws --keyring-provider disabled
RUN chmod a+x /code/docker-entrypoint.sh

FROM python:3.10-slim-bookworm
RUN apt-get update; apt-get install -y --no-install-recommends git libpq5
COPY --from=build /code /code
ENV PATH="/code/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1
WORKDIR /code
ENTRYPOINT ["/code/docker-entrypoint.sh"]
EXPOSE 8000