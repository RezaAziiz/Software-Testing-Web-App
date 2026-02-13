"""create table ms_student

Revision ID: df98bda87f5c
Revises: a08efd02e371
Create Date: 2023-06-12 23:59:14.451703

"""
from alembic import op
from utilities.utils import get_hashed_password
import sqlalchemy as sa
import uuid

# revision identifiers, used by Alembic.
revision = 'df98bda87f5c'
down_revision = 'caf52c27f8cb'
branch_labels = None
depends_on = None

active_type_enum = sa.Enum("Y", "N", name="activetypeenum")
gender_type_enum = sa.Enum("M", "F", name="gendertypeenum")

def upgrade():
    pgw = op.create_table(
        "ms_student",
        sa.Column("ms_student_id", sa.String(255), primary_key=True, index=True),
        sa.Column("isactive", active_type_enum, nullable=False, server_default='Y'),
        sa.Column("ms_student_nim", sa.String(20), nullable=False), #Nomor Induk Mahasiswa (NIM)
        sa.Column("ms_student_name", sa.String(255), nullable=False),
        sa.Column("ms_student_kelas", sa.String(255), nullable=False),
        sa.Column("ms_student_prodi", sa.String(255)),
        sa.Column("ms_student_password", sa.String(255), nullable=False),
        sa.Column("ms_student_current_token", sa.String(512)),
        sa.Column("ms_student_token", sa.String(5)),
        sa.Column("createdby", sa.String(255), nullable=False, server_default='1'),
        sa.Column("created", sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp()),
        sa.Column("updatedby", sa.String(255), nullable=False, server_default='1'),
        sa.Column("updated", sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp()),        
    )
    op.bulk_insert(
        pgw,
        [{
            'ms_student_id': '07501030',
            'ms_student_nim':'07501030',
            'ms_student_name':'Yuda Permana',
            'ms_student_kelas':'1 B',
            'ms_student_password': get_hashed_password('admin123!!'),
        }]
    )


def downgrade():
    op.drop_table('ms_student')
