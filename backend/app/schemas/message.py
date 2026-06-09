from pydantic import BaseModel
from datetime import datetime

class MessageCreate(BaseModel):
    chat_id: int
    content: str

class MessageResponse(BaseModel):
    id: int
    chat_id: int
    sender_id: int
    content: str
    created_at: datetime

    class Config:
        from_attributes = True