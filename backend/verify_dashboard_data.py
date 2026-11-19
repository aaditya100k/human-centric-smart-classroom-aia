import requests
from datetime import date, datetime

BASE_URL = "http://127.0.0.1:8000/api"

def test_dashboard_data_verification():
    print("=" * 60)
    print("STARTING DASHBOARD FASTAPI + MYSQL DATA VERIFICATION")
    print("=" * 60)

    # 0. Authenticate
    r_auth = requests.post(f"{BASE_URL}/auth/login", json={"email": "admin@aura.edu", "password": "admin123"})
    assert r_auth.status_code == 200, f"Auth failed: {r_auth.text}"
    token = r_auth.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Fetch Students
    r_students = requests.get(f"{BASE_URL}/students", headers=headers)
    assert r_students.status_code == 200, f"Failed to get students: {r_students.text}"
    students = r_students.json()
    student_count = len(students)
    print(f"1. [GET /api/students] -> Total Students in MySQL: {student_count}")
    assert student_count > 0, "No students found in MySQL!"

    # 2. Fetch Classrooms
    r_classrooms = requests.get(f"{BASE_URL}/classrooms", headers=headers)
    assert r_classrooms.status_code == 200, f"Failed to get classrooms: {r_classrooms.text}"
    classrooms = r_classrooms.json()
    classroom_count = len(classrooms)
    active_classroom_count = sum(1 for c in classrooms if (c.get("status") or "").lower() == "active")
    print(f"2. [GET /api/classrooms] -> Total Classrooms: {classroom_count}, Active: {active_classroom_count}")
    assert classroom_count > 0, "No classrooms found in MySQL!"

    # 3. Fetch Today's Attendance Summary
    r_today = requests.get(f"{BASE_URL}/attendance/today", headers=headers)
    assert r_today.status_code == 200, f"Failed to get today attendance: {r_today.text}"
    today_summary = r_today.json()
    present_today = today_summary.get("present_count", 0)
    attendance_rate = today_summary.get("attendance_rate", 0.0)
    print(f"3. [GET /api/attendance/today] -> Present Today: {present_today}, Rate: {attendance_rate}%")

    # 4. Fetch Recent Attendance Records
    r_attendance = requests.get(f"{BASE_URL}/attendance", params={"limit": 15}, headers=headers)
    assert r_attendance.status_code == 200, f"Failed to get attendance records: {r_attendance.text}"
    recent_attendance = r_attendance.json()
    print(f"4. [GET /api/attendance] -> Retrieved {len(recent_attendance)} recent attendance records from MySQL.")

    # 5. Direct Database Sanity Check
    from app.database import SessionLocal
    from app.models.student import Student
    from app.models.classroom import Classroom
    from app.models.attendance import Attendance

    db = SessionLocal()
    db_students_cnt = db.query(Student).count()
    db_classrooms_cnt = db.query(Classroom).count()
    db_active_classrooms_cnt = db.query(Classroom).filter(Classroom.status == "Active").count()
    db_attendance_cnt = db.query(Attendance).count()
    db.close()

    print(f"5. [Direct MySQL Verification]")
    print(f"   - Student Count: API={student_count}, MySQL={db_students_cnt}")
    print(f"   - Classroom Count: API={classroom_count}, MySQL={db_classrooms_cnt}")
    print(f"   - Active Classrooms: API={active_classroom_count}, MySQL={db_active_classrooms_cnt}")
    print(f"   - Total Attendance Records: MySQL={db_attendance_cnt}")

    assert student_count == db_students_cnt, "API student count does not match MySQL!"
    assert classroom_count == db_classrooms_cnt, "API classroom count does not match MySQL!"
    assert active_classroom_count == db_active_classrooms_cnt, "API active classroom count does not match MySQL!"

    print("=" * 60)
    print("DASHBOARD DATA VERIFICATION SUCCESSFUL! (100% Verified)")
    print("=" * 60)

if __name__ == "__main__":
    test_dashboard_data_verification()
