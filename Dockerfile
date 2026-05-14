FROM ghcr.io/astral-sh/uv:python3.13-alpine

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /core

COPY uv.lock pyproject.toml ./
RUN uv sync --frozen

COPY ./app ./app
COPY ./migration ./migration
COPY alembic.ini ./
COPY certs ./certs
COPY .env ./
COPY entrypoint.sh ./

RUN chmod +x /core/entrypoint.sh

ENTRYPOINT ["/core/entrypoint.sh"]