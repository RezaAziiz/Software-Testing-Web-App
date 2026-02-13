from sqlalchemy import (
    Column,
    Integer,
    MetaData,
    String,
    Table,
    Text,
    Float
)
from sqlalchemy.sql.sqltypes import Date

metadata = MetaData()
PenyelesaianModul = Table(
    "tr_penyelesaian_modul", metadata,
    Column("tr_id_topik_modul", String(255), primary_key=True, index=True),
    Column("tr_student_id", String(255), primary_key=True, index=True),
    Column("tr_nilai", Float), 
    Column("tr_tgl_mulai", Date()),
    Column("tr_tgl_selesai", Date()),
    Column("tr_persentase_coverage", Float),
    Column("tr_result_report", Text),
    Column("tr_coverage_report", Text),
    Column("tr_tgl_eksekusi", Date()),
    Column("tr_status_eksekusi", String(1)),
    Column("tr_status_penyelesaian", String(1)),
    Column("createdby", String(255)),
    Column("created", Date()),
    Column("updatedby", String(255)),
    Column("updated", Date()),
)