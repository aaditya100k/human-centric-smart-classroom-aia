"""
API route definitions organized by domain.
"""
from app.routers.auth import router as auth_router
from app.routers.students import router as students_router
from app.routers.classrooms import router as classrooms_router
from app.routers.attendance import router as attendance_router
from app.routers.monitoring import router as monitoring_router
from app.routers.face_recognition import router as face_recognition_router
from app.routers.analytics import router as analytics_router
from app.routers.alerts import router as alerts_router
from app.routers.notifications import router as notifications_router

__all__ = [
    "auth_router",
    "students_router",
    "classrooms_router",
    "attendance_router",
    "monitoring_router",
    "face_recognition_router",
    "analytics_router",
    "alerts_router",
    "notifications_router",
]
