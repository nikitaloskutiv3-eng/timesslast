from pydantic import BaseModel

class ChatCreate(BaseModel):
    name: str | None = None

class ChatResponse(BaseModel):
    id: int
    name: str | None = None
    is_private: bool = False
    members: list[int] = []

    class Config:
        from_attributes = True

class PrivateChatCreate(BaseModel):
    user_id: int