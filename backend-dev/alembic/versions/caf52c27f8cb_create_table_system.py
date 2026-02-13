"""create table system

Revision ID: caf52c27f8cb
Revises: 93fae10afc47
Create Date: 2023-05-10 07:21:57.009727

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'caf52c27f8cb'
down_revision = None
branch_labels = None
depends_on = None

active_type_enum = sa.Enum("Y", "N", name="activetypeenum")
def upgrade():
    pgw = op.create_table(
        "ms_system",
        sa.Column("ms_system_category", sa.String(100), primary_key=True),
        sa.Column("ms_system_sub_category", sa.String(100), primary_key=True),
        sa.Column("ms_system_cd", sa.String(100), primary_key=True),
        sa.Column("ms_system_value", sa.String(255), nullable=False),
        sa.Column("ms_system_description", sa.String(255), nullable=True),
        sa.Column("isactive", active_type_enum, nullable=False, server_default='Y'),
        sa.Column("createdby", sa.String(255), nullable=False, server_default='1'),
        sa.Column("created", sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp()),
        sa.Column("updatedby", sa.String(255), nullable=False, server_default='1'),
        sa.Column("updated", sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp())
    )
    op.bulk_insert(
        pgw,
        [
            # Tingkat Kesulitan
            {
            "ms_system_category" : "modul",
            "ms_system_sub_category" : "tingkat_kesulitan",
            "ms_system_cd" : "1",
            "ms_system_value" : "Sangat Mudah",
            "ms_system_description" : "Tingkat Kesulitan Sangat Mudah"
            },
            {
            "ms_system_category" : "modul",
            "ms_system_sub_category" : "tingkat_kesulitan",
            "ms_system_cd" : "2",
            "ms_system_value" : "Mudah",
            "ms_system_description" : "Tingkat Kesulitan Mudah"
            },
            {
            "ms_system_category" : "modul",
            "ms_system_sub_category" : "tingkat_kesulitan",
            "ms_system_cd" : "3",
            "ms_system_value" : "Sedang",
            "ms_system_description" : "Tingkat Kesulitan Sedang"
            },
            {
            "ms_system_category" : "modul",
            "ms_system_sub_category" : "tingkat_kesulitan",
            "ms_system_cd" : "4",
            "ms_system_value" : "Sulit",
            "ms_system_description" : "Tingkat Kesulitan Sulit"
            },
            {
            "ms_system_category" : "modul",
            "ms_system_sub_category" : "param_validation",
            "ms_system_cd" : "1",
            "ms_system_value" : "{\"nama_rule\":\"range\",\"id_rule\":\"1\",\"jml_param\":\"2\",\"min_value\":\"\",\"max_value\":\"\"}",
            "ms_system_description" : "Range Value"
            },
            {
            "ms_system_category" : "modul",
            "ms_system_sub_category" : "param_validation",
            "ms_system_cd" : "2",
            "ms_system_value" : "{\"nama_rule\":\"condition\",\"id_rule\":\"2\",\"jml_param\":\"2\",\"condition\":\"\",\"value\":\"\"}",
            "ms_system_description" : "Condition Value"
            },
            {
            "ms_system_category" : "modul",
            "ms_system_sub_category" : "param_validation",
            "ms_system_cd" : "3",
            "ms_system_value" : "{\"nama_rule\":\"enumerasi\",\"id_rule\":\"3\",\"jml_param\":\"1\",\"value\":\"\"}",
            "ms_system_description" : "Enumerasi"
            },
            {
            "ms_system_category" : "modul",
            "ms_system_sub_category" : "param_validation",
            "ms_system_cd" : "4",
            "ms_system_value" : "{\"nama_rule\":\"countOfLength\",\"id_rule\":\"4\",\"jml_param\":\"2\",\"min_value\":\"\",\"max_value\":\"\"}",
            "ms_system_description" : "Count Of Length"
            },
            {
            "ms_system_category" : "modul",
            "ms_system_sub_category" : "jenis_modul",
            "ms_system_cd" : "F",
            "ms_system_value" : "Function",
            "ms_system_description" : "Jenis Modul Function"
            },
            {
            "ms_system_category" : "rule_option",
            "ms_system_sub_category" : "condition",
            "ms_system_cd" : ">",
            "ms_system_value" : ">",
            "ms_system_description" : "Lebih Besar"
            },
            {
            "ms_system_category" : "rule_option",
            "ms_system_sub_category" : "condition",
            "ms_system_cd" : "<",
            "ms_system_value" : "<",
            "ms_system_description" : "Lebih Kecil"
            },
            {
            "ms_system_category" : "rule_option",
            "ms_system_sub_category" : "condition",
            "ms_system_cd" : "<=",
            "ms_system_value" : "<=",
            "ms_system_description" : "Lebih Kecil Sama Dengan"
            },
            {
            "ms_system_category" : "rule_option",
            "ms_system_sub_category" : "condition",
            "ms_system_cd" : ">=",
            "ms_system_value" : ">=",
            "ms_system_description" : "Lebih Besar Sama Dengan"
            },
             {
            "ms_system_category" : "rule_option",
            "ms_system_sub_category" : "condition",
            "ms_system_cd" : "=",
            "ms_system_value" : "=",
            "ms_system_description" : "Sama Dengan"
            },
            {
            "ms_system_category" : "rule_option",
            "ms_system_sub_category" : "condition",
            "ms_system_cd" : "!=",
            "ms_system_value" : "!=",
            "ms_system_description" : "Tidak Sama Dengan"
            },
            {
            "ms_system_category" : "rule_data_type",
            "ms_system_sub_category" : "condition_list",
            "ms_system_cd" : "int",
            "ms_system_value" : "('>','>=','=','!=','<=','<')",
            "ms_system_description" : "list condition untuk integer"
            },
            {
            "ms_system_category" : "rule_data_type",
            "ms_system_sub_category" : "condition_list",
            "ms_system_cd" : "float",
            "ms_system_value" : "('>','>=','=','!=','<=','<')",
            "ms_system_description" : "list condition untuk float"
            },
            {
            "ms_system_category" : "rule_data_type",
            "ms_system_sub_category" : "condition_list",
            "ms_system_cd" : "char",
            "ms_system_value" : "('=','!=')",
            "ms_system_description" : "list condition untuk char"
            },
            {
            "ms_system_category" : "rule_data_type",
            "ms_system_sub_category" : "condition_list",
            "ms_system_cd" : "boolean",
            "ms_system_value" : "('=','!=')",
            "ms_system_description" : "list condition untuk boolean"
            },
             {
            "ms_system_category" : "rule_data_type",
            "ms_system_sub_category" : "condition_list",
            "ms_system_cd" : "String",
            "ms_system_value" : "('=','!=')",
            "ms_system_description" : "list condition untuk string"
            },
            {
            "ms_system_category" : "modul",
            "ms_system_sub_category" : "data_type",
            "ms_system_cd" : "String",
            "ms_system_value" : "String",
            "ms_system_description" : "data type String"
            },
            {
            "ms_system_category" : "modul",
            "ms_system_sub_category" : "data_type",
            "ms_system_cd" : "char",
            "ms_system_value" : "char",
            "ms_system_description" : "data type char"
            },
            {
            "ms_system_category" : "modul",
            "ms_system_sub_category" : "data_type",
            "ms_system_cd" : "boolean",
            "ms_system_value" : "boolean",
            "ms_system_description" : "data type boolean"
            },
             {
            "ms_system_category" : "modul",
            "ms_system_sub_category" : "data_type",
            "ms_system_cd" : "int",
            "ms_system_value" : "int",
            "ms_system_description" : "data type int"
            },
             {
            "ms_system_category" : "modul",
            "ms_system_sub_category" : "data_type",
            "ms_system_cd" : "float",
            "ms_system_value" : "float",
            "ms_system_description" : "data type float"
            },
             {
            "ms_system_category" : "common",
            "ms_system_sub_category" : "minimum_value",
            "ms_system_cd" : "coverage",
            "ms_system_value" : "80",
            "ms_system_description" : "minimum value coverage"
            },
            {
            "ms_system_category" : "rule_data_type",
            "ms_system_sub_category" : "validation_list",
            "ms_system_cd" : "boolean",
            "ms_system_value" : "('2')",
            "ms_system_description" : "List Validasi untuk tipe data boolean"
            },
            {
            "ms_system_category" : "rule_data_type",
            "ms_system_sub_category" : "validation_list",
            "ms_system_cd" : "float",
            "ms_system_value" : "('1','2','3')",
            "ms_system_description" : "List Validasi untuk tipe data float"
            },
            {
            "ms_system_category" : "rule_data_type",
            "ms_system_sub_category" : "validation_list",
            "ms_system_cd" : "char",
            "ms_system_value" : "('2','3')",
            "ms_system_description" : "List Validasi untuk tipe data char"
            },
            {
            "ms_system_category" : "rule_data_type",
            "ms_system_sub_category" : "validation_list",
            "ms_system_cd" : "String",
            "ms_system_value" : "('2','3','4')",
            "ms_system_description" : "List Validasi untuk tipe data String"
            },
            {
            "ms_system_category" : "rule_data_type",
            "ms_system_sub_category" : "validation_list",
            "ms_system_cd" : "int",
            "ms_system_value" : "('1','2','3','4')",
            "ms_system_description" : "List Validasi untuk tipe data int"
            },
        ]
    )


def downgrade():
    op.drop_table('ms_system')