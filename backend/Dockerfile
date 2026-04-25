FROM python:3.12-slim
WORKDIR /app/backend
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8000 \
    ENV=local \
    SQLITE_PATH=/app/data/comments.db
COPY requirements.txt .
RUN pip install --disable-pip-version-check -r requirements.txt
COPY app ./app
RUN adduser --disabled-password --gecos "" appuser \
    && mkdir -p /app/data \
    && chown -R appuser:appuser /app
USER appuser
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 CMD python -c "import os, urllib.request; urllib.request.urlopen(f'http://127.0.0.1:{os.getenv(\"PORT\", \"8000\")}/health', timeout=3)"
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
