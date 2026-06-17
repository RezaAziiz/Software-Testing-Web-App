import uuid
from core.types import NodeType, AstNodeType

class CfgNode:
    def __init__(self, ast_node):
        self.id_node = str(uuid.uuid4())
        self.ast_node = ast_node
        self.ast_node_type = ast_node.type if ast_node else AstNodeType.VIRTUAL
        self.source_code = ast_node.text.decode('utf8') if ast_node else ""
        self.line_start = ast_node.start_point[0] + 1 if ast_node else 0
        self.line_end = ast_node.end_point[0] + 1 if ast_node else 0
        self.execution_order = None
        self.node_type = NodeType.UNKNOWN
