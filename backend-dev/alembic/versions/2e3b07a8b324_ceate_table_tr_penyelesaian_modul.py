"""ceate table tr penyelesaian modul

Revision ID: 2e3b07a8b324
Revises: 07cf33e3341a
Create Date: 2024-05-05 11:04:44.206215

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2e3b07a8b324'
down_revision = '07cf33e3341a'
branch_labels = None
depends_on = None

execute_type_enum = sa.Enum("Y", "N", name="executetypeenum")
selesai_type_enum = sa.Enum("Y", "N", name="selesaitypeenum")
def upgrade():
    pgw = op.create_table(
        "tr_penyelesaian_modul",
        sa.Column("tr_id_topik_modul", sa.String(255), primary_key=True, index=True),
        sa.Column("tr_student_id", sa.String(255), primary_key=True, index=True),
        sa.Column("tr_nilai", sa.Float), 
        sa.Column("tr_tgl_mulai", sa.DateTime, nullable=False), #Nomor Induk Mahasiswa (NIM)
        sa.Column("tr_tgl_selesai", sa.DateTime),
        sa.Column("tr_persentase_coverage", sa.Float), 
        sa.Column("tr_result_report", sa.Text),
        sa.Column("tr_coverage_report", sa.Text),
        sa.Column("tr_tgl_eksekusi", sa.DateTime),
        sa.Column("tr_status_eksekusi", execute_type_enum, nullable=False, server_default='N'),
        sa.Column("tr_status_penyelesaian", selesai_type_enum, nullable=False, server_default='N'),
        sa.Column("createdby", sa.String(255), nullable=False, server_default='1'),
        sa.Column("created", sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp()),
        sa.Column("updatedby", sa.String(255), nullable=False, server_default='1'),
        sa.Column("updated", sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp()),     
    )


def downgrade():
    op.drop_table('tr_penyelesaian_modul')
