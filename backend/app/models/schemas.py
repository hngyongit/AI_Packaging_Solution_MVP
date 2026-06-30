from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class MessageCreate(BaseModel):
    conversation_id: Optional[str] = None
    content: str
    image_url: Optional[str] = None


class MessageResponse(BaseModel):
    id: str
    conversation_id: str
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime
    mockup_task_id: Optional[str] = None
    image_url: Optional[str] = None  # for user: uploaded image; for assistant: mockup result


class ConversationResponse(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime
