import datetime as dt
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class AttendanceBase(BaseModel):
    student_id: str
    classroom_id: Optional[int] = None
    status: Optional[str] = "Present"  # "Present", "Absent", "Late", "Excused"
    verification_method: Optional[str] = "Face AI"  # "Face AI", "Manual", "Biometric"
    confidence: Optional[float] = 0.95


class AttendanceCreate(AttendanceBase):
    date: Optional[dt.date] = None
    timestamp: Optional[dt.datetime] = None


class AttendanceUpdate(BaseModel):
    status: Optional[str] = None
    verification_method: Optional[str] = None
    confidence: Optional[float] = None
    classroom_id: Optional[int] = None


class AttendanceResponse(AttendanceBase):
    id: int
    date: dt.date
    timestamp: dt.datetime
    student_name: Optional[str] = None
    classroom_name: Optional[str] = None
    student_department: Optional[str] = None
    attendance_rate: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)


class AttendanceSummary(BaseModel):
    total_records: int
    total_students: Optional[int] = None
    present_count: int
    absent_count: int
    late_count: int
    attendance_rate: float
    records: List[AttendanceResponse]


class FaceAttendanceRequest(BaseModel):
    student_id: str
    classroom_id: int
    confidence: Optional[float] = 0.87



