from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.student import Student
from app.models.classroom import Classroom
from app.schemas.student import StudentCreate, StudentUpdate, StudentResponse
from app.services.attendance_service import AttendanceService

router = APIRouter(prefix="/api/students", tags=["Students"])


def _format_student(student: Student, db: Session) -> StudentResponse:
    rate = AttendanceService.calculate_student_rate(db, student.id)
    return StudentResponse(
        id=student.id,
        name=student.name,
        email=student.email,
        department=student.department,
        classroom_id=student.classroom_id,
        classroom_name=student.classroom.name if student.classroom else None,
        status=student.status,
        attendance_rate=rate,
        created_at=student.created_at,
        updated_at=student.updated_at,
    )


@router.get("", response_model=List[StudentResponse])
def get_students(
    search: Optional[str] = Query(None, description="Search by student name or ID"),
    department: Optional[str] = Query(None, description="Filter by department"),
    classroom_id: Optional[int] = Query(None, description="Filter by classroom ID"),
    status: Optional[str] = Query(None, description="Filter by status (Active/Inactive)"),
    db: Session = Depends(get_db),
):
    """
    List all students with optional filters for search, department, and classroom.
    """
    query = db.query(Student)

    if search:
        search_pattern = f"%{search}%"
        query = query.filter((Student.name.ilike(search_pattern)) | (Student.id.ilike(search_pattern)))
    if department:
        query = query.filter(Student.department == department)
    if classroom_id:
        query = query.filter(Student.classroom_id == classroom_id)
    if status:
        query = query.filter(Student.status == status)

    students = query.order_by(Student.name.asc()).all()
    return [_format_student(s, db) for s in students]


@router.get("/{id}", response_model=StudentResponse)
def get_student(id: str, db: Session = Depends(get_db)):
    """
    Get detailed student profile by student ID (e.g. 'ST-2024-001').
    """
    student = db.query(Student).filter(Student.id == id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID '{id}' was not found.",
        )
    return _format_student(student, db)


@router.post("", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
def create_student(student_in: StudentCreate, db: Session = Depends(get_db)):
    """
    Register a new student.
    """
    existing_id = db.query(Student).filter(Student.id == student_in.id).first()
    if existing_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Student ID '{student_in.id}' already exists.",
        )

    existing_email = db.query(Student).filter(Student.email == student_in.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Email '{student_in.email}' is already registered to another student.",
        )

    if student_in.classroom_id:
        cls = db.query(Classroom).filter(Classroom.id == student_in.classroom_id).first()
        if not cls:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Classroom with ID {student_in.classroom_id} does not exist.",
            )

    student = Student(
        id=student_in.id.strip().upper(),
        name=student_in.name.strip(),
        email=student_in.email.strip().lower(),
        department=student_in.department.strip(),
        classroom_id=student_in.classroom_id,
        status=student_in.status or "Active",
    )
    db.add(student)
    db.commit()
    db.refresh(student)

    return _format_student(student, db)


@router.put("/{id}", response_model=StudentResponse)
def update_student(id: str, update_in: StudentUpdate, db: Session = Depends(get_db)):
    """
    Update an existing student's details.
    """
    student = db.query(Student).filter(Student.id == id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID '{id}' was not found.",
        )

    if update_in.email and update_in.email != student.email:
        existing = db.query(Student).filter(Student.email == update_in.email).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Email '{update_in.email}' is already taken.",
            )
        student.email = update_in.email

    if update_in.name is not None:
        student.name = update_in.name
    if update_in.department is not None:
        student.department = update_in.department
    if update_in.classroom_id is not None:
        if update_in.classroom_id > 0:
            cls = db.query(Classroom).filter(Classroom.id == update_in.classroom_id).first()
            if not cls:
                raise HTTPException(status_code=400, detail="Invalid classroom ID.")
            student.classroom_id = update_in.classroom_id
        else:
            student.classroom_id = None
    if update_in.status is not None:
        student.status = update_in.status

    db.commit()
    db.refresh(student)
    return _format_student(student, db)


@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_student(id: str, db: Session = Depends(get_db)):
    """
    Delete a student by ID.
    """
    student = db.query(Student).filter(Student.id == id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID '{id}' was not found.",
        )

    db.delete(student)
    db.commit()
    return {"success": True, "message": f"Student '{id}' deleted successfully."}
