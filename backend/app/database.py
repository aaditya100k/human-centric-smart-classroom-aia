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
        db.close()
    except Exception as seed_err:
        logger.warning(f"Could not seed default users: {seed_err}")

    return True

