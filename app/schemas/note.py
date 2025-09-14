from pydantic import BaseModel
from enum import Enum
from typing import Optional
from datetime import datetime


class NoteStatus(str, Enum):
    queued = "queued"
    processing = "processing"
    done = "done"
    failed = "failed"


class NoteCreate(BaseModel):
    raw_text: str
    idempotency_key: Optional[str] = None



class NoteOut(BaseModel):
    id: int
    raw_text: str
    summary: Optional[str]
    status: NoteStatus
    attempts: int               # 🔹 yeni
    last_error: Optional[str]   # 🔹 yeni
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
