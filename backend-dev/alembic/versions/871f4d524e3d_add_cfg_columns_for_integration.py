"""add_cfg_columns_for_integration

Revision ID: 871f4d524e3d
Revises: e9f97ee0b898
Create Date: 2026-05-09 15:48:07.862011

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '871f4d524e3d'
down_revision = 'e9f97ee0b898'
branch_labels = None
depends_on = None


def upgrade():
    # === ms_cfg_node: tambah kolom baru untuk integrasi CFG engine ===
    op.add_column('ms_cfg_node', sa.Column('ms_execution_order', sa.Integer(), nullable=True))
    op.add_column('ms_cfg_node', sa.Column('ms_line_start', sa.Integer(), nullable=True))
    op.add_column('ms_cfg_node', sa.Column('ms_line_end', sa.Integer(), nullable=True))
    op.add_column('ms_cfg_node', sa.Column('ms_ast_node_type', sa.String(length=100), nullable=True))
    op.add_column('ms_cfg_node', sa.Column('ms_node_type', sa.String(length=50), nullable=True))
    # Hapus kolom lama ms_no yang digantikan oleh ms_execution_order
    op.drop_column('ms_cfg_node', 'ms_no')

    # === ms_cfg_edge: tambah kolom ms_branch_type ===
    op.add_column('ms_cfg_edge', sa.Column('ms_branch_type', sa.String(length=50), nullable=True))


def downgrade():
    # === Rollback ms_cfg_edge ===
    op.drop_column('ms_cfg_edge', 'ms_branch_type')

    # === Rollback ms_cfg_node ===
    op.drop_column('ms_cfg_node', 'ms_node_type')
    op.drop_column('ms_cfg_node', 'ms_ast_node_type')
    op.drop_column('ms_cfg_node', 'ms_line_end')
    op.drop_column('ms_cfg_node', 'ms_line_start')
    op.drop_column('ms_cfg_node', 'ms_execution_order')
    # Kembalikan kolom ms_no
    op.add_column('ms_cfg_node', sa.Column('ms_no', mysql.INTEGER(), autoincrement=False, nullable=True))
