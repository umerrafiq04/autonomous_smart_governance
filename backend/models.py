from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime

from backend.database import Base


class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String, nullable=False)

    description = Column(Text, nullable=False)

    issue_type = Column(String, nullable=True)

    severity = Column(String, nullable=True)

    department = Column(String, nullable=True)

    status = Column(String, default="Pending")

    eta = Column(String, nullable=True)

    image_path = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)

    complaint_id = Column(Integer, nullable=False)

    sender = Column(String, nullable=False)

    message = Column(Text, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)