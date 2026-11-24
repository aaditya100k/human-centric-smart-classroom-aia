import os
import logging
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, status
from app.utils.security import get_current_user
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.database import init_db
from app.routers import (
    auth_router,
    students_router,
    classrooms_router,
    attendance_router,
    monitoring_router,
    face_recognition_router,
    analytics_router,
    alerts_router,
    notifications_router,
    privacy_router,
    research_router,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("smart_classroom")

# Load environment configuration
load_dotenv()

# Parse allowed CORS origins from .env
origins_env = os.getenv(
    "ALLOWED_ORIGINS",
    "http://127.0.0.1:5500,http://localhost:5500,http://127.0.0.1:8000,http://localhost:8000,http://localhost:3000"
)
origins = [origin.strip() for origin in origins_env.split(",") if origin.strip()]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.
    Initializes database tables on startup.
    """
    logger.info("Initializing Smart Classroom Backend...")
    db_initialized = init_db()
    if db_initialized:
        logger.info("Database initialized successfully.")
    else:
        logger.warning(
            "Database connection failed or pending. Ensure MySQL service is running. "
            "Server will continue running so /docs and /api/health remain accessible."
        )
    yield
    logger.info("Shutting down Smart Classroom Backend.")


app = FastAPI(
    title="Human-Centric Smart Classroom Monitoring System with AI",
    description="Production-grade FastAPI REST API for Smart Classroom AI Attendance, Emotion, and Attention Monitoring.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Configure CORS Middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if "*" not in origins else ["*"],
    allow_credentials=True if "*" not in origins else False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health", tags=["System Health"], status_code=status.HTTP_200_OK)
def health_check():
    """
    System Health Check endpoint to verify backend operational status.
    """
    return {
        "status": "ok",
        "message": "Smart Classroom Backend is running"
    }


# Include all modular routers
app.include_router(auth_router)
app.include_router(students_router, dependencies=[Depends(get_current_user)])
app.include_router(classrooms_router, dependencies=[Depends(get_current_user)])
app.include_router(attendance_router, dependencies=[Depends(get_current_user)])
app.include_router(monitoring_router)
app.include_router(face_recognition_router)
app.include_router(analytics_router, dependencies=[Depends(get_current_user)])
app.include_router(alerts_router, dependencies=[Depends(get_current_user)])
app.include_router(notifications_router, dependencies=[Depends(get_current_user)])
app.include_router(privacy_router, dependencies=[Depends(get_current_user)])
app.include_router(research_router, dependencies=[Depends(get_current_user)])


# Serve frontend_refactored static files and redirect root URL
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, RedirectResponse

frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend_refactored"))
if os.path.exists(frontend_dir):
    logger.info(f"Mounting frontend directory from {frontend_dir}")
    app.mount("/frontend", StaticFiles(directory=frontend_dir, html=True), name="frontend")

    @app.get("/", tags=["Frontend"])
    def redirect_to_frontend():
        """Redirect root URL to the interactive frontend login page."""
        return RedirectResponse(url="/frontend/html/edumonitor_ai_login_page.html")

# Serve uploaded student photos and other assets
uploads_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "uploads"))
os.makedirs(uploads_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

# Global Exception Handler for friendly error messages
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled exception on {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred. Please verify backend and database configuration."},
    )

