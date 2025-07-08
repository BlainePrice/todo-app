from pydantic import BaseModel
from datetime import datetime

class UserCreate(BaseModel):
    username: str
    password: str

class UserOut(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

class TodoItemCreate(BaseModel):
    title: str
    description: str | None = None
    completed: bool = False

class TodoItem(TodoItemCreate):
    id: int

    class Config:
        from_attributes = True

class SupportTicketCreate(BaseModel):
    title: str
    description: str

class SupportTicket(SupportTicketCreate):
    id: int
    status: str
    created_at: datetime
    user_id: int

    class Config:
        from_attributes = True

