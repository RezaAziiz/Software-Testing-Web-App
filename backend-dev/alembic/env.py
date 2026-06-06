from logging.config import fileConfig
import sys
import os

from sqlalchemy import engine_from_config, MetaData
from sqlalchemy import pool

from alembic import context

# Tambahkan root project ke sys.path agar import models bisa dilakukan
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Override sqlalchemy.url dynamically from .env
from decouple import config as env_config
import urllib.parse

db_user = env_config("DATABASE_USER", default="root")
db_password = env_config("DATABASE_PASSWORD", default="")
db_url = env_config("DATABASE_URL", default="localhost:3306/flow_kit_db")

password_encoded = urllib.parse.quote_plus(db_password) if db_password else ""
sqlalchemy_url = f"mysql+pymysql://{db_user}:{password_encoded}@{db_url}" if password_encoded else f"mysql+pymysql://{db_user}@{db_url}"
config.set_main_option("sqlalchemy.url", sqlalchemy_url)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)

# Import semua model agar tabel-nya terdaftar ke MetaData
from models.node import Node, metadata as node_metadata
from models.edge import Edge, metadata as edge_metadata
from models.modul import Modul, metadata as modul_metadata
from models.classes import Class, metadata as classes_metadata
from models.student import Student, metadata as student_metadata
from models.teacher import Teacher, metadata as teacher_metadata
from models.system import System, metadata as system_metadata
from models.topik import Topik, metadata as topik_metadata
from models.topik_modul import TopikModul, metadata as topik_modul_metadata
from models.param_modul import ParamModul, metadata as param_modul_metadata
from models.test_case import TestCase, metadata as test_case_metadata
from models.penyelesaian_modul import PenyelesaianModul, metadata as penyelesaian_metadata
from models.tr_node import TrNode, metadata as tr_node_metadata
from models.tr_edge import TrEdge, metadata as tr_edge_metadata

# Gabungkan semua MetaData ke satu objek untuk autogenerate
combined_metadata = MetaData()
for m in [
    node_metadata, edge_metadata, modul_metadata, classes_metadata,
    student_metadata, teacher_metadata, system_metadata, topik_metadata,
    topik_modul_metadata, param_modul_metadata, test_case_metadata,
    penyelesaian_metadata, tr_node_metadata, tr_edge_metadata,
]:
    for table in m.tables.values():
        table.tometadata(combined_metadata)

target_metadata = combined_metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
