from sqlalchemy import (
    Column,
    MetaData,
    String,
    Table,
)
from sqlalchemy.sql.sqltypes import DateTime

metadata = MetaData()
Edge = Table(
    "ms_cfg_edge", metadata,
    Column("ms_id_edge", String(255), primary_key=True, index=True),
    Column("ms_id_modul", String(255)),
    Column("ms_id_start_node", String(50)), 
    Column("ms_id_finish_node", String(255)),
    Column("ms_label", String(255)),
    Column("createdby", String(255)),
    Column("created", DateTime()),
    Column("updatedby", String(255)),
    Column("updated", DateTime()),
)