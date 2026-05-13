"""
CFGService - Orchestrates CFG generation from Java source code
Handles parsing, generation, optimization, and database persistence
"""
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import uuid4

from core.parser import JavaParser
from core.cfg_generator import CFGGeneratorVisitor
from core.types import NodeType, BranchType
from config.database import conn
from models.node import Node
from models.edge import Edge
from models.modul import Modul
from core.metrics import calculate_cyclomatic_complexity

logger = logging.getLogger(__name__)


class CFGResult:
    """Data class for CFG generation result"""
    def __init__(self, nodes: List[Any], edges: List[Dict], method_name: str = ""):
        self.nodes = nodes
        self.edges = edges
        self.method_name = method_name
        self.total_nodes = len(nodes)
        self.total_edges = len(edges)
    
    def to_dict(self):
        """Convert to dictionary for API response"""
        nodes_data = []
        for node in self.nodes:
            nodes_data.append({
                "id_node": node.id_node,
                "execution_order": node.execution_order,
                "code_fragment": node.source_code,
                "node_type": node.node_type.value if isinstance(node.node_type, NodeType) else str(node.node_type),
                "ast_node_type": node.ast_node_type,
                "line_start": node.line_start,
                "line_end": node.line_end,
            })
        
        edges_data = []
        for edge in self.edges:
            edges_data.append({
                "id_edge": edge["id_edge"],
                "id_start_node": edge["id_start_node"],
                "id_finish_node": edge["id_finish_node"],
                "branch_type": edge["branch_type"].value if isinstance(edge["branch_type"], BranchType) else str(edge["branch_type"]),
                "label": edge.get("label"),
            })
        
        return {
            "method_parsed": self.method_name,
            "total_nodes": self.total_nodes,
            "total_edges": self.total_edges,
            "nodes": nodes_data,
            "edges": edges_data,
        }


