from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.api import deps
from app.models.user import User
from app.models.category import Category
from app.schemas.category import Category as CategorySchema, CategoryCreate, CategoryUpdate
import uuid

router = APIRouter()

@router.get("/", response_model=List[CategorySchema])
async def read_categories(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Retrieve categories.
    """
    result = await db.execute(select(Category).filter(Category.owner_id == current_user.id))
    return result.scalars().all()

@router.post("/", response_model=CategorySchema)
async def create_category(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    category_in: CategoryCreate
) -> Any:
    """
    Create new category.
    """
    db_obj = Category(
        name=category_in.name,
        color=category_in.color,
        owner_id=current_user.id
    )
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

@router.patch("/{id}", response_model=CategorySchema)
async def update_category(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    id: uuid.UUID,
    category_in: CategoryUpdate
) -> Any:
    """
    Update a category.
    """
    result = await db.execute(select(Category).filter(Category.id == id, Category.owner_id == current_user.id))
    db_obj = result.scalars().first()
    if not db_obj:
        raise HTTPException(status_code=404, detail="Category not found")
    
    update_data = category_in.dict(exclude_unset=True)
    for field in update_data:
        setattr(db_obj, field, update_data[field])
    
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

@router.delete("/{id}", response_model=CategorySchema)
async def delete_category(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    id: uuid.UUID
) -> Any:
    """
    Delete a category.
    """
    result = await db.execute(select(Category).filter(Category.id == id, Category.owner_id == current_user.id))
    db_obj = result.scalars().first()
    if not db_obj:
        raise HTTPException(status_code=404, detail="Category not found")
    
    await db.delete(db_obj)
    await db.commit()
    return db_obj
