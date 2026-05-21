from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from app.schemas.item_permission import ItemPermission
from app.schemas.category import Category as CategorySchema

class ItemBase(BaseModel):
    name: str
    is_folder: bool = False
    parent_id: Optional[UUID] = None
    category: Optional[str] = None
    category_id: Optional[UUID] = None

class ItemCreate(ItemBase):
    pass

class ItemUpdate(BaseModel):
    name: Optional[str] = None
    parent_id: Optional[UUID] = None
    is_starred: Optional[bool] = None
    is_pinned: Optional[bool] = None
    is_trashed: Optional[bool] = None
    is_archived: Optional[bool] = None
    category: Optional[str] = None
    category_id: Optional[UUID] = None

class Item(ItemBase):
    id: UUID
    owner_id: UUID
    size: Optional[int] = None
    mime_type: Optional[str] = None
    is_starred: bool
    is_pinned: Optional[bool] = False
    is_trashed: bool
    trashed_at: Optional[datetime] = None
    is_archived: bool = False
    is_public: bool = False
    sharing_token: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    permissions: List[ItemPermission] = []
    category_obj: Optional[CategorySchema] = None

    class Config:
        from_attributes = True

class ItemWithChildren(Item):
    children: List["Item"] = []

class FolderCreate(BaseModel):
    name: str
    parent_id: Optional[UUID] = None
    category: Optional[str] = None
    category_id: Optional[UUID] = None
