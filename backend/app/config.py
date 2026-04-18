from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    app_name: str = "Supplier Backorder Monitor"
    app_environment: str = "development"
    sqlite_path: str = "data/comments.db"
    cors_origins: str | None = "http://localhost:5173,http://127.0.0.1:5173"
    current_user: str = "poc.planner"
    use_mock_data: bool = False

    snowflake_account: str | None = None
    snowflake_user: str | None = None
    snowflake_password: str | None = None
    snowflake_warehouse: str | None = None
    snowflake_database: str | None = None
    snowflake_schema: str | None = None
    snowflake_role: str | None = None

    frontend_dist: str = "../frontend/dist"

    model_config = SettingsConfigDict(env_file=BACKEND_DIR / ".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        configured = []
        if self.cors_origins:
            configured = [
                origin.strip()
                for origin in self.cors_origins.split(",")
                if origin.strip() and origin.strip() != "*"
            ]

        # Local Vite ports can shift when a default port is already in use.
        # Keep explicit origins here instead of using "*" with credentials.
        local_dev_origins = [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:5174",
            "http://127.0.0.1:5174",
        ]
        if self.app_environment.lower() in {"development", "dev", "local", "test"}:
            configured.extend(local_dev_origins)

        return sorted(set(configured))

    @property
    def can_use_snowflake(self) -> bool:
        return not self.use_mock_data and not self.missing_snowflake_env

    @property
    def missing_snowflake_env(self) -> list[str]:
        required = {
            "SNOWFLAKE_ACCOUNT": self.snowflake_account,
            "SNOWFLAKE_USER": self.snowflake_user,
            "SNOWFLAKE_PASSWORD": self.snowflake_password,
            "SNOWFLAKE_WAREHOUSE": self.snowflake_warehouse,
            "SNOWFLAKE_DATABASE": self.snowflake_database,
            "SNOWFLAKE_SCHEMA": self.snowflake_schema,
        }
        return [name for name, value in required.items() if not value]

    @property
    def snowflake_env_status(self) -> dict[str, bool]:
        return {
            "SNOWFLAKE_ACCOUNT": bool(self.snowflake_account),
            "SNOWFLAKE_USER": bool(self.snowflake_user),
            "SNOWFLAKE_PASSWORD": bool(self.snowflake_password),
            "SNOWFLAKE_WAREHOUSE": bool(self.snowflake_warehouse),
            "SNOWFLAKE_DATABASE": bool(self.snowflake_database),
            "SNOWFLAKE_SCHEMA": bool(self.snowflake_schema),
            "SNOWFLAKE_ROLE": bool(self.snowflake_role),
        }

    @property
    def snowflake_view_name(self) -> str:
        if self.snowflake_database and self.snowflake_schema:
            return f"{self.snowflake_database}.{self.snowflake_schema}.V_SUPPLIER_BACKORDER"
        return "V_SUPPLIER_BACKORDER"

    @property
    def frontend_dist_path(self) -> Path:
        return Path(__file__).resolve().parent.parent / self.frontend_dist


@lru_cache
def get_settings() -> Settings:
    return Settings()
