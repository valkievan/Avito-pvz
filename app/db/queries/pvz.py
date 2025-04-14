from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from app.models.pvz import PVZCreate


def create_pvz_query(pvz: PVZCreate) -> tuple:
    query = """
    INSERT INTO pvz (city)
    VALUES (%s)
    RETURNING id, registration_date, city
    """
    params = (pvz.city,)
    return query, params


def get_pvz_query(pvz_id: UUID) -> tuple:
    query = """
    SELECT id, registration_date, city
    FROM pvz
    WHERE id = %s
    """
    params = (str(pvz_id),)
    return query, params


def get_pvzs_query(
    page: int = 1, limit: int = 10, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None
) -> tuple[str, list[Any]]:
    query = """
    SELECT p.id, p.registration_date, p.city
    FROM pvz p
    """

    params = []
    conditions = []

    if start_date or end_date:
        query += """
        JOIN receptions r ON p.id = r.pvz_id
        """

        if start_date:
            conditions.append("r.date_time >= %s")
            params.append(start_date)

        if end_date:
            conditions.append("r.date_time <= %s")
            params.append(end_date)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += """
    ORDER BY p.registration_date DESC
    LIMIT %s OFFSET %s
    """

    params.extend([limit, (page - 1) * limit])

    return query, params


def get_pvz_with_receptions_query(pvz_id: UUID) -> tuple:
    query = """
    SELECT
        p.id AS pvz_id,
        p.registration_date,
        p.city,
        r.id AS reception_id,
        r.date_time,
        r.status,
        pr.id AS product_id,
        pr.date_time AS product_date_time,
        pr.type
    FROM pvz p
    LEFT JOIN receptions r ON p.id = r.pvz_id
    LEFT JOIN products pr ON r.id = pr.reception_id
    WHERE p.id = %s
    ORDER BY r.date_time DESC, pr.date_time ASC
    """
    params = (str(pvz_id),)
    return query, params


def get_pvzs_count_query(
    start_date: Optional[datetime] = None, end_date: Optional[datetime] = None
) -> tuple[str, list[Any]]:
    query = """
    SELECT COUNT(DISTINCT p.id) as total
    FROM pvz p
    """

    params = []
    conditions = []

    if start_date or end_date:
        query += """
        JOIN receptions r ON p.id = r.pvz_id
        """

        if start_date:
            conditions.append("r.date_time >= %s")
            params.append(start_date)

        if end_date:
            conditions.append("r.date_time <= %s")
            params.append(end_date)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    return query, params
