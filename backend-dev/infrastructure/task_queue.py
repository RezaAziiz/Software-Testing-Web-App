import asyncio
import uuid
import logging
import traceback
from datetime import datetime
from config.database import engine
from repositories.modul_repository import ModulRepository
from repositories.cfg_repository import CfgRepository
from repositories.test_case_repository import TestCaseRepository
from repositories.penyelesaian_repository import PenyelesaianRepository
from repositories.system_config_repository import SystemConfigRepository
from services.test_execution_service import TestExecutionService
from infrastructure.file_storage import FileStorageManager
from infrastructure.gradle_executor import GradleExecutor
from infrastructure.test_code_generator import TestCodeGenerator
from infrastructure.parsers.junit_parser import JUnitResultParser
from infrastructure.parsers.jacoco_parser import JaCoCoParser
from infrastructure.cfg_coverage_sync import CfgCoverageSync
from decouple import config

logger = logging.getLogger("uvicorn.error")

class TaskQueueManager:
    def __init__(self, max_workers: int = 2):
        self.queue = asyncio.Queue()
        self.tasks_status = {}  # Format: { "task_id": {"status": "processing", "result": None, "error": None, "timestamp": ...} }
        self.max_workers = max_workers
        self.workers = []

    async def start(self):
        """Mulai background workers saat aplikasi startup"""
        logger.info(f"Starting {self.max_workers} background workers for Test Execution Queue...")
        for _ in range(self.max_workers):
            worker_task = asyncio.create_task(self._worker_loop())
            self.workers.append(worker_task)

    async def stop(self):
        """Hentikan background workers saat aplikasi shutdown"""
        logger.info("Stopping background workers...")
        for w in self.workers:
            w.cancel()
        await asyncio.gather(*self.workers, return_exceptions=True)

    def enqueue_test(self, id_topik_modul: str, student_id: str) -> str:
        """Masukkan tugas ke antrean dan kembalikan task_id"""
        task_id = str(uuid.uuid4())
        self.tasks_status[task_id] = {
            "status": "processing",
            "result": None,
            "error": None,
            "timestamp": datetime.now().isoformat()
        }
        self.queue.put_nowait({"task_id": task_id, "id_topik_modul": id_topik_modul, "student_id": student_id})
        logger.info(f"[TASK QUEUE] Task {task_id} enqueued for Topic: {id_topik_modul}, Student: {student_id}")
        return task_id

    def get_status(self, task_id: str) -> dict:
        """Cek status tugas"""
        return self.tasks_status.get(task_id, {"status": "not_found", "error": "Task ID tidak ditemukan"})

    async def _worker_loop(self):
        """Looping abadi worker untuk mengambil dan mengeksekusi tugas"""
        while True:
            try:
                task_data = await self.queue.get()
                task_id = task_data["task_id"]
                id_topik_modul = task_data["id_topik_modul"]
                student_id = task_data["student_id"]
                
                logger.info(f"[TASK QUEUE] Worker picked up Task {task_id}")
                
                # Eksekusi synchronous task di thread terpisah agar event loop tidak blocking
                result = await asyncio.to_thread(self._process_test_execution_sync, id_topik_modul, student_id, task_id)
                
                # Simpan hasil
                self.tasks_status[task_id]["status"] = "completed"
                self.tasks_status[task_id]["result"] = result
                
                logger.info(f"[TASK QUEUE] Task {task_id} completed successfully")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"[TASK QUEUE] Error in Task {task_id}: {str(e)}\n{traceback.format_exc()}")
                self.tasks_status[task_id]["status"] = "failed"
                self.tasks_status[task_id]["error"] = str(e)
            finally:
                self.queue.task_done()

    def _process_test_execution_sync(self, id_topik_modul: str, student_id: str, task_id: str):
        """Eksekusi tes dengan koneksi DB mandiri (Synchronous)"""
        connection = engine.connect()
        trans = connection.begin()
        try:
            modul_repo = ModulRepository(connection)
            cfg_repo = CfgRepository(connection)
            test_case_repo = TestCaseRepository(connection)
            penyelesaian_repo = PenyelesaianRepository(connection)
            sys_config_repo = SystemConfigRepository(connection)
            
            file_manager = FileStorageManager()
            gradle_executor = GradleExecutor(config('GRADLE_COMMAND', default='gradle'))
            test_code_gen = TestCodeGenerator()
            junit_parser = JUnitResultParser()
            jacoco_parser = JaCoCoParser()
            cfg_sync = CfgCoverageSync(cfg_repo)
            
            service = TestExecutionService(
                modul_repo=modul_repo,
                test_case_repo=test_case_repo,
                penyelesaian_repo=penyelesaian_repo,
                cfg_repo=cfg_repo,
                system_repo=sys_config_repo,
                file_manager=file_manager,
                gradle_executor=gradle_executor,
                test_code_gen=test_code_gen,
                junit_parser=junit_parser,
                jacoco_parser=jacoco_parser,
                cfg_sync=cfg_sync
            )
            
            result = service.run_test(id_topik_modul, student_id, task_id=task_id)
            trans.commit()
            return result
        except Exception as e:
            trans.rollback()
            raise e
        finally:
            connection.close()

# Singleton instance
task_queue = TaskQueueManager(max_workers=2)
