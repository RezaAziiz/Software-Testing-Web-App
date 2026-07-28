from sqlalchemy.sql import text
from typing import Optional, Tuple, List
from models.modul import Modul
from models.param_modul import ParamModul
from models.topik_modul import TopikModul

class ModulRepository:
    def __init__(self, conn):
        self._conn = conn

    def find_by_id(self, id_modul: str):
        query = Modul.select().where(Modul.c.ms_id_modul == id_modul)
        return self._conn.execute(query).fetchone()

    def find_by_name(self, nama_modul: str):
        query = Modul.select().where(Modul.c.ms_nama_modul == nama_modul)
        return self._conn.execute(query).fetchone()

    def find_by_class_name(self, class_name: str):
        query = Modul.select().where(Modul.c.ms_class_name == class_name)
        return self._conn.execute(query).fetchone()

    def find_detail_with_lookup(self, id_modul: str):
        """Mengambil detail modul beserta join ke ms_system untuk nama jenis modul"""
        query = text("""
            SELECT m.*, 
                   (SELECT s.ms_system_value FROM ms_system as s 
                    WHERE s.ms_system_category = :category 
                      AND s.ms_system_sub_category = :subCategory 
                      AND s.ms_system_cd = m.ms_jenis_modul ) as nama_jenis_modul 
            FROM ms_modul_program as m  
            WHERE m.ms_id_modul = :idModul 
        """)
        return self._conn.execute(query, category='modul', subCategory='jenis_modul', idModul=id_modul).fetchone()
    
    def find_detail_by_topik_modul(self, id_topik_modul: str):
        """Mengambil detail modul berdasarkan id_topik_modul dengan melakukan JOIN"""
        query = text("""
            SELECT m.*, tm.ms_id_topik FROM ms_modul_program m
            INNER JOIN ms_topik_modul tm ON m.ms_id_modul = tm.ms_id_modul
            WHERE tm.ms_id_topik_modul = :idTopikModul
        """)
        return self._conn.execute(query, idTopikModul=id_topik_modul).fetchone()

    def get_parameters(self, id_modul: str) -> List:
        query = ParamModul.select().where(ParamModul.c.ms_id_modul == id_modul).order_by(ParamModul.c.no_urut.asc())
        return self._conn.execute(query).fetchall()

    def search(self, keyword: str, limit: int, offset: int) -> Tuple[List, int]:
        base_query = """ 
            SELECT m.*, 
            (SELECT s.ms_system_value FROM ms_system s WHERE s.ms_system_category='modul' AND s.ms_system_sub_category = 'jenis_modul' AND s.ms_system_cd = m.ms_jenis_modul) as jenis_modul, 
            (SELECT s.ms_system_value FROM ms_system s WHERE s.ms_system_category='modul' AND s.ms_system_sub_category = 'tingkat_kesulitan' AND s.ms_system_cd = m.ms_tingkat_kesulitan) as tingkat_kesulitan 
            FROM ms_modul_program m 
            WHERE m.ms_nama_modul LIKE :keyword 
        """
        
        # Hitung total data
        all_data_query = text(base_query)
        total_data = len(self._conn.execute(all_data_query, keyword=keyword).fetchall())

        # Ambil data paginasi
        paginated_query = text(base_query + " LIMIT :limit OFFSET :offset")
        data = self._conn.execute(paginated_query, limit=limit, offset=offset, keyword=keyword).fetchall()
        
        return data, total_data

    def insert(self, modul_data: dict) -> None:
        self._conn.execute(Modul.insert().values(**modul_data))

    def update(self, id_modul: str, modul_data: dict) -> None:
        self._conn.execute(Modul.update().values(**modul_data).where(Modul.c.ms_id_modul == id_modul))

    def delete(self, id_modul: str) -> None:
        self._conn.execute(Modul.delete().where(Modul.c.ms_id_modul == id_modul))

    def insert_parameters(self, params_data: List[dict]) -> None:
        if params_data:
            self._conn.execute(ParamModul.insert(), params_data)

    def delete_parameters(self, id_modul: str) -> None:
        self._conn.execute(ParamModul.delete().where(ParamModul.c.ms_id_modul == id_modul))

    def check_used_in_topik(self, id_modul: str) -> bool:
        """Validasi sebelum menghapus modul"""
        query = text("SELECT 1 FROM ms_topik_modul tm WHERE tm.ms_id_modul = :idModul LIMIT 1")
        result = self._conn.execute(query, idModul=id_modul).fetchone()
        return result is not None