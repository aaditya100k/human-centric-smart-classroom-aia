from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class ClassroomBase(BaseModel):
    name: str  # e.g., "Room 101"
    department: str  # e.g., "Science"
    capacity: Optional[int] = 30
    status: Optional[str] = "Active"


class ClassroomCreate(ClassroomBase):
    pass


class ClassroomUpdate(BaseModel):
    name: Optional[str] = None
    department: Optional[str] = None
    capacity: Optional[int] = None
    status: Optional[str] = None


class ClassroomResponse(ClassroomBase):
    id: int
    students_count: Optional[int] = 0
    average_attention: Optional[float] = 85.0
    occupancy_rate: Optional[float] = 0.0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
