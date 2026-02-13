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
TestCase = Table(
    "tr_test_case_modul", metadata,
    Column("tr_id_test_case", String(255), primary_key=True, index=True),
    Column("tr_id_topik_modul", String(255)),
    Column("tr_student_id", String(255)), 
    Column("tr_no", Integer),
    Column("tr_object_pengujian", String(50)),
    Column("tr_data_test_input", Text),
    Column("tr_expected_result", Text),
    Column("tr_test_result", String(1)),
    Column("createdby", String(255)),
    Column("created", Date()),
    Column("updatedby", String(255)),
    Column("updated", Date()),
)