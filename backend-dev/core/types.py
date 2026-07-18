
from enum import Enum
class BranchType(str, Enum):
    TRUE = "TRUE"
    FALSE = "FALSE"
    SEQUENTIAL = "SEQUENTIAL"
    BREAK = "BREAK"
    CONTINUE = "CONTINUE"
    RETURN = "RETURN"
    CASE = "CASE"          
    DEFAULT = "DEFAULT"

class NodeType(str, Enum):
    NORMAL = "NORMAL"
    DECISION = "DECISION"
    MERGE = "MERGE"
    RETURN = "RETURN"
    BREAK = "BREAK"
    CONTINUE = "CONTINUE"
    UNKNOWN = "UNKNOWN"
    SWITCH = "SWITCH"
    START = "START"  
    END = "END"

class AstNodeType(str, Enum):
    """AST node types from tree-sitter Java grammar"""
    # Struktur
    METHOD_DECLARATION = "method_declaration"
    BLOCK = "block"
    IDENTIFIER = "identifier"
    
    # Komentar
    LINE_COMMENT = "line_comment"
    BLOCK_COMMENT = "block_comment"
    
    # Statement Percabangan & Perulangan (Decision/Loop)
    IF_STATEMENT = "if_statement"
    WHILE_STATEMENT = "while_statement"
    DO_STATEMENT = "do_statement"
    FOR_STATEMENT = "for_statement"
    LABELED_STATEMENT = "labeled_statement"
    ENHANCED_FOR_STATEMENT = "enhanced_for_statement"
    
    # Switch Case
    SWITCH_STATEMENT = "switch_statement"
    SWITCH_EXPRESSION = "switch_expression"
    SWITCH_BLOCK_GROUP = "switch_block_statement_group"
    SWITCH_LABEL = "switch_label"
    
    # Control Flow Interruption (Jumps)
    RETURN_STATEMENT = "return_statement"
    BREAK_STATEMENT = "break_statement"
    CONTINUE_STATEMENT = "continue_statement"
    
    # Statements
    EXPRESSION_STATEMENT = "expression_statement"
    
    # Ekspresi
    PARENTHESIZED_EXPRESSION = "parenthesized_expression"
    
    # Virtual nodes (Start/End)
    VIRTUAL = "virtual"
