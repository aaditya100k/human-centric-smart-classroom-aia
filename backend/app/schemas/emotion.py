from datetime import datetime
from typing import Optional, Dict
from pydantic import BaseModel, ConfigDict


class EmotionRecordBase(BaseModel):
    classroom_id: int
    student_id: Optional[str] = None
    dominant_emotion: Optional[str] = "Neutral"
    confidence: Optional[float] = 0.85
    engagement_level: Optional[float] = 80.0
    raw_scores: Optional[str] = None


class EmotionRecordCreate(EmotionRecordBase):
    pass


class EmotionRecordResponse(EmotionRecordBase):
    id: int
    timestamp: datetime
    student_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class EmotionAnalyticsResponse(BaseModel):
    distribution: Dict[str, int]
    average_engagement: float
    total_samples: int
    most_common_emotion: str
