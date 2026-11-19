# Human-Centric Smart Classroom Monitoring System - Backend

Production-style, modular REST API backend built with **Python FastAPI**, **SQLAlchemy ORM**, **MySQL**, and **Pydantic schemas**.

---

## Architecture Overview

```
backend/
├── app/
│   ├── __init__.py                 # Application package marker
│   ├── main.py                     # FastAPI app, CORS, lifespan startup, /api/health, router inclusions
│   ├── database.py                 # SQLAlchemy engine, sessionmaker, declarative Base, get_db dependency
│   │
│   ├── models/                     # SQLAlchemy ORM database models
│   │   ├── __init__.py             # Exports all ORM models
│   │   ├── user.py                 # users table (auth, admins, faculty)
│   │   ├── classroom.py            # classrooms table (rooms, capacity, status)
│   │   ├── student.py              # students table (profiles, departments, room assignment)
│   │   ├── attendance.py           # attendance table (Face AI / manual records)
│   │   ├── emotion.py              # emotion_records table (emotion classification scores)
│   │   ├── attention.py            # attention_records table (gaze, head pose, attention score)
│   │   ├── temperature.py          # temperature_records table (ESP32 thermal readings)
│   │   ├── alert.py                # alerts table (threshold breaches & notifications)
│   │   └── notification.py         # notifications table (system alerts & read status)
│   │
│   ├── schemas/                    # Pydantic v2 validation and serialization schemas
│   │   ├── __init__.py             # Exports all Pydantic schemas
│   │   ├── user.py                 # UserCreate, UserLogin, UserResponse, Token
│   │   ├── classroom.py            # ClassroomCreate, ClassroomUpdate, ClassroomResponse
│   │   ├── student.py              # StudentCreate, StudentUpdate, StudentResponse
│   │   ├── attendance.py           # AttendanceCreate, AttendanceResponse, AttendanceSummary
│   │   ├── emotion.py              # EmotionRecordCreate, EmotionAnalyticsResponse
│   │   ├── attention.py            # AttentionRecordCreate, AttentionAnalyticsResponse
│   │   ├── temperature.py          # TemperatureRecordCreate, TemperatureAnalyticsResponse
│   │   ├── alert.py                # AlertCreate, AlertUpdate, AlertResponse
│   │   └── notification.py         # NotificationCreate, NotificationResponse
│   │
│   ├── routers/                    # Clean modular REST API routers
│   │   ├── __init__.py             # Exports all APIRouters
│   │   ├── auth.py                 # POST /api/auth/register, POST /api/auth/login
│   │   ├── students.py             # CRUD /api/students
│   │   ├── classrooms.py           # CRUD /api/classrooms
│   │   ├── attendance.py           # /api/attendance, /today, /student/{id}
│   │   ├── monitoring.py           # /api/monitoring/status, /start, /stop
│   │   ├── analytics.py            # /api/analytics/{attendance,emotion,attention,temperature,dashboard}
│   │   ├── alerts.py               # /api/alerts, PUT /api/alerts/{id}
│   │   └── notifications.py        # /api/notifications, PUT /api/notifications/{id}/read
│   │
│   ├── services/                   # Business logic and computation layer
│   │   ├── __init__.py             # Exports all services
│   │   ├── attendance_service.py   # Attendance processing, daily summary, and student rate calculations
│   │   ├── analytics_service.py    # Multi-dimensional aggregations, emotion distributions, KPI dashboard
│   │   └── monitoring_service.py   # State manager with hooks for OpenCV, ESP32, and WebSockets
│   │
│   └── utils/                      # Helper utilities
│       ├── __init__.py             # Utils package marker
│       └── security.py             # JWT token issuance, bcrypt hashing, get_current_user dependency
│
├── requirements.txt                # Production Python dependencies
├── .env.example                    # Environment configuration template
├── .env                            # Active environment configuration
└── README.md                       # Comprehensive guide and documentation
```

---

## 1. Creating MySQL Database

Make sure your MySQL server (via MySQL Workbench, XAMPP, or standalone MySQL service) is started.

Open your MySQL command line or client and execute:

