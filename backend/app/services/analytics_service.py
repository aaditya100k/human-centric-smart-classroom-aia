from datetime import date, datetime, timedelta
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.student import Student
from app.models.classroom import Classroom
from app.models.attendance import Attendance
from app.models.emotion import EmotionRecord
from app.models.attention import AttentionRecord
from app.models.temperature import TemperatureRecord
from app.models.alert import Alert
from app.models.notification import Notification

from app.schemas.emotion import EmotionAnalyticsResponse
from app.schemas.attention import AttentionAnalyticsResponse
from app.schemas.temperature import TemperatureAnalyticsResponse, TemperatureRecordResponse


class AnalyticsService:
    @staticmethod
    def get_attendance_analytics(db: Session, classroom_id: Optional[int] = None) -> Dict[str, Any]:
        query = db.query(Attendance)
        if classroom_id:
            query = query.filter(Attendance.classroom_id == classroom_id)

        total_records = query.count()
        present_count = query.filter(Attendance.status == "Present").count()
        absent_count = query.filter(Attendance.status == "Absent").count()
        late_count = query.filter(Attendance.status == "Late").count()

        avg_rate = round(((present_count + late_count) / total_records * 100), 1) if total_records > 0 else 0.0

        # Group by last 7 days
        seven_days_ago = date.today() - timedelta(days=7)
        daily_query = db.query(
            Attendance.date,
            func.count(Attendance.id).label("total"),
            func.sum(func.case((Attendance.status == "Present", 1), else_=0)).label("present")
        ).filter(Attendance.date >= seven_days_ago)

        if classroom_id:
            daily_query = daily_query.filter(Attendance.classroom_id == classroom_id)

        daily_stats = daily_query.group_by(Attendance.date).order_by(Attendance.date).all()
        daily_trends = [
            {
                "date": str(row.date),
                "total": row.total,
                "present": int(row.present or 0),
                "rate": round((int(row.present or 0) / row.total * 100), 1) if row.total > 0 else 0.0
            }
            for row in daily_stats
        ]

        return {
            "total_records": total_records,
            "present_count": present_count,
            "absent_count": absent_count,
            "late_count": late_count,
            "overall_attendance_rate": avg_rate,
            "daily_trends": daily_trends,
        }

    @staticmethod
    def get_emotion_analytics(db: Session, classroom_id: Optional[int] = None) -> EmotionAnalyticsResponse:
        query = db.query(EmotionRecord)
        if classroom_id:
            query = query.filter(EmotionRecord.classroom_id == classroom_id)

        records = query.all()
        total_samples = len(records)

        distribution: Dict[str, int] = {
            "Happy": 0,
            "Neutral": 0,
            "Focused": 0,
            "Stressed": 0,
            "Bored": 0,
            "Sad": 0,
            "Surprised": 0,
        }

        total_engagement = 0.0
        for r in records:
            emo = r.dominant_emotion.capitalize() if r.dominant_emotion else "Neutral"
            distribution[emo] = distribution.get(emo, 0) + 1
            total_engagement += (r.engagement_level or 80.0)

        average_engagement = round(total_engagement / total_samples, 1) if total_samples > 0 else 80.0
        most_common = max(distribution, key=distribution.get) if total_samples > 0 else "Neutral"

        return EmotionAnalyticsResponse(
            distribution=distribution,
            average_engagement=average_engagement,
            total_samples=total_samples,
            most_common_emotion=most_common,
        )

    @staticmethod
    def get_attention_analytics(db: Session, classroom_id: Optional[int] = None) -> AttentionAnalyticsResponse:
        query = db.query(AttentionRecord)
        if classroom_id:
            query = query.filter(AttentionRecord.classroom_id == classroom_id)

        records = query.all()
        total_records = len(records)

        distribution: Dict[str, int] = {
            "Focused": 0,
            "Distracted": 0,
            "Drowsy": 0,
        }

        total_score = 0.0
        for r in records:
            status = r.status.capitalize() if r.status else "Focused"
            distribution[status] = distribution.get(status, 0) + 1
            total_score += (r.attention_score or 85.0)

        average_score = round(total_score / total_records, 1) if total_records > 0 else 85.0

        return AttentionAnalyticsResponse(
            average_score=average_score,
            status_distribution=distribution,
            focused_count=distribution.get("Focused", 0),
            distracted_count=distribution.get("Distracted", 0),
            drowsy_count=distribution.get("Drowsy", 0),
            total_records=total_records,
        )

    @staticmethod
    def get_temperature_analytics(db: Session, classroom_id: Optional[int] = None) -> TemperatureAnalyticsResponse:
        query = db.query(TemperatureRecord)
        if classroom_id:
            query = query.filter(TemperatureRecord.classroom_id == classroom_id)

        records = query.order_by(TemperatureRecord.timestamp.desc()).all()
        total_readings = len(records)

        if total_readings > 0:
            temps = [r.temperature for r in records]
            avg_temp = round(sum(temps) / total_readings, 1)
            min_temp = round(min(temps), 1)
            max_temp = round(max(temps), 1)
            fever_count = sum(1 for r in records if r.is_fever or r.temperature >= 37.5)
        else:
            avg_temp = 36.6
            min_temp = 36.2
            max_temp = 37.1
            fever_count = 0

        recent_readings = [
            TemperatureRecordResponse(
                id=r.id,
                classroom_id=r.classroom_id,
                student_id=r.student_id,
                temperature=r.temperature,
                unit=r.unit,
                sensor_id=r.sensor_id,
                is_fever=r.is_fever,
                timestamp=r.timestamp,
                student_name=r.student.name if r.student else None,
            )
            for r in records[:10]
        ]

        return TemperatureAnalyticsResponse(
            average_temperature=avg_temp,
            min_temperature=min_temp,
            max_temperature=max_temp,
            fever_alerts_count=fever_count,
            total_readings=total_readings,
            recent_readings=recent_readings,
        )

    @staticmethod
    def get_dashboard_summary(db: Session) -> Dict[str, Any]:
        total_students = db.query(Student).count()
        total_classrooms = db.query(Classroom).count()
        active_classrooms = db.query(Classroom).filter(Classroom.status == "Active").count()
        
        # Today's attendance stats
        today = date.today()
        today_total = db.query(Attendance).filter(Attendance.date == today).count()
        today_present = db.query(Attendance).filter(
            Attendance.date == today,
            Attendance.status.in_(["Present", "Late"])
        ).count()
        today_attendance_rate = round((today_present / today_total * 100), 1) if today_total > 0 else 0.0

        # Unresolved active alerts
        active_alerts_count = db.query(Alert).filter(Alert.is_resolved == False).count()

        # Unread notifications
        unread_notifications_count = db.query(Notification).filter(Notification.is_read == False).count()

        # Recent activities (from notifications and alerts)
        recent_notifications = db.query(Notification).order_by(
            Notification.created_at.desc()
        ).limit(5).all()

        recent_activities = [
            {
                "id": n.id,
                "title": n.title,
                "message": n.message,
                "category": n.category,
                "created_at": n.created_at.isoformat() if n.created_at else None,
                "is_read": n.is_read,
            }
            for n in recent_notifications
        ]

        return {
            "total_students": total_students,
            "total_classrooms": total_classrooms,
            "active_classrooms": active_classrooms,
            "active_classrooms_display": f"{active_classrooms}/{total_classrooms}",
            "today_attendance_rate": today_attendance_rate,
            "active_alerts_count": active_alerts_count,
            "unread_notifications_count": unread_notifications_count,
            "recent_activities": recent_activities,
        }
