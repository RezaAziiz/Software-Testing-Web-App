"""ceate table tr cfg edge

Revision ID: b955425bbdf1
Revises: ca51309275cc
Create Date: 2024-05-05 11:21:50.890264

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b955425bbdf1'
down_revision = 'ca51309275cc'
branch_labels = None
depends_on = None

status_type_enum = sa.Enum("Y", "N", name="statustypeenum")
def upgrade():
    pgw = op.create_table(
        "tr_cfg_edge",
        sa.Column("tr_id_edge", sa.String(255), primary_key=True, index=True),
        sa.Column("tr_id_topik_modul", sa.String(255),  primary_key=True, index=True),
        sa.Column("tr_id_student", sa.String(255), primary_key=True, index=True),
        sa.Column("tr_status", status_type_enum, nullable=False, server_default='N'), #Y=Executed N=Not Executed
        sa.Column("createdby", sa.String(255), nullable=False, server_default='1'),
        sa.Column("created", sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp()),
        sa.Column("updatedby", sa.String(255), nullable=False, server_default='1'),
        sa.Column("updated", sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp()),     
    )

def downgrade():
    op.drop_table('tr_cfg_edge')