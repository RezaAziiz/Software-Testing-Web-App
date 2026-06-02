from sqlalchemy.sql import text
from models.system import System

class SystemConfigRepository:
    """Mengelola pengambilan data konfigurasi sistem / master parameter"""
    
    def __init__(self, conn):
        self._conn = conn

    def get_system_value(self, category: str, sub_category: str, code: str):
        query = System.select().where(
            System.c.ms_system_category == category,
            System.c.ms_system_sub_category == sub_category,
            System.c.ms_system_cd == code
        )
        result = self._conn.execute(query).fetchone()
        return result['ms_system_value'] if result else None

    def get_minimum_coverage(self) -> float:
        """Fungsi spesifik yang sering dipakai untuk mengecek batas minimum coverage"""
        val = self.get_system_value('common', 'minimum_value', 'coverage')
        return float(val) if val else 0.0