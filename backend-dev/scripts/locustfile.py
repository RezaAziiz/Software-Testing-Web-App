from locust import HttpUser, task, between, events
from jose import jwt
from datetime import datetime, timedelta

# Konfigurasi Token (diambil dari .env)
SECRET_KEY = "TA_UAT_2026_SecretKey_8fK2xP9mL4qR7vN1"
ALGORITHM = "HS256"

# Data untuk Load Test (Topik Modul IsVokal)
ID_TOPIK_MODUL = "45feae30-d562-456b-b204-ec45a9b81bb3"

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.database import conn
from sqlalchemy import text

# Ambil semua student_id di awal
student_rows = conn.execute(text('SELECT ms_student_id FROM ms_student')).fetchall()
all_student_ids = [row[0] for row in student_rows]

def generate_student_token(userid: str) -> str:
    """Generate JWT Token secara manual agar Locust bisa bypass Login"""
    expire = datetime.utcnow() + timedelta(minutes=60)
    data = {
        "userid": userid,
        "role": "student",
        "exp": expire
    }
    encoded_jwt = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

class StudentExecutionUser(HttpUser):
    # Tunggu 1 detik antar request jika task berulang
    wait_time = between(1.0, 1.0)
    
    def on_start(self):
        """Dijalankan sekali ketika user (mahasiswa) virtual ini spawn"""
        import random
        # Pilih student ID secara acak dari 59 mahasiswa di DB
        self.student_id = random.choice(all_student_ids)
        self.token = generate_student_token(self.student_id)
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    @task
    def execute_test_case(self):
        """Aksi utama: mahasiswa klik tombol 'Eksekusi Test Case'"""
        response = self.client.post(
            f"/modul/run/{ID_TOPIK_MODUL}",
            headers=self.headers
        )
        if response.status_code != 200:
            print(f"Failed execution: {response.status_code} - {response.text}")