from sqlalchemy.sql import text
from datetime import datetime
from models.penyelesaian_modul import PenyelesaianModul

class PenyelesaianRepository:
    def __init__(self, conn):
        self._conn = conn

    def find_by_topik_and_student(self, id_topik_modul: str, student_id: str):
        query = PenyelesaianModul.select().where(
            PenyelesaianModul.c.tr_id_topik_modul == id_topik_modul,
            PenyelesaianModul.c.tr_student_id == student_id
        )
        return self._conn.execute(query).fetchone()

    def upsert_execution_status(self, id_topik_modul: str, student_id: str, status_eksekusi: str, report_path: str = ""):
        """Menyimpan status eksekusi (Y/N) dan path HTML report Gradle"""
        existing = self.find_by_topik_and_student(id_topik_modul, student_id)
        now = datetime.now()
        
        if existing is None:
            query = PenyelesaianModul.insert().values(
                tr_id_topik_modul=id_topik_modul,
                tr_student_id=student_id,
                tr_tgl_mulai=now,
                tr_result_report=report_path,
                tr_tgl_eksekusi=now,
                tr_status_eksekusi=status_eksekusi,
                updated=now,
                created=now,
                updatedby=student_id,
                createdby=student_id
            )
        else:
            query = PenyelesaianModul.update().values(
                tr_tgl_eksekusi=now,
                tr_status_eksekusi=status_eksekusi,
                updated=now,
                updatedby=student_id,
            ).where(
                PenyelesaianModul.c.tr_id_topik_modul == id_topik_modul,
                PenyelesaianModul.c.tr_student_id == student_id
            )
        self._conn.execute(query)

    def update_coverage_and_score(self, id_topik_modul: str, student_id: str, coverage: float, nilai: float, status_penyelesaian: str, coverage_report: str = ""):
        """Menyimpan nilai coverage JaCoCo dan nilai akhir mahasiswa"""
        now = datetime.now()
        query = PenyelesaianModul.update().values(
            tr_persentase_coverage=coverage,
            tr_nilai=nilai,
            tr_status_penyelesaian=status_penyelesaian,
            tr_coverage_report=coverage_report,
            tr_tgl_selesai=now if status_penyelesaian == 'Y' else None,
            updated=now,
            updatedby=student_id,
        ).where(
            PenyelesaianModul.c.tr_id_topik_modul == id_topik_modul,
            PenyelesaianModul.c.tr_student_id == student_id
        )
        self._conn.execute(query)