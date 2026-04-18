from typing import Any
from fastapi import HTTPException
from app.models.backorder import parse_shipment_key
from app.repositories.comments import CommentRepository
from app.schemas.backorders import ActionSummary, BackorderDetail, BackorderListItem
from app.schemas.comments import CommentCreate, CommentRead, CommentUpdate
from app.snowflake.client import SnowflakeBackorderClient


class BackorderService:
    def __init__(self) -> None:
        self.snowflake = SnowflakeBackorderClient()
        self.comments = CommentRepository()

    def list_backorders(self, filters: dict[str, Any]) -> list[BackorderListItem]:
        rows = self.snowflake.list_backorders(filters)
        grouped_comments = self.comments.latest_by_shipments([row["shipment_key"] for row in rows])
        return [
            BackorderListItem(**row, action_summary=self._summary(grouped_comments.get(row["shipment_key"], [])))
            for row in rows
        ]

    def detail(self, shipment_key: str) -> BackorderDetail:
        self._validate_key(shipment_key)
        row = self.snowflake.get_backorder(shipment_key)
        if not row:
            raise HTTPException(status_code=404, detail="Backorder not found")
        comments = self.comments.list_for_shipment(shipment_key)
        item = BackorderListItem(**row, action_summary=self._summary(comments))
        return BackorderDetail(backorder=item, comments=[CommentRead(**comment) for comment in comments])

    def list_comments(self, shipment_key: str) -> list[CommentRead]:
        self._validate_key(shipment_key)
        return [CommentRead(**comment) for comment in self.comments.list_for_shipment(shipment_key)]

    def create_comment(self, shipment_key: str, payload: CommentCreate, user_name: str) -> CommentRead:
        self._validate_key(shipment_key)
        row = self.snowflake.get_backorder(shipment_key)
        if not row:
            raise HTTPException(status_code=404, detail="Backorder not found")
        comment = self.comments.create(shipment_key, row, payload, user_name)
        return CommentRead(**comment)

    def update_comment(self, comment_id: int, payload: CommentUpdate, user_name: str) -> CommentRead:
        comment = self.comments.update(comment_id, payload, user_name)
        if not comment:
            raise HTTPException(status_code=404, detail="Comment not found")
        return CommentRead(**comment)

    def delete_comment(self, comment_id: int, user_name: str) -> dict[str, bool]:
        deleted = self.comments.soft_delete(comment_id, user_name)
        if not deleted:
            raise HTTPException(status_code=404, detail="Comment not found")
        return {"deleted": True}

    def planner_codes(self) -> list[str]:
        return self.snowflake.planner_codes()

    def debug_snowflake(self) -> dict[str, Any]:
        return self.snowflake.debug_connection()

    @staticmethod
    def _summary(comments: list[dict[str, Any]]) -> ActionSummary:
        if not comments:
            return ActionSummary()
        latest = comments[0]
        preview = latest.get("comment_text") or ""
        if len(preview) > 120:
            preview = preview[:117] + "..."
        return ActionSummary(
            latest_action_status=latest.get("action_status"),
            latest_action_owner=latest.get("action_owner"),
            latest_due_date=latest.get("due_date"),
            latest_comment_preview=preview,
            latest_planner_code=latest.get("planner_code"),
            comment_count=len(comments),
        )

    @staticmethod
    def _validate_key(shipment_key: str) -> None:
        try:
            parse_shipment_key(shipment_key)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
