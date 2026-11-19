from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class TemperatureRecordBase(BaseModel):
    classroom_id: int
    student_id: Optional[str] = None
    temperature: float  # e.g., 36.5
    unit: Optional[str] = "C"
    sensor_id: Optional[str] = "ESP32-01"
    is_fever: Optional[bool] = False


class TemperatureRecordCreate(TemperatureRecordBase):
    pass


class TemperatureRecordResponse(TemperatureRecordBase):
    id: int
    timestamp: datetime
    student_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class TemperatureAnalyticsResponse(BaseModel):
    average_temperature: float
    min_temperature: float
    max_temperature: float
    fever_alerts_count: int
    total_readings: int
    recent_readings: List[TemperatureRecordResponse]