```sql
CREATE DATABASE IF NOT EXISTS smart_classroom CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

---

## 2. Configuring `.env`

Copy `.env.example` to `.env` if not already present:

```bash
cp .env.example .env
```

Edit `.env` to match your local MySQL credentials:

```ini
DATABASE_URL=mysql+pymysql://root:YOUR_PASSWORD@localhost:3306/smart_classroom
SECRET_KEY=your_custom_jwt_secret_key_here
ALLOWED_ORIGINS=http://127.0.0.1:5500,http://localhost:5500,http://localhost:3000,http://127.0.0.1:8000
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

> **Note on Local Development**: If MySQL is not running yet during initial testing, the application starts gracefully and displays informative connection status while keeping `/api/health` and `/docs` accessible.

---

## 3. Installing Dependencies

From the `backend/` directory:

```bash
pip install -r requirements.txt
```

---

## 4. Starting the Backend

From the `backend/` directory, run:

```bash
uvicorn app.main:app --reload
```

Or using the Python module syntax:

```bash
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

On startup, SQLAlchemy automatically creates all database tables if they do not already exist.

---

## 5. Testing `/api/health`

Open your web browser or run `curl`:

```bash
curl http://127.0.0.1:8000/api/health
```

Expected JSON response:

```json
{
  "status": "ok",
  "message": "Smart Classroom Backend is running"
}
```

---

## 6. Opening Swagger Interactive Documentation

Once the backend is running, open the interactive Swagger UI in your browser:

- **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc UI**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 7. REST API Endpoints Reference

### Authentication
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/auth/register` | Register new admin or faculty user |
| `POST` | `/api/auth/login` | Authenticate and obtain JWT token |

### Students
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/students` | List all students with search & filters |
| `GET` | `/api/students/{id}` | Get student profile by ID |
| `POST` | `/api/students` | Enroll a new student |
| `PUT` | `/api/students/{id}` | Update student information |
| `DELETE` | `/api/students/{id}` | Remove a student |

### Classrooms
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/classrooms` | List all classrooms with occupancy stats |
| `GET` | `/api/classrooms/{id}` | Get classroom details |
| `POST` | `/api/classrooms` | Create a new classroom |
| `PUT` | `/api/classrooms/{id}` | Update classroom details |
| `DELETE` | `/api/classrooms/{id}` | Delete classroom |

### Attendance
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/attendance` | List attendance records with date/student/classroom filters |
| `POST` | `/api/attendance` | Record attendance (Face AI or manual) |
| `GET` | `/api/attendance/today` | Today's attendance summary and stats |
| `GET` | `/api/attendance/student/{student_id}` | Complete attendance history for student |

### Live Monitoring
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/monitoring/status` | Current monitoring status, FPS, and uptime |
| `POST` | `/api/monitoring/start` | Start monitoring session |
| `POST` | `/api/monitoring/stop` | Stop monitoring session |

### Analytics
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/analytics/dashboard` | Overall KPI summary for dashboard |
| `GET` | `/api/analytics/attendance` | Attendance rates and 7-day trend |
| `GET` | `/api/analytics/emotion` | Emotion breakdown & engagement score |
| `GET` | `/api/analytics/attention` | Attention scores and distraction counts |
| `GET` | `/api/analytics/temperature` | Thermal metrics and fever alerts |

### Alerts & Notifications
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/alerts` | List system alerts |
| `POST` | `/api/alerts` | Create an alert |
| `PUT` | `/api/alerts/{id}` | Update or resolve an alert |
| `GET` | `/api/notifications` | List user notifications |
| `PUT` | `/api/notifications/{id}/read` | Mark notification as read |
| `PUT` | `/api/notifications/read-all` | Mark all notifications as read |

---

## 8. Future AI & Hardware Extensions

The `app/services/monitoring_service.py` is architected with extension hooks for easy integration of:
- **OpenCV**: Direct camera capture frame loop (`hook_opencv_frame`)
- **Face Recognition**: Automated student attendance logging
- **Emotion & Attention**: Model inference pipelines (FER, MediaPipe Face Mesh)
- **ESP32 Sensor**: Ingest temperature telemetry (`hook_esp32_reading`)
- **WebSocket Streaming**: Real-time push updates to `frontend_refactored/`
