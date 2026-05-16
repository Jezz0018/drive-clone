from pydantic import BaseModel
from uuid import UUID

class Captcha(BaseModel):
    id: UUID
    challenge: str

    class Config:
        from_attributes = True
