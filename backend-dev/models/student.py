# models/student.py
from sqlalchemy import (
    Column,
    Integer,
    MetaData,
    String,
    Table,
)
from sqlalchemy.sql.sqltypes import Date

metadata = MetaData()
Student = Table(
    "ms_student", metadata,
    Column("ms_student_id", String(255), primary_key=True, index=True),
    Column("isactive", String(1)),
    Column("ms_student_nim", String(20)), #Nomor Induk Mahasiswa
    Column("ms_student_name", String(255)),
    Column("ms_student_kelas", String(255)),
    Column("ms_student_prodi", String(255)),
    Column("ms_student_password", String(255)),
    Column("ms_student_current_token", String(512)),
    Column("ms_student_token", String(100)),
    Column("createdby", String(255)),
    Column("created", Date()),
    Column("updatedby", String(255)),
    Column("updated", Date()),
)