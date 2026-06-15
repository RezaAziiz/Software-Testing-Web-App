from sqlalchemy.sql import text
from models.node import Node
from models.edge import Edge
from models.modul import Modul
from models.tr_node import TrNode
from models.tr_edge import TrEdge
from datetime import datetime
from typing import List, Dict, Any

class CfgRepository:
    def __init__(self, conn):
        self._conn = conn
    
    def insert_nodes(self, nodes_data: List[Dict[str, Any]]) -> None:
        if nodes_data:
            self._conn.execute(Node.insert(), nodes_data)

    def insert_edges(self, edges_data: List[Dict[str, Any]]) -> None:
        if edges_data:
            self._conn.execute(Edge.insert(), edges_data)

    def update_modul_cc(self, modul_id: str, cc_score: int, updated_by: str) -> None:
        query = Modul.update().values(
            ms_cc=cc_score,
            updatedby=updated_by,
            updated=datetime.now()
        ).where(Modul.c.ms_id_modul == modul_id)
        self._conn.execute(query)

    def delete_master_cfg(self, modul_id: str) -> None:
        # Delete edges first to avoid foreign key constraints
        self._conn.execute(Edge.delete().where(Edge.c.ms_id_modul == modul_id))
        self._conn.execute(Node.delete().where(Node.c.ms_id_modul == modul_id))

    def get_master_nodes(self, modul_id: str) -> list:
        query = Node.select().where(Node.c.ms_id_modul == modul_id).order_by(Node.c.ms_execution_order)
        return self._conn.execute(query).fetchall()

    def get_master_edges(self, modul_id: str) -> list:
        query = Edge.select().where(Edge.c.ms_id_modul == modul_id)
        return self._conn.execute(query).fetchall()

    def reset_tr_nodes(self, id_topik_modul: str, student_id: str) -> None:
        query = TrNode.delete().where(
            TrNode.c.tr_id_topik_modul == id_topik_modul, 
            TrNode.c.tr_id_student == student_id
        )
        self._conn.execute(query)
        
    def reset_tr_edges(self, id_topik_modul: str, student_id: str) -> None:
        query = TrEdge.delete().where(
            TrEdge.c.tr_id_topik_modul == id_topik_modul, 
            TrEdge.c.tr_id_student == student_id
        )
        self._conn.execute(query)

    def get_cfg_with_status(self, id_topik_modul: str, student_id: str) -> tuple[list, list]:
        """Mengambil node dan edge beserta status eksekusinya untuk endpoint getResultTest"""
        
        query_nodes = text("""
            SELECT n.*, tn.tr_status 
            FROM ms_cfg_node n 
            INNER JOIN tr_cfg_node tn ON n.ms_id_node = tn.tr_id_node 
            WHERE tn.tr_id_topik_modul = :idTopikModul 
              AND tn.tr_id_student = :idUser 
            ORDER BY n.ms_execution_order;
        """)
        
        query_edges = text("""
            SELECT e.*, te.tr_status 
            FROM ms_cfg_edge e 
            INNER JOIN tr_cfg_edge te ON e.ms_id_edge = te.tr_id_edge 
            INNER JOIN ms_cfg_node n ON e.ms_id_start_node = n.ms_id_node 
            WHERE te.tr_id_topik_modul = :idTopikModul 
              AND te.tr_id_student = :idUser 
            ORDER BY n.ms_line_number;
        """)
        
        nodes = self._conn.execute(query_nodes, idTopikModul=id_topik_modul, idUser=student_id).fetchall()
        edges = self._conn.execute(query_edges, idTopikModul=id_topik_modul, idUser=student_id).fetchall()
        
        return nodes, edges
    
    def bulk_insert_tr_nodes(self, tr_nodes_data: list) -> None:
        if tr_nodes_data:
            self._conn.execute(TrNode.insert(), tr_nodes_data)

    def bulk_insert_tr_edges(self, tr_edges_data: list) -> None:
        if tr_edges_data:
            self._conn.execute(TrEdge.insert(), tr_edges_data)