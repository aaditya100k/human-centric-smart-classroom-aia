from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base


class StudentConsent(Base):
    __tablename__ = "student_consents"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id = Column(String(50), ForeignKey("students.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    camera_processing = Column(Boolean, default=False, nullable=False)
    face_recognition = Column(Boolean, default=False, nullable=False)
    attendance_processing = Column(Boolean, default=False, nullable=False)
    emotion_inference = Column(Boolean, default=False, nullable=False)
    status = Column(String(30), default="Pending", nullable=False)  # "Granted", "Revoked", "Pending", "Partially Granted"
    consent_timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    withdrawn_timestamp = Column(DateTime(timezone=True), nullable=True)
    notes = Column(String(255), nullable=True)

    # Relationships
    student = relationship("Student", back_populates="consent")
