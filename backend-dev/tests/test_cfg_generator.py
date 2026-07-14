import pytest
from unittest.mock import MagicMock, patch
from core.cfg_generator import CFGGeneratorVisitor, ExitNode
from core.nodes.base_node import CfgNode
from core.nodes.bool_node import CfgBoolExprNode
from core.types import NodeType, BranchType, AstNodeType

class TestCFGGeneratorVisitor:
    
    # 1. Test helper method: _register_node
    def test__register_node(self):
        """Tests that _register_node appends the node to the nodes list and assigns execution order to non-merge nodes."""
        visitor = CFGGeneratorVisitor()
        node = CfgNode(None)
        node.node_type = NodeType.NORMAL
        
        registered = visitor._register_node(node)
        
        assert registered == node
        assert node in visitor.nodes
        assert node.execution_order == 1
        assert visitor.current_execution_order == 2

    def test__register_node_merge(self):
        """Tests that _register_node does not assign execution order to NodeType.MERGE nodes."""
        visitor = CFGGeneratorVisitor()
        node = CfgNode(None)
        node.node_type = NodeType.MERGE
        
        registered = visitor._register_node(node)
        
        assert node.execution_order is None
        assert visitor.current_execution_order == 1

    # 2. Test helper method: create_edge
    def test_create_edge(self):
        """Tests that create_edge appends a valid edge dict to self.edges with correct properties."""
        visitor = CFGGeneratorVisitor()
        src = CfgNode(None)
        target = CfgNode(None)
        
        visitor.create_edge(src, target, BranchType.TRUE)
        
        assert len(visitor.edges) == 1
        edge = visitor.edges[0]
        assert edge["id_start_node"] == src.id_node
        assert edge["id_finish_node"] == target.id_node
        assert edge["branch_type"] == BranchType.TRUE

    # 3. Test helper method: _process_loop_exits
    def test__process_loop_exits(self):
        """Tests that _process_loop_exits appends break/return exits and builds loop back-edges for continues/sequential exits."""
        visitor = CFGGeneratorVisitor()
        loop_node = CfgNode(None)
        
        exit_break = ExitNode(CfgNode(None), BranchType.BREAK)
        exit_continue = ExitNode(CfgNode(None), BranchType.CONTINUE)
        exit_return = ExitNode(CfgNode(None), BranchType.RETURN)
        exit_sequential = ExitNode(CfgNode(None), BranchType.SEQUENTIAL)
        
        body_exits = [exit_break, exit_continue, exit_return, exit_sequential]
        exit_nodes = []
        
        processed_exits = visitor._process_loop_exits(body_exits, loop_node, exit_nodes)
        
        # Break exits are converted to exit_nodes with BranchType.SEQUENTIAL (loop termination exits)
        break_exit = next(x for x in processed_exits if x.node == exit_break.node)
        assert break_exit.branch_type == BranchType.SEQUENTIAL
        
        # Return exits remain untouched (exit execution scope)
        return_exit = next(x for x in processed_exits if x.node == exit_return.node)
        assert return_exit.branch_type == BranchType.RETURN
        
        # Continue exits create sequential edge back to loop node
        continue_edge = next(e for e in visitor.edges if e["id_start_node"] == exit_continue.node.id_node)
        assert continue_edge["id_finish_node"] == loop_node.id_node
        assert continue_edge["branch_type"] == BranchType.SEQUENTIAL

        # Other standard exits create loop-back edges
        seq_edge = next(e for e in visitor.edges if e["id_start_node"] == exit_sequential.node.id_node)
        assert seq_edge["id_finish_node"] == loop_node.id_node
        assert seq_edge["branch_type"] == BranchType.SEQUENTIAL

    # 4. Test helper method: _reassign_execution_orders
    def test__reassign_execution_orders(self):
        """Tests that _reassign_execution_orders re-numbers normal nodes while keeping start/end/merge nodes order to None."""
        visitor = CFGGeneratorVisitor()
        
        n_start = CfgNode(None)
        n_start.node_type = NodeType.START
        
        n_merge = CfgNode(None)
        n_merge.node_type = NodeType.MERGE
        
        n_normal1 = CfgNode(None)
        n_normal1.node_type = NodeType.NORMAL
        
        n_normal2 = CfgNode(None)
        n_normal2.node_type = NodeType.NORMAL
        
        n_end = CfgNode(None)
        n_end.node_type = NodeType.END
        
        visitor.nodes = [n_start, n_merge, n_normal1, n_normal2, n_end]
        visitor._reassign_execution_orders()
        
        assert n_start.execution_order is None
        assert n_merge.execution_order is None
        assert n_end.execution_order is None
        assert n_normal1.execution_order == 1
        assert n_normal2.execution_order == 2

    # 5. Test helper method: _get_body_block
    def test__get_body_block(self):
        """Tests that _get_body_block retrieves child block of AstNodeType.BLOCK."""
        visitor = CFGGeneratorVisitor()
        
        mock_method_node = MagicMock()
        mock_child_block = MagicMock()
        mock_child_block.type = AstNodeType.BLOCK
        mock_child_other = MagicMock()
        mock_child_other.type = "other"
        
        mock_method_node.children = [mock_child_other, mock_child_block]
        
        result = visitor._get_body_block(mock_method_node)
        assert result == mock_child_block

    # 6. Test visitor method: visit_return_statement
    @patch("core.nodes.node_factory.NodeFactory.create_node")
    def test_visit_return_statement(self, mock_create_node):
        """Tests that visit_return_statement creates and registers a Return node, returning an exit node of RETURN type."""
        visitor = CFGGeneratorVisitor()
        mock_ast_node = MagicMock()
        mock_node = CfgNode(None)
        mock_create_node.return_value = mock_node
        
        entry_node, exits = visitor.visit_return_statement(mock_ast_node)
        
        assert entry_node == mock_node
        assert len(exits) == 1
        assert exits[0].node == mock_node
        assert exits[0].branch_type == BranchType.RETURN
        assert mock_node in visitor.nodes

    # 7. Test visitor method: visit_break_statement
    @patch("core.nodes.node_factory.NodeFactory.create_node")
    def test_visit_break_statement(self, mock_create_node):
        """Tests that visit_break_statement creates and registers a Break node, returning an exit node of BREAK type."""
        visitor = CFGGeneratorVisitor()
        mock_ast_node = MagicMock()
        mock_node = CfgNode(None)
        mock_create_node.return_value = mock_node
        
        entry_node, exits = visitor.visit_break_statement(mock_ast_node)
        
        assert entry_node == mock_node
        assert len(exits) == 1
        assert exits[0].node == mock_node
        assert exits[0].branch_type == BranchType.BREAK
        assert mock_node in visitor.nodes

    # 8. Test visitor method: visit_continue_statement
    @patch("core.nodes.node_factory.NodeFactory.create_node")
    def test_visit_continue_statement(self, mock_create_node):
        """Tests that visit_continue_statement creates and registers a Continue node, returning an exit node of CONTINUE type."""
        visitor = CFGGeneratorVisitor()
        mock_ast_node = MagicMock()
        mock_node = CfgNode(None)
        mock_create_node.return_value = mock_node
        
        entry_node, exits = visitor.visit_continue_statement(mock_ast_node)
        
        assert entry_node == mock_node
        assert len(exits) == 1
        assert exits[0].node == mock_node
        assert exits[0].branch_type == BranchType.CONTINUE
        assert mock_node in visitor.nodes

    # 9. Test visitor method: generic_visit
    @patch("core.nodes.node_factory.NodeFactory.create_node")
    def test_generic_visit(self, mock_create_node):
        """Tests that generic_visit registers the default statement node, returning exit node of SEQUENTIAL type."""
        visitor = CFGGeneratorVisitor()
        mock_ast_node = MagicMock()
        mock_node = CfgNode(None)
        mock_create_node.return_value = mock_node
        
        entry_node, exits = visitor.generic_visit(mock_ast_node)
        
        assert entry_node == mock_node
        assert len(exits) == 1
        assert exits[0].node == mock_node
        assert exits[0].branch_type == BranchType.SEQUENTIAL
        assert mock_node in visitor.nodes

    @patch("core.cfg_generator.optimize_merge_nodes")
    def test_build_cfg_empty_body(self, mock_optimize):
        """Tests build_cfg when method has no body block."""
        visitor = CFGGeneratorVisitor()
        mock_method_node = MagicMock()
        mock_method_node.children = [] # Tidak ada block
        
        nodes, edges = visitor.build_cfg(mock_method_node)
        
        assert nodes == []
        assert edges == []
        mock_optimize.assert_not_called()

    @patch("core.cfg_generator.optimize_merge_nodes")
    @patch.object(CFGGeneratorVisitor, 'visit_block')
    def test_build_cfg_with_body(self, mock_visit_block, mock_optimize):
        """Tests build_cfg normal flow with start, end, and body."""
        visitor = CFGGeneratorVisitor()
        
        # Mock AST node dan return dari visit_block
        mock_body = MagicMock()
        mock_body.type = AstNodeType.BLOCK
        mock_method_node = MagicMock()
        mock_method_node.children = [mock_body]
        
        # Simulasi kembalian optimize_merge_nodes
        mock_optimize.return_value = (visitor.nodes, visitor.edges)
        
        # Simulasi return dari visit_block: node pertama dan exit nodes
        mock_first_node = CfgNode(None)
        mock_exit_node = ExitNode(mock_first_node, BranchType.SEQUENTIAL)
        mock_visit_block.return_value = (mock_first_node, [mock_exit_node])
        
        nodes, edges = visitor.build_cfg(mock_method_node)
        
        # Verifikasi Start dan End node dibuat
        assert any(n.node_type == NodeType.START for n in nodes)
        assert any(n.node_type == NodeType.END for n in nodes)
        mock_optimize.assert_called_once()
        mock_visit_block.assert_called_once()

    def test_visit_block(self):
        """Tests that visit_block iterates over statements, ignoring comments."""
        visitor = CFGGeneratorVisitor()
        
        mock_ast_block = MagicMock()
        
        # Setup child 1: Comment (should be ignored)
        mock_comment = MagicMock()
        mock_comment.is_named = True
        mock_comment.type = AstNodeType.LINE_COMMENT
        
        # Setup child 2: Normal statement
        mock_stmt = MagicMock()
        mock_stmt.is_named = True
        mock_stmt.type = "some_statement"
        
        mock_ast_block.children = [mock_comment, mock_stmt]
        
        # Patch getattr to mock the dynamically called visit method
        mock_stmt_node = CfgNode(None)
        mock_exit = ExitNode(mock_stmt_node, BranchType.SEQUENTIAL)
        
        with patch.object(visitor, 'generic_visit', return_value=(mock_stmt_node, [mock_exit])) as mock_visit:
            incoming = [ExitNode(CfgNode(None), BranchType.SEQUENTIAL)]
            entry, exits = visitor.visit_block(mock_ast_block, incoming)
            
            assert entry == mock_stmt_node
            assert len(exits) == 1
            mock_visit.assert_called_once_with(mock_stmt)

    @patch("core.cfg_generator.NodeFactory.create_node")
    def test_visit_if_statement_no_else(self, mock_create_node):
        """Tests IF statement without ELSE branch."""
        visitor = CFGGeneratorVisitor()
        mock_ast = MagicMock()
        
        # Mocking child_by_field_name ('condition', 'consequence', 'alternative')
        mock_ast.child_by_field_name.side_effect = lambda field: MagicMock() if field == 'condition' else None
        
        cond_node = CfgNode(None)
        cond_node.id_node = "cond_1"
        mock_create_node.return_value = cond_node
        
        entry_node, exits = visitor.visit_if_statement(mock_ast)
        
        assert entry_node == cond_node
        assert len(visitor.nodes) == 1 # Merge node dihapus karena cuma 1 incoming (jalur false)
        assert len(exits) == 1
        assert exits[0].branch_type == BranchType.FALSE

    @patch("core.cfg_generator.NodeFactory.create_node")
    @patch.object(CFGGeneratorVisitor, 'visit_block')
    def test_visit_while_statement(self, mock_visit_block, mock_create_node):
        """Tests WHILE statement routing."""
        visitor = CFGGeneratorVisitor()
        mock_ast = MagicMock()
        
        mock_body = MagicMock()
        mock_body.type = AstNodeType.BLOCK
        mock_ast.child_by_field_name.side_effect = lambda field: mock_body if field == 'body' else MagicMock()
        
        # --- PERBAIKAN DI SINI ---
        # Ganti cond_node = CfgNode(None) menjadi MagicMock()
        cond_node = MagicMock() 
        cond_node.id_node = "while_cond"
        mock_create_node.return_value = cond_node
        # -------------------------
        
        # Mock body block return
        body_node = CfgNode(None)
        body_node.id_node = "body_node"
        mock_visit_block.return_value = (body_node, [ExitNode(body_node, BranchType.SEQUENTIAL)])
        
        entry, exits = visitor.visit_while_statement(mock_ast)
        
        assert entry == cond_node
        assert len(exits) == 1
        assert exits[0].branch_type == BranchType.FALSE # Default exit dari loop
        # Cek apakah loopback edge terbentuk
        assert any(e["id_start_node"] == body_node.id_node and e["id_finish_node"] == cond_node.id_node for e in visitor.edges)

    @patch("core.cfg_generator.NodeFactory.create_node")
    def test_visit_do_statement_empty_body(self, mock_create_node):
        """Tests DO-WHILE loop structure with empty body fallback."""
        visitor = CFGGeneratorVisitor()
        mock_ast = MagicMock()
        
        # No body
        mock_ast.child_by_field_name.return_value = None
        
        # --- PERBAIKAN DI SINI ---
        # Ganti cond_node = CfgNode(None) menjadi MagicMock()
        cond_node = MagicMock()
        cond_node.id_node = "do_cond"
        mock_create_node.return_value = cond_node
        # -------------------------
        
        entry, exits = visitor.visit_do_statement(mock_ast)
        
        assert entry == cond_node # Jika kosong, lari ke cond node
        assert len(exits) == 1
        assert exits[0].branch_type == BranchType.FALSE
        assert any(e["id_start_node"] == cond_node.id_node and e["id_finish_node"] == cond_node.id_node for e in visitor.edges)

    @patch.object(CFGGeneratorVisitor, '_process_switch')
    def test_visit_switch_statement(self, mock_process_switch):
        """Tests that switch statement delegates to _process_switch."""
        visitor = CFGGeneratorVisitor()
        mock_ast = MagicMock()
        mock_process_switch.return_value = ("entry", ["exits"])
        
        res = visitor.visit_switch_statement(mock_ast)
        assert res == ("entry", ["exits"])
        mock_process_switch.assert_called_once_with(mock_ast)

    @patch("core.cfg_generator.NodeFactory.create_node")
    def test_process_switch_empty(self, mock_create_node):
        """Tests switch logic with no body/cases."""
        visitor = CFGGeneratorVisitor()
        mock_ast = MagicMock()
        mock_ast.child_by_field_name.side_effect = lambda field: None if field == 'body' else MagicMock()
        
        cond_node = CfgNode(None)
        cond_node.id_node = "switch_cond"
        mock_create_node.return_value = cond_node
        
        entry, exits = visitor._process_switch(mock_ast)
        
        assert entry == cond_node
        # Akan ada 2 node (cond_node & merge_node)
        assert len(visitor.nodes) == 2
        # Keluar lewat branch False ke merge node
        assert any(e["branch_type"] == BranchType.FALSE for e in visitor.edges)

    @patch("core.cfg_generator.NodeFactory.create_node")
    @patch.object(CFGGeneratorVisitor, 'visit_block')
    def test_visit_for_statement_with_body(self, mock_visit_block, mock_create_node):
        """Tests FOR statement routing, creating TRUE edges to body and returning FALSE exits."""
        visitor = CFGGeneratorVisitor()
        mock_ast = MagicMock()
        
        # Mock body block
        mock_body = MagicMock()
        mock_body.type = AstNodeType.BLOCK
        mock_ast.child_by_field_name.side_effect = lambda field: mock_body if field == 'body' else None
        
        # Mock condition node (MagicMock untuk menghindari AttributeError pada set_true_node)
        for_node = MagicMock()
        for_node.id_node = "for_cond"
        # Setup source_code agar operasi split('\\n') di dalam fungsi tidak error
        for_node.source_code = "for (int i = 0; i < 10; i++) {\n // body \n}" 
        mock_create_node.return_value = for_node
        
        # Mock body block return
        body_node = CfgNode(None)
        body_node.id_node = "body_node"
        mock_visit_block.return_value = (body_node, [ExitNode(body_node, BranchType.SEQUENTIAL)])
        
        entry, exits = visitor.visit_for_statement(mock_ast)
        
        # Verifikasi
        assert entry == for_node
        assert for_node in visitor.nodes
        assert for_node.source_code == "for (int i = 0; i < 10; i++) {" # Ekstraksi baris pertama berhasil
        
        # Mengecek jalur ke body (TRUE)
        assert any(e["id_start_node"] == for_node.id_node and 
                   e["id_finish_node"] == body_node.id_node and 
                   e["branch_type"] == BranchType.TRUE for e in visitor.edges)
        
        # Mengecek default exit dari perulangan adalah FALSE
        assert len(exits) == 1
        assert exits[0].branch_type == BranchType.FALSE

    @patch("core.cfg_generator.NodeFactory.create_node")
    def test_visit_for_statement_empty_body(self, mock_create_node):
        """Tests FOR statement flow when the body is empty or null."""
        visitor = CFGGeneratorVisitor()
        mock_ast = MagicMock()
        
        # Tidak ada body
        mock_ast.child_by_field_name.return_value = None
        
        for_node = MagicMock()
        for_node.id_node = "for_cond_empty"
        for_node.source_code = "for (;;) "
        mock_create_node.return_value = for_node
        
        entry, exits = visitor.visit_for_statement(mock_ast)
        
        assert entry == for_node
        assert len(exits) == 1
        assert exits[0].branch_type == BranchType.FALSE
    
    # ==========================================
    # EDGE CASES & FALLBACKS TESTS (Covering Red Lines)
    # ==========================================

    def test_visit_block_dead_code_break(self):
        """TC-CFG-21: Tests that visit_block breaks iteration if current_incoming becomes empty (e.g., after return)."""
        visitor = CFGGeneratorVisitor()
        mock_ast_block = MagicMock()
        
        # Setup: 2 statement. Statement 1 adalah RETURN, Statement 2 adalah NORMAL (dead code)
        mock_stmt_1 = MagicMock()
        mock_stmt_1.is_named = True
        mock_stmt_1.type = AstNodeType.RETURN_STATEMENT
        
        mock_stmt_2 = MagicMock()
        mock_stmt_2.is_named = True
        mock_stmt_2.type = AstNodeType.EXPRESSION_STATEMENT
        
        mock_ast_block.children = [mock_stmt_1, mock_stmt_2]
        
        mock_node_1 = CfgNode(None)
        # Mocking return statement exit (yang bikin next_incoming kosong)
        mock_exit_1 = ExitNode(mock_node_1, BranchType.RETURN) 
        
        # Paksa method visitor untuk mengembalikan RETURN pada statement pertama
        with patch.object(visitor, 'visit_return_statement', return_value=(mock_node_1, [mock_exit_1])) as mock_visit_ret:
            with patch.object(visitor, 'generic_visit') as mock_generic:
                incoming = [ExitNode(CfgNode(None), BranchType.SEQUENTIAL)]
                entry, exits = visitor.visit_block(mock_ast_block, incoming)
                
                assert entry == mock_node_1
                # Karena incoming kosong setelah stmt_1, loop harus break dan generic_visit untuk stmt_2 TIDAK dipanggil
                mock_generic.assert_not_called() 
                mock_visit_ret.assert_called_once_with(mock_stmt_1)
                
                # Check apakah block_jump_exits menangkap RETURN
                assert any(ex.branch_type == BranchType.RETURN for ex in exits)

    @patch("core.cfg_generator.NodeFactory.create_node")
    def test_visit_if_statement_non_block_and_merge_removal(self, mock_create_node):
        """TC-CFG-22: Tests IF fallback (getattr) for non-block branches and merge_node removal when 0 incoming edges."""
        visitor = CFGGeneratorVisitor()
        mock_ast = MagicMock()
        
        # Setup: IF dan ELSE isinya bukan BLOCK, tapi langsung statement (misal return)
        mock_then = MagicMock()
        mock_then.type = AstNodeType.RETURN_STATEMENT
        mock_else = MagicMock()
        mock_else.type = AstNodeType.RETURN_STATEMENT
        
        def mock_child_by_name(field):
            if field == 'condition': return MagicMock()
            if field == 'consequence': return mock_then
            if field == 'alternative': return mock_else
            return None
        mock_ast.child_by_field_name.side_effect = mock_child_by_name
        
        cond_node = CfgBoolExprNode(None)
        cond_node.id_node = "cond_node_id"
        mock_create_node.return_value = cond_node
        
        then_node = CfgNode(None)
        then_node.id_node = "then_node_id"
        else_node = CfgNode(None)
        else_node.id_node = "else_node_id"
        
        # Keduanya mengembalikan RETURN, sehingga tidak ada yang tembus ke SEQUENTIAL / merge node
        with patch.object(visitor, 'visit_return_statement', side_effect=[
            (then_node, [ExitNode(then_node, BranchType.RETURN)]),
            (else_node, [ExitNode(else_node, BranchType.RETURN)])
        ]):
            entry_node, exits = visitor.visit_if_statement(mock_ast)
            
            # Verifikasi: merge_node harusnya dibuang dari visitor.nodes karena len(incoming_edges) == 0
            assert all(n.node_type != NodeType.MERGE for n in visitor.nodes)
            
            # Pastikan fallback branch (getattr) memproses node "then" dan "else"
            assert len(exits) == 2
            assert exits[0].branch_type == BranchType.RETURN
            assert exits[1].branch_type == BranchType.RETURN

    @patch("core.cfg_generator.NodeFactory.create_node")
    def test_visit_while_single_statement_body(self, mock_create_node):
        """TC-CFG-23: Tests WHILE loop routing when body is a single statement (not a block), triggering getattr."""
        visitor = CFGGeneratorVisitor()
        mock_ast = MagicMock()
        
        mock_body = MagicMock()
        mock_body.type = AstNodeType.EXPRESSION_STATEMENT # Bukan BLOCK
        mock_ast.child_by_field_name.side_effect = lambda field: mock_body if field == 'body' else MagicMock()
        
        cond_node = MagicMock() 
        cond_node.id_node = "while_cond"
        mock_create_node.return_value = cond_node
        
        body_node = CfgNode(None)
        body_node.id_node = "body_node"
        
        # Patch generic_visit yang dipanggil lewat fallback getattr(self, f'visit_{body_ast.type}')
        with patch.object(visitor, 'generic_visit', return_value=(body_node, [ExitNode(body_node, BranchType.SEQUENTIAL)])) as mock_generic:
            entry, exits = visitor.visit_while_statement(mock_ast)
            
            mock_generic.assert_called_once_with(mock_body)
            assert entry == cond_node
            assert len(exits) == 1
            assert exits[0].branch_type == BranchType.FALSE

    @patch.object(CFGGeneratorVisitor, '_process_switch')
    def test_visit_switch_expression(self, mock_process_switch):
        """TC-CFG-24: Tests that visit_switch_expression delegates to _process_switch."""
        visitor = CFGGeneratorVisitor()
        mock_ast = MagicMock()
        mock_process_switch.return_value = ("expr_entry", ["expr_exits"])
        
        res = visitor.visit_switch_expression(mock_ast)
        assert res == ("expr_entry", ["expr_exits"])
        mock_process_switch.assert_called_once_with(mock_ast)

    @patch("core.cfg_generator.NodeFactory.create_node")
    def test_process_switch_simple_batch_with_break(self, mock_create_node):
        """TC-CFG-25: Tests switch logic with a simple group that ends with a BREAK statement."""
        visitor = CFGGeneratorVisitor()
        mock_ast = MagicMock()
        mock_body = MagicMock()
        mock_ast.child_by_field_name.side_effect = lambda f: mock_body if f == 'body' else MagicMock()
        
        # Mocking hierarchy untuk raw_groups dan pending_labels
        mock_group = MagicMock()
        mock_group.type = AstNodeType.SWITCH_BLOCK_GROUP
        
        mock_label = MagicMock()
        mock_label.is_named = True
        mock_label.type = AstNodeType.SWITCH_LABEL
        mock_label.text = b'case 1:'
        mock_label.start_point = (1, 0)
        mock_label.end_point = (1, 10)
        
        mock_break = MagicMock()
        mock_break.is_named = True
        mock_break.type = AstNodeType.BREAK_STATEMENT.value # Pakai .value karena pembandingannya di kode pakai .value
        mock_break.text = b'break;'
        mock_break.start_point = (2, 0)
        mock_break.end_point = (2, 6)
        
        mock_group.children = [mock_label, mock_break]
        mock_body.children = [mock_group]
        
        cond_node = CfgNode(None)
        cond_node.id_node = "switch_cond"
        mock_create_node.return_value = cond_node
        
        entry, exits = visitor._process_switch(mock_ast)
        
        # Verifikasi
        assert entry == cond_node
        # Harus ada edge SEQUENTIAL menuju merge_node karena ada break
        assert any(e["branch_type"] == BranchType.SEQUENTIAL for e in visitor.edges)
        
        # Cek tipe node yang dibuat adalah NORMAL (karena digabung ke batch_node)
        batch_node = next((n for n in visitor.nodes if n.node_type == NodeType.NORMAL), None)
        assert batch_node is not None
        assert "case 1:\nbreak;" in batch_node.source_code

    @patch("core.cfg_generator.NodeFactory.create_node")
    def test_process_switch_complex_group(self, mock_create_node):
        """TC-CFG-26: Tests switch logic triggering the complex group branch (e.g., case containing an IF statement)."""
        visitor = CFGGeneratorVisitor()
        mock_ast = MagicMock()
        mock_body = MagicMock()
        mock_ast.child_by_field_name.side_effect = lambda f: mock_body if f == 'body' else MagicMock()
        
        mock_group = MagicMock()
        mock_group.type = AstNodeType.SWITCH_BLOCK_GROUP
        
        mock_label = MagicMock()
        mock_label.is_named = True
        mock_label.type = AstNodeType.SWITCH_LABEL
        mock_label.text = b'case 2:'
        mock_label.start_point = (1, 0)
        mock_label.end_point = (1, 7)
        
        mock_complex_stmt = MagicMock()
        mock_complex_stmt.is_named = True
        mock_complex_stmt.type = AstNodeType.IF_STATEMENT.value # Ini yang mentrigger has_complex = True
        mock_complex_stmt.text = b'if (true) {}'
        mock_complex_stmt.start_point = (2, 0)
        mock_complex_stmt.end_point = (2, 12)
        
        mock_group.children = [mock_label, mock_complex_stmt]
        mock_body.children = [mock_group]
        
        cond_node = CfgNode(None)
        cond_node.id_node = "switch_cond"
        mock_create_node.return_value = cond_node
        
        complex_entry = CfgNode(None)
        complex_entry.id_node = "complex_entry"
        
        # Kita patch visitor dari complex statement (if_statement)
        with patch.object(visitor, 'visit_if_statement', return_value=(complex_entry, [ExitNode(complex_entry, BranchType.SEQUENTIAL)])) as mock_visit_if:
            # Karena f'visit_{stmt.type}' di mana stmt.type adalah value string (e.g. 'if_statement')
            # pastikan mocking setattr atau memanfaatkan _process_switch getattr call.
            # Menggunakan method yang didapatkan dari getattr(self, f'visit_if_statement')
            setattr(visitor, f'visit_{AstNodeType.IF_STATEMENT.value}', mock_visit_if)
            
            entry, exits = visitor._process_switch(mock_ast)
            
            # Verifikasi prefix node dibuat (labelnya saja)
            prefix_node = next((n for n in visitor.nodes if n.node_type == NodeType.NORMAL), None)
            assert prefix_node is not None
            assert prefix_node.source_code == "case 2:"
            
            # Memastikan method kompleks terpanggil
            mock_visit_if.assert_called_once_with(mock_complex_stmt)

    # ==========================================
    # ADDITIONAL TESTS - Covering Remaining Red Lines
    # ==========================================

    @patch("core.cfg_generator.NodeFactory.create_node")
    @patch.object(CFGGeneratorVisitor, 'visit_block')
    def test_visit_if_statement_with_both_block_branches_merge(self, mock_visit_block, mock_create_node):
        """TC-CFG-27: Tests IF with BLOCK then AND BLOCK else, both yielding SEQUENTIAL exits → merge_node gets 2 incomings (line 170, 175, 189, 226)."""
        visitor = CFGGeneratorVisitor()
        mock_ast = MagicMock()

        mock_then = MagicMock()
        mock_then.type = AstNodeType.BLOCK
        mock_else = MagicMock()
        mock_else.type = AstNodeType.BLOCK

        def mock_child(field):
            if field == 'condition': return MagicMock()
            if field == 'consequence': return mock_then
            if field == 'alternative': return mock_else
            return None
        mock_ast.child_by_field_name.side_effect = mock_child

        from core.nodes.bool_node import CfgBoolExprNode
        cond_node = CfgBoolExprNode(None)
        cond_node.id_node = "cond_id"
        mock_create_node.return_value = cond_node

        then_node = CfgNode(None)
        then_node.id_node = "then_id"
        else_node = CfgNode(None)
        else_node.id_node = "else_id"

        # Both branches yield SEQUENTIAL → both will create edge to merge_node (line 170)
        mock_visit_block.side_effect = [
            (then_node, [ExitNode(then_node, BranchType.SEQUENTIAL)]),
            (else_node, [ExitNode(else_node, BranchType.SEQUENTIAL)]),
        ]

        entry_node, exits = visitor.visit_if_statement(mock_ast)

        # merge_node must still be in nodes (2 incomings → kept, line 226)
        assert any(n.node_type == NodeType.MERGE for n in visitor.nodes)
        # Only 1 exit: ExitNode(merge_node, SEQUENTIAL)
        assert len(exits) == 1
        assert exits[0].branch_type == BranchType.SEQUENTIAL
        # Edges: cond→then (TRUE), then→merge (SEQ), cond→else (FALSE), else→merge (SEQ)
        seq_edges = [e for e in visitor.edges if e['branch_type'] == BranchType.SEQUENTIAL]
        assert len(seq_edges) == 2  # then→merge and else→merge (line 170 × 2)

    @patch("core.cfg_generator.NodeFactory.create_node")
    def test_visit_if_statement_then_first_is_none_creates_true_edge_to_merge(self, mock_create_node):
        """TC-CFG-28: Tests IF where then branch visit_block returns None as first node → edge cond→merge TRUE (line 184)."""
        visitor = CFGGeneratorVisitor()
        mock_ast = MagicMock()

        mock_then = MagicMock()
        mock_then.type = AstNodeType.BLOCK
        mock_ast.child_by_field_name.side_effect = lambda f: (
            MagicMock() if f == 'condition' else mock_then if f == 'consequence' else None
        )

        from core.nodes.bool_node import CfgBoolExprNode
        cond_node = CfgBoolExprNode(None)
        cond_node.id_node = "cond_then_none"
        mock_create_node.return_value = cond_node

        # visit_block returns None as first_node
        with patch.object(visitor, 'visit_block', return_value=(None, [])):
            entry_node, exits = visitor.visit_if_statement(mock_ast)

        # Should have created edge cond→merge with BranchType.TRUE (line 184)
        true_edges = [e for e in visitor.edges if e['branch_type'] == BranchType.TRUE]
        assert len(true_edges) == 1
        assert true_edges[0]['id_start_node'] == cond_node.id_node

    @patch("core.cfg_generator.NodeFactory.create_node")
    def test_visit_if_statement_else_first_is_none_creates_false_edge_to_merge(self, mock_create_node):
        """TC-CFG-29: Tests IF with BLOCK else that returns None as first_node → line 198 fires (cond→merge FALSE).
        Since this produces exactly 1 incoming edge to merge_node, the optimizer removes the edge and merge_node,
        promoting it to an ExitNode(cond_node, FALSE) in the exits list."""
        visitor = CFGGeneratorVisitor()
        mock_ast = MagicMock()

        mock_else = MagicMock()
        mock_else.type = AstNodeType.BLOCK

        def mock_child(field):
            if field == 'condition': return MagicMock()
            if field == 'consequence': return None
            if field == 'alternative': return mock_else
            return None
        mock_ast.child_by_field_name.side_effect = mock_child

        from core.nodes.bool_node import CfgBoolExprNode
        cond_node = CfgBoolExprNode(None)
        cond_node.id_node = "cond_else_none"
        mock_create_node.return_value = cond_node

        # visit_block returns None as first_node for else branch → triggers line 198
        with patch.object(visitor, 'visit_block', return_value=(None, [])):
            entry_node, exits = visitor.visit_if_statement(mock_ast)

        # After line 198: cond→merge FALSE edge is created.
        # Since that's the only edge into merge_node (len==1), the optimizer removes it and
        # promotes cond_node as exit with BranchType.FALSE. merge_node is removed from nodes.
        assert all(n.node_type != NodeType.MERGE for n in visitor.nodes)
        assert any(ex.branch_type == BranchType.FALSE and ex.node.id_node == cond_node.id_node for ex in exits)

    @patch("core.cfg_generator.NodeFactory.create_node")
    def test_visit_do_statement_non_block_body(self, mock_create_node):
        """TC-CFG-30: Tests DO-WHILE with a non-block body → triggers getattr fallback (lines 291, 287-303)."""
        visitor = CFGGeneratorVisitor()
        mock_ast = MagicMock()

        mock_body = MagicMock()
        mock_body.type = AstNodeType.EXPRESSION_STATEMENT  # Not a BLOCK

        mock_ast.child_by_field_name.side_effect = lambda f: mock_body if f == 'body' else MagicMock()

        cond_node = MagicMock()
        cond_node.id_node = "do_cond_nonblock"
        mock_create_node.return_value = cond_node

        body_node = CfgNode(None)
        body_node.id_node = "do_body_node"

        with patch.object(visitor, 'generic_visit', return_value=(body_node, [ExitNode(body_node, BranchType.SEQUENTIAL)])) as mock_generic:
            entry, exits = visitor.visit_do_statement(mock_ast)

            # generic_visit called because body type is not BLOCK
            mock_generic.assert_called_once_with(mock_body)
            # entry_node should be body_first (body_node), not cond_node
            assert entry == body_node
            assert len(exits) == 1
            assert exits[0].branch_type == BranchType.FALSE
            # Loop-back edge: cond → body_node (TRUE)
            assert any(e['id_finish_node'] == body_node.id_node and e['branch_type'] == BranchType.TRUE for e in visitor.edges)

    @patch("core.cfg_generator.NodeFactory.create_node")
    def test_process_switch_pending_labels_flush(self, mock_create_node):
        """TC-CFG-31: Tests switch where the last group is label-only (no stmts) → pending_labels flushed (lines 382-386)."""
        visitor = CFGGeneratorVisitor()
        mock_ast = MagicMock()
        mock_body = MagicMock()
        mock_ast.child_by_field_name.side_effect = lambda f: mock_body if f == 'body' else MagicMock()

        # Group with label only (no statements)
        mock_group = MagicMock()
        mock_group.type = AstNodeType.SWITCH_BLOCK_GROUP

        mock_label = MagicMock()
        mock_label.is_named = True
        mock_label.type = AstNodeType.SWITCH_LABEL
        mock_label.text = b'case 99:'
        mock_label.start_point = (5, 0)
        mock_label.end_point = (5, 8)

        mock_group.children = [mock_label]  # No stmts → label-only
        mock_body.children = [mock_group]

        cond_node = CfgNode(None)
        cond_node.id_node = "switch_cond_pending"
        mock_create_node.return_value = cond_node

        entry, exits = visitor._process_switch(mock_ast)

        # merged_groups will contain 1 entry with labels but empty stmts
        # all_parts = labels + [] = [label] → not empty, so NOT continue (but handled)
        # The all_parts check passes, block_node created with just the label text
        assert entry == cond_node
        # The merged group will produce a block_node with the label text
        normal_nodes = [n for n in visitor.nodes if n.node_type == NodeType.NORMAL]
        assert len(normal_nodes) == 1
        assert "case 99:" in normal_nodes[0].source_code

    @patch("core.cfg_generator.NodeFactory.create_node")
    def test_process_switch_all_parts_empty_continue(self, mock_create_node):
        """TC-CFG-32: Tests switch simple group where all_parts is empty → hits 'continue' (line 410)."""
        visitor = CFGGeneratorVisitor()
        mock_ast = MagicMock()
        mock_body = MagicMock()
        mock_ast.child_by_field_name.side_effect = lambda f: mock_body if f == 'body' else MagicMock()

        # Group with no named children at all (labels=[], stmts=[])
        mock_group = MagicMock()
        mock_group.type = AstNodeType.SWITCH_BLOCK_GROUP
        mock_group.children = []  # No children → labels=[], stmts=[]
        mock_body.children = [mock_group]

        cond_node = CfgNode(None)
        cond_node.id_node = "switch_cond_empty_all"
        mock_create_node.return_value = cond_node

        entry, exits = visitor._process_switch(mock_ast)

        # all_parts is empty → 'continue' is hit, no block_node created
        assert entry == cond_node
        normal_nodes = [n for n in visitor.nodes if n.node_type == NodeType.NORMAL]
        assert len(normal_nodes) == 0

    @patch("core.cfg_generator.NodeFactory.create_node")
    def test_process_switch_simple_group_fallthrough_and_no_break(self, mock_create_node):
        """TC-CFG-33: Tests switch simple group without break → fallthrough_incoming set (lines 430-431, 437)."""
        visitor = CFGGeneratorVisitor()
        mock_ast = MagicMock()
        mock_body = MagicMock()
        mock_ast.child_by_field_name.side_effect = lambda f: mock_body if f == 'body' else MagicMock()

        def make_stmt(label_text, stmt_text, stmt_type_val):
            mock_label = MagicMock()
            mock_label.is_named = True
            mock_label.type = AstNodeType.SWITCH_LABEL
            mock_label.text = label_text
            mock_label.start_point = (0, 0)
            mock_label.end_point = (0, len(label_text))

            mock_stmt = MagicMock()
            mock_stmt.is_named = True
            mock_stmt.type = stmt_type_val
            mock_stmt.text = stmt_text
            mock_stmt.start_point = (1, 0)
            mock_stmt.end_point = (1, len(stmt_text))
            return mock_label, mock_stmt

        # Group 1: case 1 with simple expression (no break) → fallthrough
        lbl1, stmt1 = make_stmt(b'case 1:', b'x++;', AstNodeType.EXPRESSION_STATEMENT.value)
        mock_group1 = MagicMock()
        mock_group1.type = AstNodeType.SWITCH_BLOCK_GROUP
        mock_group1.children = [lbl1, stmt1]

        # Group 2: case 2 with simple expression (no break) → receives fallthrough from group 1
        lbl2, stmt2 = make_stmt(b'case 2:', b'y++;', AstNodeType.EXPRESSION_STATEMENT.value)
        mock_group2 = MagicMock()
        mock_group2.type = AstNodeType.SWITCH_BLOCK_GROUP
        mock_group2.children = [lbl2, stmt2]

        mock_body.children = [mock_group1, mock_group2]

        call_count = [0]
        def create_node_side_effect(*args, **kwargs):
            call_count[0] += 1
            node = CfgNode(None)
            node.id_node = f"node_{call_count[0]}"
            return node

        mock_create_node.side_effect = create_node_side_effect

        entry, exits = visitor._process_switch(mock_ast)

        # There should be fallthrough edge from group1 block_node to group2 block_node (lines 430-431)
        normal_nodes = [n for n in visitor.nodes if n.node_type == NodeType.NORMAL]
        assert len(normal_nodes) == 2

        # group2's block_node should have an incoming edge from group1's block_node (fallthrough, line 430-431)
        g1_id = normal_nodes[0].id_node
        g2_id = normal_nodes[1].id_node
        assert any(e['id_start_node'] == g1_id and e['id_finish_node'] == g2_id for e in visitor.edges)

        # group2 also has no break so fallthrough_incoming is set for it (line 437)
        # That means group2's block_node should have a SEQUENTIAL edge to merge_node at the end
        merge_node = next(n for n in visitor.nodes if n.node_type == NodeType.MERGE)
        assert any(e['id_start_node'] == g2_id and e['id_finish_node'] == merge_node.id_node for e in visitor.edges)

    @patch("core.cfg_generator.NodeFactory.create_node")
    def test_process_switch_complex_group_prefix_parts_and_fallthrough_incoming(self, mock_create_node):
        """TC-CFG-34: Tests switch complex group where simple stmts precede complex stmt (lines 450-452) and fallthrough_incoming passed to prefix_node (lines 469-470)."""
        visitor = CFGGeneratorVisitor()
        mock_ast = MagicMock()
        mock_body = MagicMock()
        mock_ast.child_by_field_name.side_effect = lambda f: mock_body if f == 'body' else MagicMock()

        # Group 1: simple case (no break) → sets fallthrough_incoming
        mock_lbl1 = MagicMock()
        mock_lbl1.is_named = True
        mock_lbl1.type = AstNodeType.SWITCH_LABEL
        mock_lbl1.text = b'case 1:'
        mock_lbl1.start_point = (0, 0)
        mock_lbl1.end_point = (0, 7)

        mock_simple1 = MagicMock()
        mock_simple1.is_named = True
        mock_simple1.type = AstNodeType.EXPRESSION_STATEMENT.value  # simple, no break
        mock_simple1.text = b'x++;'
        mock_simple1.start_point = (1, 0)
        mock_simple1.end_point = (1, 4)

        mock_group1 = MagicMock()
        mock_group1.type = AstNodeType.SWITCH_BLOCK_GROUP
        mock_group1.children = [mock_lbl1, mock_simple1]

        # Group 2: case 2 with a simple prefix stmt then an IF (complex)
        mock_lbl2 = MagicMock()
        mock_lbl2.is_named = True
        mock_lbl2.type = AstNodeType.SWITCH_LABEL
        mock_lbl2.text = b'case 2:'
        mock_lbl2.start_point = (2, 0)
        mock_lbl2.end_point = (2, 7)

        mock_simple_pre = MagicMock()
        mock_simple_pre.is_named = True
        mock_simple_pre.type = AstNodeType.EXPRESSION_STATEMENT.value  # simple prefix
        mock_simple_pre.text = b'log();'
        mock_simple_pre.start_point = (3, 0)
        mock_simple_pre.end_point = (3, 6)

        mock_complex_stmt = MagicMock()
        mock_complex_stmt.is_named = True
        mock_complex_stmt.type = AstNodeType.IF_STATEMENT.value
        mock_complex_stmt.text = b'if(a){}'
        mock_complex_stmt.start_point = (4, 0)
        mock_complex_stmt.end_point = (4, 7)

        mock_group2 = MagicMock()
        mock_group2.type = AstNodeType.SWITCH_BLOCK_GROUP
        mock_group2.children = [mock_lbl2, mock_simple_pre, mock_complex_stmt]

        mock_body.children = [mock_group1, mock_group2]

        call_count = [0]
        def create_node_factory(*args, **kwargs):
            call_count[0] += 1
            node = CfgNode(None)
            node.id_node = f"node_{call_count[0]}"
            return node

        mock_create_node.side_effect = create_node_factory

        complex_entry = CfgNode(None)
        complex_entry.id_node = "if_entry"

        with patch.object(visitor, 'visit_if_statement',
                          return_value=(complex_entry, [ExitNode(complex_entry, BranchType.SEQUENTIAL)])) as mock_if:
            setattr(visitor, f'visit_{AstNodeType.IF_STATEMENT.value}', mock_if)
            entry, exits = visitor._process_switch(mock_ast)

        # prefix_parts for group2 should contain label + simple_pre (lines 450-452)
        # prefix_node should have source_code with both label and simple stmt
        normal_nodes = [n for n in visitor.nodes if n.node_type == NodeType.NORMAL]
        # node from group1 + prefix_node from group2
        assert len(normal_nodes) >= 2

        # Fallthrough edge from group1_node to prefix_node of group2 (lines 469-470)
        g1_node = normal_nodes[0]
        prefix_node = normal_nodes[1]
        assert any(e['id_start_node'] == g1_node.id_node and e['id_finish_node'] == prefix_node.id_node for e in visitor.edges)
        assert "case 2:\nlog();" in prefix_node.source_code

    @patch("core.cfg_generator.NodeFactory.create_node")
    def test_process_switch_complex_group_no_prefix_no_incoming(self, mock_create_node):
        """TC-CFG-35: Tests switch complex group where prefix_node is None AND current_incoming is empty
        → direct cond→entry edge (lines 486-490).
        This requires a group with NO labels (labels=[]) and NO simple prefix stmts, so prefix_parts=[],
        prefix_node=None, and fallthrough_incoming=[] (first group, no prior group)."""
        visitor = CFGGeneratorVisitor()
        mock_ast = MagicMock()
        mock_body = MagicMock()
        mock_ast.child_by_field_name.side_effect = lambda f: mock_body if f == 'body' else MagicMock()

        # Group with NO labels, just a complex stmt as first item
        # labels=[] → prefix_parts=[], prefix_node=None
        # current_incoming=fallthrough_incoming=[] (first group)
        mock_complex = MagicMock()
        mock_complex.is_named = True
        mock_complex.type = AstNodeType.IF_STATEMENT.value
        mock_complex.text = b'if(b){}'
        mock_complex.start_point = (1, 0)
        mock_complex.end_point = (1, 7)

        mock_group = MagicMock()
        mock_group.type = AstNodeType.SWITCH_BLOCK_GROUP
        # Child is a complex stmt (not a label) - simulates group body without switch_label
        mock_complex.type = AstNodeType.IF_STATEMENT.value  # not SWITCH_LABEL
        mock_group.children = [mock_complex]  # No labels → labels=[], stmts=[mock_complex]

        mock_body.children = [mock_group]

        cond_node = CfgNode(None)
        cond_node.id_node = "switch_cond_no_prefix"
        mock_create_node.return_value = cond_node

        complex_entry = CfgNode(None)
        complex_entry.id_node = "complex_no_prefix_entry"

        with patch.object(visitor, 'visit_if_statement',
                          return_value=(complex_entry, [ExitNode(complex_entry, BranchType.SEQUENTIAL)])) as mock_if:
            setattr(visitor, f'visit_{AstNodeType.IF_STATEMENT.value}', mock_if)
            entry, exits = visitor._process_switch(mock_ast)

        # Lines 486-488: no prefix_node AND no current_incoming → direct edge cond→complex_entry (CASE)
        assert any(
            e['id_start_node'] == cond_node.id_node and e['id_finish_node'] == complex_entry.id_node
            for e in visitor.edges
        )

    @patch("core.cfg_generator.NodeFactory.create_node")
    def test_process_switch_complex_group_break_return_continue_exits(self, mock_create_node):
        """TC-CFG-36: Tests switch complex group where complex stmt exits with BREAK, RETURN, CONTINUE (lines 496-500)."""
        visitor = CFGGeneratorVisitor()
        mock_ast = MagicMock()
        mock_body = MagicMock()
        mock_ast.child_by_field_name.side_effect = lambda f: mock_body if f == 'body' else MagicMock()

        mock_label = MagicMock()
        mock_label.is_named = True
        mock_label.type = AstNodeType.SWITCH_LABEL
        mock_label.text = b'case 4:'
        mock_label.start_point = (0, 0)
        mock_label.end_point = (0, 7)

        mock_complex = MagicMock()
        mock_complex.is_named = True
        mock_complex.type = AstNodeType.IF_STATEMENT.value
        mock_complex.text = b'if(c){return;}'
        mock_complex.start_point = (1, 0)
        mock_complex.end_point = (1, 14)

        mock_group = MagicMock()
        mock_group.type = AstNodeType.SWITCH_BLOCK_GROUP
        mock_group.children = [mock_label, mock_complex]
        mock_body.children = [mock_group]

        cond_node = CfgNode(None)
        cond_node.id_node = "switch_cond_break_ret"
        mock_create_node.return_value = cond_node

        complex_entry = CfgNode(None)
        complex_entry.id_node = "complex_break_ret_entry"
        break_node = CfgNode(None)
        break_node.id_node = "break_node"
        return_node = CfgNode(None)
        return_node.id_node = "return_node"
        continue_node = CfgNode(None)
        continue_node.id_node = "continue_node"

        exits_from_complex = [
            ExitNode(break_node, BranchType.BREAK),
            ExitNode(return_node, BranchType.RETURN),
            ExitNode(continue_node, BranchType.CONTINUE),
        ]

        with patch.object(visitor, 'visit_if_statement',
                          return_value=(complex_entry, exits_from_complex)) as mock_if:
            setattr(visitor, f'visit_{AstNodeType.IF_STATEMENT.value}', mock_if)
            entry, exits = visitor._process_switch(mock_ast)

        # BREAK → edge to merge_node (line 498)
        merge_node = next(n for n in visitor.nodes if n.node_type == NodeType.MERGE)
        assert any(e['id_start_node'] == break_node.id_node and e['id_finish_node'] == merge_node.id_node for e in visitor.edges)

        # RETURN → appended to exit_nodes (line 500); CONTINUE → appended (line 500)
        # exit_nodes from _process_switch includes merge_node SEQUENTIAL + return + continue
        non_merge_exits = [ex for ex in exits if ex.node != merge_node]
        assert any(ex.branch_type == BranchType.RETURN for ex in non_merge_exits)
        assert any(ex.branch_type == BranchType.CONTINUE for ex in non_merge_exits)

    @patch("core.cfg_generator.NodeFactory.create_node")
    def test_process_switch_complex_group_simple_batch_with_break(self, mock_create_node):
        """TC-CFG-37: Tests switch complex group simple batch ending with BREAK → edge to merge_node, loop breaks (lines 506-543)."""
        visitor = CFGGeneratorVisitor()
        mock_ast = MagicMock()
        mock_body = MagicMock()
        mock_ast.child_by_field_name.side_effect = lambda f: mock_body if f == 'body' else MagicMock()

        mock_label = MagicMock()
        mock_label.is_named = True
        mock_label.type = AstNodeType.SWITCH_LABEL
        mock_label.text = b'case 5:'
        mock_label.start_point = (0, 0)
        mock_label.end_point = (0, 7)

        # Complex stmt first (triggers complex branch)
        mock_complex = MagicMock()
        mock_complex.is_named = True
        mock_complex.type = AstNodeType.IF_STATEMENT.value
        mock_complex.text = b'if(d){}'
        mock_complex.start_point = (1, 0)
        mock_complex.end_point = (1, 7)

        # Simple stmt (BREAK) after complex
        mock_break_stmt = MagicMock()
        mock_break_stmt.is_named = True
        mock_break_stmt.type = AstNodeType.BREAK_STATEMENT.value
        mock_break_stmt.text = b'break;'
        mock_break_stmt.start_point = (2, 0)
        mock_break_stmt.end_point = (2, 6)

        mock_group = MagicMock()
        mock_group.type = AstNodeType.SWITCH_BLOCK_GROUP
        mock_group.children = [mock_label, mock_complex, mock_break_stmt]
        mock_body.children = [mock_group]

        cond_node = CfgNode(None)
        cond_node.id_node = "switch_cond_batch_break"
        mock_create_node.return_value = cond_node

        complex_entry = CfgNode(None)
        complex_entry.id_node = "complex_batch_entry"

        with patch.object(visitor, 'visit_if_statement',
                          return_value=(complex_entry, [ExitNode(complex_entry, BranchType.SEQUENTIAL)])) as mock_if:
            setattr(visitor, f'visit_{AstNodeType.IF_STATEMENT.value}', mock_if)
            entry, exits = visitor._process_switch(mock_ast)

        # batch_node should be created and have SEQUENTIAL edge to merge_node (lines 534-535)
        merge_node = next(n for n in visitor.nodes if n.node_type == NodeType.MERGE)
        batch_nodes = [n for n in visitor.nodes if n.node_type == NodeType.NORMAL]
        assert any(n.source_code == 'break;' for n in batch_nodes)
        batch_node = next(n for n in batch_nodes if n.source_code == 'break;')
        assert any(e['id_start_node'] == batch_node.id_node and e['id_finish_node'] == merge_node.id_node for e in visitor.edges)

    @patch("core.cfg_generator.NodeFactory.create_node")
    def test_process_switch_complex_group_simple_batch_with_return(self, mock_create_node):
        """TC-CFG-38: Tests switch complex group simple batch ending with RETURN → exit_nodes gets ExitNode(batch, RETURN) (lines 538-540)."""
        visitor = CFGGeneratorVisitor()
        mock_ast = MagicMock()
        mock_body = MagicMock()
        mock_ast.child_by_field_name.side_effect = lambda f: mock_body if f == 'body' else MagicMock()

        mock_label = MagicMock()
        mock_label.is_named = True
        mock_label.type = AstNodeType.SWITCH_LABEL
        mock_label.text = b'case 6:'
        mock_label.start_point = (0, 0)
        mock_label.end_point = (0, 7)

        mock_complex = MagicMock()
        mock_complex.is_named = True
        mock_complex.type = AstNodeType.IF_STATEMENT.value
        mock_complex.text = b'if(e){}'
        mock_complex.start_point = (1, 0)
        mock_complex.end_point = (1, 7)

        mock_return_stmt = MagicMock()
        mock_return_stmt.is_named = True
        mock_return_stmt.type = AstNodeType.RETURN_STATEMENT.value
        mock_return_stmt.text = b'return x;'
        mock_return_stmt.start_point = (2, 0)
        mock_return_stmt.end_point = (2, 9)

        mock_group = MagicMock()
        mock_group.type = AstNodeType.SWITCH_BLOCK_GROUP
        mock_group.children = [mock_label, mock_complex, mock_return_stmt]
        mock_body.children = [mock_group]

        cond_node = CfgNode(None)
        cond_node.id_node = "switch_cond_batch_ret"
        mock_create_node.return_value = cond_node

        complex_entry = CfgNode(None)
        complex_entry.id_node = "complex_batch_ret_entry"

        with patch.object(visitor, 'visit_if_statement',
                          return_value=(complex_entry, [ExitNode(complex_entry, BranchType.SEQUENTIAL)])) as mock_if:
            setattr(visitor, f'visit_{AstNodeType.IF_STATEMENT.value}', mock_if)
            entry, exits = visitor._process_switch(mock_ast)

        # exit_nodes should contain a RETURN exit (lines 538-540)
        assert any(ex.branch_type == BranchType.RETURN for ex in exits)

    @patch("core.cfg_generator.NodeFactory.create_node")
    def test_process_switch_complex_group_simple_batch_sequential_fallthrough(self, mock_create_node):
        """TC-CFG-39: Tests switch complex group simple batch without break/return → current_incoming updated (line 543)."""
        visitor = CFGGeneratorVisitor()
        mock_ast = MagicMock()
        mock_body = MagicMock()
        mock_ast.child_by_field_name.side_effect = lambda f: mock_body if f == 'body' else MagicMock()

        mock_label = MagicMock()
        mock_label.is_named = True
        mock_label.type = AstNodeType.SWITCH_LABEL
        mock_label.text = b'case 7:'
        mock_label.start_point = (0, 0)
        mock_label.end_point = (0, 7)

        mock_complex = MagicMock()
        mock_complex.is_named = True
        mock_complex.type = AstNodeType.IF_STATEMENT.value
        mock_complex.text = b'if(f){}'
        mock_complex.start_point = (1, 0)
        mock_complex.end_point = (1, 7)

        # Simple stmt after complex (no break, no return)
        mock_expr_stmt = MagicMock()
        mock_expr_stmt.is_named = True
        mock_expr_stmt.type = AstNodeType.EXPRESSION_STATEMENT.value
        mock_expr_stmt.text = b'z++;'
        mock_expr_stmt.start_point = (2, 0)
        mock_expr_stmt.end_point = (2, 4)

        mock_group = MagicMock()
        mock_group.type = AstNodeType.SWITCH_BLOCK_GROUP
        mock_group.children = [mock_label, mock_complex, mock_expr_stmt]
        mock_body.children = [mock_group]

        cond_node = CfgNode(None)
        cond_node.id_node = "switch_cond_batch_seq"
        mock_create_node.return_value = cond_node

        complex_entry = CfgNode(None)
        complex_entry.id_node = "complex_seq_entry"

        with patch.object(visitor, 'visit_if_statement',
                          return_value=(complex_entry, [ExitNode(complex_entry, BranchType.SEQUENTIAL)])) as mock_if:
            setattr(visitor, f'visit_{AstNodeType.IF_STATEMENT.value}', mock_if)
            entry, exits = visitor._process_switch(mock_ast)

        # batch_node for 'z++;' should exist and have a SEQUENTIAL edge to merge_node (via fallthrough)
        batch_nodes = [n for n in visitor.nodes if n.node_type == NodeType.NORMAL]
        assert any(n.source_code == 'z++;' for n in batch_nodes)
        batch_node = next(n for n in batch_nodes if n.source_code == 'z++;')
        merge_node = next(n for n in visitor.nodes if n.node_type == NodeType.MERGE)
        # batch_node flows to merge via fallthrough_incoming at end of _process_switch
        assert any(e['id_start_node'] == batch_node.id_node and e['id_finish_node'] == merge_node.id_node for e in visitor.edges)

    @patch("core.cfg_generator.NodeFactory.create_node")
    def test_visit_for_statement_non_block_body(self, mock_create_node):
        """TC-CFG-40: Tests FOR statement routing when body is a non-block statement → getattr fallback (line 246)."""
        visitor = CFGGeneratorVisitor()
        mock_ast = MagicMock()

        mock_body = MagicMock()
        mock_body.type = AstNodeType.EXPRESSION_STATEMENT  # Not a BLOCK

        mock_ast.child_by_field_name.side_effect = lambda f: mock_body if f == 'body' else None

        for_node = MagicMock()
        for_node.id_node = "for_cond_nonblock"
        for_node.source_code = "for (;;)"
        mock_create_node.return_value = for_node

        body_node = CfgNode(None)
        body_node.id_node = "for_body_nonblock"

        with patch.object(visitor, 'generic_visit', return_value=(body_node, [ExitNode(body_node, BranchType.SEQUENTIAL)])) as mock_generic:
            entry, exits = visitor.visit_for_statement(mock_ast)

            # generic_visit called because body type is not BLOCK (line 246)
            mock_generic.assert_called_once_with(mock_body)
            assert entry == for_node
            # Loop-back edge: body_node → for_node (SEQUENTIAL via _process_loop_exits)
            assert any(e['id_finish_node'] == for_node.id_node for e in visitor.edges)

    @patch("core.cfg_generator.NodeFactory.create_node")
    @patch.object(CFGGeneratorVisitor, 'visit_block')
    def test_visit_do_statement_with_block_body(self, mock_visit_block, mock_create_node):
        """TC-CFG-41: Tests DO-WHILE with a BLOCK body → visit_block is called (line 289)."""
        visitor = CFGGeneratorVisitor()
        mock_ast = MagicMock()

        mock_body = MagicMock()
        mock_body.type = AstNodeType.BLOCK  # IS a block

        mock_ast.child_by_field_name.side_effect = lambda f: mock_body if f == 'body' else MagicMock()

        cond_node = MagicMock()
        cond_node.id_node = "do_cond_block"
        mock_create_node.return_value = cond_node

        body_node = CfgNode(None)
        body_node.id_node = "do_body_block_node"
        mock_visit_block.return_value = (body_node, [ExitNode(body_node, BranchType.SEQUENTIAL)])

        entry, exits = visitor.visit_do_statement(mock_ast)

        # visit_block should have been called (line 289)
        mock_visit_block.assert_called_once()
        # entry should be body_first (body_node) since body is non-empty (line 303)
        assert entry == body_node
        assert len(exits) == 1
        assert exits[0].branch_type == BranchType.FALSE
        # Loop-back edge: cond → body (TRUE, line 301)
        assert any(e['id_finish_node'] == body_node.id_node and e['branch_type'] == BranchType.TRUE for e in visitor.edges)

    @patch("core.cfg_generator.NodeFactory.create_node")
    def test_process_switch_default_case_detection(self, mock_create_node):
        """TC-CFG-42: Tests switch group with a 'default' label → has_default = True (line 400) and no FALSE edge from cond to merge."""
        visitor = CFGGeneratorVisitor()
        mock_ast = MagicMock()
        mock_body = MagicMock()
        mock_ast.child_by_field_name.side_effect = lambda f: mock_body if f == 'body' else MagicMock()

        mock_group = MagicMock()
        mock_group.type = AstNodeType.SWITCH_BLOCK_GROUP

        mock_default_label = MagicMock()
        mock_default_label.is_named = True
        mock_default_label.type = AstNodeType.SWITCH_LABEL
        mock_default_label.text = b'default:'
        mock_default_label.start_point = (0, 0)
        mock_default_label.end_point = (0, 8)

        mock_stmt = MagicMock()
        mock_stmt.is_named = True
        mock_stmt.type = AstNodeType.BREAK_STATEMENT.value
        mock_stmt.text = b'break;'
        mock_stmt.start_point = (1, 0)
        mock_stmt.end_point = (1, 6)

        mock_group.children = [mock_default_label, mock_stmt]
        mock_body.children = [mock_group]

        cond_node = CfgNode(None)
        cond_node.id_node = "switch_cond_default"
        mock_create_node.return_value = cond_node

        entry, exits = visitor._process_switch(mock_ast)

        # has_default = True (line 400) → NO FALSE edge from cond_node to merge_node (line 551-552 skipped)
        false_edges = [e for e in visitor.edges if e['branch_type'] == BranchType.FALSE]
        assert len(false_edges) == 0

        # The group is a DEFAULT group so edge is BranchType.DEFAULT (line 426)
        default_edges = [e for e in visitor.edges if e['branch_type'] == BranchType.DEFAULT]
        assert len(default_edges) == 1
        assert default_edges[0]['id_start_node'] == cond_node.id_node

    @patch("core.cfg_generator.NodeFactory.create_node")
    def test_process_switch_complex_group_no_prefix_with_fallthrough_incoming(self, mock_create_node):
        """TC-CFG-43: Tests switch complex group where prefix_node is None AND fallthrough_incoming is non-empty
        → edge from fallthrough node to complex entry (line 490)."""
        visitor = CFGGeneratorVisitor()
        mock_ast = MagicMock()
        mock_body = MagicMock()
        mock_ast.child_by_field_name.side_effect = lambda f: mock_body if f == 'body' else MagicMock()

        # Group 1: simple case with no break → produces fallthrough_incoming
        mock_lbl1 = MagicMock()
        mock_lbl1.is_named = True
        mock_lbl1.type = AstNodeType.SWITCH_LABEL
        mock_lbl1.text = b'case 1:'
        mock_lbl1.start_point = (0, 0)
        mock_lbl1.end_point = (0, 7)

        mock_simple_stmt = MagicMock()
        mock_simple_stmt.is_named = True
        mock_simple_stmt.type = AstNodeType.EXPRESSION_STATEMENT.value
        mock_simple_stmt.text = b'x++;'
        mock_simple_stmt.start_point = (1, 0)
        mock_simple_stmt.end_point = (1, 4)

        mock_group1 = MagicMock()
        mock_group1.type = AstNodeType.SWITCH_BLOCK_GROUP
        mock_group1.children = [mock_lbl1, mock_simple_stmt]

        # Group 2: complex group with NO labels and NO simple prefix → prefix_node=None
        # But fallthrough_incoming from group1 is non-empty → line 490 fires
        mock_complex = MagicMock()
        mock_complex.is_named = True
        mock_complex.type = AstNodeType.IF_STATEMENT.value
        mock_complex.text = b'if(x){}'
        mock_complex.start_point = (2, 0)
        mock_complex.end_point = (2, 7)

        mock_group2 = MagicMock()
        mock_group2.type = AstNodeType.SWITCH_BLOCK_GROUP
        mock_group2.children = [mock_complex]  # No label, no simple prefix

        mock_body.children = [mock_group1, mock_group2]

        call_count = [0]
        def create_node_factory(*args, **kwargs):
            call_count[0] += 1
            node = CfgNode(None)
            node.id_node = f"node_{call_count[0]}"
            return node

        mock_create_node.side_effect = create_node_factory

        complex_entry = CfgNode(None)
        complex_entry.id_node = "complex_ft_entry"

        with patch.object(visitor, 'visit_if_statement',
                          return_value=(complex_entry, [ExitNode(complex_entry, BranchType.SEQUENTIAL)])) as mock_if:
            setattr(visitor, f'visit_{AstNodeType.IF_STATEMENT.value}', mock_if)
            entry, exits = visitor._process_switch(mock_ast)

        # line 490: create_edge(inc_ft.node, entry_node, inc_ft.branch_type)
        # The fallthrough from group1's block_node should connect to complex_entry
        normal_nodes = [n for n in visitor.nodes if n.node_type == NodeType.NORMAL]
        assert len(normal_nodes) >= 1
        g1_node = normal_nodes[0]
        assert any(
            e['id_start_node'] == g1_node.id_node and e['id_finish_node'] == complex_entry.id_node
            for e in visitor.edges
        )
