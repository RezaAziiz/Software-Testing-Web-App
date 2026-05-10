from core.types import NodeType

def optimize_merge_nodes(nodes, edges):
    changed = True
    while changed:
        changed = False
        node_map = {n.id_node: n for n in nodes}
        
        for edge in edges:
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
                
    return nodes, edges
