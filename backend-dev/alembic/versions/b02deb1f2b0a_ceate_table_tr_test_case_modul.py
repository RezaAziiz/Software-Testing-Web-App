"""ceate table tr test case modul

Revision ID: b02deb1f2b0a
Revises: 2e3b07a8b324
Create Date: 2024-05-05 11:11:06.329846

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b02deb1f2b0a'
down_revision = '2e3b07a8b324'
branch_labels = None
depends_on = None

result_type_enum = sa.Enum("P", "F", name="resulttypeenum")
def upgrade():
    pgw = op.create_table(
        "tr_test_case_modul",
        sa.Column("tr_id_test_case", sa.String(255), primary_key=True, index=True),
        sa.Column("tr_id_topik_modul", sa.String(255), nullable=False),
        sa.Column("tr_student_id", sa.String(255), nullable=False),
        sa.Column("tr_no", sa.Integer), 
        sa.Column("tr_object_pengujian", sa.Text, nullable=False), 
        sa.Column("tr_data_test_input", sa.Text), #Json string
        sa.Column("tr_expected_result", sa.Text), 
        sa.Column("tr_test_result", result_type_enum), #Jenis Module F = FAILED, P=PASSED
        sa.Column("createdby", sa.String(255), nullable=False, server_default='1'),
        sa.Column("created", sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp()),
        sa.Column("updatedby", sa.String(255), nullable=False, server_default='1'),
        sa.Column("updated", sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp()),     
    )


def downgrade():
    op.drop_table('tr_test_case_modul')

