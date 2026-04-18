from datetime import datetime
from pydantic import BaseModel, Field


class CommentBase(BaseModel):
    planner_code: str | None = None
    comment_text: str = Field(..., min_length=1, max_length=4000)
    action_status: str = Field(default="Open", max_length=80)
    action_owner: str | None = Field(default=None, max_length=160)
    due_date: str | None = None


class CommentCreate(CommentBase):
    pass


class CommentUpdate(BaseModel):
    planner_code: str | None = None
    comment_text: str | None = Field(default=None, min_length=1, max_length=4000)
    action_status: str | None = Field(default=None, max_length=80)
    action_owner: str | None = Field(default=None, max_length=160)
    due_date: str | None = None


class CommentRead(CommentBase):
    id: int
    shipment_key: str
    supplier_code: str
    supplier_name: str
    plant_code: str
    part_number: str
    po_number: str
    created_by: str
    created_at: datetime
    updated_by: str | None = None
    updated_at: datetime
    is_deleted: bool = False

    model_config = {"from_attributes": True}
