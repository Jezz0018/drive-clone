from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from app.api import deps
from app.models.item import Item
from app.models.user import User
from app.schemas.item import Item as ItemSchema, ItemCreate, ItemUpdate, FolderCreate
import uuid
import os
import aiofiles
from app.core.config import settings
from datetime import datetime

from fastapi.responses import FileResponse

router = APIRouter()

@router.get("/{item_id}/download")
async def download_file(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    item_id: uuid.UUID
) -> Any:
    result = await db.execute(select(Item).filter(Item.id == item_id, Item.owner_id == current_user.id))
    db_obj = result.scalars().first()
    if not db_obj or db_obj.is_folder:
        raise HTTPException(status_code=404, detail="File not found")
    
    file_path = os.path.join(settings.UPLOAD_DIR, db_obj.file_path)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Physical file not found")
        
    return FileResponse(
        path=file_path,
        filename=db_obj.name,
        media_type=db_obj.mime_type
    )

@router.get("/", response_model=List[ItemSchema])
async def read_items(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    parent_id: Optional[uuid.UUID] = None,
    is_trashed: bool = False,
    is_starred: Optional[bool] = None,
    search: Optional[str] = None
) -> Any:
    query = select(Item).filter(Item.owner_id == current_user.id)
    
    if is_trashed:
        query = query.filter(Item.is_trashed == True)
    else:
        query = query.filter(Item.is_trashed == False)
        if parent_id:
            query = query.filter(Item.parent_id == parent_id)
        elif not search and is_starred is None:
            query = query.filter(Item.parent_id == None)
            
    if is_starred is not None:
        query = query.filter(Item.is_starred == is_starred)
        
    if search:
        query = query.filter(Item.name.ilike(f"%{search}%"))
        
    query = query.order_by(Item.is_folder.desc(), Item.name.asc())
    
    result = await db.execute(query)
    return result.scalars().all()

@router.post("/folders", response_model=ItemSchema)
async def create_folder(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    folder_in: FolderCreate
) -> Any:
    db_obj = Item(
        name=folder_in.name,
        is_folder=True,
        parent_id=folder_in.parent_id,
        owner_id=current_user.id
    )
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

@router.post("/upload", response_model=ItemSchema)
async def upload_file(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    file: UploadFile = File(...),
    parent_id: Optional[uuid.UUID] = Form(None)
) -> Any:
    file_id = uuid.uuid4()
    file_ext = os.path.splitext(file.filename)[1]
    saved_filename = f"{file_id}{file_ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, saved_filename)
    
    # Save file to disk
    async with aiofiles.open(file_path, 'wb') as out_file:
        content = await file.read()
        await out_file.write(content)
        size = len(content)
        
    db_obj = Item(
        id=file_id,
        name=file.filename,
        is_folder=False,
        size=size,
        mime_type=file.content_type,
        file_path=saved_filename,
        parent_id=parent_id,
        owner_id=current_user.id
    )
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

@router.patch("/{item_id}", response_model=ItemSchema)
async def update_item(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    item_id: uuid.UUID,
    item_in: ItemUpdate
) -> Any:
    result = await db.execute(select(Item).filter(Item.id == item_id, Item.owner_id == current_user.id))
    db_obj = result.scalars().first()
    if not db_obj:
        raise HTTPException(status_code=404, detail="Item not found")
    
    update_data = item_in.dict(exclude_unset=True)
    if "is_trashed" in update_data:
        if update_data["is_trashed"]:
            db_obj.trashed_at = datetime.utcnow()
        else:
            db_obj.trashed_at = None
            
    for field in update_data:
        setattr(db_obj, field, update_data[field])
        
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

@router.delete("/{item_id}", response_model=ItemSchema)
async def delete_item(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    item_id: uuid.UUID
) -> Any:
    result = await db.execute(select(Item).filter(Item.id == item_id, Item.owner_id == current_user.id))
    db_obj = result.scalars().first()
    if not db_obj:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # Permanent delete if already in trash, otherwise move to trash
    if db_obj.is_trashed:
        # Delete physical file if it's a file
        if not db_obj.is_folder and db_obj.file_path:
            file_path = os.path.join(settings.UPLOAD_DIR, db_obj.file_path)
            if os.path.exists(file_path):
                os.remove(file_path)
        
        await db.delete(db_obj)
        await db.commit()
        return db_obj
    else:
        db_obj.is_trashed = True
        db_obj.trashed_at = datetime.utcnow()
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
