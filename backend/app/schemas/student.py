from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict


class StudentBase(BaseModel):
    id: str  # e.g., "ST-2024-001"
    name: str
    email: EmailStr
    department: str
    classroom_id: Optional[int] = None
    status: Optional[str] = "Active"


class StudentCreate(StudentBase):
    pass


class StudentUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    department: Optional[str] = None
    classroom_id: Optional[int] = None
    status: Optional[str] = None


class StudentResponse(StudentBase):
    classroom_name: Optional[str] = None
    attendance_rate: Optional[float] = 100.0
    profile_photo_path: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
