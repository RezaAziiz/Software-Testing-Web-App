# models/student.py
from sqlalchemy import (
    Column,
    MetaData,
    String,
    Table,
)
from sqlalchemy.sql.sqltypes import DateTime

metadata = MetaData()
Topik = Table(
    "ms_topik_pengujian", metadata,
    Column("ms_id_topik", String(255), primary_key=True, index=True),
    Column("status", String(1)),
    Column("ms_kode_enroll", String(20)), 
    Column("ms_nama_topik", String(255)),
    Column("ms_deskripsi_topik", String(255)),
    Column("createdby", String(255)),
    Column("created", DateTime()),
    Column("updatedby", String(255)),
    Column("updated", DateTime()),
)