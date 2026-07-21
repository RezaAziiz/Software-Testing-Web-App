import sys
import os
import uuid
import json
from datetime import datetime

# Add the backend-dev directory to python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.database import conn
from sqlalchemy import text
from models.test_case import TestCase

ID_TOPIK_MODUL = "45feae30-d562-456b-b204-ec45a9b81bb3"

test_case_data = [
    {"no": 1, "obj": "TC1", "huruf": "a", "expected": "true"},
    {"no": 2, "obj": "TC2", "huruf": "A", "expected": "true"},
    {"no": 3, "obj": "TC3", "huruf": "I", "expected": "true"},
    {"no": 4, "obj": "TC4", "huruf": "i", "expected": "true"},
    {"no": 5, "obj": "TC5", "huruf": "U", "expected": "true"},
    {"no": 6, "obj": "TC6", "huruf": "u", "expected": "true"},
    {"no": 7, "obj": "TC7", "huruf": "e", "expected": "true"},
    {"no": 8, "obj": "TC8", "huruf": "E", "expected": "true"},
    {"no": 9, "obj": "TC9", "huruf": "O", "expected": "true"},
    {"no": 10, "obj": "TC10", "huruf": "o", "expected": "true"},
    {"no": 11, "obj": "TC11", "huruf": "B", "expected": "false"}
]

def seed():
    # Dapatkan semua student ID
    students = conn.execute(text('SELECT ms_student_id FROM ms_student')).fetchall()
    student_ids = [row[0] for row in students]
    
    print(f"Ditemukan {len(student_ids)} mahasiswa.")
    
    # Hapus data lama untuk topik ini agar tidak duplikat
    conn.execute(text(f"DELETE FROM tr_test_case_modul WHERE tr_id_topik_modul = '{ID_TOPIK_MODUL}'"))
    
    total_inserted = 0
    now = datetime.now()
    
    # Suntikkan test case baru
    for student_id in student_ids:
        for tc in test_case_data:
            input_json = json.dumps([{
                "param_name": "huruf", 
                "param_type": "char", 
                "param_value": tc["huruf"]
            }])
            expected_val = tc["expected"] # Langsung nilai string 'true' / 'false'
            
            stmt = TestCase.insert().values(
                tr_id_test_case=str(uuid.uuid4()),
                tr_id_topik_modul=ID_TOPIK_MODUL,
                tr_student_id=student_id,
                tr_no=tc["no"],
                tr_object_pengujian=tc["obj"],
                tr_data_test_input=input_json,
                tr_expected_result=expected_val,
                tr_test_result=None,
                createdby="SYSTEM_SEED",
                created=now,
                updatedby="SYSTEM_SEED",
                updated=now
            )
            conn.execute(stmt)
            total_inserted += 1
            
    print(f"Sukses menyuntikkan {total_inserted} test case untuk {len(student_ids)} mahasiswa!")

if __name__ == "__main__":
    seed()
