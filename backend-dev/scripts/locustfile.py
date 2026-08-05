from locust import HttpUser, task, between
from locust.exception import StopUser
from locust import HttpUser, task, between
from locust.exception import StopUser
from jose import jwt
from datetime import datetime, timedelta
import gevent.event
import random
import uuid
from queue import Queue
import gevent.event
import random
import uuid
from queue import Queue

# Konfigurasi Token (diambil dari .env)
SECRET_KEY = "TA_UAT_2026_SecretKey_8fK2xP9mL4qR7vN1"
ALGORITHM = "HS256"

# Data untuk Load Test (Topik Modul IsVokal)
ID_TOPIK_MODUL = "45feae30-d562-456b-b204-ec45a9b81bb3"

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.database import engine
from sqlalchemy import text

import json

# Target jumlah mahasiswa konkuren
TARGET_CONCURRENCY = 270
JSON_CACHE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dummy_students.json")

all_student_ids = []

try:
    # 1. Coba koneksi ke Database & Lakukan Seeding jika DB dapat dijangkau
    with engine.connect() as db_conn:
        print("[LOAD TEST SETUP] Menghapus data dummy lama dari Database...")
        with engine.begin() as transaction_conn:
            transaction_conn.execute(text("DELETE FROM tr_test_case_modul WHERE createdby = 'DUMMY_SEED'"))
            transaction_conn.execute(text("DELETE FROM ms_student WHERE ms_student_nim LIKE 'DUMMY%'"))

        template_tc = db_conn.execute(text("""
            SELECT tr_no, tr_object_pengujian, tr_data_test_input, tr_expected_result, tr_test_result 
            FROM tr_test_case_modul 
            WHERE tr_id_topik_modul = :topik 
            LIMIT 50
        """), {"topik": ID_TOPIK_MODUL}).fetchall()

        if not template_tc:
            template_tc = [
                (1, "Huruf Vokal a", "'a'", "'Y'", "Y"),
                (2, "Huruf Konsonan b", "'b'", "'N'", "Y"),
                (3, "Huruf Vokal e", "'e'", "'Y'", "Y")
            ]

        print(f"[LOAD TEST SETUP] Membuat {TARGET_CONCURRENCY} dummy students ke DB...")
        hashed_pwd = "$2b$12$tGgYpT.R/P/4gC9tZ.Vz9eJd9pYy8u2d/f.6e2y5d8u3d/F.F.G.G"
        
        with engine.begin() as transaction_conn:
            for i in range(TARGET_CONCURRENCY):
                new_id = str(uuid.uuid4())
                new_nim = f"DUMMY{1000 + i}"
                new_name = f"Dummy Student {i}"
                
                transaction_conn.execute(text("""
                    INSERT INTO ms_student (ms_student_id, ms_student_nim, ms_student_name, ms_student_kelas, ms_student_prodi, ms_student_password)
                    VALUES (:id, :nim, :name, 'DUMMY', 'DUMMY', :pwd)
                """), {"id": new_id, "nim": new_nim, "name": new_name, "pwd": hashed_pwd})
                
                for tc in template_tc:
                    new_tc_id = str(uuid.uuid4())
                    transaction_conn.execute(text("""
                        INSERT INTO tr_test_case_modul (
                            tr_id_test_case, tr_id_topik_modul, tr_student_id, tr_no, 
                            tr_object_pengujian, tr_data_test_input, tr_expected_result, 
                            tr_test_result, createdby, created
                        ) VALUES (
                            :tc_id, :topik, :student_id, :no, 
                            :obj, :input_data, :expected, 
                            :result, 'DUMMY_SEED', :created
                        )
                    """), {
                        "tc_id": new_tc_id,
                        "topik": ID_TOPIK_MODUL,
                        "student_id": new_id,
                        "no": tc[0],
                        "obj": tc[1],
                        "input_data": tc[2],
                        "expected": tc[3],
                        "result": tc[4],
                        "created": datetime.utcnow().date()
                    })
                
                all_student_ids.append(new_id)

        # Simpan daftar student ID ke dummy_students.json agar laptop kien/tester bisa pakai tanpa DB
        with open(JSON_CACHE_PATH, "w") as f:
            json.dump(all_student_ids, f)
        print(f"[LOAD TEST SETUP] Berhasil menyimpan {len(all_student_ids)} Student IDs ke {JSON_CACHE_PATH}")

except Exception as e:
    print(f"[LOAD TEST SETUP] Koneksi DB tidak tersedia ({e}). Membaca dari {JSON_CACHE_PATH}...")
    if os.path.exists(JSON_CACHE_PATH):
        with open(JSON_CACHE_PATH, "r") as f:
            all_student_ids = json.load(f)
        print(f"[LOAD TEST SETUP] Berhasil memuat {len(all_student_ids)} Student IDs dari file lokal.")
    else:
        print(f"[LOAD TEST SETUP] ERROR: File {JSON_CACHE_PATH} tidak ditemukan dan DB tidak dapat diakses.")

# Antrean Thread-Safe untuk mendistribusikan Student ID secara unik ke tiap virtual user
student_queue = Queue()
for sid in all_student_ids:
    student_queue.put(sid)

# Barrier untuk mengoordinasikan "Klik Secara Bersamaan" (Concurrent Click)
barrier = gevent.event.Event()
spawned_users = 0

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
    # Jeda antar request setelah klik serentak pertama
    wait_time = between(1.0, 2.0)
    
    def on_start(self):
        """Dijalankan sekali ketika user (mahasiswa) virtual ini spawn"""
        global spawned_users
        
        # Ambil student_id unik dari antrean
        try:
            self.student_id = student_queue.get_nowait()
        except Exception:
            self.student_id = random.choice(all_student_ids)
            
        self.token = generate_student_token(self.student_id)
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        # Hitung jumlah user yang sudah spawn
        spawned_users += 1
        if spawned_users >= TARGET_CONCURRENCY:
            # Jika user ke-200 sudah spawn, picu agar semua klik secara serentak
            print(f"[LOCUST] {spawned_users} user telah siap. Memulai eksekusi serentak...")
            barrier.set()

    @task
    def execute_test_case(self):
        """Aksi utama: mahasiswa klik tombol 'Eksekusi Test Case' secara concurrent"""
        # Tunggu sampai semua (200) user selesai spawn
        barrier.wait()
        
        response = self.client.post(
            f"/modul/run/{ID_TOPIK_MODUL}",
            headers=self.headers
        )
        if response.status_code != 200:
            print(f"Failed execution: {response.status_code} - {response.text}")
            
        # Berhenti otomatis setelah 1x klik serentak per mahasiswa
        raise StopUser()