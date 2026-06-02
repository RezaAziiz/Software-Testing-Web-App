import os
import logging
from datetime import datetime

# Mengimpor Repositories
from repositories.modul_repository import ModulRepository
from repositories.test_case_repository import TestCaseRepository
from repositories.penyelesaian_repository import PenyelesaianRepository
from repositories.system_config_repository import SystemConfigRepository
from repositories.cfg_repository import CfgRepository
from infrastructure.file_storage import FileStorageManager
from infrastructure.gradle_executor import GradleExecutor
from infrastructure.test_code_generator import TestCodeGenerator
from infrastructure.parsers.junit_parser import JUnitResultParser
from infrastructure.parsers.jacoco_parser import JaCoCoParser
from infrastructure.cfg_coverage_sync import CfgCoverageSync

logger = logging.getLogger(__name__)

class TestExecutionService:
    def __init__(
        self,
        modul_repo: ModulRepository,
        test_case_repo: TestCaseRepository,
        penyelesaian_repo: PenyelesaianRepository,
        cfg_repo :CfgRepository,
        system_repo: SystemConfigRepository,
        file_manager: FileStorageManager,
        gradle_executor: GradleExecutor,
        test_code_gen: TestCodeGenerator,
        junit_parser: JUnitResultParser,
        jacoco_parser: JaCoCoParser,
        cfg_sync: CfgCoverageSync
    ):
        self.modul_repo = modul_repo
        self.test_case_repo = test_case_repo
        self.penyelesaian_repo = penyelesaian_repo
        self.system_repo = system_repo
        self.cfg_repo = cfg_repo
        self.file_manager = file_manager
        self.gradle_executor = gradle_executor
        self.test_code_gen = test_code_gen
        self.junit_parser = junit_parser
        self.jacoco_parser = jacoco_parser
        self.cfg_sync = cfg_sync

    def run_test(self, id_topik_modul: str, student_id: str) -> dict:
        """
        Orkestrasi eksekusi test case mahasiswa: Setup -> CodeGen -> Gradle -> Parse -> CFG Sync -> Save.
        """
        # Ambil data Modul & Test Case
        modul_data = self.modul_repo.find_detail_by_topik_modul(id_topik_modul)
        if not modul_data:
            raise ValueError("Data modul tidak ditemukan")
            
        id_modul = modul_data['ms_id_modul']
        test_cases = self.test_case_repo.find_by_topik_and_student(id_topik_modul, student_id)
        if not test_cases:
            raise ValueError("Tidak ada test case yang bisa dieksekusi")

        # Setup Workspace (Infrastructure)
        workspace_path = f"engine-testing/{student_id}/{id_topik_modul}"
        source_file_path = f"modules/{id_modul}/{modul_data['ms_source_code']}"
        
        try:
            test_dir = self.file_manager.setup_test_workspace(
                workspace_path, source_file_path, modul_data['ms_source_code']
            )
            
            # Generate Java JUnit Class (Infrastructure)
            self.test_code_gen.generate_junit_class(
                class_name=modul_data['ms_class_name'],
                function_name=modul_data['ms_function_name'],
                return_type=modul_data['ms_return_type'],
                test_cases=test_cases,
                output_path=test_dir
            )
            
            # Eksekusi Gradle 
            is_build_success = self.gradle_executor.run_tests(workspace_path)
            status_eksekusi = 'Y' if is_build_success else 'N'
            
            # Salin Report ke Static 
            self.file_manager.copy_reports_to_static(workspace_path, student_id, id_topik_modul)
            report_test_url = f"static/{student_id}/{id_topik_modul}/report_test/index.html"
            
            # Simpan Status Awal Penyelesaian
            self.penyelesaian_repo.upsert_execution_status(
                id_topik_modul, student_id, status_eksekusi, report_test_url
            )

            if not is_build_success:
                self.penyelesaian_repo.update_coverage_and_score(
                    id_topik_modul, student_id, coverage=0, nilai=0, status_penyelesaian='N'
                )
                return {"status_eksekusi": False, "tgl_eksekusi": datetime.now().strftime('%d %B %Y, %H:%M:%S')}

            # Parse Hasil JUnit & Update Status Test Case (Infrastructure & Repo)
            junit_xml = f"static/{student_id}/{id_topik_modul}/test-results/TEST-{modul_data['ms_class_name']}Test.xml"
            is_all_passed, junit_results = self.junit_parser.parse(junit_xml)
            
            for result in junit_results:
                self.test_case_repo.update_result(
                    id_topik_modul, student_id, result['test_name'], result['status']
                )

            # Parse Hasil JaCoCo Coverage (Infrastructure)
            jacoco_xml = f"static/{student_id}/{id_topik_modul}/jacoco_report_test/jacocoTestReport.xml"
            coverage_percent = self.jacoco_parser.parse_method_coverage(
                jacoco_xml, modul_data['ms_function_name']
            )
            
            # Hitung Nilai (Business Rule)
            nilai = round(coverage_percent * int(modul_data['ms_tingkat_kesulitan']), 0)
            min_coverage = float(self.system_repo.get_minimum_coverage())
            status_penyelesaian = 'Y' if (coverage_percent > min_coverage and is_all_passed) else 'N'
            coverage_report_url = f"static/{student_id}/{id_topik_modul}/jacoco_report_test/html/index.html"

            # Update Coverage ke DB
            self.penyelesaian_repo.update_coverage_and_score(
                id_topik_modul, student_id, coverage_percent, nilai, status_penyelesaian, coverage_report_url
            )

            # CFG Synchronization (Infrastructure) 
            line_statuses = self.jacoco_parser.parse_line_execution_status(jacoco_xml)
            if line_statuses:
                self.cfg_sync.synchronize(id_topik_modul, student_id, id_modul, line_statuses)

            return {
                "modul_id": id_modul,
                "topik_modul_id": id_topik_modul,
                "result_test": is_all_passed,
                "coverage_score": coverage_percent,
                "minimum_coverage_score": min_coverage,
                "point": nilai,
                "status_eksekusi": True,
                "tgl_eksekusi": datetime.now().strftime('%d %B %Y, %H:%M:%S')
            }
        
        

        finally:
            # bersihkan workspace, baik sukses maupun error
            self.file_manager.cleanup_workspace(workspace_path)

    def get_execution_result(self, id_topik_modul: str, student_id: str) -> dict:
        """
        Merakit data hasil pengujian untuk dirender di halaman Visualisasi CFG.
        Menggabungkan data penyelesaian, modul, statistik test case, dan status graph.
        """
        # Get Penyelesaian Data
        data_result = self.penyelesaian_repo.find_by_topik_and_student(id_topik_modul, student_id)
        if not data_result:
            raise ValueError("Data hasil pengujian tidak ada")
            
        # Get Modul Detail
        modul_data = self.modul_repo.find_detail_by_topik_modul(id_topik_modul)
        id_modul = modul_data['ms_id_modul']
        
        # Get Status CFG (Warna Merah/Hijau) dari CfgRepository
        nodes, edges = self.cfg_repo.get_cfg_with_status(id_topik_modul, student_id)
        
        # Get Test Case Statistics dari TestCaseRepository
        tc_stats = self.test_case_repo.get_statistics_by_topik_and_student(id_topik_modul, student_id)
        
        # Minimum Coverage dari SystemConfigRepository
        min_coverage = float(self.system_repo.get_minimum_coverage())

        return {
            "modul_id": id_modul,
            "topik_modul_id": id_topik_modul,
            "status_eksekusi": data_result['tr_status_eksekusi'],
            "coverageScore": data_result['tr_persentase_coverage'],
            "minimum_coverage_score": min_coverage,
            "point": data_result['tr_nilai'],
            "totalTestCase": tc_stats['total'],
            "totalPassTestCase": tc_stats['countPass'],
            "totalFailedTestCase": tc_stats['countFailed'],
            "executionDate": data_result['tr_tgl_eksekusi'].strftime('%d %B %Y, %H:%M:%S'),
            "linkReportTesting": data_result['tr_result_report'],
            "linkReportCoverage": data_result['tr_coverage_report'],
            "linkSourceCoverage": f"static/{student_id}/{id_topik_modul}/jacoco_report_test/html/default/{modul_data['ms_class_name']}.java.html",
            "cfg": {
                "nodes": [dict(n) for n in nodes],
                "edges": [dict(e) for e in edges],
            }
        }