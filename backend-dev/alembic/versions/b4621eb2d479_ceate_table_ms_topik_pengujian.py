"""ceate table ms topik pengujian

Revision ID: b4621eb2d479
Revises: e8ace6cc1ac1
Create Date: 2024-05-05 10:11:56.197304

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b4621eb2d479'
down_revision = 'e8ace6cc1ac1'
branch_labels = None
depends_on = None


status_type_enum = sa.Enum("D", "P", name="statustypeenum")
def upgrade():
    pgw = op.create_table(
        "ms_topik_pengujian",
        sa.Column("ms_id_topik", sa.String(255), primary_key=True, index=True),
        sa.Column("status", status_type_enum, nullable=False, server_default='D'), #D=Draft P=Publish
        sa.Column("ms_kode_enroll", sa.String(20)), 
        sa.Column("ms_nama_topik", sa.String(255), nullable=False),
        sa.Column("ms_deskripsi_topik",sa.String(255)),
        sa.Column("createdby", sa.String(255), nullable=False, server_default='1'),
        sa.Column("created", sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp()),
        sa.Column("updatedby", sa.String(255), nullable=False, server_default='1'),
        sa.Column("updated", sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp()),     
    )


def downgrade():
    op.drop_table('ms_topik_pengujian')
