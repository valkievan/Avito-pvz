from uuid import UUID

from fastapi import HTTPException, status

from app.db.connection import get_db_cursor
from app.db.queries.product import (
    create_product_query,
    delete_product_query,
    get_last_product_in_reception_query,
    get_product_query,
    get_products_for_reception_query,
)
from app.models.product import Product, ProductCreate
from app.services.reception import get_active_reception, get_reception


async def create_product(product: ProductCreate) -> Product:
    if product.type not in ["электроника", "одежда", "обувь"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product type must be one of: электроника, одежда, обувь",
        )

    active_reception = await get_active_reception(product.pvz_id)

    with get_db_cursor() as cursor:
        query, params = create_product_query(product.type, active_reception.id)
        cursor.execute(query, params)
        new_product = cursor.fetchone()

        return Product(
            id=new_product["id"],
            date_time=new_product["date_time"],
            type=new_product["type"],
            reception_id=new_product["reception_id"],
        )


async def get_product(product_id: UUID) -> Product:
    with get_db_cursor() as cursor:
        query, params = get_product_query(product_id)
        cursor.execute(query, params)
        product_data = cursor.fetchone()

        if not product_data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

        return Product(
            id=product_data["id"],
            date_time=product_data["date_time"],
            type=product_data["type"],
            reception_id=product_data["reception_id"],
        )


async def get_products_for_reception(reception_id: UUID) -> list[Product]:
    await get_reception(reception_id)

    with get_db_cursor() as cursor:
        query, params = get_products_for_reception_query(reception_id)
        cursor.execute(query, params)
        products_data = cursor.fetchall()

        return [
            Product(
                id=product["id"],
                date_time=product["date_time"],
                type=product["type"],
                reception_id=product["reception_id"],
            )
            for product in products_data
        ]


async def delete_last_product(pvz_id: UUID) -> None:
    active_reception = await get_active_reception(pvz_id)

    with get_db_cursor() as cursor:
        query, params = get_last_product_in_reception_query(active_reception.id)
        cursor.execute(query, params)
        last_product = cursor.fetchone()

        if not last_product:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="No products found in the active reception"
            )

        # Удаляем товар
        delete_query, delete_params = delete_product_query(last_product["id"])
        cursor.execute(delete_query, delete_params)
        deleted_product = cursor.fetchone()

        if not deleted_product:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to delete product")
