from core.types import BranchType, NodeType

def _dedupe_edges(edges):
    seen = set()
    unique = []
    for edge in edges:
        key = (edge['id_start_node'], edge['id_finish_node'], edge['branch_type'], edge['label'])
        if key not in seen:
            seen.add(key)
            unique.append(edge)
    return unique


def optimize_merge_nodes(nodes, edges):
    changed = True
    while changed:
        changed = False
        node_map = {n.id_node: n for n in nodes}

        incoming = {n.id_node: [] for n in nodes}
        outgoing = {n.id_node: [] for n in nodes}
        
        for edge in edges:
            outgoing[edge['id_start_node']].append(edge)
            incoming[edge['id_finish_node']].append(edge)

        for edge in list(edges):
            if edge['branch_type'] != BranchType.SEQUENTIAL:
                continue

            start_node = node_map.get(edge['id_start_node'])
            finish_node = node_map.get(edge['id_finish_node'])
            
            if not start_node or not finish_node:
                continue
            if start_node.node_type != NodeType.NORMAL or finish_node.node_type != NodeType.NORMAL:
                continue
            if len(outgoing[start_node.id_node]) != 1 or len(incoming[finish_node.id_node]) != 1:
                continue

            start_node.source_code = start_node.source_code.rstrip() + "\n" + finish_node.source_code.lstrip()
            start_node.line_end = finish_node.line_end

            for e in edges:
                if e['id_start_node'] == finish_node.id_node:
                    e['id_start_node'] = start_node.id_node
                if e['id_finish_node'] == finish_node.id_node:
                    e['id_finish_node'] = start_node.id_node

            edges.remove(edge)
            nodes.remove(finish_node)
            changed = True
            break

        if changed:
            edges = _dedupe_edges(edges)
            continue

        node_map = {n.id_node: n for n in nodes}
        for edge in list(edges):
            start_node = node_map.get(edge['id_start_node'])
            finish_node = node_map.get(edge['id_finish_node'])

            if start_node and finish_node and start_node.node_type == NodeType.MERGE and finish_node.node_type == NodeType.MERGE:
                for e in edges:
                    if e['id_finish_node'] == start_node.id_node:
                        e['id_finish_node'] = finish_node.id_node
                edges.remove(edge)
                nodes.remove(start_node)
                changed = True
                break

        if changed:
            edges = _dedupe_edges(edges)

    return nodes, edges