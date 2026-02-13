# models/student.py
from sqlalchemy import (
    Column,
    Integer,
    MetaData,
    String,
    Table,
    Text
)
from sqlalchemy.sql.sqltypes import Date

metadata = MetaData()
Modul = Table(
    "ms_modul_program", metadata,
    Column("ms_id_modul", String(255), primary_key=True, index=True),
    Column("ms_jenis_modul", String(1)),
    Column("ms_nama_modul", String(50)), 
    Column("ms_deskripsi_modul", Text),
    Column("ms_source_code", String(255)),
    Column("ms_class_name", String(255)),
    Column("ms_function_name", String(255)),
    Column("ms_return_type", String(255)),
    Column("ms_jml_parameter", Integer),
    Column("ms_tingkat_kesulitan", String(512)),
    Column("ms_cc", Integer),
    Column("createdby", String(255)),
    Column("created", Date()),
    Column("updatedby", String(255)),
    Column("updated", Date()),
)