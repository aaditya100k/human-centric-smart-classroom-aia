import os
import logging
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

logger = logging.getLogger("smart_classroom.database")

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://root:password@localhost:3306/smart_classroom"
)

# Engine connection arguments depending on SQL dialect
connect_args = {}
engine_kwargs = {
    "pool_pre_ping": True,
}

if DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False
else:
    engine_kwargs["pool_recycle"] = 3600

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    **engine_kwargs
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """
    FastAPI dependency yielding a SQLAlchemy database session.
    Automatically closes the session after request processing.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Create tables if they do not exist.
    If MySQL is not running, automatically falls back to local SQLite database
    so the application works seamlessly out-of-the-box.
    """
    global engine, SessionLocal
    try:
        from app.models import (
            user,
            student,
            student_face_embedding,
            classroom,
            attendance,
            emotion,
            attention,
            temperature,
            alert,
            notification,
            student_consent,
            retention_policy,
            audit_log,
        )
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables verified / created successfully.")
    except Exception as exc:
        logger.warning(f"MySQL connection unavailable ({exc}). Falling back to local SQLite database: sqlite:///./smart_classroom.db")
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker

        sqlite_url = "sqlite:///./smart_classroom.db"
        engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        Base.metadata.create_all(bind=engine)
        logger.info("Local SQLite database tables created successfully.")

    # Seed default users if table is empty
    try:
        db = SessionLocal()
        from app.models.user import User
        from app.utils.security import get_password_hash

        if db.query(User).count() == 0:
            admin_user = User(
                username="admin",
                email="admin@aura.edu",
                hashed_password=get_password_hash("admin123"),
                full_name="System Administrator",
                role="admin",
                is_active=True,
            )
            teacher_user = User(
                username="teacher",
                email="teacher@aura.edu",
                hashed_password=get_password_hash("teacher123"),
                full_name="Faculty Teacher",
                role="teacher",
                is_active=True,
            )
            db.add_all([admin_user, teacher_user])
            db.commit()
            logger.info("Default admin and teacher user accounts seeded (admin/admin123, teacher/teacher123).")

        # Seed default retention policies if table is empty
        from app.models.retention_policy import RetentionPolicy
        if db.query(RetentionPolicy).count() == 0:
            default_policies = [
                RetentionPolicy(
                    policy_name="raw_video_frames",
                    description="Live Camera Stream Buffer: Zero-persistence RAM processing only; never saved to disk.",
                    retention_days=0,
                    storage_type="Volatile RAM (Ephemeral)",
                    auto_purge_enabled=True,
                ),
                RetentionPolicy(
                    policy_name="face_embeddings",
                    description="128-D SFace biometric vectors: Retained for active academic term or until consent revoked.",
                    retention_days=180,
                    storage_type="Encrypted Vector Store",
                    auto_purge_enabled=True,
                ),
                RetentionPolicy(
                    policy_name="attendance_records",
                    description="Classroom attendance logs & verification audit history.",
                    retention_days=365,
                    storage_type="Relational Database",
                    auto_purge_enabled=True,
                ),
                RetentionPolicy(
                    policy_name="emotion_records",
                    description="Aggregated engagement and emotion distribution summaries for pedagogical feedback.",
                    retention_days=90,
                    storage_type="Pseudonymized Relational DB",
                    auto_purge_enabled=True,
                ),
            ]
            db.add_all(default_policies)
            db.commit()
            logger.info("Default data retention policies seeded.")

        # Ensure all existing students have a default consent record
        from app.models.student import Student
        from app.models.student_consent import StudentConsent
        students_without_consent = (
            db.query(Student)
            .outerjoin(StudentConsent, Student.id == StudentConsent.student_id)
            .filter(StudentConsent.id.is_(None))
            .all()
        )
        for s in students_without_consent:
            consent = StudentConsent(
                student_id=s.id,
                camera_processing=True,
                face_recognition=True,
                attendance_processing=True,
                emotion_inference=True,
                status="Granted",
                notes="Initial academic enrollment consent",
            )
            db.add(consent)
        if students_without_consent:
            db.commit()
            logger.info(f"Initialized consent records for {len(students_without_consent)} existing students.")

        db.close()
    except Exception as seed_err:
        logger.warning(f"Could not seed default users: {seed_err}")

    return True

