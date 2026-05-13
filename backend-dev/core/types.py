
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
