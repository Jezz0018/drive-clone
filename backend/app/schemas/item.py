from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime

class ItemBase(BaseModel):
    name: str
    is_folder: bool = False
    parent_id: Optional[UUID] = None

class ItemCreate(ItemBase):
    pass

class ItemUpdate(BaseModel):
    name: Optional[str] = None
    parent_id: Optional[UUID] = None
    is_starred: Optional[bool] = None
    is_trashed: Optional[bool] = None

class Item(ItemBase):
    id: UUID
    owner_id: UUID
    size: Optional[int] = None
    mime_type: Optional[str] = None
    is_starred: bool
    is_trashed: bool
    trashed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ItemWithChildren(Item):
    children: List["Item"] = []

class FolderCreate(BaseModel):
    name: str
    parent_id: Optional[UUID] = None
