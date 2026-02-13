from sqlalchemy import (
    Column,
    MetaData,
    String,
    Table,
    Integer
)
from sqlalchemy.sql.sqltypes import DateTime

metadata = MetaData()
TrNode = Table(
    "tr_cfg_node", metadata,
    Column("tr_id_node", String(255), primary_key=True, index=True),
    Column("tr_id_topik_modul", String(255)),
    Column("tr_id_student", String(255)),
    Column("tr_status", String(1)), 
    Column("createdby", String(255)),
    Column("created", DateTime()),
    Column("updatedby", String(255)),
    Column("updated", DateTime()),
)