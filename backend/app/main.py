from pathlib import Path
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from app.config import get_settings
from app.db.sqlite import run_migrations
from app.routes.backorders import router as backorder_router


settings = get_settings()
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger(__name__)
app = FastAPI(title=settings.app_name)

# CORS must be registered before API routes/static fallbacks so browser
# preflight requests from the Vite dev server receive the allow-origin headers.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "env": settings.env}


@app.on_event("startup")
def startup() -> None:
    run_migrations()
    logger.info("SQLite initialized path=%s", settings.sqlite_path)
    logger.info("Mock data enabled=%s", settings.use_mock_data)
    logger.info("Snowflake env present=%s missing=%s", settings.snowflake_env_status, settings.missing_snowflake_env)


app.include_router(backorder_router)

dist_path = settings.frontend_dist_path
if dist_path.exists():
    assets_path = Path(dist_path) / "assets"
    if assets_path.exists():
        app.mount("/assets", StaticFiles(directory=assets_path), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    def serve_frontend(full_path: str) -> FileResponse:
        return FileResponse(Path(dist_path) / "index.html")
