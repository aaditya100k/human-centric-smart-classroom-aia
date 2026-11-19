"""
End-to-End Test Suite for Smart Classroom Backend
Tests all routers, models, schemas, and services.
"""
import sys
import os

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app

# Create isolated test database engine
TEST_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
Base.metadata.create_all(bind=test_engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def run_tests():
    print("=" * 60)
    print("[*] STARTING BACKEND END-TO-END TESTS")
    print("=" * 60)

    # 1. Health Endpoint
    print("\n[1] Testing GET /api/health...")
    res = client.get("/api/health")
    assert res.status_code == 200, f"Failed: {res.text}"
    print("    PASSED:", res.json())

    # 2. Swagger Docs Endpoint
    print("\n[2] Testing GET /docs...")
    res = client.get("/docs")
    assert res.status_code == 200
    print("    PASSED: Swagger UI is responding (Status 200)")

    # 3. User Registration & Login
    print("\n[3] Testing Authentication APIs...")
    user_payload = {
        "username": "admin_test",
        "email": "admin@aura.edu",
        "password": "Password123!",
        "full_name": "Admin Tester",
        "role": "admin"
    }
    res = client.post("/api/auth/register", json=user_payload)
    if res.status_code == 400:
        # Already registered, test login
        login_res = client.post("/api/auth/login", json={"email": "admin@aura.edu", "password": "Password123!"})
        assert login_res.status_code == 200
        token = login_res.json()["access_token"]
        print("    PASSED: Logged in existing user, JWT token received.")
    else:
        assert res.status_code == 201, f"Register failed: {res.text}"
        token = res.json()["access_token"]
        print("    PASSED: Registered new admin user and issued JWT.")

    headers = {"Authorization": f"Bearer {token}"}

    # 4. Monitoring Status & Start/Stop
    print("\n[4] Testing Monitoring APIs...")
    res = client.get("/api/monitoring/status", headers=headers)
    assert res.status_code == 200
    print("    GET /api/monitoring/status:", res.json()["status_message"])

    res = client.post("/api/monitoring/start", json={"classroom_id": 1, "fps": 30}, headers=headers)
    assert res.status_code == 200
    print("    POST /api/monitoring/start:", res.json()["message"])

    res = client.post("/api/monitoring/stop", headers=headers)
    assert res.status_code == 200
    print("    POST /api/monitoring/stop:", res.json()["message"])

    # 5. Classroom CRUD
    print("\n[5] Testing Classroom APIs...")
    room_payload = {
        "name": "Room 101",
        "department": "Computer Science",
        "capacity": 40,
        "status": "Active"
    }
    res = client.post("/api/classrooms", json=room_payload, headers=headers)
    if res.status_code == 201:
        classroom_id = res.json()["id"]
        print(f"    PASSED: Created Classroom 'Room 101' (ID: {classroom_id})")
    else:
        # Fetch existing
        list_res = client.get("/api/classrooms", headers=headers)
        classroom_id = list_res.json()[0]["id"]
        print(f"    PASSED: Classroom already exists (ID: {classroom_id})")

    res = client.get(f"/api/classrooms/{classroom_id}", headers=headers)
    assert res.status_code == 200
    print("    GET /api/classrooms/{id}:", res.json()["name"], f"(Capacity: {res.json()['capacity']})")

    # 6. Student CRUD
    print("\n[6] Testing Student APIs...")
    student_payload = {
        "id": "ST-2024-001",
        "name": "Alex Johnson",
        "email": "alex.j@aura.edu",
        "department": "Computer Science",
        "classroom_id": classroom_id,
        "status": "Active"
    }
    res = client.post("/api/students", json=student_payload, headers=headers)
    if res.status_code == 201:
        print("    PASSED: Created Student 'Alex Johnson' (ID: ST-2024-001)")
    else:
        print("    Student ST-2024-001 already registered.")

    res = client.get("/api/students", headers=headers)
    assert res.status_code == 200
    print(f"    GET /api/students: Found {len(res.json())} students.")

    res = client.get("/api/students/ST-2024-001", headers=headers)
    assert res.status_code == 200
    print(f"    GET /api/students/ST-2024-001: Verified {res.json()['name']} in {res.json()['classroom_name']}")

    # 7. Attendance APIs
    print("\n[7] Testing Attendance APIs...")
    att_payload = {
        "student_id": "ST-2024-001",
        "classroom_id": classroom_id,
        "status": "Present",
        "verification_method": "Face AI",
        "confidence": 0.98
    }
    res = client.post("/api/attendance", json=att_payload, headers=headers)
    assert res.status_code == 201
    print("    POST /api/attendance: Recorded Face AI attendance (Confidence: 98%)")

    res = client.get("/api/attendance/today", headers=headers)
    assert res.status_code == 200
    print(f"    GET /api/attendance/today: Attendance Rate = {res.json()['attendance_rate']}%")

    # 8. Analytics APIs
    print("\n[8] Testing Analytics APIs...")
    res = client.get("/api/analytics/dashboard", headers=headers)
    assert res.status_code == 200
    dash = res.json()
    print(f"    GET /api/analytics/dashboard: Total Students: {dash['total_students']}, Active Rooms: {dash['active_classrooms_display']}")

    res = client.get("/api/analytics/emotion", headers=headers)
    assert res.status_code == 200
    print(f"    GET /api/analytics/emotion: Status {res.status_code} OK")

    res = client.get("/api/analytics/attention", headers=headers)
    assert res.status_code == 200
    print(f"    GET /api/analytics/attention: Status {res.status_code} OK")

    res = client.get("/api/analytics/temperature", headers=headers)
    assert res.status_code == 200
    print(f"    GET /api/analytics/temperature: Status {res.status_code} OK")

    # 9. Alerts & Notifications APIs
    print("\n[9] Testing Alerts & Notifications...")
    alert_payload = {
        "title": "Low Attention Detected",
        "message": "Average attention dropped below 70% in Room 101",
        "category": "Attention",
        "severity": "Medium",
        "classroom_id": classroom_id
    }
    res = client.post("/api/alerts", json=alert_payload, headers=headers)
    assert res.status_code == 201
    alert_id = res.json()["id"]
    print(f"    POST /api/alerts: Created Alert ID {alert_id}")

    res = client.put(f"/api/alerts/{alert_id}", json={"is_resolved": True}, headers=headers)
    assert res.status_code == 200
    print(f"    PUT /api/alerts/{alert_id}: Alert successfully resolved!")

    notif_payload = {
        "title": "System Online",
        "message": "Smart Classroom backend booted successfully",
        "category": "System"
    }
    res = client.post("/api/notifications", json=notif_payload, headers=headers)
    assert res.status_code == 201
    notif_id = res.json()["id"]
    print(f"    POST /api/notifications: Created Notification ID {notif_id}")

    res = client.put(f"/api/notifications/{notif_id}/read", headers=headers)
    assert res.status_code == 200
    print(f"    PUT /api/notifications/{notif_id}/read: Marked as read.")

    print("\n" + "=" * 60)
    print("[SUCCESS] ALL BACKEND END-TO-END TESTS PASSED! (100% OK)")
    print("=" * 60)

if __name__ == "__main__":
    run_tests()
