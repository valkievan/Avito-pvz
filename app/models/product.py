from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ProductBase(BaseModel):
    type: str = Field(..., pattern="^(электроника|одежда|обувь)$")


class ProductCreate(ProductBase):
    pvz_id: UUID


class Product(ProductBase):
    id: UUID
    date_time: datetime
    reception_id: UUID

    class Config:
        from_attributes = True
