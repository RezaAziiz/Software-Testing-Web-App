"""ceate table ms modul pengujian

Revision ID: 65977e3e9358
Revises: b4621eb2d479
Create Date: 2024-05-05 10:19:12.716761

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '65977e3e9358'
down_revision = 'b4621eb2d479'
branch_labels = None
depends_on = None



jenis_type_enum = sa.Enum("F", "P", name="jenistypeenum")
def upgrade():
    pgw = op.create_table(
        "ms_modul_program",
        sa.Column("ms_id_modul", sa.String(255), primary_key=True, index=True),
        sa.Column("ms_jenis_modul", jenis_type_enum, nullable=False, server_default='F'), #Jenis Module F = Function, P=Procedure
        sa.Column("ms_nama_modul", sa.String(50), nullable=False), #Nomor Induk Mahasiswa (NIM)
        sa.Column("ms_deskripsi_modul", sa.Text, nullable=False),
        sa.Column("ms_source_code", sa.String(255)),
        sa.Column("ms_class_name", sa.String(255), nullable=False),
        sa.Column("ms_function_name", sa.String(255), nullable=False),
        sa.Column("ms_return_type", sa.String(255)),
        sa.Column("ms_jml_parameter", sa.Integer, nullable=False),
        sa.Column("ms_tingkat_kesulitan", sa.String(255), nullable=False),
        sa.Column("ms_cc", sa.Integer),
        sa.Column("createdby", sa.String(255), nullable=False, server_default='1'),
        sa.Column("created", sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp()),
        sa.Column("updatedby", sa.String(255), nullable=False, server_default='1'),
        sa.Column("updated", sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp()),     
    )


def downgrade():
    op.drop_table('ms_modul_program')

