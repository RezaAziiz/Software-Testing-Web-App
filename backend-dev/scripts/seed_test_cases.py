import os
import sys
import uuid
import json
from datetime import datetime

# Add backend-dev to path so we can import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.database import conn
from models.student import Student
from models.test_case import TestCase

def seed_test_cases():
    print("Mulai seeding test case untuk 59 mahasiswa...")
    id_topik_modul = '30febb1f-cb72-424b-8b3d-b558bbb4f1ed'
    
    # Ambil semua mahasiswa (atau filter berdasarkan batch jika perlu, di sini kita ambil semua yang isactive='Y')
    query = Student.select().where(Student.c.isactive == 'Y')
    students = conn.execute(query).fetchall()
    
    if not students:
        print("Tidak ada data mahasiswa aktif yang ditemukan. Pastikan sudah import ms_student.sql")
        return
        
    print(f"Ditemukan {len(students)} mahasiswa aktif.")
    
    test_cases_inserted = 0
    
    for idx, student in enumerate(students):
        student_id = student.ms_student_id
        
        # Cek apakah sudah ada test case untuk student ini di topik ini
        check_query = TestCase.select().where(
            TestCase.c.tr_id_topik_modul == id_topik_modul,
            TestCase.c.tr_student_id == student_id
        )
        existing = conn.execute(check_query).fetchone()
        
        if existing:
            print(f"[{idx+1}/{len(students)}] Student {student.ms_student_name} sudah memiliki test case. Melewati...")
            continue
            
        # Jika belum ada, buat test case baru (Test Ganjil/Genap Pilihan A)
        data_input = [
            {"param_type": "char", "param_value": "A"},
            {"param_type": "int", "param_value": "10"}
        ]
        
        test_case_data = {
            "tr_id_test_case": str(uuid.uuid4()),
            "tr_id_topik_modul": id_topik_modul,
            "tr_student_id": student_id,
            "tr_no": 1,
            "tr_object_pengujian": "testGenapPilihanA",
            "tr_data_test_input": json.dumps(data_input),
            "tr_expected_result": "bil (10) adalah bilangan Genap",
            "tr_test_result": None,
            "createdby": "seeder",
            "created": datetime.today(),
            "updatedby": "seeder",
            "updated": datetime.today()
        }
        
        conn.execute(TestCase.insert().values(**test_case_data))
        test_cases_inserted += 1
        print(f"[{idx+1}/{len(students)}] Berhasil insert test case untuk {student.ms_student_name}")
        
    print(f"Selesai! {test_cases_inserted} test cases berhasil di-seed.")

if __name__ == "__main__":
    seed_test_cases()
