from datetime import date
import logging
from typing import Any
from fastapi import HTTPException
from app.config import get_settings
from app.models.backorder import make_shipment_key, parse_shipment_key
from app.snowflake.mock_data import MOCK_BACKORDERS

logger = logging.getLogger(__name__)


class SnowflakeBackorderClient:
    def __init__(self) -> None:
        self.settings = get_settings()

    def list_backorders(self, filters: dict[str, Any]) -> list[dict[str, Any]]:
        logger.info("Backorder fetch requested with filters=%s", _safe_filters(filters))
        if self.settings.use_mock_data:
            logger.warning("USE_MOCK_DATA is enabled; returning mock backorders instead of Snowflake rows")
            return self._filter_mock(filters)
        if self.settings.missing_snowflake_env:
            message = f"Snowflake environment is incomplete: missing {self.settings.missing_snowflake_env}"
            logger.error(message)
            raise HTTPException(status_code=503, detail=message)
        try:
            return self._query_snowflake(filters)
        except HTTPException:
            raise
        except Exception as exc:
            logger.exception("Snowflake backorder query failed")
            raise HTTPException(status_code=502, detail=f"Snowflake query failed: {exc}") from exc

    def get_backorder(self, shipment_key: str) -> dict[str, Any] | None:
        supplier_code, plant_code, part_number, po_number = parse_shipment_key(shipment_key)
        rows = self.list_backorders(
            {
                "supplier_code": supplier_code,
                "plant_code": plant_code,
                "part_number": part_number,
                "po_number": po_number,
            }
        )
        return rows[0] if rows else None

    def planner_codes(self) -> list[str]:
        rows = self.list_backorders({})
        return sorted({row.get("planner_code") for row in rows if row.get("planner_code")})

    def debug_connection(self) -> dict[str, Any]:
        if self.settings.use_mock_data:
            return {
                "debug_only": True,
                "mode": "mock",
                "connection_ok": False,
                "row_count": None,
                "sample_rows": self._filter_mock({})[:5],
                "env_present": self.settings.snowflake_env_status,
                "missing_env": self.settings.missing_snowflake_env,
                "message": "USE_MOCK_DATA is enabled; Snowflake was not queried.",
            }
        if self.settings.missing_snowflake_env:
            return {
                "debug_only": True,
                "mode": "snowflake",
                "connection_ok": False,
                "row_count": None,
                "sample_rows": [],
                "env_present": self.settings.snowflake_env_status,
                "missing_env": self.settings.missing_snowflake_env,
                "message": "Snowflake environment is incomplete.",
            }

        try:
            import snowflake.connector

            view_name = self.settings.snowflake_view_name
            logger.info("Snowflake debug connection start account=%s database=%s schema=%s view=%s",
                        self.settings.snowflake_account, self.settings.snowflake_database,
                        self.settings.snowflake_schema, view_name)
            with snowflake.connector.connect(**self._connection_kwargs()) as conn:
                logger.info("Snowflake debug connection success")
                cursor = conn.cursor()
                cursor.execute(f"SELECT COUNT(*) AS row_count FROM {view_name}")
                row_count = cursor.fetchone()[0]
                cursor.execute(
                    f"""
                    SELECT supplier_code, supplier_name, plant_code, planner_code, part_number, po_number,
                           due_date, ordered_qty, received_qty, open_qty, is_backorder,
                           backorder_days, backorder_status
                    FROM {view_name}
                    LIMIT 5
                    """
                )
                columns = [col[0].lower() for col in cursor.description]
                sample_rows = [self._normalize_row(dict(zip(columns, row))) for row in cursor.fetchall()]
            logger.info("Snowflake debug query success row_count=%s sample_count=%s", row_count, len(sample_rows))
            return {
                "debug_only": True,
                "mode": "snowflake",
                "connection_ok": True,
                "row_count": row_count,
                "sample_rows": sample_rows,
                "env_present": self.settings.snowflake_env_status,
                "missing_env": [],
                "view": view_name,
            }
        except Exception as exc:
            logger.exception("Snowflake debug endpoint failed")
            return {
                "debug_only": True,
                "mode": "snowflake",
                "connection_ok": False,
                "row_count": None,
                "sample_rows": [],
                "env_present": self.settings.snowflake_env_status,
                "missing_env": self.settings.missing_snowflake_env,
                "view": self.settings.snowflake_view_name,
                "error": str(exc),
            }

    def _filter_mock(self, filters: dict[str, Any]) -> list[dict[str, Any]]:
        rows = [dict(row) for row in MOCK_BACKORDERS]
        planner_codes = normalize_planner_codes(filters)
        search = (filters.get("search") or "").lower().strip()

        def matches(row: dict[str, Any]) -> bool:
            exact_fields = ["supplier_code", "plant_code", "part_number", "po_number"]
            for field in exact_fields:
                value = filters.get(field)
                if value and str(row.get(field, "")).lower() != str(value).lower():
                    return False
            if planner_codes and row.get("planner_code") not in planner_codes:
                return False
            min_days = filters.get("min_backorder_days")
            if min_days not in (None, "") and int(row.get("backorder_days") or 0) < int(min_days):
                return False
            if search:
                haystack = " ".join(str(row.get(k, "")) for k in row).lower()
                if search not in haystack:
                    return False
            return True

        rows = [row for row in rows if matches(row)]
        rows.sort(key=lambda row: int(row.get("backorder_days") or 0), reverse=True)
        for row in rows:
            row["shipment_key"] = make_shipment_key(
                row["supplier_code"], row["plant_code"], row["part_number"], row["po_number"]
            )
        return rows

    def _query_snowflake(self, filters: dict[str, Any]) -> list[dict[str, Any]]:
        import snowflake.connector

        where: list[str] = ["is_backorder = TRUE"]
        params: list[Any] = []
        for field in ["supplier_code", "plant_code", "part_number", "po_number"]:
            value = filters.get(field)
            if value:
                where.append(f"{field} = %s")
                params.append(value)
        planner_codes = normalize_planner_codes(filters)
        if planner_codes:
            placeholders = ",".join(["%s"] * len(planner_codes))
            where.append(f"planner_code IN ({placeholders})")
            params.extend(planner_codes)
        if filters.get("min_backorder_days") not in (None, ""):
            where.append("backorder_days >= %s")
            params.append(int(filters["min_backorder_days"]))
        if filters.get("search"):
            search = f"%{filters['search']}%"
            where.append(
                "(supplier_code ILIKE %s OR supplier_name ILIKE %s OR part_number ILIKE %s OR po_number ILIKE %s)"
            )
            params.extend([search, search, search, search])

        sql = f"""
            SELECT supplier_code, supplier_name, plant_code, planner_code, part_number, po_number,
                   due_date, ordered_qty, received_qty, open_qty, is_backorder,
                   backorder_days, backorder_status
            FROM {self.settings.snowflake_view_name}
            WHERE {' AND '.join(where)}
            ORDER BY backorder_days DESC
        """
        logger.info("Snowflake connection start account=%s database=%s schema=%s warehouse=%s",
                    self.settings.snowflake_account, self.settings.snowflake_database,
                    self.settings.snowflake_schema, self.settings.snowflake_warehouse)
        if self.settings.is_local:
            logger.info("Snowflake query: %s params=%s", " ".join(sql.split()), params)
        with snowflake.connector.connect(**self._connection_kwargs()) as conn:
            logger.info("Snowflake connection success")
            cursor = conn.cursor()
            logger.info("Snowflake query execution start")
            cursor.execute(sql, params)
            columns = [col[0].lower() for col in cursor.description]
            rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
        logger.info("Snowflake query execution success row_count=%s columns=%s", len(rows), columns)
        rows = [self._normalize_row(row) for row in rows]
        return rows

    def _connection_kwargs(self) -> dict[str, Any]:
        kwargs = {
            "account": self.settings.snowflake_account,
            "user": self.settings.snowflake_user,
            "password": self.settings.snowflake_password,
            "warehouse": self.settings.snowflake_warehouse,
            "database": self.settings.snowflake_database,
            "schema": self.settings.snowflake_schema,
        }
        if self.settings.snowflake_role:
            kwargs["role"] = self.settings.snowflake_role
        return kwargs

    @staticmethod
    def _normalize_row(row: dict[str, Any]) -> dict[str, Any]:
        normalized = {str(key).lower(): value for key, value in row.items()}
        if isinstance(normalized.get("due_date"), date):
            normalized["due_date"] = normalized["due_date"].isoformat()
        for key in (
            "supplier_code",
            "supplier_name",
            "plant_code",
            "planner_code",
            "part_number",
            "po_number",
            "backorder_status",
        ):
            if normalized.get(key) is not None:
                normalized[key] = str(normalized[key])
        missing = [
            key for key in ("supplier_code", "plant_code", "part_number", "po_number")
            if normalized.get(key) in (None, "")
        ]
        if missing:
            raise ValueError(f"Snowflake row is missing required key columns: {missing}")
        normalized["shipment_key"] = make_shipment_key(
            str(normalized["supplier_code"]),
            str(normalized["plant_code"]),
            str(normalized["part_number"]),
            str(normalized["po_number"]),
        )
        return normalized


def _safe_filters(filters: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in filters.items() if value not in (None, "", [])}


def normalize_planner_codes(filters: dict[str, Any]) -> list[str]:
    raw_values: list[str] = []
    for key in ("planner_codes", "planner_code"):
        value = filters.get(key)
        if not value:
            continue
        if isinstance(value, list):
            raw_values.extend(str(item) for item in value)
        else:
            raw_values.extend(str(value).split(","))
    return sorted({value.strip() for value in raw_values if value.strip()})
