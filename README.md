# Supplier Backorder Monitor

Practical POC for planners to monitor supplier backorders from Snowflake and manage action comments in SQLite.

## Stack

- Frontend: React, TypeScript, Vite
- Backend: FastAPI, Python
- Workflow data: SQLite with automatic lightweight migrations
- Backorder data: Snowflake view `V_SUPPLIER_BACKORDER`, with mock fallback
- Deployment: Docker-ready, including a root single-container Dockerfile suitable for AWS App Runner

## Project Layout

```text
backend/
  app/
    main.py
    routes/
    services/
    repositories/
    db/
    snowflake/
    models/
    schemas/
frontend/
  src/
    pages/
    components/
    api/
    types/
Dockerfile
docker-compose.yml
README.md
```

## Local Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

SQLite is created automatically at `data/comments.db`. On startup, the backend checks `PRAGMA table_info(comments)` and applies `ALTER TABLE` for missing columns, including `planner_code`.

For local Vite development, CORS keeps explicit allowed origins for `localhost` and `127.0.0.1` on ports `5173` and `5174`. This avoids browser preflight failures when Vite moves to the next port while still avoiding `*` with credentialed requests.

## Local Frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. Vite proxies `/api` to `http://localhost:8000`.

## Mock Data Mode

The backend defaults to mock data:

```env
USE_MOCK_DATA=true
```

Set `USE_MOCK_DATA=false` and provide Snowflake variables to read from `V_SUPPLIER_BACKORDER`.

## Snowflake Environment

```env
SNOWFLAKE_ACCOUNT=
SNOWFLAKE_USER=
SNOWFLAKE_PASSWORD=
SNOWFLAKE_WAREHOUSE=
SNOWFLAKE_DATABASE=
SNOWFLAKE_SCHEMA=
SNOWFLAKE_ROLE=
```

Snowflake is read-only. Comments and action tracking are stored only in SQLite.

## API

- `GET /api/backorders`
- `GET /api/backorders/{shipment_key}`
- `GET /api/backorders/{shipment_key}/comments`
- `POST /api/backorders/{shipment_key}/comments`
- `PUT /api/comments/{comment_id}`
- `DELETE /api/comments/{comment_id}`
- `GET /api/planner-codes`

`shipment_key` is always:

```text
supplier_code|plant_code|part_number|po_number
```

Planner filtering supports `planner_code`, repeated `planner_codes`, and comma-separated planner codes.

## Comment Ordering

Comments are returned and rendered in this order:

```sql
ORDER BY created_at DESC, id DESC
```

Edits update the existing row in place and do not move older comments to the top.

## UX Flows

- Add comment: save, then navigate back to the list page.
- Edit comment: save, stay on detail page, refresh detail data.
- Delete comment: soft delete by setting `is_deleted = 1`.

## Docker

Single-container build for App Runner style deployment:

```bash
docker build -t supplier-backorder-monitor .
docker run --rm -p 8000:8000 -e USE_MOCK_DATA=true supplier-backorder-monitor
```

Open `http://localhost:8000`.

Local two-service compose:

```bash
docker compose up --build
```

## AWS App Runner Notes

Use the root `Dockerfile` for the simplest deployment. Configure these environment variables in App Runner:

- `USE_MOCK_DATA=false`
- `SQLITE_PATH=/app/data/comments.db`
- Snowflake connection variables listed above

For a POC, SQLite lives inside the container filesystem. For durable production workflow data, move comments to a managed database or DynamoDB.
