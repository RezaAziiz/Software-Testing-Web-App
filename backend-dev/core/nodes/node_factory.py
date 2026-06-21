from .normal_node import CfgNormalNode
from .bool_node import CfgBoolExprNode
from core.types import NodeType, AstNodeType

class NodeFactory:
    @staticmethod
    def create_node(ast_node, force_decision=False, custom_type=None):
        if not ast_node:
            return None

        decision_types = [
            AstNodeType.IF_STATEMENT,
            AstNodeType.WHILE_STATEMENT,
            AstNodeType.FOR_STATEMENT,
            AstNodeType.SWITCH_STATEMENT,
            AstNodeType.SWITCH_EXPRESSION,
            AstNodeType.DO_STATEMENT,

        ]
        switch_types = [AstNodeType.SWITCH_STATEMENT, AstNodeType.SWITCH_EXPRESSION]
            
        if force_decision or ast_node.type in [t.value for t in decision_types]:
            node = CfgBoolExprNode(ast_node)
            
            if custom_type: 
                node.node_type = custom_type
            elif ast_node.type in [t.value for t in switch_types]:
                node.node_type = NodeType.SWITCH 
            else:
                node.node_type = NodeType.DECISION
                
            return node
        
        node = CfgNormalNode(ast_node)
        
        if custom_type:
            node.node_type = custom_type
        elif ast_node.type == AstNodeType.RETURN_STATEMENT:
            node.node_type = NodeType.RETURN
        elif ast_node.type == AstNodeType.BREAK_STATEMENT:
            node.node_type = NodeType.BREAK
        elif ast_node.type == AstNodeType.CONTINUE_STATEMENT:
            node.node_type = NodeType.CONTINUE
            
        return node
