from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.analytics_service import AnalyticsService
from app.schemas.emotion import EmotionAnalyticsResponse
from app.schemas.attention import AttentionAnalyticsResponse
from app.schemas.temperature import TemperatureAnalyticsResponse

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


@router.get("/attendance")
def get_attendance_analytics(
    classroom_id: Optional[int] = Query(None, description="Optional classroom filter"),
    db: Session = Depends(get_db),
):
    """
    Get aggregated attendance analytics, percentages, and 7-day daily trends.
    """
    return AnalyticsService.get_attendance_analytics(db, classroom_id=classroom_id)


@router.get("/emotion", response_model=EmotionAnalyticsResponse)
def get_emotion_analytics(
    classroom_id: Optional[int] = Query(None, description="Optional classroom filter"),
    db: Session = Depends(get_db),
):
    """
    Get emotion distribution breakdown (Happy, Neutral, Focused, Stressed, etc.) and engagement score.
    """
    return AnalyticsService.get_emotion_analytics(db, classroom_id=classroom_id)


@router.get("/attention", response_model=AttentionAnalyticsResponse)
def get_attention_analytics(
    classroom_id: Optional[int] = Query(None, description="Optional classroom filter"),
    db: Session = Depends(get_db),
):
    """
    Get classroom attention scores, status distribution (Focused vs Distracted vs Drowsy).
    """
    return AnalyticsService.get_attention_analytics(db, classroom_id=classroom_id)


@router.get("/temperature", response_model=TemperatureAnalyticsResponse)
def get_temperature_analytics(
    classroom_id: Optional[int] = Query(None, description="Optional classroom filter"),
    db: Session = Depends(get_db),
):
    """
    Get classroom thermal metrics, fever alerts, and recent sensor readings.
    """
    return AnalyticsService.get_temperature_analytics(db, classroom_id=classroom_id)


@router.get("/dashboard")
def get_dashboard_kpis(db: Session = Depends(get_db)):
    """
    Consolidated KPI overview for top-level dashboard:
    total students, active rooms, today's attendance rate, active alerts, and recent activity.
    """
    return AnalyticsService.get_dashboard_summary(db)
