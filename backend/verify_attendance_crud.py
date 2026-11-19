import requests
from datetime import date, datetime

BASE_URL = "http://127.0.0.1:8000/api"

def test_attendance_endpoints():
    print("=" * 60)
    print("STARTING ATTENDANCE MANAGEMENT MODULE VERIFICATION")
    print("=" * 60)

    # 0. Authenticate
    r_auth = requests.post(f"{BASE_URL}/auth/login", json={"email": "admin@aura.edu", "password": "admin123"})
    assert r_auth.status_code == 200, f"Auth failed: {r_auth.text}"
    token = r_auth.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Fetch Students to get valid student IDs
    r_students = requests.get(f"{BASE_URL}/students", headers=headers)
    assert r_students.status_code == 200, f"Failed to get students: {r_students.text}"
    students = r_students.json()
    print(f"1. [GET /api/students] -> Found {len(students)} students.")
    assert len(students) > 0, "No students found to test attendance."
    test_student = students[0]
    test_student_id = test_student["id"]
    test_student_name = test_student["name"]
    print(f"   Selected test student: {test_student_name} ({test_student_id})")

    # 2. Fetch Classrooms to get valid classroom ID
    r_classrooms = requests.get(f"{BASE_URL}/classrooms", headers=headers)
    assert r_classrooms.status_code == 200, f"Failed to get classrooms: {r_classrooms.text}"
    classrooms = r_classrooms.json()
    print(f"2. [GET /api/classrooms] -> Found {len(classrooms)} classrooms.")
    test_classroom_id = classrooms[0]["id"] if len(classrooms) > 0 else None

    # 3. Clean up any existing test records for today for this student to ensure a fresh test
    today_str = date.today().isoformat()
    r_existing = requests.get(f"{BASE_URL}/attendance", params={"student_id": test_student_id, "date": today_str}, headers=headers)
    if r_existing.status_code == 200:
        for rec in r_existing.json():
            requests.delete(f"{BASE_URL}/attendance/{rec['id']}", headers=headers)

    # 4. Test POST /api/attendance (Create Attendance)
    post_payload = {
        "student_id": test_student_id,
        "classroom_id": test_classroom_id,
        "date": today_str,
        "status": "Present",
        "verification_method": "Face AI",
        "confidence": 0.98
    }
    r_post = requests.post(f"{BASE_URL}/attendance", json=post_payload, headers=headers)
    print(f"3. [POST /api/attendance] -> Status: {r_post.status_code}")
    assert r_post.status_code == 201, f"Failed to record attendance: {r_post.text}"
    created_rec = r_post.json()
    created_id = created_rec["id"]
    print(f"   Created Record ID: {created_id}, Student: {created_rec.get('student_name')}, Room: {created_rec.get('classroom_name')}, Status: {created_rec.get('status')}")
    assert created_rec["student_id"] == test_student_id
    assert created_rec["status"] == "Present"

    # 5. Test Duplicate Attendance Prevention (Should return 400 Bad Request)
    r_dup = requests.post(f"{BASE_URL}/attendance", json=post_payload, headers=headers)
    print(f"4. [POST Duplicate Check] -> Status: {r_dup.status_code}")
    assert r_dup.status_code == 400, f"Expected 400 on duplicate, got {r_dup.status_code}: {r_dup.text}"
    print(f"   Duplicate rejected properly with message: {r_dup.json().get('detail')}")

    # 6. Test GET /api/attendance
    r_get_all = requests.get(f"{BASE_URL}/attendance", headers=headers)
    assert r_get_all.status_code == 200
    all_records = r_get_all.json()
    print(f"5. [GET /api/attendance] -> Total records retrieved: {len(all_records)}")
    assert any(r["id"] == created_id for r in all_records), "Created record not in list!"

    # 7. Test GET /api/attendance/today
    r_today = requests.get(f"{BASE_URL}/attendance/today", headers=headers)
    assert r_today.status_code == 200
    summary = r_today.json()
    print(f"6. [GET /api/attendance/today] -> Total Records Today: {summary.get('total_records')}, Present: {summary.get('present_count')}, Rate: {summary.get('attendance_rate')}%")
    assert summary.get("present_count") >= 1, "Today summary present count should be >= 1"

    # 8. Test GET /api/attendance/student/{student_id}
    r_student_att = requests.get(f"{BASE_URL}/attendance/student/{test_student_id}", headers=headers)
    assert r_student_att.status_code == 200
    student_records = r_student_att.json()
    print(f"7. [GET /api/attendance/student/{test_student_id}] -> Student History Count: {len(student_records)}")
    assert len(student_records) >= 1, "Student history should have at least 1 record."

    # 9. Test PUT /api/attendance/{id} (Update Status)
    r_put = requests.put(f"{BASE_URL}/attendance/{created_id}", json={"status": "Late"}, headers=headers)
    assert r_put.status_code == 200, f"Failed to update attendance: {r_put.text}"
    updated = r_put.json()
    print(f"8. [PUT /api/attendance/{created_id}] -> Updated status to: {updated.get('status')}")
    assert updated["status"] == "Late"

    # 10. Direct Database Check
    from app.database import SessionLocal
    from app.models.attendance import Attendance
    db = SessionLocal()
    db_rec = db.query(Attendance).filter(Attendance.id == created_id).first()
    assert db_rec is not None, "Record not found in MySQL directly!"
    print(f"9. [Direct MySQL Verification] -> Record #{db_rec.id} confirmed in smart_classroom.attendance table with status '{db_rec.status}'")
    db.close()

    print("=" * 60)
    print("ALL ATTENDANCE MANAGEMENT TESTS PASSED SUCCESSFULLY! (100% Verified)")
    print("=" * 60)

if __name__ == "__main__":
    test_attendance_endpoints()