class CFGService:
    """Service for generating and managing Control Flow Graphs from Java code"""
    
    def __init__(self):
        self.parser = JavaParser()
        self.logger = logger
    
    def generate_cfg_from_java_code(
        self, 
        java_code: str, 
        method_name: Optional[str] = None
    ) -> CFGResult:
        """
        Generate CFG from Java source code
        
        Args:
            java_code: Java source code as string
            method_name: Optional specific method name to analyze. If not provided, uses first method found
        
        Returns:
            CFGResult: Generated nodes and edges
        
        Raises:
            ValueError: If code cannot be parsed or no methods found
        """
        try:
            # Parse Java code to AST
            tree = self.parser.parse_source_code(java_code)
            
            # Extract target method
            if method_name:
                method_node = self.parser.find_method_by_name(tree, method_name)
                if not method_node:
                    raise ValueError(f"Method '{method_name}' not found in source code")
            else:
                # Use first method if not specified
                methods = self.parser.extract_all_methods(tree)
                if not methods:
                    raise ValueError("No methods found in source code")
                method_node = methods[0]
                # Extract method name for response
                for child in method_node.children:
                    if child.type == 'identifier':
                        method_name = child.text.decode('utf8')
                        break
            
            # Generate CFG
            generator = CFGGeneratorVisitor()
            nodes, edges = generator.build_cfg(method_node)
            cc_score = calculate_cyclomatic_complexity(nodes, edges)
            
            self.logger.info(f"Generated CFG for method '{method_name}': {len(nodes)} nodes, {len(edges)} edges")
            
            return CFGResult(nodes, edges, method_name or "unknown")
        
        except Exception as e:
            self.logger.error(f"Error generating CFG: {str(e)}")
            raise ValueError(f"Failed to generate CFG: {str(e)}")
    
    def save_cfg_to_database(
        self, 
        modul_id: str, 
        cfg_result: CFGResult,
        source_code: str,
        created_by: str = "system"
    ) -> bool:
        """
        Save generated CFG nodes and edges to database
        
        Args:
            modul_id: Module ID for which CFG is being saved
            cfg_result: CFGResult object with nodes and edges
            source_code: Original Java source code
            created_by: User/system creating the record
        
        Returns:
            bool: True if save successful, False otherwise
        """
        try:
            now = datetime.now()
            
            # Insert nodes
            for node in cfg_result.nodes:
                insert_stmt = Node.insert().values(
                    ms_id_node=node.id_node,
                    ms_id_modul=modul_id,
                    ms_execution_order=node.execution_order,
                    ms_line_number=node.line_start,
                    ms_line_start=node.line_start,
                    ms_line_end=node.line_end,
                    ms_source_code=node.source_code,
                    ms_ast_node_type=node.ast_node_type,
                    ms_node_type=node.node_type.value if isinstance(node.node_type, NodeType) else str(node.node_type),
                    createdby=created_by,
                    created=now,
                    updatedby=created_by,
                    updated=now,
                )
                conn.execute(insert_stmt)
            
            # Insert edges
            for edge in cfg_result.edges:
                insert_stmt = Edge.insert().values(
                    ms_id_edge=edge["id_edge"],
                    ms_id_modul=modul_id,
                    ms_id_start_node=edge["id_start_node"],
                    ms_id_finish_node=edge["id_finish_node"],
                    ms_branch_type=edge["branch_type"].value if isinstance(edge["branch_type"], BranchType) else str(edge["branch_type"]),
                    ms_label=edge.get("label"),
                    createdby=created_by,
                    created=now,
                    updatedby=created_by,
                    updated=now,
                )
                conn.execute(insert_stmt)
            
            # Calculate and update module cyclomatic complexity score
            cc_score = calculate_cyclomatic_complexity(cfg_result.nodes, cfg_result.edges)
            update_modul = Modul.update().values(
                ms_cc=cc_score,
                updatedby=created_by,
                updated=now,
            ).where(Modul.c.ms_id_modul == modul_id)
            conn.execute(update_modul)
            
            self.logger.info(f"Saved CFG for modul {modul_id}: {len(cfg_result.nodes)} nodes, {len(cfg_result.edges)} edges, cc={cc_score}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error saving CFG to database: {str(e)}")
            raise
    
    def delete_cfg_for_modul(self, modul_id: str) -> bool:
        """
        Delete existing CFG data for a module (for re-generation)
        
        Args:
            modul_id: Module ID
        
        Returns:
            bool: True if successful
        """
        try:
            # Delete edges first (foreign key constraint)
            delete_edges = Edge.delete().where(Edge.c.ms_id_modul == modul_id)
            conn.execute(delete_edges)
            
            # Delete nodes
            delete_nodes = Node.delete().where(Node.c.ms_id_modul == modul_id)
            conn.execute(delete_nodes)
            
            self.logger.info(f"Deleted CFG for modul {modul_id}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error deleting CFG: {str(e)}")
            raise
    
    def get_cfg_for_modul(self, modul_id: str) -> tuple[List, List]:
        """
        Retrieve CFG nodes and edges for a module from database
        
        Args:
            modul_id: Module ID
        
        Returns:
            tuple: (nodes_list, edges_list)
        """
        try:
            # Get nodes
            select_nodes = Node.select().where(Node.c.ms_id_modul == modul_id).order_by(Node.c.ms_execution_order)
            nodes_result = conn.execute(select_nodes).fetchall()
            
            nodes_data = []
            for row in nodes_result:
                nodes_data.append({
                    "id_node": row.ms_id_node,
                    "execution_order": row.ms_execution_order,
                    "code_fragment": row.ms_source_code,
                    "node_type": row.ms_node_type,
                    "ast_node_type": row.ms_ast_node_type,
                    "line_start": row.ms_line_start,
                    "line_end": row.ms_line_end,
                })
            
            # Get edges
            select_edges = Edge.select().where(Edge.c.ms_id_modul == modul_id)
            edges_result = conn.execute(select_edges).fetchall()
            
            edges_data = []
            for row in edges_result:
                edges_data.append({
                    "id_edge": row.ms_id_edge,
                    "id_start_node": row.ms_id_start_node,
                    "id_finish_node": row.ms_id_finish_node,
                    "branch_type": row.ms_branch_type,
                    "label": row.ms_label,
                })
            
            self.logger.info(f"Retrieved CFG for modul {modul_id}: {len(nodes_data)} nodes, {len(edges_data)} edges")
            return nodes_data, edges_data
        
        except Exception as e:
            self.logger.error(f"Error retrieving CFG: {str(e)}")
            return [], []
    
    def extract_method_names(self, java_code: str) -> List[str]:
        """
        Extract all method names from Java source code
        
        Args:
            java_code: Java source code
        
        Returns:
            List of method names found
        """
        try:
            tree = self.parser.parse_source_code(java_code)
            methods = self.parser.extract_all_methods(tree)
            
            method_names = []
            for method in methods:
                for child in method.children:
                    if child.type == 'identifier':
                        method_names.append(child.text.decode('utf8'))
                        break
            
            return method_names
        except Exception as e:
            self.logger.error(f"Error extracting method names: {str(e)}")
            return []
