from .base_node import CfgNode
from core.types import NodeType

class CfgBoolExprNode(CfgNode):
    def __init__(self, ast_node):
        super().__init__(ast_node)
        self.node_type = NodeType.DECISION
        self.true_node = None
        self.false_node = None
        
    def set_true_node(self, node):
        self.true_node = node
        
    def set_false_node(self, node):
        self.false_node = node
