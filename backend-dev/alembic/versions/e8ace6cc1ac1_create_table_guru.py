"""create table guru

Revision ID: e8ace6cc1ac1
Revises: 42c364441fec
Create Date: 2023-06-12 14:55:36.898079

"""
from alembic import op
from utilities.utils import get_hashed_password
import sqlalchemy as sa
import uuid

# revision identifiers, used by Alembic.
revision = 'e8ace6cc1ac1'
down_revision = 'df98bda87f5c'
branch_labels = None
depends_on = None


active_type_enum = sa.Enum("Y", "N", name="activetypeenum")
gender_type_enum = sa.Enum("M", "F", name="gendertypeenum")
def upgrade():
    pgw = op.create_table(
        "ms_teacher",
        sa.Column("ms_teacher_id", sa.String(255), primary_key=True, index=True),
        sa.Column("ms_teacher_kode_dosen", sa.String(20), nullable=False),
        sa.Column("ms_teacher_name", sa.String(255), nullable=False),
        sa.Column("isactive", active_type_enum, nullable=False, server_default='Y'),
        sa.Column("ms_teacher_password", sa.String(255), nullable=False),
        sa.Column("ms_teacher_current_token", sa.String(512)),
        sa.Column("ms_teacher_token", sa.String(5)),
        sa.Column("createdby", sa.String(255), nullable=False, server_default='1'),
        sa.Column("created", sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp()),
        sa.Column("updatedby", sa.String(255), nullable=False, server_default='1'),
        sa.Column("updated", sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp()),
    )
    op.bulk_insert(
        pgw,
        [{
            'ms_teacher_id': '1',
            'ms_teacher_kode_dosen':'KO067N',
            'ms_teacher_name':'Asri Maspupah',
            'ms_teacher_password': get_hashed_password('admin123!!'),
        }]
    )


def downgrade():
    op.drop_table('ms_teacher')