import uuid
from dataclasses import dataclass
from core.nodes.base_node import CfgNode
from core.nodes.node_factory import NodeFactory
from core.types import BranchType, NodeType, AstNodeType
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
            if child.type == AstNodeType.BLOCK:
                return child
        return None

    # CORE BUILDER
    def build_cfg(self, method_node):
        body_block = self._get_body_block(method_node)
                
        if not body_block:
            return self.nodes, self.edges
            
        # BUAT START NODE
        start_node = CfgNode(None)
        start_node.node_type = NodeType.START
        start_node.source_code = "Start"
        self._register_node(start_node)
            
        # VISIT BLOK UTAMA
        # Masukkan start_node sebagai incoming_nodes agar langsung tersambung ke baris kode pertama
        first_node, final_exits = self.visit_block(
            body_block, 
            incoming_nodes=[ExitNode(start_node, BranchType.SEQUENTIAL)]
        )
        
        # BUAT END NODE
        end_node = CfgNode(None)
        end_node.node_type = NodeType.END
        end_node.source_code = "End"
        self._register_node(end_node)
        
        for ex in final_exits:
            self.create_edge(ex.node, end_node, BranchType.SEQUENTIAL)
        self.nodes, self.edges = optimize_merge_nodes(self.nodes, self.edges)
        self._reassign_execution_orders()
        
        return self.nodes, self.edges

    def _reassign_execution_orders(self):
        """Reassign sequential execution order only for non-merge/start/end nodes.
        Merge, Start, and End nodes keep a null execution order to stay unlabeled.
        """
        order = 1
        for node in self.nodes:
            # Abaikan penomoran untuk MERGE, START, dan END
            if node.node_type in [NodeType.MERGE, NodeType.START, NodeType.END]:
                node.execution_order = None
            else:
                node.execution_order = order
                order += 1

    # VISITOR METHODS
    def visit_block(self, ast_block, incoming_nodes):
        statements = [
            child for child in ast_block.children 
            if child.is_named and child.type not in [AstNodeType.LINE_COMMENT, AstNodeType.BLOCK_COMMENT]
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

        # Buat MERGE NODE sebagai titik kumpul
        merge_node = CfgNode(ast_node)
        merge_node.node_type = NodeType.MERGE
        merge_node.source_code = "" 
        self._register_node(merge_node)

        exit_nodes = [] 

        def process_exits(exits):
            for ex in exits:
                # Interupsi flow tidak boleh masuk ke merge node! Biarkan melayang ke outer scope.
                if ex.branch_type in [BranchType.RETURN, BranchType.BREAK, BranchType.CONTINUE]:
                    exit_nodes.append(ex)
                else:
                    self.create_edge(ex.node, merge_node, BranchType.SEQUENTIAL)

        # Proses blok TRUE
        if then_ast:
            if then_ast.type == AstNodeType.BLOCK:
                then_first, then_exits = self.visit_block(then_ast, incoming_nodes=[])
            else:
                then_first, then_exits = getattr(self, f'visit_{then_ast.type}', self.generic_visit)(then_ast)
            
            if then_first:
                cond_node.set_true_node(then_first)
                self.create_edge(cond_node, then_first, BranchType.TRUE)
                process_exits(then_exits)
            else:
                self.create_edge(cond_node, merge_node, BranchType.TRUE)
                
        # Proses blok FALSE
        if else_ast:
            if else_ast.type == AstNodeType.BLOCK:
                else_first, else_exits = self.visit_block(else_ast, incoming_nodes=[])
            else:
                else_first, else_exits = getattr(self, f'visit_{else_ast.type}', self.generic_visit)(else_ast)
                
            if else_first:
                cond_node.set_false_node(else_first)
                self.create_edge(cond_node, else_first, BranchType.FALSE)
                process_exits(else_exits)
            else:
                self.create_edge(cond_node, merge_node, BranchType.FALSE)
        else:
            # Jika if tanpa else, jalur False langsung memotong ke titik kumpul
            self.create_edge(cond_node, merge_node, BranchType.FALSE)

        # Hitung berapa banyak garis yang masuk ke merge_node
        incoming_edges = [e for e in self.edges if e['id_finish_node'] == merge_node.id_node]
        
        if len(incoming_edges) == 0:
            # Tidak ada jalur yang masuk (semua cabang return/break), buang merge node
            if merge_node in self.nodes:
                self.nodes.remove(merge_node)
                
        elif len(incoming_edges) == 1:
            single_edge = incoming_edges[0]
            
            # Hapus edge penengah dan hapus merge node
            self.edges.remove(single_edge)
            self.nodes.remove(merge_node)
            
            # Ambil node asalnya, teruskan branch type-nya langsung keluar dari if
            src_node_id = single_edge['id_start_node']
            src_node = next((n for n in self.nodes if n.id_node == src_node_id), None)
            
            if src_node:
                exit_nodes.append(ExitNode(src_node, single_edge['branch_type']))
                
        else:
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
            if body_ast.type == AstNodeType.BLOCK:
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
            if body_ast.type == AstNodeType.BLOCK:
                body_first, body_exits = self.visit_block(body_ast, incoming_nodes=[])
            else:
                body_first, body_exits = getattr(self, f'visit_{body_ast.type}', self.generic_visit)(body_ast)
            
            cond_node.set_true_node(body_first)
            self.create_edge(cond_node, body_first, BranchType.TRUE)
            
            exit_nodes = self._process_loop_exits(body_exits, cond_node, exit_nodes)

        return cond_node, exit_nodes
    
    def visit_do_statement(self, ast_node):
        body_ast = ast_node.child_by_field_name('body')
        cond_ast = ast_node.child_by_field_name('condition')

        # 1. Buat Node Kondisi, TAPI JANGAN DI-REGISTER DULU agar penomorannya mengalah
        cond_node = NodeFactory.create_node(cond_ast, force_decision=True)

        exit_nodes = [ExitNode(cond_node, BranchType.FALSE)]

        # 2. Proses Body terlebih dahulu agar masuk ke array `self.nodes` lebih awal
        if body_ast:
            if body_ast.type == AstNodeType.BLOCK:
                body_first, body_exits = self.visit_block(body_ast, incoming_nodes=[])
            else:
                body_first, body_exits = getattr(self, f'visit_{body_ast.type}', self.generic_visit)(body_ast)
            
            # 3. SEKARANG baru kita register cond_node (setelah body selesai didaftarkan)
            self._register_node(cond_node)
            
            # Arahkan aliran keluaran body ke kondisi
            exit_nodes = self._process_loop_exits(body_exits, cond_node, exit_nodes)
            
            # Loop back
            cond_node.set_true_node(body_first)
            self.create_edge(cond_node, body_first, BranchType.TRUE)
            
            entry_node = body_first
        else:
            # Fallback jika body kosong
            self._register_node(cond_node)
            cond_node.set_true_node(cond_node)
            self.create_edge(cond_node, cond_node, BranchType.TRUE)
            entry_node = cond_node

        return entry_node, exit_nodes

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
        has_default = False

        # Tipe-tipe statement yang memiliki control flow kompleks
        complex_types = [
            AstNodeType.IF_STATEMENT.value,
            AstNodeType.WHILE_STATEMENT.value,
            AstNodeType.DO_STATEMENT.value,
            AstNodeType.FOR_STATEMENT.value,
            AstNodeType.SWITCH_STATEMENT.value,
            AstNodeType.SWITCH_EXPRESSION.value,
        ]
        comment_types = [AstNodeType.LINE_COMMENT, AstNodeType.BLOCK_COMMENT]

        if not body_ast:
            if not has_default:
                self.create_edge(cond_node, merge_node, BranchType.FALSE)
            exit_nodes.append(ExitNode(merge_node, BranchType.SEQUENTIAL))
            return cond_node, exit_nodes

        # PHASE 1: Pre-merge groups
        raw_groups = [
            g for g in body_ast.children
            if g.type == AstNodeType.SWITCH_BLOCK_GROUP
        ]

        merged_groups = []  # list of dict: { 'labels': [...], 'stmts': [...] }
        pending_labels = []

        for group in raw_groups:
            children = [
                c for c in group.children
                if c.is_named and c.type not in comment_types
            ]
            labels = [c for c in children if c.type == AstNodeType.SWITCH_LABEL]
            stmts = [c for c in children if c.type != AstNodeType.SWITCH_LABEL]

            pending_labels.extend(labels)

            if len(stmts) > 0:
                # Group ini punya statement maka gabungkan dengan pending labels
                merged_groups.append({
                    'labels': list(pending_labels),
                    'stmts': stmts,
                })
                pending_labels = []
            # else: label-only group → labels ditampung, lanjut ke group berikutnya

        # Jika ada sisa pending labels tanpa statement (edge case)
        if pending_labels:
            merged_groups.append({
                'labels': list(pending_labels),
                'stmts': [],
            })

        # PHASE 2: Process setiap merged group
        fallthrough_incoming = []

        for mg in merged_groups:
            labels = mg['labels']
            stmts = mg['stmts']
            current_incoming = fallthrough_incoming
            fallthrough_incoming = []

            # Deteksi default case
            group_is_default = any('default' in l.text.decode('utf8') for l in labels)
            if group_is_default:
                has_default = True

            # Deteksi apakah ada statement kompleks
            has_complex = any(s.type in complex_types for s in stmts)

            if not has_complex:
                # === SIMPLE GROUP ===
                # Gabungkan semua (labels + stmts termasuk break) jadi 1 node
                all_parts = labels + stmts
                if not all_parts:
                    continue

                combined_text = '\n'.join(c.text.decode('utf8') for c in all_parts)
                line_start = all_parts[0].start_point[0] + 1
                line_end = all_parts[-1].end_point[0] + 1

                has_break = any(c.type == AstNodeType.BREAK_STATEMENT.value for c in stmts)

                block_node = CfgNode(all_parts[0])
                block_node.node_type = NodeType.NORMAL
                block_node.source_code = combined_text
                block_node.line_start = line_start
                block_node.line_end = line_end
                self._register_node(block_node)

                # Edge dari switch condition ke block node
                branch_type = BranchType.DEFAULT if group_is_default else BranchType.CASE
                self.create_edge(cond_node, block_node, branch_type)

                # Fallthrough dari group sebelumnya
                for inc in current_incoming:
                    self.create_edge(inc.node, block_node, inc.branch_type)

                if has_break:
                    self.create_edge(block_node, merge_node, BranchType.SEQUENTIAL)
                    fallthrough_incoming = []
                else:
                    fallthrough_incoming = [ExitNode(block_node, BranchType.SEQUENTIAL)]

            else:
                # === COMPLEX GROUP ===
                # Strategy: labels + simple prefix jadi 1 node, then visit complex, then simple suffix

                # Phase A: Prefix = labels + simple stmts sebelum complex pertama
                prefix_parts = list(labels)
                complex_start_idx = 0
                for i, s in enumerate(stmts):
                    if s.type in complex_types:
                        complex_start_idx = i
                        break
                    prefix_parts.append(s)
                    complex_start_idx = i + 1

                prefix_node = None
                if prefix_parts:
                    prefix_text = '\n'.join(c.text.decode('utf8') for c in prefix_parts)
                    prefix_line_start = prefix_parts[0].start_point[0] + 1
                    prefix_line_end = prefix_parts[-1].end_point[0] + 1

                    prefix_node = CfgNode(prefix_parts[0])
                    prefix_node.node_type = NodeType.NORMAL
                    prefix_node.source_code = prefix_text
                    prefix_node.line_start = prefix_line_start
                    prefix_node.line_end = prefix_line_end
                    self._register_node(prefix_node)

                    branch_type = BranchType.DEFAULT if group_is_default else BranchType.CASE
                    self.create_edge(cond_node, prefix_node, branch_type)

                    for inc in current_incoming:
                        self.create_edge(inc.node, prefix_node, inc.branch_type)

                    current_incoming = [ExitNode(prefix_node, BranchType.SEQUENTIAL)]

                # Phase B: Process remaining stmts
                remaining_stmts = stmts[complex_start_idx:]

                i = 0
                while i < len(remaining_stmts):
                    stmt = remaining_stmts[i]

                    if stmt.type in complex_types:
                        method_name = f'visit_{stmt.type}'
                        visitor_method = getattr(self, method_name, self.generic_visit)
                        entry_node, stmt_exits = visitor_method(stmt)

                        if not prefix_node and len(current_incoming) == 0:
                            bt = BranchType.DEFAULT if group_is_default else BranchType.CASE
                            self.create_edge(cond_node, entry_node, bt)
                            for inc_ft in fallthrough_incoming:
                                self.create_edge(inc_ft.node, entry_node, inc_ft.branch_type)
                        else:
                            for inc in current_incoming:
                                self.create_edge(inc.node, entry_node, inc.branch_type)

                        next_incoming = []
                        for ex in stmt_exits:
                            if ex.branch_type == BranchType.BREAK:
                                self.create_edge(ex.node, merge_node, BranchType.SEQUENTIAL)
                            elif ex.branch_type in [BranchType.RETURN, BranchType.CONTINUE]:
                                exit_nodes.append(ex)
                            else:
                                next_incoming.append(ex)
                        current_incoming = next_incoming
                        i += 1

                    else:
                        # Kumpulkan simple stmts berturut-turut
                        simple_batch = []
                        while i < len(remaining_stmts) and remaining_stmts[i].type not in complex_types:
                            simple_batch.append(remaining_stmts[i])
                            i += 1

                        has_break_in_batch = any(
                            s.type == AstNodeType.BREAK_STATEMENT.value for s in simple_batch
                        )
                        has_return_in_batch = any(
                            s.type == AstNodeType.RETURN_STATEMENT.value for s in simple_batch
                        )

                        batch_text = '\n'.join(s.text.decode('utf8') for s in simple_batch)
                        batch_line_start = simple_batch[0].start_point[0] + 1
                        batch_line_end = simple_batch[-1].end_point[0] + 1

                        batch_node = CfgNode(simple_batch[0])
                        batch_node.node_type = NodeType.NORMAL
                        batch_node.source_code = batch_text
                        batch_node.line_start = batch_line_start
                        batch_node.line_end = batch_line_end
                        self._register_node(batch_node)

                        for inc in current_incoming:
                            self.create_edge(inc.node, batch_node, inc.branch_type)

                        if has_break_in_batch:
                            self.create_edge(batch_node, merge_node, BranchType.SEQUENTIAL)
                            current_incoming = []
                            break
                        elif has_return_in_batch:
                            exit_nodes.append(ExitNode(batch_node, BranchType.RETURN))
                            current_incoming = []
                            break
                        else:
                            current_incoming = [ExitNode(batch_node, BranchType.SEQUENTIAL)]

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