import uuid
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Integer, BigInteger
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base

class Item(Base):
    __tablename__ = "items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, index=True, nullable=False)
    is_folder = Column(Boolean, default=False)
    
    # Metadata for files
    size = Column(BigInteger, nullable=True) # in bytes
    mime_type = Column(String, nullable=True)
    file_path = Column(String, nullable=True) # UUID filename on disk
    
    # Adjacency List for nested folders
    parent_id = Column(UUID(as_uuid=True), ForeignKey("items.id"), nullable=True)
    
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    is_starred = Column(Boolean, default=False)
    is_trashed = Column(Boolean, default=False)
    trashed_at = Column(DateTime, nullable=True)
    is_archived = Column(Boolean, default=False)
    category = Column(String, nullable=True) # e.g., 'personal', 'work', 'project'
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    
    # Sharing
    is_public = Column(Boolean, default=False)
    sharing_token = Column(String, unique=True, index=True, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner = relationship("User", back_populates="items")
    parent = relationship("Item", remote_side=[id], backref="children")
    permissions = relationship("ItemPermission", back_populates="item", cascade="all, delete-orphan")
    category_obj = relationship("Category", back_populates="items")
