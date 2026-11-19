from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Date, func
from sqlalchemy.orm import relationship
from app.database import Base


class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id = Column(String(50), ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    classroom_id = Column(Integer, ForeignKey("classrooms.id", ondelete="SET NULL"), nullable=True, index=True)
    date = Column(Date, default=func.current_date(), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    status = Column(String(20), default="Present", nullable=False)  # "Present", "Absent", "Late"
    verification_method = Column(String(50), default="Face AI", nullable=False)  # "Face AI", "Manual", "Biometric"
    confidence = Column(Float, default=0.95, nullable=False)

    # Relationships
    student = relationship("Student", back_populates="attendance_records")
    classroom = relationship("Classroom", back_populates="attendance_records")
