from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class PVZBase(BaseModel):
    city: str = Field(..., pattern="^(Москва|Санкт-Петербург|Казань)$")


class PVZCreate(PVZBase):
    pass


class PVZ(PVZBase):
    id: UUID
    registration_date: datetime

    class Config:
        from_attributes = True
