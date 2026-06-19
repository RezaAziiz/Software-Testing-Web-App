import logging
from collections import Counter, deque
from typing import Any, Dict, List, Set, Tuple
from core.types import NodeType
import networkx as nx

logger = logging.getLogger(__name__)


class NodeAdapter:
    """Adapter untuk mengkonversi node dict ke format yang diharapkan oleh generate_independent_paths()"""
    def __init__(self, node_dict: Dict[str, Any]):
        self.node_dict = node_dict
        self.id_node = str(node_dict.get("ms_id_node") or node_dict.get("id_node"))
        self.node_type = self._parse_node_type(node_dict)
        self.execution_order = node_dict.get("ms_execution_order") or node_dict.get("execution_order")
    
    def _parse_node_type(self, node_dict: Dict[str, Any]) -> NodeType:
        """Konversi string node_type ke NodeType enum"""
        node_type_str = (node_dict.get("ms_node_type") or node_dict.get("node_type") or "").upper()
        try:
            return NodeType[node_type_str]
        except (KeyError, TypeError):
            return NodeType.DECISION  # default fallback


def _path_vector(path, edge_index):
    vector = 0
    for source, target in zip(path, path[1:]):
        matching_indexes = [
            index
            for (edge_source, edge_target, _), index in edge_index.items()
            if edge_source == source and edge_target == target
        ]
        for index in matching_indexes:
            vector ^= 1 << index
    return vector


def _adds_rank(existing_vectors, vector):
    return _rank(existing_vectors + [vector]) > _rank(existing_vectors)


def _rank(vectors):
    basis = {}

    for vector in vectors:
        candidate = vector
        while candidate:
            pivot = candidate.bit_length() - 1
            if pivot not in basis:
                basis[pivot] = candidate
                break
            candidate ^= basis[pivot]

    return len(basis)


def _shortest_node_path(starts, target_id, adjacency, terminal_nodes=None, exclude_nodes=None):
    excluded = set(exclude_nodes) if exclude_nodes else set()
    queue = deque((start_id, [start_id]) for start_id in starts)
    visited = set(starts) | excluded

    while queue:
        current_id, path = queue.popleft()
        if current_id == target_id or (terminal_nodes and current_id in terminal_nodes):
            return path

        for edge in adjacency.get(current_id, []):
            next_id = edge["id_finish_node"]
            if next_id in visited:
                continue
            visited.add(next_id)
            queue.append((next_id, path + [next_id]))

    return None


def _path_covering_edge(target_edge, start_nodes, terminal_nodes, adjacency):
    prefix = _shortest_node_path(
        start_nodes,
        target_edge["id_start_node"],
        adjacency,
    )
    suffix = _shortest_node_path(
        [target_edge["id_finish_node"]],
        None,
        adjacency,
        terminal_nodes,
    )

    if not prefix or not suffix:
        return None

    return prefix + suffix


def _format_path(path, node_by_id):
    labels = []
    ids = []

    for node_id in path:
        node = node_by_id.get(node_id)
        if not node or node.node_type == NodeType.MERGE:
            continue

        if node.node_type == NodeType.START:
            label = "Start"
        elif node.node_type == NodeType.END:
            label = "End"
        else:
            label = str(node.execution_order) if node.execution_order is not None else node_id

        if not labels or labels[-1] != label:
            labels.append(label)
        ids.append(node_id)

    return {
        "ids": ids,
        "nodes": labels,
        "path": "→".join(labels),
    }


