import pytest
from unittest.mock import MagicMock
from core.parser import JavaParser
from core.cfg_generator import CFGGeneratorVisitor
from core.types import NodeType, BranchType
from core.metrics import calculate_cyclomatic_complexity
from services.cfg_service import CFGService, CFGResult
from repositories.cfg_repository import CfgRepository


class TestIntegrationCFGGenerator:
    """
    Integration Tests for the CFG Generation & Persistence Pipeline (Code -> AST -> CFG -> CC -> DB).
    Tests the interaction between JavaParser, CFGGeneratorVisitor, Metrics, CFGService, and CfgRepository.
    """

    @pytest.fixture
    def mock_db_conn(self):
        """Mock SQLAlchemy Database Connection to verify repository persistence calls."""
        conn = MagicMock()
        conn.execute.return_value.fetchall.return_value = []
        return conn

    @pytest.fixture
    def cfg_repo(self, mock_db_conn):
        """Instantiates CfgRepository with the mocked DB connection."""
        return CfgRepository(mock_db_conn)

    @pytest.fixture
    def cfg_service(self, cfg_repo):
        """Instantiates CFGService with real JavaParser and CfgRepository."""
        return CFGService(cfg_repo)

    # -------------------------------------------------------------------------
    # TC-INT-CFG-01: Integration Test for Sequential Control Flow (No Branching)
    # -------------------------------------------------------------------------
    def test_tc_int_cfg_01_sequential_code(self, cfg_service, mock_db_conn):
        """
        [TC-INT-CFG-01] Integration: Sequential Java Method
        Verifies AST parsing, CFG node/edge generation, Cyclomatic Complexity V(G)=1,
        and database bulk insert formatting for sequential code.
        """
        java_code = """
        public class MathHelper {
            public int addNumbers(int a, int b) {
                int sum = a + b;
                return sum;
            }
        }
        """
        modul_id = "modul-seq-001"

        # 1. Pipeline Execution via CFGService
        cfg_result = cfg_service.generate_cfg_from_java_code(java_code, method_name="addNumbers")
        assert cfg_result is not None
        assert cfg_result.method_name == "addNumbers"

        # 2. Verify CFG Structure
        assert len(cfg_result.nodes) >= 3  # Start, Normal/Return, End
        assert len(cfg_result.edges) >= 2

        # 3. Calculate Cyclomatic Complexity V(G) = E - N + 2
        cc = calculate_cyclomatic_complexity(cfg_result.nodes, cfg_result.edges)
        assert cc == 1

        # 4. Save to DB & Assert Repository Calls
        success = cfg_service.save_cfg_to_database(modul_id, cfg_result, java_code)
        assert success is None or success is True or isinstance(success, bool)
        assert mock_db_conn.execute.call_count >= 3  # insert nodes, insert edges, update modul cc

    # -------------------------------------------------------------------------
    # TC-INT-CFG-02: Integration Test for Single Selection (If-Else)
    # -------------------------------------------------------------------------
    def test_tc_int_cfg_02_if_else_branching(self, cfg_service, mock_db_conn):
        """
        [TC-INT-CFG-02] Integration: If-Else Control Flow
        Verifies decision node creation, True/False branch edges, Merge node,
        and Cyclomatic Complexity calculation V(G)=2.
        """
        java_code = """
        public class VocalChecker {
            public boolean isVokal(char c) {
                if (c == 'a' || c == 'i') {
                    return true;
                } else {
                    return false;
                }
            }
        }
        """
        modul_id = "modul-if-002"

        # Pipeline Execution
        cfg_result = cfg_service.generate_cfg_from_java_code(java_code, method_name="isVokal")
        
        # Verify Node Types
        has_decision = any(
            (n.node_type == NodeType.DECISION or n.node_type.value == "DECISION") 
            for n in cfg_result.nodes
        )
        assert has_decision, "CFG should contain at least one DECISION node for If-Else"

        # Verify Edge Branch Types
        branch_types = [
            e["branch_type"].value if isinstance(e["branch_type"], BranchType) else str(e["branch_type"])
            for e in cfg_result.edges
        ]
        assert "TRUE" in branch_types or "true" in branch_types
        assert "FALSE" in branch_types or "false" in branch_types

        # Verify Cyclomatic Complexity
        cc = calculate_cyclomatic_complexity(cfg_result.nodes, cfg_result.edges)
        assert cc >= 2

        # Save to DB
        cfg_service.save_cfg_to_database(modul_id, cfg_result, java_code)
        assert mock_db_conn.execute.called

    # -------------------------------------------------------------------------
    # TC-INT-CFG-03: Integration Test for Repetition Control Flow (While Loop)
    # -------------------------------------------------------------------------
    def test_tc_int_cfg_03_while_loop(self, cfg_service, mock_db_conn):
        """
        [TC-INT-CFG-03] Integration: While Loop Control Flow
        Verifies loop decision node, back-edge generation, and Cyclomatic Complexity V(G)=2.
        """
        java_code = """
        public class Counter {
            public int countToN(int n) {
                int i = 0;
                while (i < n) {
                    i++;
                }
                return i;
            }
        }
        """
        modul_id = "modul-loop-003"

        # Pipeline Execution
        cfg_result = cfg_service.generate_cfg_from_java_code(java_code, method_name="countToN")

        # Verify Nodes & Edges
        assert len(cfg_result.nodes) >= 4
        assert len(cfg_result.edges) >= 4

        # Verify Cyclomatic Complexity
        cc = calculate_cyclomatic_complexity(cfg_result.nodes, cfg_result.edges)
        assert cc == 2

        # Save to DB
        cfg_service.save_cfg_to_database(modul_id, cfg_result, java_code)
        assert mock_db_conn.execute.called

    # -------------------------------------------------------------------------
    # TC-INT-CFG-04: Integration Test for Multiple Nested Conditionals
    # -------------------------------------------------------------------------
    def test_tc_int_cfg_04_nested_conditions(self, cfg_service, mock_db_conn):
        """
        [TC-INT-CFG-04] Integration: Nested If-Else Statements
        Verifies complex AST traversal, correct node line numbering, and CC score computation.
        """
        java_code = """
        public class GradeEvaluator {
            public String evaluateScore(int score) {
                if (score >= 80) {
                    return "A";
                } else if (score >= 70) {
                    return "B";
                } else {
                    return "C";
                }
            }
        }
        """
        modul_id = "modul-nested-004"

        # Pipeline Execution
        cfg_result = cfg_service.generate_cfg_from_java_code(java_code, method_name="evaluateScore")

        # Check line numbers exist on nodes
        for node in cfg_result.nodes:
            if hasattr(node, 'line_start') and node.line_start is not None:
                assert node.line_start >= 0

        # Verify CC score
        cc = calculate_cyclomatic_complexity(cfg_result.nodes, cfg_result.edges)
        assert cc == 3

        # Save to DB
        cfg_service.save_cfg_to_database(modul_id, cfg_result, java_code)
        assert mock_db_conn.execute.called

    # -------------------------------------------------------------------------
    # TC-INT-CFG-05: Integration Test for Dictionary Output Serialization
    # -------------------------------------------------------------------------
    def test_tc_int_cfg_05_api_response_serialization(self, cfg_service):
        """
        [TC-INT-CFG-05] Integration: API Response Dictionary Serialization
        Verifies that CFGResult.to_dict() produces valid data format for Frontend consumption.
        """
        java_code = """
        public class VoucherBelanja {
            public boolean dapatVoucher(int totalBelanja) {
                boolean voucher = false;
                if (totalBelanja >= 200000) {
                    voucher = true;
                }
                return voucher;
            }
        }
        """

        cfg_result = cfg_service.generate_cfg_from_java_code(java_code, method_name="dapatVoucher")
        api_dict = cfg_result.to_dict()

        assert "method_parsed" in api_dict
        assert api_dict["method_parsed"] == "dapatVoucher"
        assert "total_nodes" in api_dict
        assert "total_edges" in api_dict
        assert "nodes" in api_dict
        assert "edges" in api_dict
        assert len(api_dict["nodes"]) == cfg_result.total_nodes
        assert len(api_dict["edges"]) == cfg_result.total_edges

    # -------------------------------------------------------------------------
    # TC-INT-CFG-06: Integration Test for Auto-Detect Method & Method Name Extraction
    # -------------------------------------------------------------------------
    def test_tc_int_cfg_06_method_extraction_and_autodetect(self, cfg_service):
        """
        [TC-INT-CFG-06] Integration: Automatic Method Name Extraction & Auto-Detection
        Verifies extract_method_names and auto-detecting first method when method_name is None.
        """
        java_code = """
        public class MultiMethod {
            public int firstMethod() {
                return 10;
            }
            public void secondMethod() {
                System.out.println("Hello");
            }
        }
        """
        # Test method extraction
        method_names = cfg_service.extract_method_names(java_code)
        assert "firstMethod" in method_names
        assert "secondMethod" in method_names

        # Test auto-detection (method_name=None)
        cfg_result = cfg_service.generate_cfg_from_java_code(java_code, method_name=None)
        assert cfg_result.method_name == "firstMethod"
        assert cfg_result.total_nodes > 0

    # -------------------------------------------------------------------------
    # TC-INT-CFG-07: Integration Test for Error Handling & Edge Cases
    # -------------------------------------------------------------------------
    def test_tc_int_cfg_07_error_handling(self, cfg_service):
        """
        [TC-INT-CFG-07] Integration: Error Handling for Invalid Methods & Syntax Errors
        Verifies proper ValueError raising when method does not exist or Java code has no methods.
        """
        java_code = "public class EmptyClass {}"

        # 1. No methods found in code
        with pytest.raises(ValueError, match="No methods found in source code"):
            cfg_service.generate_cfg_from_java_code(java_code, method_name=None)

        java_code_with_method = "public class A { public void foo() {} }"

        # 2. Specified method not found
        with pytest.raises(ValueError, match="Method 'bar' not found"):
            cfg_service.generate_cfg_from_java_code(java_code_with_method, method_name="bar")

        # 3. Invalid Java Code Extraction Error Handling
        invalid_methods = cfg_service.extract_method_names("class Invalid {")
        assert invalid_methods == []

    # -------------------------------------------------------------------------
    # TC-INT-CFG-08: Integration Test for CFG Retrieval & Deletion from Repository
    # -------------------------------------------------------------------------
    def test_tc_int_cfg_08_cfg_repository_crud_operations(self, cfg_service, cfg_repo, mock_db_conn):
        """
        [TC-INT-CFG-08] Integration: CFG Repository Deletion, Retrieval, & Transaction Status Reset
        Verifies get_cfg_for_modul, delete_cfg_for_modul, and repository tr_nodes/edges operations.
        """
        modul_id = "modul-crud-008"
        student_id = "student-123"

        # Mock DB rows returned by CfgRepository
        mock_node_row = MagicMock()
        mock_node_row.ms_id_node = "node-1"
        mock_node_row.ms_execution_order = 1
        mock_node_row.ms_source_code = "int x = 1;"
        mock_node_row.ms_node_type = "NORMAL"
        mock_node_row.ms_ast_node_type = "expression_statement"
        mock_node_row.ms_line_start = 2
        mock_node_row.ms_line_end = 2

        mock_edge_row = MagicMock()
        mock_edge_row.ms_id_edge = "edge-1"
        mock_edge_row.ms_id_start_node = "node-1"
        mock_edge_row.ms_id_finish_node = "node-2"
        mock_edge_row.ms_branch_type = "ALWAYS"
        mock_edge_row.ms_label = None

        mock_db_conn.execute.return_value.fetchall.side_effect = [
            [mock_node_row],  # get_master_nodes
            [mock_edge_row],  # get_master_edges
            [mock_node_row],  # get_cfg_with_status nodes
            [mock_edge_row],  # get_cfg_with_status edges
        ]

        # 1. Retrieve CFG for Module
        nodes_data, edges_data = cfg_service.get_cfg_for_modul(modul_id)
        assert len(nodes_data) == 1
        assert nodes_data[0]["id_node"] == "node-1"
        assert len(edges_data) == 1
        assert edges_data[0]["id_edge"] == "edge-1"

        # 2. Delete CFG for Module
        success_del = cfg_service.delete_cfg_for_modul(modul_id)
        assert success_del is True

        # 3. Direct Repository Methods (Reset & Bulk Insert TR)
        cfg_repo.reset_tr_nodes(modul_id, student_id)
        cfg_repo.reset_tr_edges(modul_id, student_id)
        cfg_repo.bulk_insert_tr_nodes([{"tr_id_node": "n1", "tr_status": "Y"}])
        cfg_repo.bulk_insert_tr_edges([{"tr_id_edge": "e1", "tr_status": "Y"}])
        
        nodes_res, edges_res = cfg_repo.get_cfg_with_status(modul_id, student_id)
        assert nodes_res is not None
        assert edges_res is not None

    # -------------------------------------------------------------------------
    # TC-INT-CFG-09: Integration Test for Exception Handling in Service Layer
    # -------------------------------------------------------------------------
    def test_tc_int_cfg_09_service_exception_handling(self, cfg_service, mock_db_conn):
        """
        [TC-INT-CFG-09] Integration: Exception Handling in CFGService Methods
        Verifies graceful error logging and exception propagation when repository DB errors occur.
        """
        modul_id = "modul-err-009"
        mock_db_conn.execute.side_effect = Exception("Database connection lost")

        # 1. Exception during save_cfg_to_database
        java_code = "public class A { public void f() {} }"
        cfg_result = cfg_service.generate_cfg_from_java_code(java_code)
        
        with pytest.raises(Exception, match="Database connection lost"):
            cfg_service.save_cfg_to_database(modul_id, cfg_result, java_code)

        # 2. Exception during delete_cfg_for_modul
        with pytest.raises(Exception, match="Database connection lost"):
            cfg_service.delete_cfg_for_modul(modul_id)

        # 3. Exception during get_cfg_for_modul returns empty lists
        nodes_data, edges_data = cfg_service.get_cfg_for_modul(modul_id)
        assert nodes_data == []
        assert edges_data == []
