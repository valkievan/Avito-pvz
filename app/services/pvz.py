from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from fastapi import HTTPException, status

from app.db.connection import get_db_cursor
from app.db.queries.pvz import (
    create_pvz_query,
    get_pvz_query,
    get_pvz_with_receptions_query,
    get_pvzs_count_query,
    get_pvzs_query,
)
from app.models.pvz import PVZ, PVZCreate


async def create_pvz(pvz: PVZCreate) -> PVZ:
    if pvz.city not in ["Москва", "Санкт-Петербург", "Казань"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="City must be one of: Moscow, Saint-Petersburg, Kazan",
        )

    with get_db_cursor() as cursor:
        query, params = create_pvz_query(pvz)
        cursor.execute(query, params)
        new_pvz = cursor.fetchone()

        return PVZ(id=new_pvz["id"], city=new_pvz["city"], registration_date=new_pvz["registration_date"])


async def get_pvz(pvz_id: UUID) -> PVZ:
    with get_db_cursor() as cursor:
        query, params = get_pvz_query(pvz_id)
        cursor.execute(query, params)
        pvz_data = cursor.fetchone()

        if not pvz_data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PVZ not found")

        return PVZ(id=pvz_data["id"], city=pvz_data["city"], registration_date=pvz_data["registration_date"])


async def get_pvzs_with_pagination_and_filtering(
    page: int = 1, limit: int = 10, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None
) -> dict[str, Any]:
    with get_db_cursor() as cursor:
        count_query, count_params = get_pvzs_count_query(start_date, end_date)
        cursor.execute(count_query, count_params)
        total = cursor.fetchone()["total"]

        query, params = get_pvzs_query(page, limit, start_date, end_date)
        cursor.execute(query, params)
        pvz_rows = cursor.fetchall()

        pvz_list = []

        for pvz_row in pvz_rows:
            pvz_id = pvz_row["id"]
            pvz_with_receptions_query, pvz_with_receptions_params = get_pvz_with_receptions_query(pvz_id)
            cursor.execute(pvz_with_receptions_query, pvz_with_receptions_params)
            detail_rows = cursor.fetchall()

            pvz_data = {
                "pvz": {
                    "id": pvz_row["id"],
                    "registration_date": pvz_row["registration_date"],
                    "city": pvz_row["city"],
                },
                "receptions": [],
            }

            receptions_dict = {}
            for row in detail_rows:
                if row["reception_id"] and row["reception_id"] not in receptions_dict:
                    receptions_dict[row["reception_id"]] = {
                        "reception": {
                            "id": row["reception_id"],
                            "date_time": row["date_time"],
                            "pvz_id": pvz_id,
                            "status": row["status"],
                        },
                        "products": [],
                    }

                if row["product_id"]:
                    reception_id = row["reception_id"]
                    if reception_id in receptions_dict:
                        receptions_dict[reception_id]["products"].append(
                            {
                                "id": row["product_id"],
                                "date_time": row["product_date_time"],
                                "type": row["type"],
                                "reception_id": reception_id,
                            }
                        )

            pvz_data["receptions"] = list(receptions_dict.values())
            pvz_list.append(pvz_data)

        return {"total": total, "page": page, "limit": limit, "items": pvz_list}
