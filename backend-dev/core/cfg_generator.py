import uuid
from dataclasses import dataclass
from core.nodes.base_node import CfgNode
from core.nodes.node_factory import NodeFactory
from core.types import BranchType, NodeType
from core.optimizer import optimize_merge_nodes

@dataclass
class ExitNode:
    """Dataclass untuk standarisasi tipe data keluaran"""
    node: CfgNode
    branch_type: BranchType = BranchType.SEQUENTIAL
class CFGGeneratorVisitor:
    def __init__(self):
        self.nodes = []
        self.edges = []
        self.current_execution_order = 1

    # HELPER METHODS
    def _register_node(self, node):
        """Helper untuk meregistrasikan node ke dalam array dan menambah sequence."""
        if node.node_type != NodeType.MERGE:
            node.execution_order = self.current_execution_order
            self.current_execution_order += 1
        else:
            node.execution_order = None
        self.nodes.append(node)
        return node

    def create_edge(self, source_node, target_node, branch_type=BranchType.SEQUENTIAL):
        if source_node and target_node:
            self.edges.append({
                "id_edge": str(uuid.uuid4()),
                "id_start_node": source_node.id_node,
                "id_finish_node": target_node.id_node,
                "branch_type": branch_type,
                "label": branch_type,
            })

    def _process_loop_exits(self, body_exits, loop_node, exit_nodes):
        """Helper untuk menangani kondisi node yang meloncat keluar dari loop (Break/Continue/Return)"""
        for exit_item in body_exits:
            branch = exit_item.branch_type
            src_node = exit_item.node
            
            if branch == BranchType.BREAK:
                exit_nodes.append(ExitNode(src_node, BranchType.SEQUENTIAL))
            elif branch == BranchType.CONTINUE:
                self.create_edge(src_node, loop_node, BranchType.SEQUENTIAL)
            elif branch == BranchType.RETURN:
                exit_nodes.append(exit_item)
            else:
                self.create_edge(src_node, loop_node, branch)
        return exit_nodes

    def _get_body_block(self, method_node):
        for child in method_node.children:
            if child.type == 'block':
                return child
        return None

    # CORE BUILDER
    def build_cfg(self, method_node):
        body_block = self._get_body_block(method_node)
                
        if not body_block:
            return self.nodes, self.edges
            
        self.visit_block(body_block, incoming_nodes=[])
        
        self.nodes, self.edges = optimize_merge_nodes(self.nodes, self.edges)
        self._reassign_execution_orders()
        
        return self.nodes, self.edges

    def _reassign_execution_orders(self):
        """Reassign sequential execution order only for non-merge nodes.
        Merge nodes keep a null execution order to stay unlabeled.
        """
        order = 1
        for node in self.nodes:
            if node.node_type == NodeType.MERGE:
                node.execution_order = None
            else:
                node.execution_order = order
                order += 1

    # VISITOR METHODS
    def visit_block(self, ast_block, incoming_nodes):
        statements = [
            child for child in ast_block.children 
            if child.is_named and child.type not in ['line_comment', 'block_comment']
        ]
        current_incoming = incoming_nodes
        first_node_of_block = None
        block_jump_exits = []
        
        for stmt in statements:
            method_name = f'visit_{stmt.type}'
            visitor_method = getattr(self, method_name, self.generic_visit)
            
            entry_node, exit_nodes = visitor_method(stmt)
            
            if not first_node_of_block:
                first_node_of_block = entry_node
                
            for inc in current_incoming:
                self.create_edge(inc.node, entry_node, inc.branch_type)
                
            next_incoming = []
            for ex in exit_nodes:
                if ex.branch_type in [BranchType.RETURN, BranchType.BREAK, BranchType.CONTINUE]:
                    block_jump_exits.append(ex)
                else:
                    next_incoming.append(ex)
            
            current_incoming = next_incoming
            if len(current_incoming) == 0:
                break 
            
        return first_node_of_block, current_incoming + block_jump_exits

    def generic_visit(self, ast_node):
        node = NodeFactory.create_node(ast_node)
        self._register_node(node)
        return node, [ExitNode(node)]

    def visit_if_statement(self, ast_node):
        cond_ast = ast_node.child_by_field_name('condition')
        then_ast = ast_node.child_by_field_name('consequence')
        else_ast = ast_node.child_by_field_name('alternative')

        cond_node = NodeFactory.create_node(cond_ast, force_decision=True)
        self._register_node(cond_node)

        # Buat MERGE NODE
        merge_node = CfgNode(ast_node)
        merge_node.node_type = NodeType.MERGE
        merge_node.source_code = "" 
        self._register_node(merge_node)

        exit_nodes = [] 
        connected_to_merge = set()

        # Proses blok TRUE
        if then_ast:
            if then_ast.type == 'block':
                then_first, then_exits = self.visit_block(then_ast, incoming_nodes=[])
            else:
                then_first, then_exits = getattr(self, f'visit_{then_ast.type}', self.generic_visit)(then_ast)
            
            cond_node.set_true_node(then_first)
            self.create_edge(cond_node, then_first, BranchType.TRUE)
            
            for ex in then_exits:
                if ex.branch_type in [BranchType.BREAK, BranchType.CONTINUE]:
                    exit_nodes.append(ex) 
                else:
                    if ex.node.id_node not in connected_to_merge:
                        self.create_edge(ex.node, merge_node, BranchType.SEQUENTIAL) 
                        connected_to_merge.add(ex.node.id_node)
                        
                    if ex.branch_type == BranchType.RETURN:
                        if not any(e.node == merge_node and e.branch_type == BranchType.RETURN for e in exit_nodes):
                            exit_nodes.append(ExitNode(merge_node, BranchType.RETURN))
            
        # Proses blok FALSE
        if else_ast:
            if else_ast.type == 'block':
                else_first, else_exits = self.visit_block(else_ast, incoming_nodes=[])
            else:
                else_first, else_exits = getattr(self, f'visit_{else_ast.type}', self.generic_visit)(else_ast)
                
            cond_node.set_false_node(else_first)
            self.create_edge(cond_node, else_first, BranchType.FALSE)
            
            for ex in else_exits:
                if ex.branch_type in [BranchType.BREAK, BranchType.CONTINUE]:
                    exit_nodes.append(ex)
                else:
                    if ex.node.id_node not in connected_to_merge:
                        self.create_edge(ex.node, merge_node, BranchType.SEQUENTIAL) 
                        connected_to_merge.add(ex.node.id_node)
                        
                    if ex.branch_type == BranchType.RETURN:
                        if not any(e.node == merge_node and e.branch_type == BranchType.RETURN for e in exit_nodes):
                            exit_nodes.append(ExitNode(merge_node, BranchType.RETURN))
        else:
            self.create_edge(cond_node, merge_node, BranchType.FALSE)
            
        if not any(e.node == merge_node and e.branch_type == BranchType.SEQUENTIAL for e in exit_nodes):
            exit_nodes.append(ExitNode(merge_node, BranchType.SEQUENTIAL))

        return cond_node, exit_nodes

    def visit_for_statement(self, ast_node):
        body_ast = ast_node.child_by_field_name('body')
        for_node = NodeFactory.create_node(ast_node, force_decision=True)
        
        full_text = for_node.source_code
        first_line = full_text.split('\n')[0].strip()
        for_node.source_code = first_line

        self._register_node(for_node)

        exit_nodes = [ExitNode(for_node, BranchType.FALSE)] 

        if body_ast:
            if body_ast.type == 'block':
                body_first, body_exits = self.visit_block(body_ast, incoming_nodes=[])
            else:
                body_first, body_exits = getattr(self, f'visit_{body_ast.type}', self.generic_visit)(body_ast)
            
            for_node.set_true_node(body_first)
            self.create_edge(for_node, body_first, BranchType.TRUE)
            
            exit_nodes = self._process_loop_exits(body_exits, for_node, exit_nodes)

        return for_node, exit_nodes

    def visit_while_statement(self, ast_node):
        cond_ast = ast_node.child_by_field_name('condition')
        body_ast = ast_node.child_by_field_name('body')

        cond_node = NodeFactory.create_node(cond_ast, force_decision=True)
        self._register_node(cond_node)

        exit_nodes = [ExitNode(cond_node, BranchType.FALSE)]
        
        if body_ast:
            if body_ast.type == 'block':
                body_first, body_exits = self.visit_block(body_ast, incoming_nodes=[])
            else:
                body_first, body_exits = getattr(self, f'visit_{body_ast.type}', self.generic_visit)(body_ast)
            
            cond_node.set_true_node(body_first)
            self.create_edge(cond_node, body_first, BranchType.TRUE)
            
            exit_nodes = self._process_loop_exits(body_exits, cond_node, exit_nodes)

        return cond_node, exit_nodes
    

    def visit_switch_statement(self, ast_node):
        return self._process_switch(ast_node)
        
    def visit_switch_expression(self, ast_node):
        return self._process_switch(ast_node)
        
    def _process_switch(self, ast_node):
        cond_ast = ast_node.child_by_field_name('condition')
        body_ast = ast_node.child_by_field_name('body') # Ini adalah switch_block

        # Buat Node Kondisi Switch
        cond_node = NodeFactory.create_node(cond_ast, force_decision=True)
        self._register_node(cond_node)

        # Buat MERGE NODE untuk titik kumpul di akhir switch
        merge_node = CfgNode(ast_node)
        merge_node.node_type = NodeType.MERGE
        merge_node.source_code = "" 
        self._register_node(merge_node)

        exit_nodes = []
        fallthrough_incoming = []
        has_default = False

        if body_ast:
            for group in body_ast.children:
                if group.type == 'switch_block_statement_group':
                    
                    current_incoming = fallthrough_incoming
                    fallthrough_incoming = []
                    
                    for child in group.children:
                        if not child.is_named or child.type in ['line_comment', 'block_comment']:
                            continue
                            
                        if child.type == 'switch_label':
                            label_node = NodeFactory.create_node(child)
                            self._register_node(label_node)
                            
                            is_default = 'default' in child.text.decode('utf8')
                            if is_default:
                                has_default = True
                                branch_type = BranchType.DEFAULT
                            else:
                                branch_type = BranchType.CASE
                            
                            self.create_edge(cond_node, label_node, branch_type)
                            
                            # Jika ada efek fallthrough
                            for inc in current_incoming:
                                self.create_edge(inc.node, label_node, inc.branch_type)
                                
                            # Siapkan statement selanjutnya
                            current_incoming = [ExitNode(label_node, BranchType.SEQUENTIAL)]
                            
                        else:
                            # instruksi dalam case (misal: vokal = true; atau break;)
                            method_name = f'visit_{child.type}'
                            visitor_method = getattr(self, method_name, self.generic_visit)
                            entry_node, stmt_exits = visitor_method(child)
                            
                            for inc in current_incoming:
                                self.create_edge(inc.node, entry_node, inc.branch_type)
                                
                            next_incoming = []
                            for ex in stmt_exits:
                                if ex.branch_type == BranchType.BREAK:
                                    # Break memotong switch, arahnya keluar ke merge node!
                                    self.create_edge(ex.node, merge_node, BranchType.SEQUENTIAL)
                                elif ex.branch_type in [BranchType.RETURN, BranchType.CONTINUE]:
                                    exit_nodes.append(ex)
                                else:
                                    next_incoming.append(ex)
                                    
                            current_incoming = next_incoming
                            if len(current_incoming) == 0:
                                break
                                
                    # Jika case selesai tanpa break, sisa garisnya akan jatuh/fallthrough ke case bawahnya
                    fallthrough_incoming = current_incoming
                    
        # Sisa Fallthrough di bagian paling bawah otomatis mengalir ke Merge Node
        for inc in fallthrough_incoming:
            self.create_edge(inc.node, merge_node, inc.branch_type)
            
        if not has_default:
            self.create_edge(cond_node, merge_node, BranchType.FALSE)
            
        exit_nodes.append(ExitNode(merge_node, BranchType.SEQUENTIAL))
        
        return cond_node, exit_nodes
    
    def visit_return_statement(self, ast_node):
        node = NodeFactory.create_node(ast_node)
        self._register_node(node)
        return node, [ExitNode(node, BranchType.RETURN)]

    def visit_break_statement(self, ast_node):
        node = NodeFactory.create_node(ast_node)
        self._register_node(node)
        return node, [ExitNode(node, BranchType.BREAK)]

    def visit_continue_statement(self, ast_node):
        node = NodeFactory.create_node(ast_node)
        self._register_node(node)
        return node, [ExitNode(node, BranchType.CONTINUE)]