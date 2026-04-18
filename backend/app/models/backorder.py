from datetime import date
from pydantic import BaseModel


class BackorderRecord(BaseModel):
    supplier_code: str
    supplier_name: str
    plant_code: str
    planner_code: str | None = None
    part_number: str
    po_number: str
    due_date: date | None = None
    ordered_qty: float = 0
    received_qty: float = 0
    open_qty: float = 0
    is_backorder: bool = True
    backorder_days: int = 0
    backorder_status: str = "Open"

    @property
    def shipment_key(self) -> str:
        return make_shipment_key(
            self.supplier_code,
            self.plant_code,
            self.part_number,
            self.po_number,
        )


def make_shipment_key(supplier_code: str, plant_code: str, part_number: str, po_number: str) -> str:
    return "|".join([supplier_code, plant_code, part_number, po_number])


def parse_shipment_key(shipment_key: str) -> tuple[str, str, str, str]:
    parts = shipment_key.split("|")
    if len(parts) != 4 or not all(parts):
        raise ValueError("shipment_key must use supplier_code|plant_code|part_number|po_number")
    return parts[0], parts[1], parts[2], parts[3]
