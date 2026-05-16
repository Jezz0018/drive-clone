import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base
import enum

class PermissionLevel(str, enum.Enum):
    VIEWER = "viewer"
    EDITOR = "editor"

class ItemPermission(Base):
    __tablename__ = "item_permissions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    item_id = Column(UUID(as_uuid=True), ForeignKey("items.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    level = Column(String, nullable=False, default=PermissionLevel.VIEWER) # String for simplicity with frontend
    
    created_at = Column(DateTime, default=datetime.utcnow)

    item = relationship("Item", back_populates="permissions")
    user = relationship("User", backref="shared_items")
