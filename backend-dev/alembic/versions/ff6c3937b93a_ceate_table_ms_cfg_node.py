"""ceate table ms cfg node

Revision ID: ff6c3937b93a
Revises: 89e26bb3ccb7
Create Date: 2024-05-05 10:52:01.484849

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ff6c3937b93a'
down_revision = '5c7720292c7a'
branch_labels = None
depends_on = None


def upgrade():
    pgw = op.create_table(
        "ms_cfg_node",
        sa.Column("ms_id_node", sa.String(255), primary_key=True, index=True),
        sa.Column("ms_id_modul", sa.String(255), nullable=False),
        sa.Column("ms_no", sa.Integer, nullable=False), 
        sa.Column("ms_line_number", sa.Integer, nullable=False),
        sa.Column("ms_source_code", sa.Text),
        sa.Column("createdby", sa.String(255), nullable=False, server_default='1'),
        sa.Column("created", sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp()),
        sa.Column("updatedby", sa.String(255), nullable=False, server_default='1'),
        sa.Column("updated", sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp()),     
    )

def downgrade():
    op.drop_table('ms_cfg_node')
