from uuid import UUID

from fastapi import HTTPException, status

from app.db.connection import get_db_cursor
from app.db.queries.reception import (
    close_reception_query,
    create_reception_query,
    get_active_reception_for_pvz_query,
    get_reception_query,
)
from app.models.reception import Reception, ReceptionCreate
from app.services.pvz import get_pvz


async def create_reception(reception: ReceptionCreate) -> Reception:
    await get_pvz(reception.pvz_id)

    with get_db_cursor() as cursor:
        query, params = get_active_reception_for_pvz_query(reception.pvz_id)
        cursor.execute(query, params)
        active_reception = cursor.fetchone()

        if active_reception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="There is already an active reception for this PVZ. Close it before creating a new one.",
            )

        query, params = create_reception_query(reception)
        cursor.execute(query, params)
        new_reception = cursor.fetchone()

        return Reception(
            id=new_reception["id"],
            date_time=new_reception["date_time"],
            pvz_id=new_reception["pvz_id"],
            status=new_reception["status"],
        )


async def get_reception(reception_id: UUID) -> Reception:
    with get_db_cursor() as cursor:
        query, params = get_reception_query(reception_id)
        cursor.execute(query, params)
        reception_data = cursor.fetchone()

        if not reception_data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reception not found")

        return Reception(
            id=reception_data["id"],
            date_time=reception_data["date_time"],
            pvz_id=reception_data["pvz_id"],
            status=reception_data["status"],
        )


async def get_active_reception(pvz_id: UUID) -> Reception:
    with get_db_cursor() as cursor:
        query, params = get_active_reception_for_pvz_query(pvz_id)
        cursor.execute(query, params)
        reception_data = cursor.fetchone()

        if not reception_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="No active reception found for this PVZ"
            )

        return Reception(
            id=reception_data["id"],
            date_time=reception_data["date_time"],
            pvz_id=reception_data["pvz_id"],
            status=reception_data["status"],
        )


async def close_reception(pvz_id: UUID) -> Reception:
    with get_db_cursor() as cursor:
        query, params = get_active_reception_for_pvz_query(pvz_id)
        cursor.execute(query, params)
        active_reception = cursor.fetchone()

        if not active_reception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="No active reception found for this PVZ"
            )

        query, params = close_reception_query(active_reception["id"])
        cursor.execute(query, params)
        closed_reception = cursor.fetchone()

        if not closed_reception:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to close reception")

        return Reception(
            id=closed_reception["id"],
            date_time=closed_reception["date_time"],
            pvz_id=closed_reception["pvz_id"],
            status=closed_reception["status"],
        )
