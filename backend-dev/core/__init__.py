# CFG Core Module - Migrated from ast_to_cfg_engine
from .parser import JavaParser
from .cfg_generator import CFGGeneratorVisitor
from .optimizer import optimize_merge_nodes
from .types import NodeType, BranchType
from .nodes.node_factory import NodeFactory

__all__ = [
    'JavaParser',
    'CFGGeneratorVisitor',
    'optimize_merge_nodes',
    'NodeType',
    'BranchType',
    'NodeFactory',
]
