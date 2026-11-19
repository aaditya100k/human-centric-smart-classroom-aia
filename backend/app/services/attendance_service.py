from datetime import date, datetime
from typing import Optional, List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.attendance import Attendance
from app.models.student import Student
from app.models.classroom import Classroom
from app.schemas.attendance import AttendanceCreate, AttendanceUpdate, AttendanceResponse, AttendanceSummary


class AttendanceService:
    @staticmethod
    def record_attendance(db: Session, data: AttendanceCreate) -> AttendanceResponse:
        record_date = data.date or date.today()
        record_timestamp = data.timestamp or datetime.now()

        # Validate student exists
        student = db.query(Student).filter(Student.id == data.student_id).first()
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Student with ID '{data.student_id}' does not exist."
            )

        # Validate classroom if provided
        classroom = None
        if data.classroom_id is not None:
            classroom = db.query(Classroom).filter(Classroom.id == data.classroom_id).first()
            if not classroom:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Classroom with ID '{data.classroom_id}' does not exist."
                )

        # Check duplicate attendance for the same student + classroom + date
        dup_query = db.query(Attendance).filter(
            Attendance.student_id == data.student_id,
            Attendance.date == record_date
        )
        if data.classroom_id is not None:
            dup_query = dup_query.filter(
                (Attendance.classroom_id == data.classroom_id) | (Attendance.classroom_id.is_(None))
            )

        existing = dup_query.first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Attendance record already exists for student '{data.student_id}' on {record_date}."
            )

        # Create new record
        record = Attendance(
            student_id=data.student_id,
            classroom_id=data.classroom_id,
            date=record_date,
            timestamp=record_timestamp,
            status=data.status or "Present",
            verification_method=data.verification_method or "Face AI",
            confidence=data.confidence if data.confidence is not None else 0.95,
        )
        db.add(record)
        db.commit()
        db.refresh(record)

        student_rate = AttendanceService.calculate_student_rate(db, record.student_id)

        return AttendanceResponse(
            id=record.id,
            student_id=record.student_id,
            classroom_id=record.classroom_id,
            date=record.date,
            timestamp=record.timestamp,
            status=record.status,
            verification_method=record.verification_method,
            confidence=record.confidence,
            student_name=student.name,
            classroom_name=classroom.name if classroom else (record.classroom.name if record.classroom else None),
            student_department=student.department,
            attendance_rate=student_rate,
        )

    @staticmethod
    def get_attendance_list(
        db: Session,
        target_date: Optional[date] = None,
        student_id: Optional[str] = None,
        classroom_id: Optional[int] = None,
        status_filter: Optional[str] = None,
        department: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[AttendanceResponse]:
        query = db.query(Attendance).join(Student, Attendance.student_id == Student.id, isouter=True).join(Classroom, Attendance.classroom_id == Classroom.id, isouter=True)
        
        if target_date:
            query = query.filter(Attendance.date == target_date)
        if student_id:
            query = query.filter(Attendance.student_id == student_id)
        if classroom_id:
            query = query.filter(Attendance.classroom_id == classroom_id)
        if status_filter and status_filter != "All":
            query = query.filter(Attendance.status == status_filter)
        if department and department != "All":
            query = query.filter(Student.department == department)
        if search:
            search_pattern = f"%{search.strip()}%"
            query = query.filter(
                (Student.name.ilike(search_pattern)) |
                (Student.id.ilike(search_pattern)) |
                (Classroom.name.ilike(search_pattern))
            )

        records = query.order_by(Attendance.timestamp.desc()).offset(offset).limit(limit).all()

        responses = []
        for r in records:
            student_rate = AttendanceService.calculate_student_rate(db, r.student_id)
            responses.append(AttendanceResponse(
                id=r.id,
                student_id=r.student_id,
                classroom_id=r.classroom_id,
                date=r.date,
                timestamp=r.timestamp,
                status=r.status,
                verification_method=r.verification_method,
                confidence=r.confidence,
                student_name=r.student.name if r.student else None,
                classroom_name=r.classroom.name if r.classroom else None,
                student_department=r.student.department if r.student else None,
                attendance_rate=student_rate,
            ))
        return responses

    @staticmethod
    def get_student_attendance(db: Session, student_id: str) -> List[AttendanceResponse]:
        return AttendanceService.get_attendance_list(db, student_id=student_id, limit=365)

    @staticmethod
    def get_today_summary(db: Session) -> AttendanceSummary:
        today = date.today()
        records = AttendanceService.get_attendance_list(db, target_date=today, limit=1000)
        total_students = db.query(Student).count()
        
        total_records = len(records)
        present = sum(1 for r in records if r.status == "Present")
        absent = sum(1 for r in records if r.status == "Absent")
        late = sum(1 for r in records if r.status == "Late")
        
        # Calculate rate based on total students if available, else total records
        base_count = total_students if total_students > 0 else total_records
        rate = round((present / base_count * 100), 1) if base_count > 0 else 0.0

        return AttendanceSummary(
            total_records=total_records,
            total_students=total_students,
            present_count=present,
            absent_count=absent,
            late_count=late,
            attendance_rate=rate,
            records=records,
        )

    @staticmethod
    def update_attendance(db: Session, attendance_id: int, data: AttendanceUpdate) -> AttendanceResponse:
        record = db.query(Attendance).filter(Attendance.id == attendance_id).first()
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Attendance record with ID {attendance_id} not found."
            )

        if data.status is not None:
            record.status = data.status
        if data.verification_method is not None:
            record.verification_method = data.verification_method
        if data.confidence is not None:
            record.confidence = data.confidence
        if data.classroom_id is not None:
            record.classroom_id = data.classroom_id

        db.commit()
        db.refresh(record)

        student_rate = AttendanceService.calculate_student_rate(db, record.student_id)

        return AttendanceResponse(
            id=record.id,
            student_id=record.student_id,
            classroom_id=record.classroom_id,
            date=record.date,
            timestamp=record.timestamp,
            status=record.status,
            verification_method=record.verification_method,
            confidence=record.confidence,
            student_name=record.student.name if record.student else None,
            classroom_name=record.classroom.name if record.classroom else None,
            student_department=record.student.department if record.student else None,
            attendance_rate=student_rate,
        )

    @staticmethod
    def delete_attendance(db: Session, attendance_id: int) -> dict:
        record = db.query(Attendance).filter(Attendance.id == attendance_id).first()
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Attendance record with ID {attendance_id} not found."
            )
        db.delete(record)
        db.commit()
        return {"message": f"Attendance record {attendance_id} deleted successfully."}

    @staticmethod
    def calculate_student_rate(db: Session, student_id: str) -> float:
        total = db.query(Attendance).filter(Attendance.student_id == student_id).count()
        if total == 0:
            return 100.0  # Default initial rate
        present_or_late = db.query(Attendance).filter(
            Attendance.student_id == student_id,
            Attendance.status.in_(["Present", "Late"])
        ).count()
        return round((present_or_late / total) * 100, 1)

    @staticmethod
    def record_face_attendance(
        db: Session,
        student_id: str,
        classroom_id: int,
        confidence: float = 0.87
    ) -> dict:
        """
        Record automatic Face AI attendance for a recognized student.
        Prevents duplicate records for the same student + date.
        Does NOT overwrite existing manual attendance.
        """
        if not student_id:
            return {"status": "rejected", "detail": "Student ID is required."}

        if classroom_id is None:
            return {"status": "rejected", "detail": "Classroom ID is required for automatic attendance."}

        # 1. Validate student exists
        student = db.query(Student).filter(Student.id == student_id).first()
        if not student:
            return {"status": "rejected", "detail": f"Student with ID '{student_id}' does not exist."}

        # 2. Validate classroom exists
        classroom = db.query(Classroom).filter(Classroom.id == classroom_id).first()
        if not classroom:
            return {"status": "rejected", "detail": f"Classroom with ID '{classroom_id}' does not exist."}

        today_date = date.today()

        # 3. Check for existing attendance record today
        existing = db.query(Attendance).filter(
            Attendance.student_id == student_id,
            Attendance.date == today_date
        ).first()

        if existing:
            return {
                "status": "already_marked",
                "student_id": student_id,
                "classroom_id": existing.classroom_id or classroom_id,
                "verification_method": existing.verification_method,
                "existing_status": existing.status,
                "detail": f"Student '{student_id}' is already marked {existing.status} for today."
            }

        # 4. Create new Face AI attendance record
        new_record = Attendance(
            student_id=student_id,
            classroom_id=classroom_id,
            date=today_date,
            timestamp=datetime.now(),
            status="Present",
            verification_method="Face AI",
            confidence=round(float(confidence), 2)
        )
        db.add(new_record)
        db.commit()
        db.refresh(new_record)

        return {
            "status": "marked",
            "student_id": student_id,
            "student_name": student.name,
            "classroom_id": classroom_id,
            "classroom_name": classroom.name,
            "verification_method": "Face AI",
            "confidence": new_record.confidence,
            "detail": f"Attendance marked Present via Face AI for {student.name} in {classroom.name}."
        }


