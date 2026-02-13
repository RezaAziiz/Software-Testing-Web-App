# models/student.py
from sqlalchemy import (
    Column,
    MetaData,
    String,
    Table,
    Integer
)
from sqlalchemy.sql.sqltypes import DateTime

metadata = MetaData()
TopikModul = Table(
    "ms_topik_modul", metadata,
    Column("ms_id_topik_modul", String(255), primary_key=True, index=True),
    Column("ms_id_topik", String(255)),
    Column("ms_id_modul",  String(255)),
    Column("ms_no",  Integer),
    Column("createdby", String(255)),
    Column("created", DateTime()),
    Column("updatedby", String(255)),
    Column("updated", DateTime()),
)