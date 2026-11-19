from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.database import Base


class TemperatureRecord(Base):
    __tablename__ = "temperature_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id = Column(String(50), ForeignKey("students.id", ondelete="SET NULL"), nullable=True, index=True)
    classroom_id = Column(Integer, ForeignKey("classrooms.id", ondelete="CASCADE"), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    temperature = Column(Float, default=36.5, nullable=False)  # in Celsius
    unit = Column(String(10), default="C", nullable=False)
    sensor_id = Column(String(50), default="ESP32-01", nullable=False)
    is_fever = Column(Boolean, default=False, nullable=False)

    # Relationships
    student = relationship("Student", back_populates="temperature_records")
    classroom = relationship("Classroom", back_populates="temperature_records")
