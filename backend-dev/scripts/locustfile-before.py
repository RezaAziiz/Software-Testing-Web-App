from locust import HttpUser, task, between
from locust.exception import StopUser
from jose import jwt
from datetime import datetime, timedelta
import gevent.event
import random
import uuid
from queue import Queue
import sys
import os
import json

# Konfigurasi Token (diambil dari .env)
SECRET_KEY = "secret"
ALGORITHM = "HS256"

# Data untuk Load Test (Topik Modul DecimalToRoman)
ID_TOPIK_MODUL = "fdcf55b0-a7ba-45e4-8a69-073fa8466faa"

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Persiapan maksimal jumlah dummy untuk dicadangkan di DB (500 sudah cukup untuk test s.d 500 user)
MAX_DUMMY_USERS = 1
JSON_CACHE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dummy_students.json")

all_student_ids = []

try:
    from config.database import engine
    from sqlalchemy import text
    
    # 1. Coba koneksi ke Database & Lakukan Seeding jika DB dapat dijangkau
    with engine.connect() as db_conn:
        if os.path.exists(JSON_CACHE_PATH):
            print(f"[LOAD TEST SETUP] File {JSON_CACHE_PATH} ditemukan. Melewati proses seeding DB...")
            with open(JSON_CACHE_PATH, "r") as f:
                all_student_ids = json.load(f)
            print(f"[LOAD TEST SETUP] Berhasil memuat {len(all_student_ids)} Student IDs dari file lokal.")
        else:
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
                    (1, "Konversi angka 1", '[{"param_name": "bilangan", "param_type": "int", "param_value": "1"}]', 'I', "P"),
                    (2, "Konversi angka 4", '[{"param_name": "bilangan", "param_type": "int", "param_value": "4"}]', 'IV', "P"),
                    (3, "Konversi angka 5", '[{"param_name": "bilangan", "param_type": "int", "param_value": "5"}]', 'V', "P"),
                    (4, "Konversi angka 9", '[{"param_name": "bilangan", "param_type": "int", "param_value": "9"}]', 'IX', "P"),
                    (5, "Konversi angka 10", '[{"param_name": "bilangan", "param_type": "int", "param_value": "10"}]', 'X', "P"),
                    (6, "Konversi angka 40", '[{"param_name": "bilangan", "param_type": "int", "param_value": "40"}]', 'XL', "P"),
                    (7, "Konversi angka 50", '[{"param_name": "bilangan", "param_type": "int", "param_value": "50"}]', 'L', "P"),
                    (8, "Konversi angka 90", '[{"param_name": "bilangan", "param_type": "int", "param_value": "90"}]', 'XC', "P"),
                    (9, "Konversi angka 400", '[{"param_name": "bilangan", "param_type": "int", "param_value": "400"}]', 'CD', "P"),
                    (10, "Konversi angka 1994", '[{"param_name": "bilangan", "param_type": "int", "param_value": "1994"}]', 'MCMXCIV', "P")
                ]
    
            print(f"[LOAD TEST SETUP] Membuat {MAX_DUMMY_USERS} dummy students ke DB...")
            hashed_pwd = "$2b$12$tGgYpT.R/P/4gC9tZ.Vz9eJd9pYy8u2d/f.6e2y5d8u3d/F.F.G.G"
            
            with engine.begin() as transaction_conn:
                for i in range(MAX_DUMMY_USERS):
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
    
            # Simpan daftar student ID ke dummy_students.json agar laptop teman/tester bisa pakai tanpa DB
            with open(JSON_CACHE_PATH, "w") as f:
                json.dump(all_student_ids, f)
            print(f"[LOAD TEST SETUP] Berhasil menyimpan {len(all_student_ids)} Student IDs ke {JSON_CACHE_PATH}")
            
            # Tutup engine DB secara manual untuk mencegah warning 'greenlet is being finalized'
            engine.dispose()

