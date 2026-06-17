import logging
from collections import Counter
from typing import Any, Dict, List, Set, Tuple

logger = logging.getLogger(__name__)


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
        if not nodes or not edges:
            return []

        # normalize nodes
        node_by_id: Dict[str, Dict[str, Any]] = {}
        for node in nodes:
            node_dict = self._normalize_node(node)
            node_id = self._get_node_id(node_dict)
            if node_id is not None:
                node_by_id[node_id] = node_dict

        def get_order(node_id: str) -> float:
            node = node_by_id.get(node_id, {})
            order = node.get("ms_execution_order") or node.get("execution_order")
            if order is not None:
                try:
                    return float(order)
                except (ValueError, TypeError):
                    pass
            return float("inf")

        def sort_key(node_id: str):
            return (get_order(node_id), str(node_id))

        # build adjacency with edge metadata
        adjacency: Dict[str, List[Tuple[str, Dict[str, Any]]]] = {nid: [] for nid in node_by_id}
        incoming_count: Dict[str, int] = {nid: 0 for nid in node_by_id}
        outgoing_count: Dict[str, int] = {nid: 0 for nid in node_by_id}

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

            # normalize branch_type name from edge metadata (support multiple column names)
            branch_type = (
                edge_dict.get("ms_branch_type")
                or edge_dict.get("ms_label")
                or edge_dict.get("branch_type")
                or edge_dict.get("label")
                or ""
            )
            # store the edge metadata for later decisions
            edge_meta = {
                "branch_type": str(branch_type).upper(),
                "edge_id": str(edge_dict.get("ms_id_edge") or edge_dict.get("id_edge") or "")
            }

            adjacency[source_str].append((target_str, edge_meta))
            incoming_count[target_str] += 1
            outgoing_count[source_str] += 1

        # sort neighbors deterministically
        for src, neighbors in adjacency.items():
            neighbors.sort(key=lambda t: (get_order(t[0]), t[0]))

        all_node_ids = sorted(node_by_id.keys(), key=sort_key)

        # prefer explicit START/END nodes if present
        entry_nodes = [nid for nid in all_node_ids if (node_by_id[nid].get("ms_node_type") or node_by_id[nid].get("node_type") or "").upper() == "START"]
        if not entry_nodes:
            entry_nodes = [nid for nid in all_node_ids if incoming_count[nid] == 0]

        exit_nodes = [nid for nid in all_node_ids if (node_by_id[nid].get("ms_node_type") or node_by_id[nid].get("node_type") or "").upper() == "END"]
        if not exit_nodes:
            exit_nodes = [nid for nid in all_node_ids if outgoing_count[nid] == 0]

        starts = entry_nodes if entry_nodes else all_node_ids[:1]
        goals = set(exit_nodes if exit_nodes else all_node_ids[-1:])

        # unexecuted nodes set (use node execution status)
        unexecuted_set = {
            self._get_node_id(self._normalize_node(node))
            for node in nodes
            for node_dict in [self._normalize_node(node)]
            if str(node_dict.get("tr_status", "")).upper() == "N"
        }
        unexecuted_set.discard(None)

        # display map (labels)
        display_map: Dict[str, str] = {}
        sorted_ids = sorted(node_by_id.keys(), key=sort_key)
        for idx, nid in enumerate(sorted_ids, start=1):
            display_map[nid] = self._get_node_label(node_by_id[nid], idx)

        def format_path(path: List[str]) -> str:
            labels = [display_map.get(nid, "") for nid in path if display_map.get(nid, "")]
            return "→".join(labels)

        # Loop/back-edge detection helper
        def is_loop_back_edge(src: str, tgt: str, edge_meta: Dict[str, Any]) -> bool:
            bt = (edge_meta.get("branch_type") or "").upper()
            # explicit CONTINUE is loop-back
            if bt == "CONTINUE":
                return True
            # RETURN/BREAK are not loop-back
            if bt in ("RETURN", "BREAK"):
                return False
            # otherwise heuristics: back-edge if target execution order <= source execution order
            try:
                return get_order(tgt) <= get_order(src)
            except Exception:
                return False

        # DFS with per-loop iteration counters
        visited_paths: Set[str] = set()
        max_depth = min(15, 5 * max(1, len(node_by_id)))
        loop_iteration_limit = 2  # allow up to N iterations per loop header

        def dfs(current: str, path: List[str], has_unexecuted: bool, depth: int, loop_counts: Dict[str, int]):
            if depth > max_depth:
                return

            if current in goals and has_unexecuted:
                visited_paths.add(format_path(path))

            for neighbor, edge_meta in adjacency.get(current, []):
                # if neighbor already in path and edge is not a loop-back, skip
                if neighbor in path and not is_loop_back_edge(current, neighbor, edge_meta):
                    continue

                # if edge is loop-back, enforce a per-loop iteration limit
                if is_loop_back_edge(current, neighbor, edge_meta):
                    header = neighbor
                    count = loop_counts.get(header, 0)
                    if count >= loop_iteration_limit:
                        continue
                    next_loop_counts = dict(loop_counts)
                    next_loop_counts[header] = count + 1
                else:
                    next_loop_counts = dict(loop_counts)

                dfs(
                    neighbor,
                    path + [neighbor],
                    has_unexecuted or (neighbor in unexecuted_set),
                    depth + 1,
                    next_loop_counts,
                )

        for start in starts:
            dfs(start, [start], start in unexecuted_set, 1, {})

        # Sort paths numerically by their displayed labels when possible
        def parse_path_for_sorting(path: str):
            try:
                return [float(x) for x in path.split("→")]
            except Exception:
                return [0.0]

        return sorted(visited_paths, key=parse_path_for_sorting)