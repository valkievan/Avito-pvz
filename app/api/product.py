from fastapi import APIRouter, Depends, status

from app.api.dependencies import check_if_employee
from app.models.product import Product, ProductCreate
from app.services.product import create_product

router = APIRouter()


@router.post("/products", response_model=Product, status_code=status.HTTP_201_CREATED, summary="Добавление товара в текущую приемку")
async def create_product_endpoint(product: ProductCreate, current_user: dict = Depends(check_if_employee)):
    return await create_product(product)
