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
ParamModul = Table(
    "ms_modul_parameter", metadata,
    Column("ms_id_parameter", String(255), primary_key=True, index=True),
    Column("ms_id_modul", String(255)),
    Column("ms_nama_parameter", String(255)), 
    Column("ms_tipe_data", String(50)),
    Column("ms_rules", Text),
    Column("no_urut", Integer),
    Column("createdby", String(255)),
    Column("created", Date()),
    Column("updatedby", String(255)),
    Column("updated", Date()),
)