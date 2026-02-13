"""ceate table tr cfg node

Revision ID: ca51309275cc
Revises: b02deb1f2b0a
Create Date: 2024-05-05 11:19:20.667573

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ca51309275cc'
down_revision = 'b02deb1f2b0a'
branch_labels = None
depends_on = None


status_type_enum = sa.Enum("Y", "N", "S", name="statustypeenum")
def upgrade():
    pgw = op.create_table(
        "tr_cfg_node",
        sa.Column("tr_id_node", sa.String(255), primary_key=True, index=True),
        sa.Column("tr_id_topik_modul", sa.String(255),  primary_key=True, index=True),
        sa.Column("tr_id_student", sa.String(255), primary_key=True, index=True),
        sa.Column("tr_status", status_type_enum, nullable=False, server_default='N'), #Y=Executed N=Not Executed, S=Sebagian Executed
        sa.Column("createdby", sa.String(255), nullable=False, server_default='1'),
        sa.Column("created", sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp()),
        sa.Column("updatedby", sa.String(255), nullable=False, server_default='1'),
        sa.Column("updated", sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp()),     
    )

def downgrade():
    op.drop_table('tr_cfg_node')
