from datetime import datetime
from typing import Optional, Dict
from pydantic import BaseModel, ConfigDict


class AttentionRecordBase(BaseModel):
    classroom_id: int
    student_id: Optional[str] = None
    attention_score: Optional[float] = 85.0
    status: Optional[str] = "Focused"  # "Focused", "Distracted", "Drowsy"
    gaze_direction: Optional[str] = "Forward"
    head_pose: Optional[str] = "Upright"


class AttentionRecordCreate(AttentionRecordBase):
    pass


class AttentionRecordResponse(AttentionRecordBase):
    id: int
    timestamp: datetime
    student_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class AttentionAnalyticsResponse(BaseModel):
    average_score: float
    status_distribution: Dict[str, int]
    distracted_count: int
    focused_count: int
    drowsy_count: int
    total_records: int
