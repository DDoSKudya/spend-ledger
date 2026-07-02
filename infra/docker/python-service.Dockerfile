FROM python:3.12-alpine

RUN apk upgrade --no-cache \
    && apk add --no-cache libstdc++ curl \
    && curl -LsSf https://astral.sh/uv/install.sh | sh \
    && install -m 0755 /root/.local/bin/uv /usr/local/bin/uv \
    && install -m 0755 /root/.local/bin/uvx /usr/local/bin/uvx \
    && apk del curl

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

ARG SERVICE_DIR
COPY packages/spend-ledger-common /packages/spend-ledger-common
COPY ${SERVICE_DIR}/pyproject.toml ${SERVICE_DIR}/uv.lock ./
RUN sed -i 's|../../packages/spend-ledger-common|/packages/spend-ledger-common|g' pyproject.toml uv.lock \
    && uv sync --frozen --no-dev \
    && uv pip install --editable /packages/spend-ledger-common
COPY ${SERVICE_DIR}/app ./app

ARG PORT=8000
ENV PORT=${PORT}
EXPOSE ${PORT}

CMD ["sh", "-c", "uv run uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
