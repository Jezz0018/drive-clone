from typing import Any, List, Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload
from app.api import deps
from app.models.item import Item
from app.models.user import User
from app.schemas.item import Item as ItemSchema, ItemCreate, ItemUpdate, FolderCreate
import uuid
import os
import aiofiles
from app.core.config import settings
from datetime import datetime
import secrets

from fastapi.responses import FileResponse

from sqlalchemy import select, and_, or_, func

router = APIRouter()

@router.get("/storage/usage")
async def get_storage_usage(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    # Fetch all files owned by user to sum them manually (more robust for debugging)
    result = await db.execute(
        select(Item.size, Item.category)
        .filter(Item.owner_id == current_user.id, Item.is_folder == False)
    )
    rows = result.all()
    
    total_used = 0
    breakdown_map = {}
    file_count = len(rows)
    
    for size, category in rows:
        item_size = size or 0
        total_used += item_size
        cat_name = category or "Uncategorized"
        breakdown_map[cat_name] = breakdown_map.get(cat_name, 0) + item_size

    breakdown = []
    for name, size in breakdown_map.items():
        breakdown.append({"name": name, "size": size})

    return {
        "used": total_used, 
        "limit": 10 * 1024 * 1024 * 1024, # 10GB limit
        "breakdown": breakdown,
        "file_count": file_count
    }

@router.get("/share/{token}/info", response_model=ItemSchema)
async def get_shared_item_info(
    *,
    db: AsyncSession = Depends(deps.get_db),
    token: str
) -> Any:
    result = await db.execute(
        select(Item)
        .options(selectinload(Item.permissions), selectinload(Item.category_obj))
        .filter(Item.sharing_token == token, Item.is_public == True)
    )
    db_obj = result.scalars().first()
    if not db_obj:
        raise HTTPException(status_code=404, detail="Shared item not found")
    return db_obj

@router.get("/share/{token}")
async def download_shared_item(
    *,
    db: AsyncSession = Depends(deps.get_db),
    token: str
) -> Any:
    result = await db.execute(select(Item).filter(Item.sharing_token == token, Item.is_public == True))
    db_obj = result.scalars().first()
    if not db_obj or db_obj.is_folder:
        raise HTTPException(status_code=404, detail="Shared file not found")
    
    file_path = os.path.join(settings.UPLOAD_DIR, db_obj.file_path)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Physical file not found")
        
    return FileResponse(
        path=file_path,
        filename=db_obj.name,
        media_type=db_obj.mime_type
    )

@router.post("/{item_id}/share", response_model=ItemSchema)
async def toggle_item_share(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    item_id: uuid.UUID
) -> Any:
    result = await db.execute(
        select(Item)
        .options(selectinload(Item.permissions), selectinload(Item.category_obj))
        .filter(Item.id == item_id, Item.owner_id == current_user.id)
    )
    db_obj = result.scalars().first()
    if not db_obj:
        raise HTTPException(status_code=404, detail="Item not found")
    
    if db_obj.is_public:
        db_obj.is_public = False
        # We can keep the token or clear it, clearing it makes it "more secure" if re-shared
        db_obj.sharing_token = None
    else:
        db_obj.is_public = True
        db_obj.sharing_token = secrets.token_urlsafe(16)
        
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

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

from app.models.item_permission import ItemPermission as ItemPermissionModel
from app.schemas.item_permission import ItemPermission as ItemPermissionSchema, ItemPermissionCreate, ItemPermissionUpdate

@router.post("/{item_id}/permissions", response_model=ItemPermissionSchema)
async def add_item_permission(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    item_id: uuid.UUID,
    permission_in: ItemPermissionCreate
) -> Any:
    # Check if user owns the item
    result = await db.execute(select(Item).filter(Item.id == item_id, Item.owner_id == current_user.id))
    item = result.scalars().first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found or access denied")
    
    # Find user by email
    result = await db.execute(select(User).filter(User.email == permission_in.user_email))
    target_user = result.scalars().first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User with this email not found")
    
    if target_user.id == current_user.id:
        raise HTTPException(status_code=400, detail="You cannot share an item with yourself")

    # Check if permission already exists
    result = await db.execute(select(ItemPermissionModel).filter(
        ItemPermissionModel.item_id == item_id, 
        ItemPermissionModel.user_id == target_user.id
    ))
    existing_perm = result.scalars().first()
    if existing_perm:
        existing_perm.level = permission_in.level
        db.add(existing_perm)
    else:
        db_obj = ItemPermissionModel(
            item_id=item_id,
            user_id=target_user.id,
            level=permission_in.level
        )
        db.add(db_obj)
        
    await db.commit()
    # For response, we need the email
    perm = existing_perm if existing_perm else db_obj
    await db.refresh(perm)
    setattr(perm, 'user_email', target_user.email)
    return perm

@router.delete("/{item_id}/permissions/{permission_id}", response_model=ItemPermissionSchema)
async def delete_item_permission(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    item_id: uuid.UUID,
    permission_id: uuid.UUID
) -> Any:
    # Only owner can remove permissions
    result = await db.execute(select(Item).filter(Item.id == item_id, Item.owner_id == current_user.id))
    item = result.scalars().first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
        
    result = await db.execute(select(ItemPermissionModel).filter(ItemPermissionModel.id == permission_id, ItemPermissionModel.item_id == item_id))
    perm = result.scalars().first()
    if not perm:
        raise HTTPException(status_code=404, detail="Permission not found")
        
    await db.delete(perm)
    await db.commit()
    return perm

@router.get("/{item_id}/permissions", response_model=List[ItemPermissionSchema])
async def list_item_permissions(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    item_id: uuid.UUID
) -> Any:
    # Only owner can see permissions list
    result = await db.execute(select(Item).filter(Item.id == item_id, Item.owner_id == current_user.id))
    item = result.scalars().first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
        
    result = await db.execute(
        select(ItemPermissionModel, User.email)
        .join(User, ItemPermissionModel.user_id == User.id)
        .filter(ItemPermissionModel.item_id == item_id)
    )
    rows = result.all()
    perms = []
    for row in rows:
        perm = row[0]
        email = row[1]
        setattr(perm, 'user_email', email)
        perms.append(perm)
    return perms

@router.get("/", response_model=List[ItemSchema])
async def read_items(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    parent_id: Optional[uuid.UUID] = None,
    is_trashed: bool = False,
    is_starred: Optional[bool] = None,
    is_pinned: Optional[bool] = None,
    is_archived: bool = False,
    category: Optional[str] = None,
    category_id: Optional[uuid.UUID] = None,
    search: Optional[str] = None,
    mime_type: Optional[str] = None,
    shared_with_me: bool = False,
    sort_by: str = "name",
    sort_order: str = "asc"
) -> Any:
    if shared_with_me:
        # Items shared with current user
        query = (
            select(Item)
            .options(selectinload(Item.permissions), selectinload(Item.category_obj))
            .join(ItemPermissionModel, Item.id == ItemPermissionModel.item_id)
            .filter(ItemPermissionModel.user_id == current_user.id)
            .filter(Item.is_trashed == False)
        )
    else:
        # User's own items
        query = select(Item).options(selectinload(Item.permissions), selectinload(Item.category_obj)).filter(Item.owner_id == current_user.id)
        
        if is_trashed:
            query = query.filter(Item.is_trashed == True)
        else:
            query = query.filter(Item.is_trashed == False)
            query = query.filter(Item.is_archived == is_archived)
            
            if parent_id:
                query = query.filter(Item.parent_id == parent_id)
            elif not search and is_starred is None and category is None and not category_id:
                query = query.filter(Item.parent_id == None)
                
    if is_starred is not None:
        query = query.filter(Item.is_starred == is_starred)
        
    if category_id:
        query = query.filter(Item.category_id == category_id)
    elif category:
        query = query.filter(Item.category == category)
        
    if search:
        query = query.filter(Item.name.ilike(f"%{search}%"))
        
    # Sort Logic
    order_func = Item.name.asc()
    if sort_by == "size":
        order_func = Item.size.asc() if sort_order == "asc" else Item.size.desc()
    elif sort_by == "date":
        order_func = Item.updated_at.asc() if sort_order == "asc" else Item.updated_at.desc()
    else: # name
        order_func = Item.name.asc() if sort_order == "asc" else Item.name.desc()

    query = query.order_by(Item.is_folder.desc(), order_func)
    
    result = await db.execute(query)
    return result.scalars().all()

from app.models.activity import Activity
from app.schemas.activity import Activity as ActivitySchema

@router.get("/activity", response_model=List[ActivitySchema])
async def get_activity_feed(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    result = await db.execute(
        select(Activity)
        .filter(Activity.user_id == current_user.id)
        .order_by(Activity.created_at.desc())
        .limit(5)
    )
    return result.scalars().all()

async def log_activity(db: AsyncSession, user_id: uuid.UUID, action: str, item_name: str, item_id: Optional[uuid.UUID] = None):
    activity = Activity(user_id=user_id, action=action, item_name=item_name, item_id=item_id)
    db.add(activity)
    await db.flush()

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
        owner_id=current_user.id,
        category=folder_in.category,
        category_id=folder_in.category_id
    )
    db.add(db_obj)
    await log_activity(db, current_user.id, "create_folder", folder_in.name)
    await db.commit()
    
    # Eagerly load relationships for response validation
    result = await db.execute(
        select(Item)
        .options(selectinload(Item.permissions), selectinload(Item.category_obj))
        .filter(Item.id == db_obj.id)
    )
    return result.scalars().first()

@router.post("/upload", response_model=ItemSchema)
async def upload_file(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    file: UploadFile = File(...),
    parent_id: Optional[uuid.UUID] = Form(None),
    category: Optional[str] = Form(None),
    category_id: Optional[uuid.UUID] = Form(None)
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
        owner_id=current_user.id,
        category=category,
        category_id=category_id
    )
    db.add(db_obj)
    await log_activity(db, current_user.id, "upload", file.filename, file_id)
    await db.commit()
    
    # Eagerly load relationships for response validation
    result = await db.execute(
        select(Item)
        .options(selectinload(Item.permissions), selectinload(Item.category_obj))
        .filter(Item.id == file_id)
    )
    return result.scalars().first()

@router.patch("/{item_id}", response_model=ItemSchema)
async def update_item(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    item_id: uuid.UUID,
    item_in: ItemUpdate
) -> Any:
    result = await db.execute(
        select(Item)
        .options(selectinload(Item.permissions), selectinload(Item.category_obj))
        .filter(Item.id == item_id, Item.owner_id == current_user.id)
    )
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
    result = await db.execute(
        select(Item)
        .options(selectinload(Item.permissions), selectinload(Item.category_obj))
        .filter(Item.id == item_id, Item.owner_id == current_user.id)
    )
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

@router.delete("/trash/empty", response_model=dict)
async def empty_trash(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    # Get all items in trash for this user
    result = await db.execute(select(Item).filter(Item.owner_id == current_user.id, Item.is_trashed == True))
    items_to_delete = result.scalars().all()
    
    count = 0
    for item in items_to_delete:
        # Delete physical file if it's a file
        if not item.is_folder and item.file_path:
            file_path = os.path.join(settings.UPLOAD_DIR, item.file_path)
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception as e:
                    print(f"Error deleting physical file {file_path}: {e}")
        
        await db.delete(item)
        count += 1
    
    await db.commit()
    return {"message": f"Successfully emptied trash. {count} items removed permanently."}
