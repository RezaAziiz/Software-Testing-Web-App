"""create table topik modul

Revision ID: e9f97ee0b898
Revises: b955425bbdf1
Create Date: 2024-05-09 10:08:34.777388

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e9f97ee0b898'
down_revision = 'b955425bbdf1'
branch_labels = None
depends_on = None


status_type_enum = sa.Enum("Y", "N", name="statustypeenum")
def upgrade():
    pgw = op.create_table(
        "ms_topik_modul",
        sa.Column("ms_id_topik_modul", sa.String(255), primary_key=True, index=True),
        sa.Column("ms_id_topik", sa.String(255), nullable=False,),
        sa.Column("ms_id_modul", sa.String(255), nullable=False,),
        sa.Column("ms_no", sa.Integer),
        sa.Column("createdby", sa.String(255), nullable=False, server_default='1'),
        sa.Column("created", sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp()),
        sa.Column("updatedby", sa.String(255), nullable=False, server_default='1'),
        sa.Column("updated", sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp()),     
    )

def downgrade():
    op.drop_table('ms_topik_modul')