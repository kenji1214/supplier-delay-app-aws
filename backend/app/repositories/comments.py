from datetime import datetime, timezone
from typing import Any
from app.db.sqlite import get_connection
from app.schemas.comments import CommentCreate, CommentUpdate


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class CommentRepository:
    def list_for_shipment(self, shipment_key: str) -> list[dict[str, Any]]:
        with get_connection() as conn:
            rows = conn.execute(
                """
                SELECT * FROM comments
                WHERE shipment_key = ? AND is_deleted = 0
                ORDER BY created_at DESC, id DESC
                """,
                (shipment_key,),
            ).fetchall()
            return [dict(row) for row in rows]

    def latest_by_shipments(self, shipment_keys: list[str]) -> dict[str, list[dict[str, Any]]]:
        if not shipment_keys:
            return {}
        placeholders = ",".join("?" for _ in shipment_keys)
        with get_connection() as conn:
            rows = conn.execute(
                f"""
                SELECT * FROM comments
                WHERE is_deleted = 0 AND shipment_key IN ({placeholders})
                ORDER BY shipment_key ASC, created_at DESC, id DESC
                """,
                shipment_keys,
            ).fetchall()
        grouped: dict[str, list[dict[str, Any]]] = {}
        for row in rows:
            item = dict(row)
            grouped.setdefault(item["shipment_key"], []).append(item)
        return grouped

    def get(self, comment_id: int) -> dict[str, Any] | None:
        with get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM comments WHERE id = ? AND is_deleted = 0",
                (comment_id,),
            ).fetchone()
            return dict(row) if row else None

    def create(
        self,
        shipment_key: str,
        backorder: dict[str, Any],
        payload: CommentCreate,
        user_name: str,
    ) -> dict[str, Any]:
        now = utc_now()
        values = {
            "shipment_key": shipment_key,
            "supplier_code": backorder["supplier_code"],
            "supplier_name": backorder["supplier_name"],
            "plant_code": backorder["plant_code"],
            "planner_code": payload.planner_code or backorder.get("planner_code"),
            "part_number": backorder["part_number"],
            "po_number": backorder["po_number"],
            "comment_text": payload.comment_text,
            "action_status": payload.action_status,
            "action_owner": payload.action_owner,
            "due_date": payload.due_date,
            "created_by": user_name,
            "created_at": now,
            "updated_by": user_name,
            "updated_at": now,
            "is_deleted": 0,
        }
        columns = ",".join(values.keys())
        placeholders = ",".join("?" for _ in values)
        with get_connection() as conn:
            cursor = conn.execute(
                f"INSERT INTO comments ({columns}) VALUES ({placeholders})",
                list(values.values()),
            )
            conn.commit()
            return self.get(cursor.lastrowid)  # type: ignore[arg-type]

    def update(self, comment_id: int, payload: CommentUpdate, user_name: str) -> dict[str, Any] | None:
        current = self.get(comment_id)
        if not current:
            return None

        allowed = ["planner_code", "comment_text", "action_status", "action_owner", "due_date"]
        updates = {
            key: value
            for key, value in payload.model_dump(exclude_unset=True).items()
            if key in allowed
        }
        updates["updated_by"] = user_name
        updates["updated_at"] = utc_now()

        assignments = ", ".join(f"{key} = ?" for key in updates)
        with get_connection() as conn:
            conn.execute(
                f"UPDATE comments SET {assignments} WHERE id = ? AND is_deleted = 0",
                [*updates.values(), comment_id],
            )
            conn.commit()
        return self.get(comment_id)

    def soft_delete(self, comment_id: int, user_name: str) -> bool:
        if not self.get(comment_id):
            return False
        with get_connection() as conn:
            conn.execute(
                """
                UPDATE comments
                SET is_deleted = 1, updated_by = ?, updated_at = ?
                WHERE id = ? AND is_deleted = 0
                """,
                (user_name, utc_now(), comment_id),
            )
            conn.commit()
        return True
