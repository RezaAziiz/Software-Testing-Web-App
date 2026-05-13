from .base_node import CfgNode
from core.types import NodeType

class CfgNormalNode(CfgNode):
    def __init__(self, ast_node):
        super().__init__(ast_node)
        self.node_type = NodeType.NORMAL 
