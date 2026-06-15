from sqlalchemy.sql import text
from datetime import datetime
from models.test_case import TestCase

class TestCaseRepository:
    def __init__(self, conn):
        self._conn = conn

    def find_by_topik_and_student(self, id_topik_modul: str, student_id: str) -> list:
        """Digunakan oleh TestExecutionService & TestCodeGenerator untuk mengambil data test case"""
        query = TestCase.select().where(
            TestCase.c.tr_id_topik_modul == id_topik_modul, 
            TestCase.c.tr_student_id == student_id
        ).order_by(TestCase.c.tr_no.asc())
        return self._conn.execute(query).fetchall()

    def update_result(self, id_topik_modul: str, student_id: str, object_pengujian: str, result_status: str) -> None:
        """Digunakan oleh TestExecutionService untuk mengupdate status P/F setelah parsing XML JUnit"""
        now = datetime.now()
        
        # Object pengujian dari JUnit biasanya mengubah spasi jadi underscore, jadi kita standarisasi
        formatted_object_name = object_pengujian.replace("_", " ")
        
        query = TestCase.update().values(
            tr_test_result=result_status,
            updated=now,
            updatedby=student_id,
        ).where(
            TestCase.c.tr_id_topik_modul == id_topik_modul, 
            TestCase.c.tr_student_id == student_id, 
            TestCase.c.tr_object_pengujian == formatted_object_name
        )
        self._conn.execute(query)

    
    def find_by_id(self, id_test_case: str):
        query = TestCase.select().where(TestCase.c.tr_id_test_case == id_test_case)
        return self._conn.execute(query).fetchone()

    def insert(self, data: dict) -> None:
        self._conn.execute(TestCase.insert().values(**data))

    def update(self, id_test_case: str, data: dict) -> None:
        self._conn.execute(TestCase.update().values(**data).where(TestCase.c.tr_id_test_case == id_test_case))

    def delete(self, id_test_case: str) -> None:
        self._conn.execute(TestCase.delete().where(TestCase.c.tr_id_test_case == id_test_case))

    def find_duplicate(self, id_topik_modul: str, object_pengujian: str, student_id: str, exclude_id: str = None):
        """Mencari apakah ada test case dengan object pengujian yang sama milik siswa ini"""
        query = TestCase.select().where(
            TestCase.c.tr_id_topik_modul == id_topik_modul,
            TestCase.c.tr_object_pengujian == object_pengujian,
            TestCase.c.tr_student_id == student_id
        )
        if exclude_id:
            # Pengecualian ini dipakai saat mode Update (Edit)
            query = query.where(TestCase.c.tr_id_test_case != exclude_id)
            
        return self._conn.execute(query).fetchone()
    
    def get_statistics_by_topik_and_student(self, id_topik_modul: str, student_id: str) -> dict:
        """Mengambil agregasi jumlah test case pass/fail/total"""
        query = text("""
            SELECT COUNT(*) AS total, 
                   SUM(CASE WHEN tr_test_result = 'P' THEN 1 ELSE 0 END) as countPass, 
                   SUM(CASE WHEN tr_test_result = 'F' THEN 1 ELSE 0 END) as countFailed 
            FROM tr_test_case_modul 
            WHERE tr_id_topik_modul = :idTopikModul AND tr_student_id = :idUser
        """)
        result = self._conn.execute(query, idTopikModul=id_topik_modul, idUser=student_id).fetchone()
        
        return {
            "total": int(result['total']) if result['total'] else 0,
            "countPass": int(result['countPass']) if result['countPass'] else 0,
            "countFailed": int(result['countFailed']) if result['countFailed'] else 0
        }