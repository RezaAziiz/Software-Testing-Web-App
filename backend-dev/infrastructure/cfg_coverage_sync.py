import logging
from typing import List, Dict, Any
from repositories.cfg_repository import CfgRepository

logger = logging.getLogger(__name__)

class CfgCoverageSync:
    """
    Menangani algoritma propagasi grafik untuk menentukan status coverage
    (Terlalui/Belum/Sebagian) pada Node dan Edge CFG berdasarkan data JaCoCo.
    """
    def __init__(self, cfg_repo: CfgRepository):
        self.cfg_repo = cfg_repo

    def synchronize(
        self, 
        id_topik_modul: str, 
        student_id: str, 
        id_modul: str, 
        line_statuses: List[Dict[str, Any]]
    ) -> None:
        """
        Melakukan sinkronisasi data line coverage dengan node AST, menjalankan
        propagasi graph, dan menyimpan hasilnya.
        """
        # Reset data transaksi sebelumnya
        self.cfg_repo.reset_tr_nodes(id_topik_modul, student_id)
        self.cfg_repo.reset_tr_edges(id_topik_modul, student_id)

        # Ambil data master Node dan Edge
        master_nodes = self.cfg_repo.get_master_nodes(id_modul)
        master_edges = self.cfg_repo.get_master_edges(id_modul)

        # Tentukan status awal tiap node berdasarkan JaCoCo
        # Default semua Node ke 'N' (Belum terlalui)
        node_status_map = {node.ms_id_node: 'N' for node in master_nodes}
        priority = {'Y': 2, 'S': 1, 'N': 0}

        for line_data in line_statuses:
            line_nr = line_data['line_number']
            status_exec = line_data['status']

            for node in master_nodes:
                # Match by AST range (ms_line_start <= line <= ms_line_end) atau fallback exact match
                if (node.ms_line_start is not None and node.ms_line_end is not None and int(node.ms_line_start) <= line_nr <= int(node.ms_line_end)) or \
                   (node.ms_line_number is not None and int(node.ms_line_number) == line_nr):
                    
                    current_status = node_status_map[node.ms_id_node]
                    # Update hanya jika status baru punya prioritas lebih tinggi (Y > S > N)
                    if priority[status_exec] > priority[current_status]:
                        node_status_map[node.ms_id_node] = status_exec

        # Bangun Adjacency List untuk propagasi
        preds_map = {}
        succs_map = {}
        for edge in master_edges:
            u = edge.ms_id_start_node
            v = edge.ms_id_finish_node
            preds_map.setdefault(v, []).append(u)
            succs_map.setdefault(u, []).append(v)

        # Algoritma Fixed-Point Propagation
        changed = True
        while changed:
            changed = False
            
            # Backward propagation
            for v, status_v in list(node_status_map.items()):
                if status_v in ['Y', 'S']:
                    p_list = preds_map.get(v, [])
                    # Jika hanya punya 1 parent, dan parent-nya 'N', maka parent jadi 'Y'
                    if len(p_list) == 1:
                        u = p_list[0]
                        if node_status_map.get(u) == 'N':
                            node_status_map[u] = 'Y'
                            changed = True
            
            # Forward propagation
            for u, status_u in list(node_status_map.items()):
                if status_u in ['Y', 'S']:
                    s_list = succs_map.get(u, [])
                    # Jika hanya punya 1 child, dan child-nya 'N', maka child jadi 'Y'
                    if len(s_list) == 1:
                        v = s_list[0]
                        if node_status_map.get(v) == 'N':
                            node_status_map[v] = 'Y'
                            changed = True

        #  Hitung status eksekusi Edge
        edge_status_map = {}
        for edge in master_edges:
            u_status = node_status_map.get(edge.ms_id_start_node, 'N')
            v_status = node_status_map.get(edge.ms_id_finish_node, 'N')
            
            # Edge dieksekusi jika source dan finish node-nya dieksekusi
            if u_status in ['Y', 'S'] and v_status in ['Y', 'S']:
                edge_status_map[edge.ms_id_edge] = 'Y'
            else:
                edge_status_map[edge.ms_id_edge] = 'N'

        # Format data dan lakukan Bulk Insert ke Database via Repository
        import datetime
        now = datetime.datetime.now()
        
        tr_nodes_data = [{
            "tr_id_node": node_id,
            "tr_id_topik_modul": id_topik_modul,
            "tr_id_student": student_id,
            "tr_status": status,
            "created": now,
            "createdby": student_id,
            "updated": now,
            "updatedby": student_id
        } for node_id, status in node_status_map.items()]
        
        tr_edges_data = [{
            "tr_id_edge": edge_id,
            "tr_id_topik_modul": id_topik_modul,
            "tr_id_student": student_id,
            "tr_status": status,
            "created": now,
            "createdby": student_id,
            "updated": now,
            "updatedby": student_id
        } for edge_id, status in edge_status_map.items()]

        self.cfg_repo.bulk_insert_tr_nodes(tr_nodes_data)
        self.cfg_repo.bulk_insert_tr_edges(tr_edges_data)
        
        logger.info(f"CFG Coverage sync complete for module {id_modul}, user {student_id}")