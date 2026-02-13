# models/system.py
from sqlalchemy import (
    Column,
    Integer,
    MetaData,
    String,
    Table,
)
from sqlalchemy.sql.sqltypes import Date

metadata = MetaData()
System = Table(
    "ms_system", metadata,
    Column("ms_system_category", String(100), primary_key=True),
    Column("ms_system_sub_category", String(100), primary_key=True),
    Column("ms_system_cd", String(100), primary_key=True),
    Column("ms_system_value", String(255)),
    Column("ms_system_description", String(255)),
    Column("isactive", String(1)),
    Column("createdby", String(255)),
    Column("created", Date()),
    Column("updatedby", String(255)),
    Column("updated", Date()),
)