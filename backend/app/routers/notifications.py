from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.notification import Notification
from app.schemas.notification import NotificationCreate, NotificationResponse

router = APIRouter(prefix="/api/notifications", tags=["Notifications"])


@router.get("", response_model=List[NotificationResponse])
def get_notifications(
    category: Optional[str] = Query(None, description="Filter by category (Alert, System, Warning)"),
    is_read: Optional[bool] = Query(None, description="Filter by read state"),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """
    List notifications ordered from most recent to oldest.
    """
    query = db.query(Notification)
    if category:
        query = query.filter(Notification.category == category)
    if is_read is not None:
        query = query.filter(Notification.is_read == is_read)

    notifications = query.order_by(Notification.created_at.desc()).limit(limit).all()
    return notifications


@router.post("", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
def create_notification(notif_in: NotificationCreate, db: Session = Depends(get_db)):
    """
    Post a new system notification.
    """
    notification = Notification(
        title=notif_in.title.strip(),
        message=notif_in.message.strip(),
        category=notif_in.category or "System",
        user_id=notif_in.user_id,
        is_read=False,
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification


@router.put("/{id}/read", response_model=NotificationResponse)
def mark_notification_read(id: int, db: Session = Depends(get_db)):
    """
    Mark a specific notification as read.
    """
    notif = db.query(Notification).filter(Notification.id == id).first()
    if not notif:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Notification ID {id} not found.",
        )

    notif.is_read = True
    db.commit()
    db.refresh(notif)
    return notif


@router.put("/read-all", status_code=status.HTTP_200_OK)
def mark_all_read(db: Session = Depends(get_db)):
    """
    Mark all unread notifications as read.
    """
    db.query(Notification).filter(Notification.is_read == False).update({"is_read": True})
    db.commit()
    return {"success": True, "message": "All notifications marked as read."}
