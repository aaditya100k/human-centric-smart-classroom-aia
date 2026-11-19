import requests
import pymysql

BASE_URL = "http://127.0.0.1:8000/api"

def test_full_student_crud():
    # 0. Authenticate
    r_auth = requests.post(f"{BASE_URL}/auth/login", json={"email": "admin@aura.edu", "password": "admin123"})
    assert r_auth.status_code == 200, f"Auth failed: {r_auth.text}"
    token = r_auth.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    conn = pymysql.connect(host='127.0.0.1', user='root', password='', database='smart_classroom', autocommit=True)
    cur = conn.cursor(pymysql.cursors.DictCursor)

    # 1. GET ALL
    res = requests.get(f"{BASE_URL}/students", headers=headers)
    assert res.status_code == 200, f"GET failed: {res.text}"
    all_students = res.json()
    print(f"1. GET: Found {len(all_students)} students in MySQL database.")

    # 2. CREATE
    create_body = {
        'id': 'ST-E2E-001',
        'name': 'Rahul Sharma',
        'email': 'rahul.s@aura.edu',
        'department': 'Computer Science',
        'classroom_id': 1,
        'status': 'Active'
    }
    r_post = requests.post(f"{BASE_URL}/students", json=create_body, headers=headers)
    assert r_post.status_code == 201, f"POST failed: {r_post.text}"
    created = r_post.json()
    print(f"2. POST: Created student {created['id']} ({created['name']}).")

    # Verify in DB
    cur.execute('SELECT * FROM students WHERE id=%s', ('ST-E2E-001',))
    row = cur.fetchone()
    assert row and row['name'] == 'Rahul Sharma', 'DB Insert verification failed!'
    print("   -> Verified in MySQL: Record exists with correct data.")

    # 3. UPDATE
    update_body = {
        'name': 'Rahul M. Sharma',
        'email': 'rahul.m@aura.edu',
        'department': 'Computer Science',
        'status': 'Active'
    }
    r_put = requests.put(f"{BASE_URL}/students/ST-E2E-001", json=update_body, headers=headers)
    assert r_put.status_code == 200, f"PUT failed: {r_put.text}"
    updated = r_put.json()
    print(f"3. PUT: Updated student {updated['id']} name to {updated['name']}.")

    # Verify in DB
    cur.execute('SELECT * FROM students WHERE id=%s', ('ST-E2E-001',))
    row = cur.fetchone()
    assert row and row['name'] == 'Rahul M. Sharma', 'DB Update verification failed!'
    print("   -> Verified in MySQL: Record was updated in MySQL.")

    # 4. DELETE
    r_del = requests.delete(f"{BASE_URL}/students/ST-E2E-001", headers=headers)
    assert r_del.status_code == 200, f"DELETE failed: {r_del.text}"
    deleted = r_del.json()
    print(f"4. DELETE: {deleted['message']}")

    # Verify in DB
    cur.execute('SELECT * FROM students WHERE id=%s', ('ST-E2E-001',))
    row = cur.fetchone()
    assert row is None, 'DB Delete verification failed!'
    print("   -> Verified in MySQL: Record was deleted from MySQL.")

    conn.close()
    print("\n*** FULL END-TO-END VERIFICATION: 100% SUCCESSFUL! ***")

if __name__ == '__main__':
    test_full_student_crud()
