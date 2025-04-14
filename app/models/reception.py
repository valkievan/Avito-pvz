from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ReceptionBase(BaseModel):
    pvz_id: UUID


class ReceptionCreate(ReceptionBase):
    pass


class Reception(ReceptionBase):
    id: UUID
    date_time: datetime
    status: str

    class Config:
        from_attributes = True
