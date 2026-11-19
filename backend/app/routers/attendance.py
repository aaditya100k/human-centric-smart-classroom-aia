from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.attendance import AttendanceCreate, AttendanceUpdate, AttendanceResponse, AttendanceSummary, FaceAttendanceRequest
from app.services.attendance_service import AttendanceService
from app.utils.security import get_current_user

router = APIRouter(prefix="/api/attendance", tags=["Attendance"])


@router.get("", response_model=List[AttendanceResponse])
def get_attendance(
    target_date: Optional[date] = Query(None, alias="date", description="Filter by date (YYYY-MM-DD)"),
    student_id: Optional[str] = Query(None, description="Filter by student ID"),
    classroom_id: Optional[int] = Query(None, description="Filter by classroom ID"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status (Present, Absent, Late)"),
    department: Optional[str] = Query(None, description="Filter by student department"),
    search: Optional[str] = Query(None, description="Search by student name, ID, or room name"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """
    List attendance records with optional filtering by date, student, classroom, status, department, or search.
    """
    return AttendanceService.get_attendance_list(
        db=db,
        target_date=target_date,
        student_id=student_id,
        classroom_id=classroom_id,
        status_filter=status_filter,
        department=department,
        search=search,
        limit=limit,
        offset=offset,
    )


@router.get("/today", response_model=AttendanceSummary)
def get_today_attendance(db: Session = Depends(get_db)):
    """
    Get summary and records of attendance for today.
    """
    return AttendanceService.get_today_summary(db=db)


@router.get("/student/{student_id}", response_model=List[AttendanceResponse])
def get_student_attendance(student_id: str, db: Session = Depends(get_db)):
    """
    Get full attendance history for a specific student.
    """
    return AttendanceService.get_student_attendance(db=db, student_id=student_id)


@router.post("", response_model=AttendanceResponse, status_code=status.HTTP_201_CREATED)
def record_attendance(data: AttendanceCreate, db: Session = Depends(get_db)):
    """
    Record attendance with validation and duplicate prevention (for student + classroom + date).
    """
    return AttendanceService.record_attendance(db=db, data=data)


@router.post("/face", status_code=status.HTTP_200_OK)
def record_face_attendance_endpoint(
    data: FaceAttendanceRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Record automatic Face AI attendance for a recognized student.
    Enforces JWT authentication and duplicate prevention.
    """
    from fastapi import HTTPException
    res = AttendanceService.record_face_attendance(
        db=db,
        student_id=data.student_id,
        classroom_id=data.classroom_id,
        confidence=data.confidence or 0.87
    )
    if res.get("status") == "rejected":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=res.get("detail", "Automatic face attendance failed.")
        )
    return res


@router.put("/{attendance_id}", response_model=AttendanceResponse)
def update_attendance(attendance_id: int, data: AttendanceUpdate, db: Session = Depends(get_db)):
    """
    Update an attendance record (status, confidence, verification method, classroom).
    """
    return AttendanceService.update_attendance(db=db, attendance_id=attendance_id, data=data)


@router.delete("/{attendance_id}", response_model=dict)
def delete_attendance(attendance_id: int, db: Session = Depends(get_db)):
    """
    Delete an attendance record by ID.
    """
    return AttendanceService.delete_attendance(db=db, attendance_id=attendance_id)


