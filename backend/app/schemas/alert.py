from datetime import datetime
from typing import Optional
# pyrefly: ignore [missing-import]
from pydantic import BaseModel, ConfigDict


class AlertBase(BaseModel):
    title: str
    message: str
    category: Optional[str] = "System"  # "Attendance", "Emotion", "Attention", "Temperature", "System"
    severity: Optional[str] = "Medium"  # "Low", "Medium", "High", "Critical"
    classroom_id: Optional[int] = None
    student_id: Optional[str] = None


class AlertCreate(AlertBase):
    pass


class AlertUpdate(BaseModel):
    is_resolved: Optional[bool] = None
    severity: Optional[str] = None
    title: Optional[str] = None
    message: Optional[str] = None


class AlertResponse(AlertBase):
    id: int
    is_resolved: bool
    resolved_at: Optional[datetime] = None
    created_at: datetime
    classroom_name: Optional[str] = None
    student_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
