from datetime import date
from pydantic import BaseModel
from app.schemas.comments import CommentRead


class ActionSummary(BaseModel):
    latest_action_status: str | None = None
    latest_action_owner: str | None = None
    latest_due_date: str | None = None
    latest_comment_preview: str | None = None
    latest_planner_code: str | None = None
    comment_count: int = 0


class BackorderListItem(BaseModel):
    shipment_key: str
    supplier_code: str
    supplier_name: str
    plant_code: str
    planner_code: str | None = None
    part_number: str
    po_number: str
    due_date: date | None = None
    ordered_qty: float
    received_qty: float
    open_qty: float
    is_backorder: bool
    backorder_days: int
    backorder_status: str
    action_summary: ActionSummary


class BackorderDetail(BaseModel):
    backorder: BackorderListItem
    comments: list[CommentRead]
