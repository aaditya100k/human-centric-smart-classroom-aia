from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.alert import Alert
from app.models.classroom import Classroom
from app.models.student import Student
from app.schemas.alert import AlertCreate, AlertUpdate, AlertResponse

router = APIRouter(prefix="/api/alerts", tags=["Alerts"])


def _format_alert(a: Alert) -> AlertResponse:
    return AlertResponse(
        id=a.id,
        title=a.title,
        message=a.message,
        category=a.category,
        severity=a.severity,
        classroom_id=a.classroom_id,
        student_id=a.student_id,
        is_resolved=a.is_resolved,
        resolved_at=a.resolved_at,
        created_at=a.created_at,
        classroom_name=a.classroom.name if a.classroom else None,
        student_name=a.student.name if a.student else None,
    )


@router.get("", response_model=List[AlertResponse])
def get_alerts(
    category: Optional[str] = Query(None, description="Filter by category"),
    severity: Optional[str] = Query(None, description="Filter by severity (Low, Medium, High, Critical)"),
    is_resolved: Optional[bool] = Query(None, description="Filter by resolved status"),
    classroom_id: Optional[int] = Query(None, description="Filter by classroom ID"),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """
    List alerts with optional filtering.
    """
    query = db.query(Alert)
    if category:
        query = query.filter(Alert.category == category)
    if severity:
        query = query.filter(Alert.severity == severity)
    if is_resolved is not None:
        query = query.filter(Alert.is_resolved == is_resolved)
    if classroom_id:
        query = query.filter(Alert.classroom_id == classroom_id)

    alerts = query.order_by(Alert.created_at.desc()).limit(limit).all()
    return [_format_alert(a) for a in alerts]


@router.post("", response_model=AlertResponse, status_code=status.HTTP_201_CREATED)
def create_alert(alert_in: AlertCreate, db: Session = Depends(get_db)):
    """
    Create a new system or sensor alert.
    """
    if alert_in.classroom_id:
        cls = db.query(Classroom).filter(Classroom.id == alert_in.classroom_id).first()
        if not cls:
            raise HTTPException(status_code=400, detail="Referenced classroom does not exist.")

    if alert_in.student_id:
        st = db.query(Student).filter(Student.id == alert_in.student_id).first()
        if not st:
            raise HTTPException(status_code=400, detail="Referenced student does not exist.")

    alert = Alert(
        title=alert_in.title.strip(),
        message=alert_in.message.strip(),
        category=alert_in.category or "System",
        severity=alert_in.severity or "Medium",
        classroom_id=alert_in.classroom_id,
        student_id=alert_in.student_id,
        is_resolved=False,
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)

    return _format_alert(alert)


@router.put("/{id}", response_model=AlertResponse)
def update_alert(id: int, update_in: AlertUpdate, db: Session = Depends(get_db)):
    """
    Update or resolve an alert by ID.
    """
    alert = db.query(Alert).filter(Alert.id == id).first()
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert with ID {id} not found.",
        )

    if update_in.is_resolved is not None:
        alert.is_resolved = update_in.is_resolved
        if update_in.is_resolved:
            alert.resolved_at = datetime.now(timezone.utc)
        else:
            alert.resolved_at = None

    if update_in.severity is not None:
        alert.severity = update_in.severity
    if update_in.title is not None:
        alert.title = update_in.title.strip()
    if update_in.message is not None:
        alert.message = update_in.message.strip()

    db.commit()
    db.refresh(alert)
    return _format_alert(alert)
