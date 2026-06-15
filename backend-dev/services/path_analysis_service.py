import logging
from typing import List, Dict, Any, Set, Optional

logger = logging.getLogger(__name__)

class PathAnalysisService:
    def __init__(self):
        pass

    def find_reachable_path(self, starts: List[str], goals: Set[str], adjacency: Dict[str, List[str]]) -> Optional[List[str]]:
        """
        Melakukan pencarian jalur (Breadth-First Search) dari start nodes ke target nodes.
        """
        queue = [[start] for start in starts]
        visited = set(starts)

        while queue:
            path = queue.pop(0)
            current = path[-1]

            if current in goals:
                return path

            neighbors = adjacency.get(current, [])
            for neighbor in neighbors:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(path + [neighbor])

        return None

    def build_unexecuted_paths(self, nodes: List[Any], edges: List[Any]) -> List[str]:
        """
        Membangun list string yang merepresentasikan jalur yang belum tereksekusi pada CFG.
        Misalnya: ["1→2→4", "1→3→5"]
        """
        if not nodes or not edges:
            return []

        node_by_id = {}
        for node in nodes:
            # Mengambil node yang berupa object dict atau SQLAlchemy
            node_dict = dict(node) if hasattr(node, "keys") else node.__dict__ if hasattr(node, "__dict__") else node
            try:
                if not isinstance(node_dict, dict):
                    node_dict = dict(node)
            except Exception:
                pass
            
            node_id = node_dict.get('ms_id_node') or node_dict.get('id_node')
            if node_id is not None:
                node_id_str = str(node_id)
                node_by_id[node_id_str] = node_dict

        def get_order(node_id: str) -> float:
            node = node_by_id.get(node_id, {})
            order = node.get('ms_execution_order') or node.get('execution_order')
            if order is not None:
                try:
                    return float(order)
                except (ValueError, TypeError):
                    pass
            return float('inf')

        def sort_key(node_id: str):
            return (get_order(node_id), str(node_id))

        adjacency: Dict[str, List[str]] = {node_id: [] for node_id in node_by_id}
        incoming_count: Dict[str, int] = {node_id: 0 for node_id in node_by_id}
        outgoing_count: Dict[str, int] = {node_id: 0 for node_id in node_by_id}

        for edge in edges:
            edge_dict = dict(edge) if hasattr(edge, "keys") else edge.__dict__ if hasattr(edge, "__dict__") else edge
            try:
                if not isinstance(edge_dict, dict):
                    edge_dict = dict(edge)
            except Exception:
                pass

            source = edge_dict.get('id_node_start') or edge_dict.get('ms_id_start_node') or edge_dict.get('id_start_node')
            target = edge_dict.get('id_node_finish') or edge_dict.get('ms_id_finish_node') or edge_dict.get('id_finish_node')
            
            if source is None or target is None:
                continue
                
            source_str = str(source)
            target_str = str(target)
            
            if source_str not in node_by_id or target_str not in node_by_id:
                continue

            adjacency[source_str].append(target_str)
            incoming_count[target_str] += 1
            outgoing_count[source_str] += 1

        for neighbors in adjacency.values():
            neighbors.sort(key=sort_key)

        all_node_ids = sorted(node_by_id.keys(), key=sort_key)
        entry_nodes = [nid for nid in all_node_ids if incoming_count[nid] == 0]
        exit_nodes = [nid for nid in all_node_ids if outgoing_count[nid] == 0]

        starts = entry_nodes if entry_nodes else all_node_ids[:1]
        goals = set(exit_nodes if exit_nodes else all_node_ids[-1:])

        unexecuted_node_ids = []
        for node in nodes:
            node_dict = dict(node) if hasattr(node, "keys") else node.__dict__ if hasattr(node, "__dict__") else node
            try:
                if not isinstance(node_dict, dict):
                    node_dict = dict(node)
            except Exception:
                pass
                
            status = str(node_dict.get('tr_status', '')).upper()
            if status == 'N':
                nid = node_dict.get('ms_id_node') or node_dict.get('id_node')
                if nid is not None:
                    unexecuted_node_ids.append(str(nid))

        unexecuted_node_ids.sort(key=sort_key)

        unique_paths = set()
        for target_id in unexecuted_node_ids:
            prefix = self.find_reachable_path(starts, {target_id}, adjacency)
            suffix = self.find_reachable_path([target_id], goals, adjacency)
            
            if not prefix or not suffix:
                continue

            full_path = prefix + suffix[1:]

            display_parts = []
            for nid in full_path:
                node = node_by_id.get(nid, {})
                order = node.get('ms_execution_order') or node.get('execution_order')
                if order is not None:
                    display_parts.append(str(order))

            if display_parts:
                display_path = "→".join(display_parts)
                unique_paths.add(display_path)

        # Sort the output paths for deterministic ordering
        def parse_path_for_sorting(path):
            try:
                return [float(x) for x in path.split('→')]
            except ValueError:
                return [0.0]
                
        sorted_paths = sorted(list(unique_paths), key=parse_path_for_sorting)
        return sorted_paths