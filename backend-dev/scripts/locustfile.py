import os
import sys
import random
from locust import HttpUser, task, events
from locust.exception import StopUser
from gevent import sleep # Import gevent sleep untuk jeda asinkron

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.database import conn
from models.student import Student
from utilities.utils import encode_jwt

student_credentials = []

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    print("Mempersiapkan JWT Tokens dari Database...")
    query = Student.select().where(Student.c.isactive == 'Y')
    
    
    students = conn.execute(query).fetchall() 
    
    if not students:
        print("ERROR: Tidak ada data mahasiswa di tabel ms_student!")
        return
        
    for student in students:
        to_encode = {
            "userid": student.ms_student_id,
            "name": student.ms_student_name,
            "nim": student.ms_student_nim,
            "login_type": "student"
        }
        token = encode_jwt(to_encode)
        student_credentials.append({
            "nim": student.ms_student_nim,
            "name": student.ms_student_name,
            "token": token
        })
    print(f"Berhasil meng-generate {len(student_credentials)} token mahasiswa.")


class LoadTestUser(HttpUser):
    
    def on_start(self):
        """Dipanggil saat satu instance user dibuat."""
        if len(student_credentials) > 0:
            self.student_data = student_credentials.pop()
            self.token = self.student_data["token"]
            self.headers = {
                "Authorization": f"Bearer {self.token}",
                "Accept": "application/json"
            }
        else:
            self.token = None
            print("WARNING: Kehabisan credentials. Locust user ini akan dihentikan.")

    @task
    def execute_test_case(self):
        if not self.token:
            raise StopUser()
            
        # Mahasiswa butuh waktu acak antara 15 detik sampai 2 menit
        # untuk membaca soal dan bikin test case sebelum klik eksekusi.
        waktu_mikir = random.randint(15, 120) 
        print(f"Mahasiswa {self.student_data['nim']} sedang merangkai test case (butuh {waktu_mikir} detik)...")
        sleep(waktu_mikir) # Jeda secara asinkron tanpa memblokir sistem
        
        id_topik_modul = '30febb1f-cb72-424b-8b3d-b558bbb4f1ed'
        url = f"/modul/run/{id_topik_modul}"
        
        # Simulasi mahasiswa menekan tombol Eksekusi Test Case
        with self.client.post(url, headers=self.headers, catch_response=True) as response:
            if response.status_code == 200:
                result = response.json()
                if result.get("status_eksekusi"):
                    response.success()
                else:
                    response.failure(f"Build gagal: {result}")
            else:
                response.failure(f"Error {response.status_code}: {response.text}")
        
        # User berhenti setelah berhasil 1x eksekusi
        raise StopUser()