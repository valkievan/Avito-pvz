from uuid import UUID

from app.models.reception import ReceptionCreate


def create_reception_query(reception: ReceptionCreate) -> tuple:
    query = """
    INSERT INTO receptions (pvz_id, status)
    VALUES (%s, 'in_progress')
    RETURNING id, date_time, pvz_id, status
    """
    params = (str(reception.pvz_id),)
    return query, params


def get_reception_query(reception_id: UUID) -> tuple:
    query = """
    SELECT id, date_time, pvz_id, status
    FROM receptions
    WHERE id = %s
    """
    params = (str(reception_id),)
    return query, params


def get_active_reception_for_pvz_query(pvz_id: UUID) -> tuple:
    query = """
    SELECT id, date_time, pvz_id, status
    FROM receptions
    WHERE pvz_id = %s AND status = 'in_progress'
    ORDER BY date_time DESC
    LIMIT 1
    """
    params = (str(pvz_id),)
    return query, params


def close_reception_query(reception_id: UUID) -> tuple:
    query = """
    UPDATE receptions
    SET status = 'close'
    WHERE id = %s AND status = 'in_progress'
    RETURNING id, date_time, pvz_id, status
    """
    params = (str(reception_id),)
    return query, params


def get_receptions_for_pvz_query(pvz_id: UUID) -> tuple:
    query = """
    SELECT id, date_time, pvz_id, status
    FROM receptions
    WHERE pvz_id = %s
    ORDER BY date_time DESC
    """
    params = (str(pvz_id),)
    return query, params