def generate_independent_paths(nodes, edges, target_count=None):
    """Generate a practical basis path set from CFG edges using ABPC Algorithm.

    Phase 1: Modify CFG to Strongly Connected Graph (End -> Start)
    Phase 2: Find Elementary Circuits using Modified Johnson Algorithm (via NetworkX)
    Phase 3: Path Extraction & Linear Independence Filtering over edge-incidence vectors
    """
    if not nodes:
        return []

    node_by_id = {node.id_node: node for node in nodes}
    edge_keys = [
        (edge["id_start_node"], edge["id_finish_node"], edge.get("branch_type", ""))
        for edge in edges
    ]
    edge_index = {key: index for index, key in enumerate(edge_keys)}

    # Tetap buat adjacency dictionary untuk backward compatibility dengan _path_covering_edge
    adjacency = {node.id_node: [] for node in nodes}
    indegree = {node.id_node: 0 for node in nodes}
    outdegree = {node.id_node: 0 for node in nodes}

    # Inisialisasi Graf NetworkX
    G = nx.DiGraph()
    for node in nodes:
        G.add_node(node.id_node)

    for edge in edges:
        source = edge["id_start_node"]
        target = edge["id_finish_node"]
        adjacency.setdefault(source, []).append(edge)
        indegree[target] = indegree.get(target, 0) + 1
        outdegree[source] = outdegree.get(source, 0) + 1
        # Tambahkan edge ke NetworkX
        G.add_edge(source, target)

    start_nodes = [node.id_node for node in nodes if indegree.get(node.id_node, 0) == 0]
    if not start_nodes:
        start_nodes = [nodes[0].id_node]

    terminal_nodes = [node.id_node for node in nodes if outdegree.get(node.id_node, 0) == 0]
    
    # Memodifikasi CFG menjadi Strongly Connected Graph
    # Menambahkan edge dari Exit kembali ke Entry
    virtual_edges = []
    for t_node in terminal_nodes:
        for s_node in start_nodes:
            G.add_edge(t_node, s_node)
            virtual_edges.append((t_node, s_node))

    # Mencari Sirkuit Dasar (Elementary Circuits)
    # Menggunakan Algoritma Johnson
    raw_cycles = list(nx.simple_cycles(G))

    # Hapus kembali virtual edge untuk membersihkan graf aslinya
    for t_node, s_node in virtual_edges:
        G.remove_edge(t_node, s_node)

    # Pemotongan Sirkuit menjadi Jalur (Path Extraction)
    candidates = []
    for cycle in raw_cycles:
        
        found_virtual_crossing = False
        for i in range(len(cycle)):
            curr_node = cycle[i]
            prev_node = cycle[i-1] # Di Python, index -1 adalah elemen terakhir
            
            # Jika menemukan transisi dari Terminal ke Start (artinya melewati virtual edge)
            if prev_node in terminal_nodes and curr_node in start_nodes:
                # Potong array cycle di titik ini, lalu gabungkan kembali agar dimulai dari Start
                straight_path = cycle[i:] + cycle[:i]
                candidates.append(straight_path)
                found_virtual_crossing = True
                break
        
        # Jika sirkuit ini internal (tidak melewati virtual edge),
        # bangun full path: Start → ... → cycle_entry → [cycle body] → cycle_entry → ... → End
        if not found_virtual_crossing and len(cycle) > 0:
            cycle_set = set(cycle)
            
            # Rotasi cycle agar entry point adalah loop header (DECISION node) 
            # yang punya outgoing edge ke luar cycle
            # Contoh: cycle [3,4,2] → node 2 (DECISION, while) punya exit ke 6 → rotate ke [2,3,4]
            best_entry_idx = 0
            best_score = -1
            best_depth = float('inf')
            for idx, node_id in enumerate(cycle):
                outgoing_targets = [e["id_finish_node"] for e in adjacency.get(node_id, [])]
                external_exits = [t for t in outgoing_targets if t not in cycle_set]
                if not external_exits:
                    continue
                # Skor: DECISION node = 10, lainnya = 1, bonus per exit
                node_obj = node_by_id.get(node_id)
                is_decision = node_obj and node_obj.node_type == NodeType.DECISION
                score = (10 if is_decision else 1) + len(external_exits)
                # Tiebreaker: jarak dari Start (lebih dekat = loop header, bukan inner decision)
                depth_path = _shortest_node_path(start_nodes, node_id, adjacency)
                depth = len(depth_path) if depth_path else float('inf')
                if score > best_score or (score == best_score and depth < best_depth):
                    best_score = score
                    best_depth = depth
                    best_entry_idx = idx
            
            # Rotate cycle
            rotated_cycle = cycle[best_entry_idx:] + cycle[:best_entry_idx]
            cycle_entry = rotated_cycle[0]
            
            # Prefix: jalur terpendek dari Start ke titik masuk cycle
            prefix = _shortest_node_path(start_nodes, cycle_entry, adjacency)
            if not prefix:
                continue
            
            # Suffix: jalur terpendek dari cycle_entry ke terminal (End)
            # Exclude node-node interior cycle agar suffix keluar loop, bukan masuk lagi
            cycle_interior = set(rotated_cycle[1:])  # semua node cycle kecuali entry
            suffix = _shortest_node_path(
                [cycle_entry], None, adjacency, terminal_nodes, 
                exclude_nodes=cycle_interior
            )
            if not suffix:
                # Fallback: coba tanpa exclude jika tidak ada jalur keluar lain
                suffix = _shortest_node_path([cycle_entry], None, adjacency, terminal_nodes)
            if not suffix:
                continue
            
            # Gabungkan: prefix + interior cycle + suffix
            full_path = prefix + rotated_cycle[1:] + suffix
            candidates.append(full_path)


    candidates.sort(key=lambda path: (len(path), path))

    # Penyaringan Jalur Redundan (Linear Independence)
    max_paths = target_count if target_count is not None else max(len(edges) - len(nodes) + 2, 1)
    selected_paths = []
    selected_vectors = []

    for path in candidates:
        vector = _path_vector(path, edge_index)
        if vector == 0:
            continue
        # Hanya ambil jalur yang memiliki edge baru (kombinasi independen)
        if _adds_rank(selected_vectors, vector):
            selected_paths.append(path)
            selected_vectors.append(vector)
            if len(selected_paths) == max_paths:
                break

    # FASE FALLBACK: Penambalan Sirkuit Tengah
    if len(selected_paths) < max_paths:
        for edge in edges:
            path = _path_covering_edge(edge, start_nodes, terminal_nodes, adjacency)
            if not path:
                continue
            vector = _path_vector(path, edge_index)
            if vector and _adds_rank(selected_vectors, vector):
                selected_paths.append(path)
                selected_vectors.append(vector)
                if len(selected_paths) == max_paths:
                    break

    return [_format_path(path, node_by_id) for path in selected_paths]


