import requests
import pymysql

BASE_URL = "http://127.0.0.1:8000/api"

def test_full_classroom_crud():
    # 0. Authenticate
    r_auth = requests.post(f"{BASE_URL}/auth/login", json={"email": "admin@aura.edu", "password": "admin123"})
    assert r_auth.status_code == 200, f"Auth failed: {r_auth.text}"
    token = r_auth.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    conn = pymysql.connect(host='127.0.0.1', user='root', password='', database='smart_classroom', autocommit=True)
    cur = conn.cursor(pymysql.cursors.DictCursor)

    # 1. GET ALL
    res = requests.get(f"{BASE_URL}/classrooms", headers=headers)
    assert res.status_code == 200, f"GET failed: {res.text}"
    all_rooms = res.json()
    print(f"1. GET /api/classrooms: Found {len(all_rooms)} classrooms in MySQL database.")
    for r in all_rooms:
        print(f"   - ID #{r['id']}: {r['name']} | Dept: {r['department']} | Capacity: {r['capacity']} | Status: {r['status']}")

    # 2. CREATE
    create_body = {
        'name': 'AI Research Lab 404',
        'department': 'Computer Science',
        'capacity': 50,
        'status': 'Active'
    }
    r_post = requests.post(f"{BASE_URL}/classrooms", json=create_body, headers=headers)
    assert r_post.status_code == 201, f"POST failed: {r_post.text}"
    created = r_post.json()
    created_id = created['id']
    print(f"\n2. POST /api/classrooms: Created classroom ID #{created_id} ('{created['name']}').")

    # Verify in DB
    cur.execute('SELECT * FROM classrooms WHERE id=%s', (created_id,))
    row = cur.fetchone()
    assert row and row['name'] == 'AI Research Lab 404' and row['capacity'] == 50, 'DB Insert verification failed!'
    print("   -> Verified in MySQL: Classroom record exists with correct data.")

    # 3. GET SINGLE
    res_single = requests.get(f"{BASE_URL}/classrooms/{created_id}", headers=headers)
    assert res_single.status_code == 200, f"GET single failed: {res_single.text}"
    single = res_single.json()
    assert single['id'] == created_id and single['name'] == 'AI Research Lab 404'
    print(f"\n3. GET /api/classrooms/{created_id}: Fetched single classroom details successfully.")

    # 4. UPDATE
    update_body = {
        'name': 'AI Research & Robotics Lab 404',
        'department': 'Computer Science',
        'capacity': 60,
        'status': 'Inactive'
    }
    r_put = requests.put(f"{BASE_URL}/classrooms/{created_id}", json=update_body, headers=headers)
    assert r_put.status_code == 200, f"PUT failed: {r_put.text}"
    updated = r_put.json()
    print(f"\n4. PUT /api/classrooms/{created_id}: Updated name to '{updated['name']}', capacity to {updated['capacity']}, status to {updated['status']}.")

    # Verify in DB
    cur.execute('SELECT * FROM classrooms WHERE id=%s', (created_id,))
    row = cur.fetchone()
    assert row and row['name'] == 'AI Research & Robotics Lab 404' and row['capacity'] == 60 and row['status'] == 'Inactive', 'DB Update verification failed!'
    print("   -> Verified in MySQL: Record was updated in MySQL.")

    # 5. DELETE
    r_del = requests.delete(f"{BASE_URL}/classrooms/{created_id}", headers=headers)
    assert r_del.status_code == 200, f"DELETE failed: {r_del.text}"
    deleted = r_del.json()
    print(f"\n5. DELETE /api/classrooms/{created_id}: {deleted['message']}")

    # Verify in DB
    cur.execute('SELECT * FROM classrooms WHERE id=%s', (created_id,))
    row = cur.fetchone()
    assert row is None, 'DB Delete verification failed!'
    print("   -> Verified in MySQL: Classroom record was removed from MySQL.")

    # 6. Verify Student Management API is unaffected
    res_students = requests.get(f"{BASE_URL}/students", headers=headers)
    assert res_students.status_code == 200
    students = res_students.json()
    print(f"\n6. Student Management Sanity Check: {len(students)} students loaded without issues.")

    conn.close()
    print("\n*** FULL CLASSROOM MANAGEMENT VERIFICATION: 100% SUCCESSFUL! ***")

if __name__ == '__main__':
    test_full_classroom_crud()
