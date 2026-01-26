from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from enum import Enum


class RequestStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"


class ProjectRequestCreate(BaseModel):
    name: str
    email: str
    title: str
    description: Optional[str] = None


class ProjectRequestResponse(ProjectRequestCreate):
    id: int
    status: RequestStatus
    created_at: datetime

    class Config:
        from_attributes = True


class ProjectRequestUpdate(BaseModel):
    status: RequestStatus


class AdminLogin(BaseModel):
    username: str
    password: str