# PathAnalysisService
class PathAnalysisService:
    def __init__(self):
        pass

    def _normalize_node(self, node: Any) -> Dict[str, Any]:
        node_dict = (
            dict(node)
            if hasattr(node, "keys")
            else node.__dict__
            if hasattr(node, "__dict__")
            else node
        )
        try:
            if not isinstance(node_dict, dict):
                node_dict = dict(node)
        except Exception:
            pass
        return node_dict if isinstance(node_dict, dict) else {}

    def _get_node_id(self, node: Dict[str, Any]) -> str | None:
        node_id = node.get("ms_id_node") or node.get("id_node")
        return str(node_id) if node_id is not None else None

    def _get_node_label(self, node: Dict[str, Any], idx: int) -> str:
        node_type = (node.get("ms_node_type") or node.get("node_type") or "").upper()
        execution_order = node.get("ms_execution_order") or node.get("execution_order")

        if node_type == "START":
            return "Start"
        if node_type == "END":
            return "End"
        if node_type == "MERGE":
            return ""
        if execution_order is not None:
            return str(execution_order)
        return str(idx)

    def build_unexecuted_paths(self, nodes: List[Any], edges: List[Any]) -> List[str]:
        """
        Generate independent paths menggunakan ABPC Algorithm, 
        kemudian filter hanya paths yang memiliki minimal satu unexecuted node (tr_status='N')
        
        Option A: Filter setelah generate semua independent paths
        """
        if not nodes or not edges:
            return []

        # normalize nodes
        node_by_id: Dict[str, Dict[str, Any]] = {}
        for node in nodes:
            node_dict = self._normalize_node(node)
            node_id = self._get_node_id(node_dict)
            if node_id is not None:
                node_by_id[node_id] = node_dict

        # normalize edges untuk format yang diharapkan oleh generate_independent_paths
        normalized_edges = []
        for edge in edges:
            edge_dict = self._normalize_node(edge)
            source = (
                edge_dict.get("id_node_start")
                or edge_dict.get("ms_id_start_node")
                or edge_dict.get("id_start_node")
            )
            target = (
                edge_dict.get("id_node_finish")
                or edge_dict.get("ms_id_finish_node")
                or edge_dict.get("id_finish_node")
            )
            
            if source is None or target is None:
                continue

            source_str = str(source)
            target_str = str(target)
            
            if source_str not in node_by_id or target_str not in node_by_id:
                continue

            branch_type = (
                edge_dict.get("ms_branch_type")
                or edge_dict.get("ms_label")
                or edge_dict.get("branch_type")
                or edge_dict.get("label")
                or ""
            )

            normalized_edges.append({
                "id_start_node": source_str,
                "id_finish_node": target_str,
                "branch_type": str(branch_type).upper(),
                "ms_id_edge": edge_dict.get("ms_id_edge") or edge_dict.get("id_edge") or ""
            })

        if not normalized_edges:
            return []

        # convert node dicts ke NodeAdapter objects
        node_adapters = [NodeAdapter(node_dict) for node_dict in node_by_id.values()]

        # PHASE A: Generate semua independent paths menggunakan ABPC Algorithm
        try:
            all_independent_paths = generate_independent_paths(node_adapters, normalized_edges)
        except Exception as e:
            logger.error(f"Error generating independent paths: {e}")
            return []

        # identify unexecuted nodes (tr_status='N')
        unexecuted_set = set()
        for node in nodes:
            norm_node = self._normalize_node(node)
            status = str(norm_node.get("tr_status", "")).upper()
            node_type = str(norm_node.get("ms_node_type") or norm_node.get("node_type") or "").upper()
            
            if status == "N" and node_type not in ["START", "END"]:
                node_id = self._get_node_id(norm_node)
                if node_id is not None:
                    unexecuted_set.add(node_id)

        # PHASE B: Filter paths untuk hanya yang memiliki minimal satu unexecuted node
        filtered_paths = []
        for path_result in all_independent_paths:
            path_ids = path_result.get("ids", [])
            if any(node_id in unexecuted_set for node_id in path_ids):
                filtered_paths.append(path_result.get("path", ""))

        # Sort paths numerically by their displayed labels
        def parse_path_for_sorting(path: str):
            try:
                return [float(x) for x in path.split("→")]
            except Exception:
                return [0.0]

        return sorted(filtered_paths, key=parse_path_for_sorting)