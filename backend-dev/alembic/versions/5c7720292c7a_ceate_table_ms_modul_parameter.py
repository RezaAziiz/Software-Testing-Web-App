"""ceate table ms modul parameter

Revision ID: 5c7720292c7a
Revises: 65977e3e9358
Create Date: 2024-05-05 10:26:00.432626

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5c7720292c7a'
down_revision = '65977e3e9358'
branch_labels = None
depends_on = None


jenis_type_enum = sa.Enum("F", "P", name="jenistypeenum")
def upgrade():
    pgw = op.create_table(
        "ms_modul_parameter",
        sa.Column("ms_id_parameter", sa.String(255), primary_key=True, index=True),
        sa.Column("ms_id_modul", sa.String(255), nullable=False),
        sa.Column("ms_nama_parameter", sa.String(255), nullable=False), #Jenis Module F = Function, P=Procedure
        sa.Column("ms_tipe_data", sa.String(50), nullable=False),
        sa.Column("ms_rules", sa.Text, nullable=False),
        sa.Column("no_urut", sa.Integer),
        sa.Column("createdby", sa.String(255), nullable=False, server_default='1'),
        sa.Column("created", sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp()),
        sa.Column("updatedby", sa.String(255), nullable=False, server_default='1'),
        sa.Column("updated", sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp()),     
    )


def downgrade():
    op.drop_table('ms_modul_parameter')