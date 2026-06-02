FROM python:3.14-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR DeepDash

COPY ./pyproject.toml .
COPY ./uv.lock .

RUN uv sync --frozen --no-dev

COPY . .

EXPOSE 8081

HEALTHCHECK --interval=30s --timeout=3s \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8081/health')" \
    || exit 1

CMD ["uv", "run", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8081"]