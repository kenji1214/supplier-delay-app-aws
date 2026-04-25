FROM node:22-alpine AS frontend-build
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend ./
RUN npm run build

FROM python:3.12-slim AS runtime
WORKDIR /app
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8000 \
    ENV=local \
    SQLITE_PATH=/app/data/comments.db \
    FRONTEND_DIST=../frontend/dist
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --disable-pip-version-check -r backend/requirements.txt
COPY backend ./backend
COPY --from=frontend-build /app/frontend/dist ./frontend/dist
RUN adduser --disabled-password --gecos "" appuser \
    && mkdir -p /app/data \
    && chown -R appuser:appuser /app
USER appuser
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 CMD python -c "import os, urllib.request; urllib.request.urlopen(f'http://127.0.0.1:{os.getenv(\"PORT\", \"8000\")}/health', timeout=3)"
WORKDIR /app/backend
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
