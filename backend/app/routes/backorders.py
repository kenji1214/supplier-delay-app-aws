from typing import Annotated
from fastapi import APIRouter, Depends, Header, HTTPException, Query, Response
from app.config import get_settings
from app.schemas.backorders import BackorderDetail, BackorderListItem
from app.schemas.comments import CommentCreate, CommentRead, CommentUpdate
from app.services.backorders import BackorderService

router = APIRouter(prefix="/api", tags=["backorders"])


def get_service() -> BackorderService:
    return BackorderService()


def current_user(x_user_name: Annotated[str | None, Header()] = None) -> str:
    return x_user_name or get_settings().current_user


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "env": get_settings().env}


@router.get("/debug/snowflake")
def debug_snowflake(service: BackorderService = Depends(get_service)) -> dict:
    if not get_settings().is_local:
        raise HTTPException(status_code=404, detail="Debug endpoint is only available in development")
    return service.debug_snowflake()


@router.get("/planner-codes")
def planner_codes(service: BackorderService = Depends(get_service)) -> list[str]:
    return service.planner_codes()


@router.get("/backorders", response_model=list[BackorderListItem])
def list_backorders(
    supplier_code: str | None = None,
    plant_code: str | None = None,
    planner_code: str | None = None,
    planner_codes: Annotated[list[str] | None, Query()] = None,
    part_number: str | None = None,
    po_number: str | None = None,
    min_backorder_days: int | None = None,
    search: str | None = None,
    service: BackorderService = Depends(get_service),
) -> list[BackorderListItem]:
    return service.list_backorders(
        {
            "supplier_code": supplier_code,
            "plant_code": plant_code,
            "planner_code": planner_code,
            "planner_codes": planner_codes,
            "part_number": part_number,
            "po_number": po_number,
            "min_backorder_days": min_backorder_days,
            "search": search,
        }
    )


@router.get("/backorders/{shipment_key}/comments", response_model=list[CommentRead])
def list_comments(
    shipment_key: str,
    service: BackorderService = Depends(get_service),
) -> list[CommentRead]:
    return service.list_comments(shipment_key)


@router.post("/backorders/{shipment_key}/comments", response_model=CommentRead, status_code=201)
def create_comment(
    shipment_key: str,
    payload: CommentCreate,
    user_name: Annotated[str, Depends(current_user)],
    service: BackorderService = Depends(get_service),
) -> CommentRead:
    return service.create_comment(shipment_key, payload, user_name)


@router.get("/backorders/{shipment_key}", response_model=BackorderDetail)
def backorder_detail(
    shipment_key: str,
    service: BackorderService = Depends(get_service),
) -> BackorderDetail:
    return service.detail(shipment_key)


@router.put("/comments/{comment_id}", response_model=CommentRead)
def update_comment(
    comment_id: int,
    payload: CommentUpdate,
    user_name: Annotated[str, Depends(current_user)],
    service: BackorderService = Depends(get_service),
) -> CommentRead:
    return service.update_comment(comment_id, payload, user_name)


@router.delete("/comments/{comment_id}", status_code=204)
def delete_comment(
    comment_id: int,
    user_name: Annotated[str, Depends(current_user)],
    service: BackorderService = Depends(get_service),
) -> Response:
    service.delete_comment(comment_id, user_name)
    return Response(status_code=204)
