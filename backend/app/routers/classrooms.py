from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.classroom import Classroom
from app.models.student import Student
from app.models.attention import AttentionRecord
from app.schemas.classroom import ClassroomCreate, ClassroomUpdate, ClassroomResponse

router = APIRouter(prefix="/api/classrooms", tags=["Classrooms"])


def _format_classroom(cls: Classroom, db: Session) -> ClassroomResponse:
    student_count = db.query(Student).filter(Student.classroom_id == cls.id).count()
    occupancy = round((student_count / cls.capacity * 100), 1) if cls.capacity > 0 else 0.0

    # Calculate average attention score from attention_records
    avg_attention = db.query(func.avg(AttentionRecord.attention_score)).filter(
        AttentionRecord.classroom_id == cls.id
    ).scalar()

    return ClassroomResponse(
        id=cls.id,
        name=cls.name,
        department=cls.department,
        capacity=cls.capacity,
        status=cls.status,
        students_count=student_count,
        average_attention=round(float(avg_attention), 1) if avg_attention is not None else 85.0,
        occupancy_rate=occupancy,
        created_at=cls.created_at,
        updated_at=cls.updated_at,
    )


@router.get("", response_model=List[ClassroomResponse])
def get_classrooms(
    department: Optional[str] = Query(None, description="Filter by department"),
    status: Optional[str] = Query(None, description="Filter by status (Active/Inactive)"),
    db: Session = Depends(get_db),
):
    """
    List all classrooms with real-time occupancy and attention metrics.
    """
    query = db.query(Classroom)
    if department:
        query = query.filter(Classroom.department == department)
    if status:
        query = query.filter(Classroom.status == status)

    classrooms = query.order_by(Classroom.name.asc()).all()
    return [_format_classroom(c, db) for c in classrooms]


@router.get("/{id}", response_model=ClassroomResponse)
def get_classroom(id: int, db: Session = Depends(get_db)):
    """
    Get classroom profile by ID.
    """
    classroom = db.query(Classroom).filter(Classroom.id == id).first()
    if not classroom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Classroom with ID {id} not found.",
        )
    return _format_classroom(classroom, db)


@router.post("", response_model=ClassroomResponse, status_code=status.HTTP_201_CREATED)
def create_classroom(cls_in: ClassroomCreate, db: Session = Depends(get_db)):
    """
    Create a new classroom.
    """
    existing = db.query(Classroom).filter(Classroom.name == cls_in.name.strip()).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Classroom '{cls_in.name}' already exists.",
        )

    classroom = Classroom(
        name=cls_in.name.strip(),
        department=cls_in.department.strip(),
        capacity=cls_in.capacity or 30,
        status=cls_in.status or "Active",
    )
    db.add(classroom)
    db.commit()
    db.refresh(classroom)

    return _format_classroom(classroom, db)


@router.put("/{id}", response_model=ClassroomResponse)
def update_classroom(id: int, update_in: ClassroomUpdate, db: Session = Depends(get_db)):
    """
    Update classroom details.
    """
    classroom = db.query(Classroom).filter(Classroom.id == id).first()
    if not classroom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Classroom with ID {id} not found.",
        )

    if update_in.name and update_in.name != classroom.name:
        existing = db.query(Classroom).filter(Classroom.name == update_in.name.strip()).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Classroom name '{update_in.name}' is already taken.",
            )
        classroom.name = update_in.name.strip()

    if update_in.department is not None:
        classroom.department = update_in.department.strip()
    if update_in.capacity is not None:
        classroom.capacity = update_in.capacity
    if update_in.status is not None:
        classroom.status = update_in.status

    db.commit()
    db.refresh(classroom)
    return _format_classroom(classroom, db)


@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_classroom(id: int, db: Session = Depends(get_db)):
    """
    Delete a classroom by ID.
    """
    classroom = db.query(Classroom).filter(Classroom.id == id).first()
    if not classroom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Classroom with ID {id} not found.",
        )

    db.delete(classroom)
    db.commit()
    return {"success": True, "message": f"Classroom ID {id} deleted successfully."}
