from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime

class CategoryBase(BaseModel):
    name: str
    color: str = "bg-indigo-500"

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(CategoryBase):
    name: Optional[str] = None
    color: Optional[str] = None

class Category(CategoryBase):
    id: UUID
    owner_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True
