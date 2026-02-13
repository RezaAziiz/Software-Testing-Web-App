from sqlalchemy import (
    Column,
    MetaData,
    String,
    Table,
)
from sqlalchemy.sql.sqltypes import DateTime

metadata = MetaData()
TrEdge = Table(
    "tr_cfg_edge", metadata,
    Column("tr_id_edge", String(255), primary_key=True, index=True),
    Column("tr_id_topik_modul", String(255)),
    Column("tr_id_student", String(255)),
    Column("tr_status", String(1)), 
    Column("createdby", String(255)),
    Column("created", DateTime()),
    Column("updatedby", String(255)),
    Column("updated", DateTime()),
)