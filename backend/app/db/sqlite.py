import sqlite3
from pathlib import Path
from app.config import get_settings


COMMENT_COLUMNS: dict[str, str] = {
    "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
    "shipment_key": "TEXT NOT NULL",
    "supplier_code": "TEXT NOT NULL",
    "supplier_name": "TEXT NOT NULL",
    "plant_code": "TEXT NOT NULL",
    "planner_code": "TEXT",
    "part_number": "TEXT NOT NULL",
    "po_number": "TEXT NOT NULL",
    "comment_text": "TEXT NOT NULL",
    "action_status": "TEXT NOT NULL DEFAULT 'Open'",
    "action_owner": "TEXT",
    "due_date": "TEXT",
    "created_by": "TEXT NOT NULL",
    "created_at": "TEXT NOT NULL",
    "updated_by": "TEXT",
    "updated_at": "TEXT NOT NULL",
    "is_deleted": "INTEGER NOT NULL DEFAULT 0",
}


def get_db_path() -> Path:
    db_path = Path(get_settings().sqlite_path)
    if not db_path.is_absolute():
        db_path = Path.cwd() / db_path
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return db_path


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def run_migrations() -> None:
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT
            )
            """
        )
        existing = {
            row["name"]
            for row in conn.execute("PRAGMA table_info(comments)").fetchall()
        }
        for column, definition in COMMENT_COLUMNS.items():
            if column == "id" or column in existing:
                continue
            conn.execute(f"ALTER TABLE comments ADD COLUMN {column} {definition}")
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_comments_shipment_active "
            "ON comments (shipment_key, is_deleted, created_at DESC, id DESC)"
        )
        conn.commit()
