import pytest
from unittest.mock import MagicMock, patch
from services.test_execution_service import TestExecutionService
from repositories.modul_repository import ModulRepository
from repositories.test_case_repository import TestCaseRepository
from repositories.penyelesaian_repository import PenyelesaianRepository
from repositories.system_config_repository import SystemConfigRepository
from repositories.cfg_repository import CfgRepository
from infrastructure.file_storage import FileStorageManager
from infrastructure.test_code_generator import TestCodeGenerator
from infrastructure.parsers.junit_parser import JUnitResultParser
from infrastructure.parsers.jacoco_parser import JaCoCoParser
from infrastructure.cfg_coverage_sync import CfgCoverageSync

class TestJavaWorkerExecution:
    @pytest.fixture
    def mock_dependencies(self):
        deps = {
            'modul_repo': MagicMock(spec=ModulRepository),
            'test_case_repo': MagicMock(spec=TestCaseRepository),
            'penyelesaian_repo': MagicMock(spec=PenyelesaianRepository),
            'cfg_repo': MagicMock(spec=CfgRepository),
            'system_repo': MagicMock(spec=SystemConfigRepository),
            'file_manager': MagicMock(spec=FileStorageManager),
            'test_code_gen': MagicMock(spec=TestCodeGenerator),
            'junit_parser': MagicMock(spec=JUnitResultParser),
            'jacoco_parser': MagicMock(spec=JaCoCoParser),
            'cfg_sync': MagicMock(spec=CfgCoverageSync),
        }
        
        # Setup base mock return values
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
        
        return deps

    @pytest.fixture
    def test_execution_service(self, mock_dependencies):
        return TestExecutionService(**mock_dependencies)

    @patch('services.test_execution_service.http_session.post')
    def test_run_test_line_execution_status_success(self, mock_post, test_execution_service, mock_dependencies):
        """
        Test Case Name: Parsing Status Eksekusi Baris (Java Worker) - Sukses
        Precondition: Mock Java Worker API merespon dengan daftar lineStatuses.
        Step to Execute: 
            1. Panggil TestExecutionService.run_test().
            2. Verifikasi panggilan synchronize() dari cfg_sync.
        Test Data: lineStatuses berisi NOT_COVERED, PARTLY_COVERED, dan FULLY_COVERED.
        Expected Result: Mapping sukses menghasilkan N, S, dan Y pada synchronize().
        """
        # Mock HTTP Response dari Java Worker
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "isAllPassed": True,
            "coveragePercent": 100.0,
            "lineStatuses": [
                {"line": 1, "status": "NOT_COVERED"},
                {"line": 2, "status": "PARTLY_COVERED"},
                {"line": 3, "status": "FULLY_COVERED"}
            ],
            "failures": []
        }
        mock_post.return_value = mock_response

        # Eksekusi
        result = test_execution_service.run_test("topik-1", "student-1")

        # Verifikasi Mapping CFG
        mock_cfg_sync = mock_dependencies['cfg_sync']
        
        # Harus dipanggil dengan format status yang sudah disesuaikan
        mock_cfg_sync.synchronize.assert_called_once_with(
            "topik-1", 
            "student-1", 
            "modul-123", 
            [
                {'line_number': 1, 'status': 'N'},
                {'line_number': 2, 'status': 'S'},
                {'line_number': 3, 'status': 'Y'}
            ]
        )
        assert result["status_eksekusi"] == True

    @patch('services.test_execution_service.http_session.post')
    def test_run_test_line_execution_status_not_found(self, mock_post, test_execution_service, mock_dependencies):
        """
        Test Case Name: Parsing Status Eksekusi Baris - Kosong
        Precondition: Mock Java Worker API mengembalikan lineStatuses kosong ([]).
        Step to Execute: 
            1. Panggil TestExecutionService.run_test().
            2. Verifikasi status pemanggilan cfg_sync.
        Test Data: lineStatuses = []
        Expected Result: cfg_sync.synchronize() tidak pernah dipanggil.
        """
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "isAllPassed": True,
            "coveragePercent": 100.0,
            "lineStatuses": [], # Tidak ada eksekusi baris
            "failures": []
        }
        mock_post.return_value = mock_response

        test_execution_service.run_test("topik-1", "student-1")

        mock_cfg_sync = mock_dependencies['cfg_sync']
        mock_cfg_sync.synchronize.assert_not_called()

    @patch('services.test_execution_service.http_session.post')
    def test_run_test_method_coverage_success(self, mock_post, test_execution_service, mock_dependencies):
        """
        Test Case Name: Parsing Coverage Method - Sukses
        Precondition: Mock Java Worker API mengembalikan coveragePercent > 0.
        Step to Execute: 
            1. Panggil TestExecutionService.run_test().
            2. Verifikasi pemanggilan update_coverage_and_score().
        Test Data: coveragePercent = 85.00, min_coverage = 80.0
        Expected Result: update_coverage_and_score() dipanggil dengan skor 850.0 dan status penyelesaian 'Y'.
        """
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "isAllPassed": True,
            "coveragePercent": 85.00,
            "lineStatuses": [],
            "failures": []
        }
        mock_post.return_value = mock_response

        # Eksekusi
        result = test_execution_service.run_test("topik-1", "student-1")

        # coveragePercent = 85.00, kesulitan = 10 (dari mock), nilai = 85.00 * 10 = 850 (round)
        # 85.00 > 80.0 (min coverage)? True, maka status 'Y'
        mock_penyelesaian = mock_dependencies['penyelesaian_repo']
        mock_penyelesaian.update_coverage_and_score.assert_called_with(
            "topik-1", "student-1", 85.00, 850.0, 'Y', "static/student-1/topik-1/jacoco_report_test/html/index.html"
        )
        assert result["coverage_score"] == 85.00

    @patch('services.test_execution_service.http_session.post')
    def test_run_test_method_coverage_zero(self, mock_post, test_execution_service, mock_dependencies):
        """
        Test Case Name: Parsing Coverage Method - 0
        Precondition: Mock Java Worker API mengembalikan coveragePercent = 0.0.
        Step to Execute: 
            1. Panggil TestExecutionService.run_test().
            2. Verifikasi argument pada update_coverage_and_score().
        Test Data: coveragePercent = 0.0
        Expected Result: update_coverage_and_score() dipanggil dengan persentase 0.0 dan nilai 0.0.
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

        mock_penyelesaian = mock_dependencies['penyelesaian_repo']
        mock_penyelesaian.update_coverage_and_score.assert_called_with(
            "topik-1", "student-1", 0.0, 0.0, 'N', "static/student-1/topik-1/jacoco_report_test/html/index.html"
        )

    @patch('services.test_execution_service.http_session.post')
    def test_run_test_exception(self, mock_post, test_execution_service, mock_dependencies):
        """
        Test Case Name: Parsing Eksekusi - Error / Exception
        Precondition: API Java Worker down / mengembalikan Exception.
        Step to Execute: 
            1. Buat mock HTTP post melemparkan Exception.
            2. Panggil TestExecutionService.run_test().
        Test Data: Exception("Connection Refused")
        Expected Result: Exception tertangani dan update_coverage_and_score() dipanggil dengan coverage=0, nilai=0.
        """
        mock_post.side_effect = Exception("Connection Refused")

        result = test_execution_service.run_test("topik-1", "student-1")

        # Jika terjadi exception, catch block akan dipanggil, update_coverage_and_score direset 0,0,'N'
        mock_penyelesaian = mock_dependencies['penyelesaian_repo']
        mock_penyelesaian.update_coverage_and_score.assert_called_with(
            "topik-1", "student-1", coverage=0, nilai=0, status_penyelesaian='N'
        )
        assert result["status_eksekusi"] == False

    @patch('services.test_execution_service.http_session.post')
    def test_run_test_with_failures(self, mock_post, test_execution_service, mock_dependencies):
        """
        Test Case Name: Penyimpanan Status Test Case - Failure (F)
        Precondition: Mock Java Worker API melaporkan daftar 'failures'.
        Step to Execute: 
            1. Panggil TestExecutionService.run_test().
            2. Verifikasi pemanggilan test_case_repo.update_result().
        Test Data: failures berisi {"testName": "pengujian_1()"}
        Expected Result: test_case_repo.update_result dipanggil dengan status 'F'.
        """
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "isAllPassed": False,
            "coveragePercent": 50.0,
            "lineStatuses": [],
            "failures": [
                {"testName": "pengujian_1()"}
            ]
        }
        mock_post.return_value = mock_response

        test_execution_service.run_test("topik-1", "student-1")

        mock_test_case_repo = mock_dependencies['test_case_repo']
        # Pastikan status = 'F' diset pada repository jika testName match dengan tr_object_pengujian
        mock_test_case_repo.update_result.assert_called_with(
            "topik-1", "student-1", "pengujian_1", "F"
        )
