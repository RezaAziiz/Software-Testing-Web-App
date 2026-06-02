import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from decouple import config

SQLALCHEMY_DATABASE_URL = (
    f"mysql+pymysql://{config('DATABASE_USER')}:{config('DATABASE_PASSWORD')}"
    f"@{config('DATABASE_URL')}"
)

# Pool pre_ping memastikan koneksi yang mati akan direstart otomatis
engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=True, autoflush=True, bind=engine)
Base = declarative_base()
conn = engine.connect().execution_options(autocommit=True)

def get_connection():
    """FastAPI dependency: satu koneksi mandiri per request, dengan auto-transaksi."""
    connection = engine.connect()
    trans = connection.begin()
    try:
        yield connection
        trans.commit()
    except Exception:
        trans.rollback()
        raise
    finally:
        connection.close()