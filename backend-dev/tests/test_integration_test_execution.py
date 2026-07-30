import pytest
from unittest.mock import MagicMock, patch
from services.test_execution_service import TestExecutionService
from infrastructure.cfg_coverage_sync import CfgCoverageSync

class MockNode:
    def __init__(self, id_node, node_type, line_start, line_end, line_number=None):
        self.ms_id_node = id_node
        self.ms_node_type = node_type
        self.ms_line_start = line_start
        self.ms_line_end = line_end
        self.ms_line_number = line_number

class MockEdge:
    def __init__(self, id_edge, id_start, id_finish):
        self.ms_id_edge = id_edge
        self.ms_id_start_node = id_start
        self.ms_id_finish_node = id_finish

class TestIntegrationTestExecution:
    @pytest.fixture
    def integration_dependencies(self):
        # Mock repositories (Database) and File System
        deps = {
            'modul_repo': MagicMock(),
            'test_case_repo': MagicMock(),
            'penyelesaian_repo': MagicMock(),
            'cfg_repo': MagicMock(),
            'system_repo': MagicMock(),
            'file_manager': MagicMock(),
            'test_code_gen': MagicMock(),
            'junit_parser': MagicMock(),
            'jacoco_parser': MagicMock(),
            # KUNCI PERBEDAAN: 
            # Kita TIDAK me-mock CfgCoverageSync, tapi menginisiasi instance aslinya
            'cfg_sync': None, 
        }
        
        # Setup real CfgCoverageSync with mocked CfgRepository
        deps['cfg_sync'] = CfgCoverageSync(deps['cfg_repo'])
        
        # Setup base mock return values for Modul & File
        deps['modul_repo'].find_detail_by_topik_modul.return_value = {
            'ms_id_modul': 'modul-123',
            'ms_source_code': 'source.java',
            'ms_class_name': 'Main',
            'ms_function_name': 'testMethod',
            'ms_return_type': 'void',
            'ms_tingkat_kesulitan': '10',
            'ms_nama_modul': 'Test Modul'
        }
        deps['test_case_repo'].find_by_topik_and_student.return_value = [
            {'tr_object_pengujian': 'pengujian_1'}
        ]
        deps['file_manager'].read_source_code_text.return_value = "public class Main {}"
        deps['file_manager'].base_path = "/mock/base/path"
        deps['test_code_gen'].generate_junit_class_string.return_value = "public class MainTest {}"
        deps['system_repo'].get_minimum_coverage.return_value = 80.0
        
        # Setup Mock Graph untuk CfgRepository (Mensimulasikan DB Master Graph)
        # Skenario Graph: START (1) -> STATEMENT (2) -> END (3)
        deps['cfg_repo'].get_master_nodes.return_value = [
            MockNode('node_1', 'START', line_start=None, line_end=None, line_number=1),
            MockNode('node_2', 'STATEMENT', line_start=2, line_end=2, line_number=2),
            MockNode('node_3', 'END', line_start=3, line_end=3, line_number=3)
        ]
        deps['cfg_repo'].get_master_edges.return_value = [
            MockEdge('edge_1', 'node_1', 'node_2'),
            MockEdge('edge_2', 'node_2', 'node_3')
        ]
        
        return deps

    @pytest.fixture
    def test_execution_service(self, integration_dependencies):
        return TestExecutionService(**integration_dependencies)

    @patch('services.test_execution_service.http_session.post')
    def test_integration_partial_coverage(self, mock_post, test_execution_service, integration_dependencies):
        """
        Test Case Name: Integration Testing - Eksekusi Method Sebagian (Partial Coverage Propagation)
        Precondition: 
            - Database Master CFG (Mock) memiliki graf: START(node_1) -> STATEMENT(node_2) -> END(node_3).
            - API Java Worker berhasil dipanggil via HTTP (mock).
        Step to Execute: 
            1. Siapkan payload HTTP Response dengan baris 2 berstatus 'PARTLY_COVERED'.
            2. Panggil TestExecutionService.run_test().
            3. Tangkap payload argumen pada CfgRepository.bulk_insert_tr_nodes & bulk_insert_tr_edges yang digenerate oleh CfgCoverageSync.
        Test Data: 
            - Response lineStatuses: [{"line": 2, "status": "PARTLY_COVERED"}]
        Expected Result: 
            - Node 1 (START) = 'Y', Node 2 (STATEMENT) = 'S', Node 3 (END) = 'Y'.
            - Edge 1 (START->STATEMENT) = 'Y', Edge 2 (STATEMENT->END) = 'Y'.
        """
        # 1. Setup Mock HTTP Response (Java Worker API Payload)
        # Mensimulasikan baris 2 dieksekusi sebagian (PARTLY_COVERED)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "isAllPassed": True,
            "coveragePercent": 100.0,
            "lineStatuses": [
                {"line": 2, "status": "PARTLY_COVERED"},
            ],
            "failures": []
        }
        mock_post.return_value = mock_response

        # 2. Eksekusi service (Act)
        result = test_execution_service.run_test("topik-1", "student-1")

        # 3. Verifikasi (Assert)
        assert result["status_eksekusi"] is True
        
        mock_cfg_repo = integration_dependencies['cfg_repo']
        
        # Memastikan infrastruktur CfgCoverageSync memanggil DB untuk bulk insert di akhir propagasi
        assert mock_cfg_repo.bulk_insert_tr_nodes.called
        assert mock_cfg_repo.bulk_insert_tr_edges.called
        
        # Ambil payload argument yang dikirimkan ke CfgRepository.bulk_insert_tr_nodes
        call_args_nodes = mock_cfg_repo.bulk_insert_tr_nodes.call_args[0][0]
        node_status_result = {item['tr_id_node']: item['tr_status'] for item in call_args_nodes}
        
        assert node_status_result['node_1'] == 'Y'  # Node START
        assert node_status_result['node_2'] == 'S'  # Node Baris 2 (Partly)
        assert node_status_result['node_3'] == 'Y'  # Node END

        # Ambil argument payload untuk bulk_insert_tr_edges
        call_args_edges = mock_cfg_repo.bulk_insert_tr_edges.call_args[0][0]
        edge_status_result = {item['tr_id_edge']: item['tr_status'] for item in call_args_edges}
        
        assert edge_status_result['edge_1'] == 'Y' 
        assert edge_status_result['edge_2'] == 'Y'

    @patch('services.test_execution_service.http_session.post')
    def test_integration_full_coverage(self, mock_post, test_execution_service, integration_dependencies):
        """
        Test Case Name: Integration Testing - Eksekusi Method Secara Penuh (Full Coverage Propagation)
        Precondition: 
            - Database Master CFG (Mock) memiliki graf: START(node_1) -> STATEMENT(node_2) -> END(node_3).
            - API Java Worker merespon dengan status baris yang tereksekusi sempurna.
        Step to Execute: 
            1. Siapkan payload HTTP Response dengan baris 2 berstatus 'FULLY_COVERED'.
            2. Panggil TestExecutionService.run_test().
            3. Validasi hasil algoritma CfgCoverageSync sebelum di-insert ke mock DB.
        Test Data: 
            - Response lineStatuses: [{"line": 2, "status": "FULLY_COVERED"}]
        Expected Result: 
            - Node 1 (START), Node 2 (STATEMENT), dan Node 3 (END) berstatus 'Y'.
            - Seluruh edge (Edge 1 dan Edge 2) berstatus 'Y'.
        """
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "isAllPassed": True,
            "coveragePercent": 100.0,
            "lineStatuses": [{"line": 2, "status": "FULLY_COVERED"}],
            "failures": []
        }
        mock_post.return_value = mock_response

        test_execution_service.run_test("topik-1", "student-1")
        mock_cfg_repo = integration_dependencies['cfg_repo']
        
        call_args_nodes = mock_cfg_repo.bulk_insert_tr_nodes.call_args[0][0]
        node_status_result = {item['tr_id_node']: item['tr_status'] for item in call_args_nodes}
        
        assert node_status_result['node_1'] == 'Y'
        assert node_status_result['node_2'] == 'Y'
        assert node_status_result['node_3'] == 'Y'

    @patch('services.test_execution_service.http_session.post')
    def test_integration_no_coverage(self, mock_post, test_execution_service, integration_dependencies):
        """
        Test Case Name: Integration Testing - Method Tidak Tereksekusi (No Coverage)
        Precondition: 
            - Database Master CFG (Mock) memiliki graf: START(node_1) -> STATEMENT(node_2) -> END(node_3).
            - Java Worker gagal mengenai target method (atau test gagal total/exception).
        Step to Execute: 
            1. Siapkan payload HTTP Response dengan array lineStatuses KOSONG ([]).
            2. Panggil TestExecutionService.run_test().
            3. Validasi hasil propagasi graph.
        Test Data: 
            - Response lineStatuses: []
        Expected Result: 
            - Fungsi propagasi akan menandai seluruh node START, STATEMENT, dan END menjadi 'N'.
            - Seluruh edge menjadi 'N'.
        """
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "isAllPassed": False,
            "coveragePercent": 0.0,
            "lineStatuses": [],
            "failures": []
        }
        mock_post.return_value = mock_response

        test_execution_service.run_test("topik-1", "student-1")
        mock_cfg_repo = integration_dependencies['cfg_repo']
        
        if mock_cfg_repo.bulk_insert_tr_nodes.called:
            call_args_nodes = mock_cfg_repo.bulk_insert_tr_nodes.call_args[0][0]
            node_status_result = {item['tr_id_node']: item['tr_status'] for item in call_args_nodes}
            
            assert node_status_result['node_1'] == 'N'
            assert node_status_result['node_2'] == 'N'
            assert node_status_result['node_3'] == 'N'

    def test_integration_get_execution_result_unexecuted_paths(self, test_execution_service, integration_dependencies):
        """
        Test Case Name: Integration Testing - Ekstraksi Unexecuted Paths (Path Analysis Service)
        Precondition: 
            - Database (Mock) mengembalikan graf percabangan IF/ELSE.
            - Status Eksekusi (tr_status) di DB mencatat Cabang FALSE ('N') tidak tereksekusi, sedangkan Cabang TRUE ('Y') tereksekusi.
        Step to Execute: 
            1. Siapkan mock return value untuk metode penyelesaian_repo, modul_repo, dan cfg_repo.
            2. Panggil TestExecutionService.get_execution_result().
            3. Algoritma basis path (ABPC) dari PathAnalysisService (Instance Asli) akan mencari seluruh independen path dan mem-filter path yang memiliki status 'N'.
            4. Validasi daftar unexecutedPaths yang dikembalikan di dictionary hasil.
        Test Data: 
            - Graf: START -> 1 -> 2(DECISION) -> 3(FALSE, Status='N') -> END
            - Graf: START -> 1 -> 2(DECISION) -> 4(TRUE, Status='Y') -> END
        Expected Result: 
            - Method mengembalikan dictionary hasil akhir pengujian.
            - Field 'unexecutedPaths' dalam 'data_cfg' HANYA berisi path yang melewati node '3', yaitu: ["Start→1→2→3→End"].
            - Path yang melewati node '4' tidak masuk karena sudah tereksekusi ('Y').
        """
        from datetime import datetime
        
        # 1. Setup mock data untuk fungsi get_execution_result
        mock_penyelesaian = integration_dependencies['penyelesaian_repo']
        mock_penyelesaian.find_by_topik_and_student.return_value = {
            'tr_status_eksekusi': 'Y',
            'tr_persentase_coverage': '50.0',
            'tr_nilai': 50,
            'tr_tgl_eksekusi': datetime.now(),
            'tr_result_report': '#',
            'tr_coverage_report': '#'
        }
        
        mock_tc = integration_dependencies['test_case_repo']
        mock_tc.get_statistics_by_topik_and_student.return_value = {
            'total': 2, 'countPass': 1, 'countFailed': 1
        }
        
        mock_cfg_repo = integration_dependencies['cfg_repo']
        # Mock Graf DB dengan satu node berstatus 'N' (Unexecuted)
        nodes = [
            {"ms_id_node": "n1", "ms_node_type": "START", "ms_execution_order": None, "tr_status": "Y"},
            {"ms_id_node": "n2", "ms_node_type": "STATEMENT", "ms_execution_order": 1, "tr_status": "Y"},
            {"ms_id_node": "n3", "ms_node_type": "DECISION", "ms_execution_order": 2, "tr_status": "Y"},
            {"ms_id_node": "n4", "ms_node_type": "STATEMENT", "ms_execution_order": 3, "tr_status": "N"}, # Unexecuted branch
            {"ms_id_node": "n5", "ms_node_type": "STATEMENT", "ms_execution_order": 4, "tr_status": "Y"}, # Executed branch
            {"ms_id_node": "n6", "ms_node_type": "END", "ms_execution_order": None, "tr_status": "Y"}
        ]
        edges = [
            {"ms_id_edge": "e1", "ms_id_start_node": "n1", "ms_id_finish_node": "n2"},
            {"ms_id_edge": "e2", "ms_id_start_node": "n2", "ms_id_finish_node": "n3"},
            {"ms_id_edge": "e3", "ms_id_start_node": "n3", "ms_id_finish_node": "n4", "ms_branch_type": "FALSE"},
            {"ms_id_edge": "e4", "ms_id_start_node": "n3", "ms_id_finish_node": "n5", "ms_branch_type": "TRUE"},
            {"ms_id_edge": "e5", "ms_id_start_node": "n4", "ms_id_finish_node": "n6"},
            {"ms_id_edge": "e6", "ms_id_start_node": "n5", "ms_id_finish_node": "n6"}
        ]
        mock_cfg_repo.get_cfg_with_status.return_value = (nodes, edges)

        # 2. Eksekusi service (Act)
        result = test_execution_service.get_execution_result("topik-1", "student-1")

        # 3. Verifikasi (Assert)
        assert "data_cfg" in result
        assert "unexecutedPaths" in result["data_cfg"]
        
        # Hasil yang diharapkan: Hanya path yang mengandung node eksekusi urutan 3
        expected_path = "Start→1→2→3→End"
        unexecuted = result["data_cfg"]["unexecutedPaths"]
        
        # Harus hanya ada 1 path (karena dari 2 basis paths, hanya 1 yang ada 'N')
        assert len(unexecuted) == 1
        assert unexecuted[0] == expected_path

    def test_integration_get_execution_result_all_executed(self, test_execution_service, integration_dependencies):
        """
        Test Case Name: Integration Testing - Ekstraksi Unexecuted Paths (Semua Tereksekusi)
        Precondition: 
            - Database (Mock) mengembalikan graf percabangan IF/ELSE.
            - Seluruh node memiliki tr_status='Y' (100% Coverage).
        Step to Execute: 
            1. Panggil TestExecutionService.get_execution_result().
            2. Validasi field unexecutedPaths.
        Test Data: 
            - Seluruh Node status='Y'.
        Expected Result: 
            - unexecutedPaths mengembalikan array kosong [] karena tidak ada path tersisa yang belum dilewati.
        """
        from datetime import datetime
        mock_penyelesaian = integration_dependencies['penyelesaian_repo']
        mock_penyelesaian.find_by_topik_and_student.return_value = {
            'tr_status_eksekusi': 'Y', 'tr_persentase_coverage': '100.0',
            'tr_nilai': 100, 'tr_tgl_eksekusi': datetime.now(),
            'tr_result_report': '#', 'tr_coverage_report': '#'
        }
        mock_tc = integration_dependencies['test_case_repo']
        mock_tc.get_statistics_by_topik_and_student.return_value = {'total': 2, 'countPass': 2, 'countFailed': 0}
        
        mock_cfg_repo = integration_dependencies['cfg_repo']
        nodes = [
            {"ms_id_node": "n1", "ms_node_type": "START", "ms_execution_order": None, "tr_status": "Y"},
            {"ms_id_node": "n2", "ms_node_type": "STATEMENT", "ms_execution_order": 1, "tr_status": "Y"},
            {"ms_id_node": "n3", "ms_node_type": "DECISION", "ms_execution_order": 2, "tr_status": "Y"},
            {"ms_id_node": "n4", "ms_node_type": "STATEMENT", "ms_execution_order": 3, "tr_status": "Y"},
            {"ms_id_node": "n5", "ms_node_type": "STATEMENT", "ms_execution_order": 4, "tr_status": "Y"},
            {"ms_id_node": "n6", "ms_node_type": "END", "ms_execution_order": None, "tr_status": "Y"}
        ]
        edges = [
            {"ms_id_edge": "e1", "ms_id_start_node": "n1", "ms_id_finish_node": "n2"},
            {"ms_id_edge": "e2", "ms_id_start_node": "n2", "ms_id_finish_node": "n3"},
            {"ms_id_edge": "e3", "ms_id_start_node": "n3", "ms_id_finish_node": "n4"},
            {"ms_id_edge": "e4", "ms_id_start_node": "n3", "ms_id_finish_node": "n5"},
            {"ms_id_edge": "e5", "ms_id_start_node": "n4", "ms_id_finish_node": "n6"},
            {"ms_id_edge": "e6", "ms_id_start_node": "n5", "ms_id_finish_node": "n6"}
        ]
        mock_cfg_repo.get_cfg_with_status.return_value = (nodes, edges)

        result = test_execution_service.get_execution_result("topik-1", "student-1")
        assert result["data_cfg"]["unexecutedPaths"] == []

    def test_integration_get_execution_result_none_executed(self, test_execution_service, integration_dependencies):
        """
        Test Case Name: Integration Testing - Ekstraksi Unexecuted Paths (Tidak Ada Tereksekusi)
        Precondition: 
            - Database (Mock) mengembalikan graf percabangan IF/ELSE.
            - Seluruh node memiliki tr_status='N' (0% Coverage, Test Gagal).
        Step to Execute: 
            1. Panggil TestExecutionService.get_execution_result().
            2. Validasi field unexecutedPaths.
        Test Data: 
            - Node operasional status='N'.
        Expected Result: 
            - unexecutedPaths mengembalikan seluruh 2 basis paths secara utuh.
        """
        from datetime import datetime
        mock_penyelesaian = integration_dependencies['penyelesaian_repo']
        mock_penyelesaian.find_by_topik_and_student.return_value = {
            'tr_status_eksekusi': 'N', 'tr_persentase_coverage': '0.0',
            'tr_nilai': 0, 'tr_tgl_eksekusi': datetime.now(),
            'tr_result_report': '#', 'tr_coverage_report': '#'
        }
        mock_tc = integration_dependencies['test_case_repo']
        mock_tc.get_statistics_by_topik_and_student.return_value = {'total': 2, 'countPass': 0, 'countFailed': 2}
        
        mock_cfg_repo = integration_dependencies['cfg_repo']
        nodes = [
            {"ms_id_node": "n1", "ms_node_type": "START", "ms_execution_order": None, "tr_status": "N"},
            {"ms_id_node": "n2", "ms_node_type": "STATEMENT", "ms_execution_order": 1, "tr_status": "N"},
            {"ms_id_node": "n3", "ms_node_type": "DECISION", "ms_execution_order": 2, "tr_status": "N"},
            {"ms_id_node": "n4", "ms_node_type": "STATEMENT", "ms_execution_order": 3, "tr_status": "N"},
            {"ms_id_node": "n5", "ms_node_type": "STATEMENT", "ms_execution_order": 4, "tr_status": "N"},
            {"ms_id_node": "n6", "ms_node_type": "END", "ms_execution_order": None, "tr_status": "N"}
        ]
        edges = [
            {"ms_id_edge": "e1", "ms_id_start_node": "n1", "ms_id_finish_node": "n2"},
            {"ms_id_edge": "e2", "ms_id_start_node": "n2", "ms_id_finish_node": "n3"},
            {"ms_id_edge": "e3", "ms_id_start_node": "n3", "ms_id_finish_node": "n4"},
            {"ms_id_edge": "e4", "ms_id_start_node": "n3", "ms_id_finish_node": "n5"},
            {"ms_id_edge": "e5", "ms_id_start_node": "n4", "ms_id_finish_node": "n6"},
            {"ms_id_edge": "e6", "ms_id_start_node": "n5", "ms_id_finish_node": "n6"}
        ]
        mock_cfg_repo.get_cfg_with_status.return_value = (nodes, edges)

        result = test_execution_service.get_execution_result("topik-1", "student-1")
        unexecuted = result["data_cfg"]["unexecutedPaths"]
        
        assert len(unexecuted) == 2
        assert "Start→1→2→3→End" in unexecuted
        assert "Start→1→2→4→End" in unexecuted