except Exception as e:
    print(f"[LOAD TEST SETUP] Koneksi DB / Module tidak tersedia ({type(e).__name__}: {e}).")
    print(f"[LOAD TEST SETUP] Membaca dari {JSON_CACHE_PATH}...")
    if os.path.exists(JSON_CACHE_PATH):
        with open(JSON_CACHE_PATH, "r") as f:
            all_student_ids = json.load(f)
        print(f"[LOAD TEST SETUP] Berhasil memuat {len(all_student_ids)} Student IDs dari file lokal.")
    else:
        print(f"[LOAD TEST SETUP] ERROR: File {JSON_CACHE_PATH} tidak ditemukan dan DB tidak dapat diakses.")
        # Fallback ke data hardcode
        all_student_ids = [
            "761bced5-cbf1-4e25-b43f-9c68425fe9be", "befe23fd-7944-47b4-8353-a32ee103c43d", 
            "3faaa480-4b32-4d5c-8933-945bd82c707e", "7ba99e9c-96be-4e17-b4f3-df0e8e676a9a", 
            "b7df7ba4-1a45-4d0a-9293-6d2d62650374", "04097a6a-5ef7-4bf5-80c4-71137e68d437", 
            "e204119a-7bea-483e-a3d0-7d51c60609db", "367ee33c-80b5-47b5-8490-aad9fdda01f3", 
            "70bfc65d-0354-49c9-9fcb-c23461a33149", "3404e6e1-3b8b-40e5-aaf2-088fb080573a", 
            "72d5b7ba-0d7e-4211-89c1-f6aab372b049", "a55200ee-8223-4d8e-9aa1-fa1ba553f19f", 
            "e60e0f59-f7c2-40d4-b426-50a16e8d4d0e", "cca4cba6-f741-4e10-8edd-cfc2b33f0870", 
            "eebe43ec-2fed-4acf-89cf-c28fb757c228", "49232b5c-01e7-42f9-9988-03912c4d3d76", 
            "bc2dec1c-43bf-40b9-ae3a-dd290b3b0e5c", "08e60354-e7fa-4925-825e-69c83947f08c", 
            "38021330-b2f9-40a0-ab96-ca0abaa2b841", "2206d446-4ffc-4fa8-8e9a-1f9a566af4c4", 
            "3d8df2eb-e357-4ac3-a83f-56b954276c71", "0bf2419c-f79d-43a1-a985-aab188c73358", 
            "a4f1a7c0-a966-44af-a995-b526a2a5591a", "8f7ca45b-68ce-405e-8305-c131e82aec13", 
            "a65bfae7-300e-45c2-ad74-76ea38aa94b1", "77896ce6-3105-4def-a41a-82bd0cecb772", 
            "cc386122-0a7b-4735-8516-e4366a98a407", "83dd3471-439e-41ce-b53c-fe7740ffea3f", 
            "d187d175-2618-4bc5-a880-f73cde0e003c", "79725c4b-0a63-433d-9966-61c1cbda6016", 
            "dd5630cb-ce06-4fbe-bfe9-e31499d7fdb8", "e39af2cd-1df8-4e2e-ad89-c4b407f286b8", 
            "f34e7b81-38a8-4ea8-a121-1daf29a8fb31", "f9383d36-df1b-49a9-9fc5-541fa92858f8", 
            "0b9aa29f-fe41-4176-9c5f-ec1ba0be45f2", "8f5a4cdd-f0aa-4661-b3fa-151dff19e68f", 
            "e48541f3-600b-4b3f-8580-7639ffe71c98", "b9b0dd2d-c7f8-4773-89f5-e4a86d672d88", 
            "b0879c8d-4755-4758-82e6-40e21d61e018", "ec2f578d-12cd-4f6c-a2b5-83d033f6e08e", 
            "15e3bb7f-701f-4fd2-bf02-d935b65eeaf9", "bb35060f-74fa-4b5d-8c4f-5a5bb58a6311", 
            "4046109e-dbe7-47fc-9b82-2f4cd189c7b9", "0d70f78c-8a2b-456f-adfc-cc1653badb74", 
            "22ba924d-f13e-474b-a228-a82a164dea00", "5f37a727-a614-44d5-814e-fb277629ed7e", 
            "5b3373e5-b1f8-488e-8aee-b392a5395386", "3d9c1d10-a81f-4ca0-b1e2-d5eac4ab6e2f", 
            "d1e0cbe7-3a4b-4b27-b9da-e5bfe5ee1ba0", "64a36fad-225a-4187-a79c-2ae47b22b3d7"
        ]
        print(f"[LOAD TEST SETUP] Menggunakan {len(all_student_ids)} data dummy secara hardcode sebagai Fallback.")

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
            self.student_id = random.choice(all_student_ids) if all_student_ids else str(uuid.uuid4())
            
        self.token = generate_student_token(self.student_id)
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        # Hitung jumlah user yang sudah spawn
        spawned_users += 1
        
        # Ambil target concurrent users dari environment Locust (contoh: locust --users 100)
        target = self.environment.runner.target_user_count if self.environment.runner else 50
        if target is None or target == 0:
            target = 50
            
        if spawned_users >= target:
            # Jika user ke-X (sesuai target) sudah spawn, picu agar semua klik secara serentak
            print(f"[LOCUST] {spawned_users}/{target} user telah siap. Memulai eksekusi serentak...")
            barrier.set()

    @task
    def execute_test_case(self):
        """Aksi utama: mahasiswa klik tombol 'Eksekusi Test Case' secara concurrent"""
        # Tunggu sampai semua user selesai spawn
        barrier.wait()
        
        response = self.client.post(
            f"/modul/run/{ID_TOPIK_MODUL}",
            headers=self.headers
        )
        if response.status_code != 200:
            print(f"Failed execution: {response.status_code} - {response.text}")
            
        # Berhenti otomatis setelah 1x klik serentak per mahasiswa
        raise StopUser()
