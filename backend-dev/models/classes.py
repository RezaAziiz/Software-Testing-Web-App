# models/class.py
from sqlalchemy import (
    Column,
    Integer,
    MetaData,
    String,
    Table,
)
from sqlalchemy.sql.sqltypes import Date

metadata = MetaData()
Class = Table(
    "ms_class", metadata,
    Column("ms_class_id", String(255), primary_key=True, index=True),
    Column("ms_class_grade", String(10)),
    Column("ms_class_major", String(100)),
    Column("ms_class_class", String(10)),
    Column("ms_class_teacher", String(100)),
    Column("ms_class_description", String(255)),
    Column("ms_class_total_hour", String(10)),

    Column("createdby", String(255)),
    Column("created", Date()),
    Column("updatedby", String(255)),
    Column("updated", Date()),
)