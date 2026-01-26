from enum import Enum
from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from database import Base

# Request status model
class RequestStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"

# Project request model
class ProjectRequest(Base):
    __tablename__ = "project_requests"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    title = Column(String, nullable=False)
    description = Column(String)
    status = Column(String, default=RequestStatus.pending.value)
    created_at = Column(DateTime, default=datetime.utcnow)

# Admin model
class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
