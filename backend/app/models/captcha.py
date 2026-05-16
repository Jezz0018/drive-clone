import uuid
from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from app.db.base import Base

class Captcha(Base):
    __tablename__ = "captchas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    challenge = Column(String, nullable=False)
    answer = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
