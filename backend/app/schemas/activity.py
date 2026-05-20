from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional

class ActivityBase(BaseModel):
    action: str
    item_name: str
    item_id: Optional[UUID] = None

class ActivityCreate(ActivityBase):
    user_id: UUID

class Activity(ActivityBase):
    id: UUID
    user_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True
