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
from infrastructure.test_code_generator import TestCodeGenerator
from infrastructure.parsers.junit_parser import JUnitResultParser
from infrastructure.parsers.jacoco_parser import JaCoCoParser
from infrastructure.cfg_coverage_sync import CfgCoverageSync
from services.path_analysis_service import PathAnalysisService
import requests
http_session = requests.Session()
adapter = requests.adapters.HTTPAdapter(pool_connections=100, pool_maxsize=300)
http_session.mount('http://', adapter)
http_session.mount('https://', adapter)

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
        self.test_code_gen = test_code_gen
        self.junit_parser = junit_parser
        self.jacoco_parser = jacoco_parser
        self.cfg_sync = cfg_sync
        self.path_analysis_service = PathAnalysisService()

    def run_test(self, id_topik_modul: str, student_id: str) -> dict:
        """
        Orkestrasi eksekusi test case mahasiswa menggunakan Persistent JVM / Worker Pool.
        """
        import requests
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
        logger.info(f"[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] [STEP 1/6] Fetch Modul & Test Cases from Database")
        logger.info(f"               -> Found Module: '{modul_data['ms_nama_modul']}' (Class: {modul_data['ms_class_name']})")
        logger.info(f"               -> Found {len(test_cases)} test cases.")
        logger.info(f"               -> Time taken: {elapsed_1:.3f}s")
        logger.info(f"[TEST EXECUTION] ------------------------------------------------------------")

        try:
            # Step 2: Prepare Source Code
            t_start = time.perf_counter()
            main_code = self.file_manager.read_source_code_text(id_modul, modul_data['ms_source_code'])

            test_code = self.test_code_gen.generate_junit_class_string(
                class_name=modul_data['ms_class_name'],
                function_name=modul_data['ms_function_name'],
                return_type=modul_data['ms_return_type'],
                test_cases=test_cases
            )
            elapsed_2 = time.perf_counter() - t_start
            logger.info(f"[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] [STEP 2/6] Prepare In-Memory Source Code")
            logger.info(f"               -> Main Class: {modul_data['ms_class_name']}")
            logger.info(f"               -> Test Class: {modul_data['ms_class_name']}Test")
            logger.info(f"               -> Time taken: {elapsed_2:.3f}s")
            logger.info(f"[TEST EXECUTION] ------------------------------------------------------------")
            
            # Step 3: Execute in Java Worker (Persistent JVM)
            t_start = time.perf_counter()
            logger.info(f"[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] [STEP 3/6] Executing Tests via Java Worker API...")
            
            import os
            report_output_dir = os.path.abspath(os.path.join(self.file_manager.base_path, "static", student_id, id_topik_modul, "jacoco_report_test", "html"))
            payload = {
                "mainClassName": modul_data['ms_class_name'],
                "mainCode": main_code,
                "testClassName": f"{modul_data['ms_class_name']}Test",
                "testCode": test_code,
                "reportOutputDir": report_output_dir
            }
            
            from decouple import config
            java_worker_url = config('JAVA_WORKER_URL', default='http://localhost:8081')
            
            t_http = time.perf_counter()
            response = http_session.post(f"{java_worker_url}/execute", json=payload, timeout=60)
            elapsed_http = time.perf_counter() - t_http
            logger.info(f"               -> Java Worker HTTP call: {elapsed_http:.3f}s (response size: {len(response.content)} bytes)")
            
            if response.status_code != 200:
                logger.error(f"Java Worker Error: {response.text}")
                raise RuntimeError("Terjadi kesalahan pada (Java Worker)")
                
            t_parse = time.perf_counter()
            result = response.json()
            
            # --- Logger untuk menampilkan JSON Response ---
            import json
            log_result = result.copy()
            if 'sourceHtmlContent' in log_result:
                log_result['sourceHtmlContent'] = '<HTML CONTENT OMITTED FOR LOGGING>'
            logger.info(f"               -> [JAVA WORKER JSON RESPONSE]:\n{json.dumps(log_result, indent=2)}")
            # ---------------------------------------------
            
            source_html = result.get('sourceHtmlContent')
            if source_html:
                import os
                # Write only the single source HTML file
                source_dir = os.path.join(report_output_dir, "default")
                os.makedirs(source_dir, exist_ok=True)
                html_path = os.path.join(source_dir, f"{modul_data['ms_class_name']}.java.html")
                with open(html_path, 'w', encoding='utf-8') as f:
                    f.write(source_html)
                
                # Ensure jacoco-resources exist (static assets, only copied once)
                resources_dir = os.path.join(report_output_dir, "jacoco-resources")
                if not os.path.exists(resources_dir):
                    bundled_resources = os.path.join(os.path.dirname(os.path.dirname(__file__)), "jacoco-resources")
                    if os.path.exists(bundled_resources):
                        import shutil
                        shutil.copytree(bundled_resources, resources_dir)
            elapsed_parse = time.perf_counter() - t_parse
            logger.info(f"               -> Parse + file write: {elapsed_parse:.3f}s")
                    
            is_build_success = True  # If it reached here, compilation and execution succeeded
            is_all_passed = result.get('isAllPassed', False)
            coverage_percent = round(float(result.get('coveragePercent', 0.0)), 2)
            
            elapsed_3 = time.perf_counter() - t_start
            logger.info(f"               -> Total Tests: {result.get('totalTests')}, Passed: {result.get('passedTests')}, Failed: {result.get('failedTests')}")
            logger.info(f"               -> Coverage: {coverage_percent:.2f}%")
            logger.info(f"               -> Time taken: {elapsed_3:.3f}s (In-Memory)")
            logger.info(f"[TEST EXECUTION] ------------------------------------------------------------")
            
            # Step 4: Simpan Status Awal Penyelesaian
            t_start = time.perf_counter()
            report_test_url = f"#"  # No static HTML report available anymore
            status_eksekusi = 'Y'
            self.penyelesaian_repo.upsert_execution_status(
                id_topik_modul, student_id, status_eksekusi, report_test_url
            )
            elapsed_4 = time.perf_counter() - t_start
            logger.info(f"[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] [STEP 4/6] Upsert Initial Execution Status to DB")
            logger.info(f"               -> Status: {status_eksekusi}")
            logger.info(f"               -> Time taken: {elapsed_4:.3f}s")
            logger.info(f"[TEST EXECUTION] ------------------------------------------------------------")

            # Step 5: Update Status Test Case & Calculate Final Score
            t_start = time.perf_counter()
            # Update Test Cases status. We assume failures have 'testName' like 'pengujian_X'
            failed_tests = [f['testName'].replace("()", "") for f in result.get('failures', [])]
            for tc in test_cases:
                tc_method_name = tc['tr_object_pengujian'].replace(" ", "_")
                tc_status = 'F' if tc_method_name in failed_tests else 'P'
                self.test_case_repo.update_result(id_topik_modul, student_id, tc['tr_object_pengujian'], tc_status)
                
            # Hitung Nilai (Business Rule)
            nilai = round(coverage_percent * int(modul_data['ms_tingkat_kesulitan']), 0)
            min_coverage = float(self.system_repo.get_minimum_coverage())
            status_penyelesaian = 'Y' if (coverage_percent > min_coverage and is_all_passed) else 'N'
            coverage_report_url = f"static/{student_id}/{id_topik_modul}/jacoco_report_test/html/index.html"

            # Update Coverage ke DB
            self.penyelesaian_repo.update_coverage_and_score(
                id_topik_modul, student_id, coverage_percent, nilai, status_penyelesaian, coverage_report_url
            )
            elapsed_5 = time.perf_counter() - t_start
            logger.info(f"[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] [STEP 5/6] Update DB Test Case Results & Score")
            logger.info(f"               -> Final Score: {nilai} | Status Penyelesaian: {status_penyelesaian}")
            logger.info(f"               -> Time taken: {elapsed_5:.3f}s")
            logger.info(f"[TEST EXECUTION] ------------------------------------------------------------")

            # Step 6: CFG Synchronization (Infrastructure)
            t_start = time.perf_counter()
            raw_line_statuses = result.get('lineStatuses', [])
            # Map the raw java worker status to CFG format
            line_statuses = []
            for ls in raw_line_statuses:
                status_code = 'N'
                if ls['status'] == 'FULLY_COVERED': status_code = 'Y'
                elif ls['status'] == 'PARTLY_COVERED': status_code = 'S'
                line_statuses.append({
                    'line_number': ls['line'],
                    'status': status_code
                })
                
            if line_statuses:
                self.cfg_sync.synchronize(id_topik_modul, student_id, id_modul, line_statuses)
            elapsed_6 = time.perf_counter() - t_start
            logger.info(f"[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] [STEP 6/6] CFG Synchronization (AST range & color propagation)")
            logger.info(f"               -> Propagated line coverage to CFG nodes and edges.")
            logger.info(f"               -> Time taken: {elapsed_6:.3f}s")
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
        
        except Exception as e:
            logger.error(f"[TEST EXECUTION] Exception occurred: {e}")
            t_start = time.perf_counter()
            self.penyelesaian_repo.update_coverage_and_score(
                id_topik_modul, student_id, coverage=0, nilai=0, status_penyelesaian='N'
            )
            total_elapsed = time.perf_counter() - total_start
            logger.info(f"[TEST EXECUTION] ==================== END OF EXECUTION (FAILED) ====================")
            logger.info(f"[TEST EXECUTION] TOTAL ELAPSED TIME: {total_elapsed:.3f}s")
            logger.info(f"[TEST EXECUTION] ============================================================")
            return {"status_eksekusi": False, "tgl_eksekusi": datetime.now().strftime('%d %B %Y, %H:%M:%S')}

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
            "coverageScore": round(float(data_result['tr_persentase_coverage']), 2),
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