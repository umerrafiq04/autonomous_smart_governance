from pydantic import BaseModel
from datetime import datetime
from typing import Optional


# =========================
# Complaint Create Schema
# =========================
class ComplaintCreate(BaseModel):
    title: str
    description: str


# =========================
# Complaint Response Schema
# =========================
class ComplaintResponse(BaseModel):
    id: int
    title: str
    description: str
    issue_type: Optional[str] = None
    severity: Optional[str] = None
    department: Optional[str] = None
    status: Optional[str] = None
    eta: Optional[str] = None
    image_path: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# =========================
# Chat Message Create Schema
# =========================
class ChatMessageCreate(BaseModel):
    complaint_id: int
    sender: str
    message: str


# =========================
# Chat Message Response Schema
# =========================
class ChatMessageResponse(BaseModel):
    id: int
    complaint_id: int
    sender: str
    message: str
    created_at: datetime

    class Config:
        from_attributes = True