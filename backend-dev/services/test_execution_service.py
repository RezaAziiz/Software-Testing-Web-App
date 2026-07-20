import os
import logging
import time
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
from services.path_analysis_service import PathAnalysisService

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
        self.path_analysis_service = PathAnalysisService()

    def run_test(self, id_topik_modul: str, student_id: str, task_id: str = "") -> dict:
        """
        Orkestrasi eksekusi test case mahasiswa: Setup -> CodeGen -> Gradle -> Parse -> CFG Sync -> Save.
        """
        total_start = time.perf_counter()
        start_time_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        
        logger.info(f"\n[TEST EXECUTION] ==================== START OF EXECUTION ====================")
        logger.info(f"[TEST EXECUTION] Topic Modul ID  : {id_topik_modul}")
        logger.info(f"[TEST EXECUTION] Student ID      : {student_id}")
        logger.info(f"[TEST EXECUTION] Timestamp       : {start_time_str}")
        logger.info(f"[TEST EXECUTION] ------------------------------------------------------------")

        # Step 1: Fetch data Modul & Test Case
        t_start = time.perf_counter()
        modul_data = self.modul_repo.find_detail_by_topik_modul(id_topik_modul)
        if not modul_data:
            logger.error(f"[TEST EXECUTION] [STEP 1 FAILED] Module data not found for Topic: {id_topik_modul}")
            raise ValueError("Data modul tidak ditemukan")
            
        id_modul = modul_data['ms_id_modul']
        test_cases = self.test_case_repo.find_by_topik_and_student(id_topik_modul, student_id)
        if not test_cases:
            logger.warning(f"[TEST EXECUTION] [STEP 1 WARN] No test cases to execute for Topic: {id_topik_modul}, Student: {student_id}")
            raise ValueError("Tidak ada test case yang bisa dieksekusi")
            
        elapsed_1 = time.perf_counter() - t_start
        logger.info(f"[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] [STEP 1/10] Fetch Modul & Test Cases from Database")
        logger.info(f"               -> Found Module: '{modul_data['ms_nama_modul']}' (Class: {modul_data['ms_class_name']})")
        logger.info(f"               -> Found {len(test_cases)} test cases.")
        logger.info(f"               -> Time taken: {elapsed_1:.3f}s")
        logger.info(f"[TEST EXECUTION] ------------------------------------------------------------")

        # Setup Workspace (Infrastructure)
        # Gunakan 8 karakter pertama UUID untuk menghindari batas MAX_PATH Windows (260 char)
        short_student = student_id[:8] if student_id else "anon"
        short_topik = id_topik_modul[:8] if id_topik_modul else "notopik"
        unique_suffix = f"_{task_id[:8]}" if task_id else ""
        
        workspace_path = f"engine-testing/{short_student}/{short_topik}{unique_suffix}"
        source_file_path = f"modules/{id_modul}/{modul_data['ms_source_code']}"
        
        try:
            # Step 2: Setup Workspace
            t_start = time.perf_counter()
            test_dir = self.file_manager.setup_test_workspace(
                workspace_path, source_file_path, modul_data['ms_source_code']
            )
            elapsed_2 = time.perf_counter() - t_start
            logger.info(f"[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] [STEP 2/10] Setup Test Workspace")
            logger.info(f"               -> Path: {workspace_path}")
            logger.info(f"               -> Time taken: {elapsed_2:.3f}s")
            logger.info(f"[TEST EXECUTION] ------------------------------------------------------------")
            
            # Step 3: Generate Java JUnit Class (Infrastructure)
            t_start = time.perf_counter()
            self.test_code_gen.generate_junit_class(
                class_name=modul_data['ms_class_name'],
                function_name=modul_data['ms_function_name'],
                return_type=modul_data['ms_return_type'],
                test_cases=test_cases,
                output_path=test_dir
            )
            elapsed_3 = time.perf_counter() - t_start
            logger.info(f"[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] [STEP 3/10] Generate JUnit Test Class")
            logger.info(f"               -> Class: {modul_data['ms_class_name']}Test.java")
            logger.info(f"               -> Target function: {modul_data['ms_function_name']}")
            logger.info(f"               -> Time taken: {elapsed_3:.3f}s")
            logger.info(f"[TEST EXECUTION] ------------------------------------------------------------")
            
            # Step 4: Eksekusi Gradle
            t_start = time.perf_counter()
            logger.info(f"[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] [STEP 4/10] Executing Gradle Tests (Running Gradle Subprocess)...")
            is_build_success = self.gradle_executor.run_tests(workspace_path)
            status_eksekusi = 'Y' if is_build_success else 'N'
            elapsed_4 = time.perf_counter() - t_start
            logger.info(f"               -> Gradle build successful: {is_build_success}")
            logger.info(f"               -> Time taken: {elapsed_4:.3f}s")
            logger.info(f"[TEST EXECUTION] ------------------------------------------------------------")
            
            # Step 5: Salin Report ke Static
            t_start = time.perf_counter()
            self.file_manager.copy_reports_to_static(workspace_path, student_id, id_topik_modul)
            report_test_url = f"static/{student_id}/{id_topik_modul}/report_test/index.html"
            elapsed_5 = time.perf_counter() - t_start
            logger.info(f"[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] [STEP 5/10] Copy Reports to Static Directory")
            logger.info(f"               -> URL: {report_test_url}")
            logger.info(f"               -> Time taken: {elapsed_5:.3f}s")
            logger.info(f"[TEST EXECUTION] ------------------------------------------------------------")
            
            # Step 6: Simpan Status Awal Penyelesaian
            t_start = time.perf_counter()
            self.penyelesaian_repo.upsert_execution_status(
                id_topik_modul, student_id, status_eksekusi, report_test_url
            )
            elapsed_6 = time.perf_counter() - t_start
            logger.info(f"[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] [STEP 6/10] Upsert Initial Execution Status to DB")
            logger.info(f"               -> Status: {status_eksekusi}")
            logger.info(f"               -> Time taken: {elapsed_6:.3f}s")
            logger.info(f"[TEST EXECUTION] ------------------------------------------------------------")

            if not is_build_success:
                t_start = time.perf_counter()
                self.penyelesaian_repo.update_coverage_and_score(
                    id_topik_modul, student_id, coverage=0, nilai=0, status_penyelesaian='N'
                )
                elapsed_failed = time.perf_counter() - t_start
                logger.warning(f"[TEST EXECUTION] Build failed. Updated score/coverage to 0 in DB (Took {elapsed_failed:.3f}s).")
                
                total_elapsed = time.perf_counter() - total_start
                logger.info(f"[TEST EXECUTION] ==================== END OF EXECUTION (FAILED) ====================")
                logger.info(f"[TEST EXECUTION] TOTAL ELAPSED TIME: {total_elapsed:.3f}s")
                logger.info(f"[TEST EXECUTION] ============================================================")
                
                return {"status_eksekusi": False, "tgl_eksekusi": datetime.now().strftime('%d %B %Y, %H:%M:%S')}

            # Step 7: Parse Hasil JUnit & Update Status Test Case (Infrastructure & Repo)
            t_start = time.perf_counter()
            junit_xml = f"static/{student_id}/{id_topik_modul}/test-results/TEST-{modul_data['ms_class_name']}Test.xml"
            is_all_passed, junit_results = self.junit_parser.parse(junit_xml)
            
            passed_count = 0
            failed_count = 0
            for result in junit_results:
                if result['status'].lower() == 'passed':
                    passed_count += 1
                else:
                    failed_count += 1
                self.test_case_repo.update_result(
                    id_topik_modul, student_id, result['test_name'], result['status']
                )
            elapsed_7 = time.perf_counter() - t_start
            logger.info(f"[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] [STEP 7/10] Parse JUnit XML & Update DB Test Case Results")
            logger.info(f"               -> Total: {len(junit_results)}, Passed: {passed_count}, Failed: {failed_count}")
            logger.info(f"               -> All Passed: {is_all_passed}")
            logger.info(f"               -> Time taken: {elapsed_7:.3f}s")
            logger.info(f"[TEST EXECUTION] ------------------------------------------------------------")

            # Step 8: Parse Hasil JaCoCo Coverage (Infrastructure)
            t_start = time.perf_counter()
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
            elapsed_8 = time.perf_counter() - t_start
            logger.info(f"[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] [STEP 8/10] Parse JaCoCo Coverage & Save Score to DB")
            logger.info(f"               -> Coverage: {coverage_percent:.2f}% (Min target: {min_coverage * 100:.2f}%)")
            logger.info(f"               -> Difficulty score multiplier: {modul_data['ms_tingkat_kesulitan']}")
            logger.info(f"               -> Final Score: {nilai} | Status Penyelesaian: {status_penyelesaian}")
            logger.info(f"               -> Time taken: {elapsed_8:.3f}s")
            logger.info(f"[TEST EXECUTION] ------------------------------------------------------------")

            # Step 9: CFG Synchronization (Infrastructure)
            t_start = time.perf_counter()
            line_statuses = self.jacoco_parser.parse_line_execution_status(jacoco_xml)
            if line_statuses:
                self.cfg_sync.synchronize(id_topik_modul, student_id, id_modul, line_statuses)
            elapsed_9 = time.perf_counter() - t_start
            logger.info(f"[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] [STEP 9/10] CFG Synchronization (AST range & color propagation)")
            logger.info(f"               -> Propagated line coverage to CFG nodes and edges.")
            logger.info(f"               -> Time taken: {elapsed_9:.3f}s")
            logger.info(f"[TEST EXECUTION] ------------------------------------------------------------")

            total_elapsed = time.perf_counter() - total_start
            logger.info(f"[TEST EXECUTION] ==================== END OF EXECUTION (SUCCESS) ====================")
            logger.info(f"[TEST EXECUTION] TOTAL ELAPSED TIME: {total_elapsed:.3f}s")
            logger.info(f"[TEST EXECUTION] ============================================================")

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
            # Step 10: bersihkan workspace di background thread agar tidak menahan response API
            import threading
            cleanup_thread = threading.Thread(
                target=self.file_manager.cleanup_workspace,
                args=(workspace_path,)
            )
            cleanup_thread.daemon = True
            cleanup_thread.start()
            
            logger.info(f"[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] [STEP 10/10] Cleanup Workspace triggered in background thread")
            logger.info(f"[TEST EXECUTION] ============================================================")

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

        # Calculate unexecuted paths using PathAnalysisService
        unexecuted_paths = self.path_analysis_service.build_unexecuted_paths(nodes, edges)
        
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
            "data_cfg": {
                "nodes": [dict(n) for n in nodes],
                "edges": [dict(e) for e in edges],
                "unexecutedPaths": unexecuted_paths,
            }
        }