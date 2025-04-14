from fastapi import APIRouter, Depends, status

from app.api.dependencies import check_if_employee
from app.models.reception import Reception, ReceptionCreate
from app.services.reception import create_reception

router = APIRouter()


@router.post("/receptions", response_model=Reception, status_code=status.HTTP_201_CREATED, summary="Создание новой приемки товаров")
async def create_reception_endpoint(
    reception: ReceptionCreate, current_user: dict = Depends(check_if_employee)
):
    return await create_reception(reception)
