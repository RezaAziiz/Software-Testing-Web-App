# models/teacher.py
from sqlalchemy import (
    Column,
    Integer,
    MetaData,
    String,
    Table,
)
from sqlalchemy.sql.sqltypes import Date

metadata = MetaData()
Teacher = Table(
    "ms_teacher", metadata,
    Column("ms_teacher_id", String(255), primary_key=True, index=True),
    Column("ms_teacher_kode_dosen", String(20)),
    Column("ms_teacher_name", String(255)),
    Column("isactive", String(1)),
    Column("ms_teacher_password", String(255)),
    Column("ms_teacher_current_token", String(512)),
    Column("ms_teacher_token", String(5)),
    Column("createdby", String(255)),
    Column("created", Date()),
    Column("updatedby", String(255)),
    Column("updated", Date()),
)