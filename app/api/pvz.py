from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Path, Query

from app.api.dependencies import (
    check_if_employee,
    check_if_moderator,
    get_current_employee_or_moderator,
)
from app.models.pvz import PVZ, PVZCreate
from app.services.product import delete_last_product
from app.services.pvz import create_pvz, get_pvzs_with_pagination_and_filtering
from app.services.reception import close_reception

router = APIRouter()


@router.post("/pvz", response_model=PVZ, status_code=201, summary="Создание ПВЗ")
async def create_pvz_endpoint(pvz: PVZCreate, current_user: dict = Depends(check_if_moderator)):
    return await create_pvz(pvz)


@router.get("/pvz", summary="Получение списка ПВЗ")
async def get_pvzs_endpoint(
    page: int = Query(1, ge=1, description="Номер страницы"),
    limit: int = Query(10, ge=1, le=30, description="Количество элементов на странице"),
    start_date: Optional[datetime] = Query(None, description="Начальная дата диапазона"),
    end_date: Optional[datetime] = Query(None, description="Конечная дата диапазона"),
    current_user: dict = Depends(get_current_employee_or_moderator),
):
    return await get_pvzs_with_pagination_and_filtering(page, limit, start_date, end_date)


@router.post("/pvz/{pvz_id}/close_last_reception", summary="Закрытие последней открытой приёмки")
async def close_reception_endpoint(
    pvz_id: UUID = Path(..., description="ID ПВЗ"), current_user: dict = Depends(check_if_employee)
):
    return await close_reception(pvz_id)


@router.post("/pvz/{pvz_id}/delete_last_product", summary="Удаление последнего добавленного товара из текущей приемки")
async def delete_last_product_endpoint(
    pvz_id: UUID = Path(..., description="ID ПВЗ"), current_user: dict = Depends(check_if_employee)
):
    await delete_last_product(pvz_id)
    return {"message": "Product successfully deleted"}
