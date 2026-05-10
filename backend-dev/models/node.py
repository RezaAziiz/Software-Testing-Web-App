from sqlalchemy import (
    Column,
    MetaData,
    String,
    Table,
    Integer
)
from sqlalchemy.sql.sqltypes import DateTime

metadata = MetaData()
Node = Table(
    "ms_cfg_node", metadata,
    Column("ms_id_node", String(255), primary_key=True, index=True),
    Column("ms_id_modul", String(255)),
    Column("ms_execution_order", Integer),
    Column("ms_line_number", Integer),
    Column("ms_line_start", Integer),
    Column("ms_line_end", Integer),
    Column("ms_source_code", String),
    Column("ms_ast_node_type", String(100)),
    Column("ms_node_type", String(50)),
    Column("createdby", String(255)),
    Column("created", DateTime()),
    Column("updatedby", String(255)),
    Column("updated", DateTime()),
)