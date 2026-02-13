"""ceate table ms cfg edge

Revision ID: 07cf33e3341a
Revises: ff6c3937b93a
Create Date: 2024-05-05 10:54:29.916145

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '07cf33e3341a'
down_revision = 'ff6c3937b93a'
branch_labels = None
depends_on = None



def upgrade():
    pgw = op.create_table(
        "ms_cfg_edge",
        sa.Column("ms_id_edge", sa.String(255), primary_key=True, index=True),
        sa.Column("ms_id_modul", sa.String(255), nullable=False),
        sa.Column("ms_id_start_node", sa.String(255), nullable=False),
        sa.Column("ms_id_finish_node", sa.String(255), nullable=False),
        sa.Column("ms_label", sa.String(255), nullable=False), 
        sa.Column("createdby", sa.String(255), nullable=False, server_default='1'),
        sa.Column("created", sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp()),
        sa.Column("updatedby", sa.String(255), nullable=False, server_default='1'),
        sa.Column("updated", sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp()),     
    )

def downgrade():
    op.drop_table('ms_cfg_edge')