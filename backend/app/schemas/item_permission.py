from pydantic import BaseModel, EmailStr
from typing import Optional, List
from uuid import UUID
from datetime import datetime

class ItemPermissionBase(BaseModel):
    level: str = "viewer"

class ItemPermissionCreate(ItemPermissionBase):
    item_id: UUID
    user_email: EmailStr # We share by email

class ItemPermissionUpdate(ItemPermissionBase):
    pass

class ItemPermission(ItemPermissionBase):
    id: UUID
    item_id: UUID
    user_id: UUID
    user_email: Optional[str] = None # Will be populated in response
    created_at: datetime

    class Config:
        from_attributes = True
