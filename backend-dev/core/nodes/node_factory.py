from .normal_node import CfgNormalNode
from .bool_node import CfgBoolExprNode
from core.types import NodeType

class NodeFactory:
    @staticmethod
    def create_node(ast_node, force_decision=False, custom_type=None):
        if not ast_node:
            return None
            
        if force_decision or ast_node.type in ['if_statement', 'while_statement', 'for_statement', 'switch_statement', 'switch_expression']:
            node = CfgBoolExprNode(ast_node)
            
            if custom_type: 
                node.node_type = custom_type
            elif ast_node.type in ['switch_statement', 'switch_expression']:
                node.node_type = NodeType.SWITCH 
            else:
                node.node_type = NodeType.DECISION
                
            return node
        
        node = CfgNormalNode(ast_node)
        
        if custom_type:
            node.node_type = custom_type
        elif ast_node.type == 'return_statement':
            node.node_type = NodeType.RETURN
        elif ast_node.type == 'break_statement':
            node.node_type = NodeType.BREAK
        elif ast_node.type == 'continue_statement':
            node.node_type = NodeType.CONTINUE
            
        return node
