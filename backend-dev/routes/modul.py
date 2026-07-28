import os
import magic
import logging
from fastapi import APIRouter, Response, status, UploadFile, Depends, Request
from fastapi.responses import FileResponse
from decouple import config

# Middleware & Utilities
from middleware.auth_bearer import JWTBearer
from utilities.utils import getDataFromJwt
from config.database import get_connection

# Schemas
from schemas.modul import (
    TestCaseSchema, TestCaseEditSchema, TestCaseDeleteSchema, 
    ModulSchema, ModulEditSchema, IdModulSchema
)

# Repositories 
from repositories.modul_repository import ModulRepository
from repositories.cfg_repository import CfgRepository
from repositories.test_case_repository import TestCaseRepository
from repositories.penyelesaian_repository import PenyelesaianRepository
from repositories.system_config_repository import SystemConfigRepository

# Infrastructure
from infrastructure.file_storage import FileStorageManager
from infrastructure.test_code_generator import TestCodeGenerator
from infrastructure.parsers.junit_parser import JUnitResultParser
from infrastructure.parsers.jacoco_parser import JaCoCoParser
from infrastructure.cfg_coverage_sync import CfgCoverageSync

# Services
from services.modul_service import ModulService
from services.cfg_service import CFGService
from services.test_case_service import TestCaseService
from services.test_execution_service import TestExecutionService

logger = logging.getLogger(__name__)

modul = APIRouter()

# DEPENDENCY INJECTION FACTORIES
def get_current_user(request: Request, _ = Depends(JWTBearer())):
    return getDataFromJwt(request)
def get_modul_repo(conn = Depends(get_connection)): return ModulRepository(conn)
def get_cfg_repo(conn = Depends(get_connection)): return CfgRepository(conn)
def get_cfg_service(cfg_repo = Depends(get_cfg_repo)): return CFGService(cfg_repo)
def get_file_manager(): return FileStorageManager()
def get_test_code_gen(): return TestCodeGenerator()
def get_junit_parser(): return JUnitResultParser()
def get_jacoco_parser(): return JaCoCoParser()
def get_cfg_sync(cfg_repo = Depends(get_cfg_repo)): return CfgCoverageSync(cfg_repo)
def get_modul_service(
    modul_repo: ModulRepository = Depends(get_modul_repo),
    cfg_service: CFGService = Depends(get_cfg_service),
    file_manager: FileStorageManager = Depends(get_file_manager)
):
    return ModulService(modul_repo, cfg_service, file_manager)
def get_test_case_service(conn = Depends(get_connection)):
    return TestCaseService(TestCaseRepository(conn), ModulRepository(conn))
def get_test_execution_service(
    conn = Depends(get_connection),
    cfg_repo = Depends(get_cfg_repo),
    file_manager: FileStorageManager = Depends(get_file_manager),
    test_code_gen: TestCodeGenerator = Depends(get_test_code_gen),
    junit_parser: JUnitResultParser = Depends(get_junit_parser),
    jacoco_parser: JaCoCoParser = Depends(get_jacoco_parser),
    cfg_sync: CfgCoverageSync = Depends(get_cfg_sync)
):
    return TestExecutionService(
        modul_repo=ModulRepository(conn),
        test_case_repo=TestCaseRepository(conn),
        penyelesaian_repo=PenyelesaianRepository(conn),
        system_repo=SystemConfigRepository(conn),
        cfg_repo=cfg_repo,
        file_manager=file_manager,
        test_code_gen=test_code_gen,
        junit_parser=junit_parser,
        jacoco_parser=jacoco_parser,
        cfg_sync=cfg_sync
    )

@modul.get('/modul/detailByIdTopikModul/{id_topik_modul}', dependencies=[Depends(JWTBearer())])
async def get_modul_detail_by_topik(
    id_topik_modul: str, 
    response: Response, 
    modul_service: ModulService = Depends(get_modul_service)
):
    try:
        data = modul_service.get_detail_by_topik(id_topik_modul)
        return {"message": "Sukses mengambil data", "data": data}
    except ValueError as e:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": str(e)}
    except Exception as e:
        logger.error(f"Error detailByIdTopikModul: {str(e)}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message": str(e)}

@modul.get('/modul/detail/{id_modul}', dependencies=[Depends(JWTBearer())])
async def get_modul_detail(
    id_modul: str, 
    response: Response, 
    modul_service: ModulService = Depends(get_modul_service),
    cfg_service: CFGService = Depends(get_cfg_service)
):
    try:
        data = modul_service.get_detail(id_modul)
        nodes, edges = cfg_service.get_cfg_for_modul(id_modul)
        data['data_cfg'] = {"nodes": nodes, "edges": edges}
        
        return {"message": "Sukses mengambil data", "data": data}
    except ValueError as e:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": str(e)}

@modul.get('/modul/search', dependencies=[Depends(JWTBearer())])
async def search_modul(
    limit: int = 10, 
    offset: int = 0, 
    page: int = 1, 
    keyword: str = None, 
    modul_service: ModulService = Depends(get_modul_service)
):
    return modul_service.search(keyword, limit, offset, page)

@modul.post("/modul/addModul")
async def add_modul(
    data_modul: ModulSchema, 
    response: Response, 
    current_user: dict = Depends(get_current_user), # ✅ JWT via DI
    modul_service: ModulService = Depends(get_modul_service)
):
    try:
        id_modul = modul_service.create(data_modul, current_user['userid'])
        return {"message": "Sukses menambahkan data modul baru", "id_modul": id_modul}
    except ValueError as e:
        response.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        return {"message": str(e)}

@modul.put("/modul/editModul")
async def edit_modul(
    data_modul: ModulEditSchema, 
    response: Response, 
    current_user: dict = Depends(get_current_user),
    modul_service: ModulService = Depends(get_modul_service)
):
    try:
        id_modul = modul_service.update(data_modul, current_user['userid'])
        return {"message": "Sukses mengupdate data modul", "id_modul": id_modul}
    except ValueError as e:
        response.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        return {"message": str(e)}

@modul.delete("/modul/delete")
async def delete_modul(
    param: IdModulSchema, 
    response: Response, 
    current_user: dict = Depends(get_current_user),
    modul_service: ModulService = Depends(get_modul_service)
):
    try:
        modul_service.delete(param.id_modul)
        return {"message": "Sukses delete data modul"}
    except ValueError as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message": str(e)}

@modul.post("/modul/uploadSourceCode/{id_modul}")
async def upload_source_code(
    id_modul: str, 
    source_code: UploadFile, 
    response: Response, 
    current_user: dict = Depends(get_current_user),
    modul_service: ModulService = Depends(get_modul_service)
):
    try:
        if not source_code.filename.lower().endswith('.java'):
            raise ValueError("File harus berekstensi .java. Harap periksa kembali file yang diunggah.")

        result = modul_service.upload_and_process(id_modul, source_code, current_user['userid'])
        return result
    except ValueError as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message": str(e)}
    except Exception as e:
        logger.error(f"Error Upload: {str(e)}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message": "Error saat Upload Data", "error": str(e)}

@modul.post("/modul/parse-metadata")
async def parse_metadata(
    source_code: UploadFile,
    response: Response,
    current_user: dict = Depends(get_current_user),
    modul_service: ModulService = Depends(get_modul_service)
):
    try:
        if not source_code.filename.lower().endswith('.java'):
            raise ValueError("File harus berekstensi .java. Harap periksa kembali file yang diunggah.")

        content = await source_code.read()
        java_code = content.decode('utf-8')
        result = modul_service.parse_metadata(java_code)
        return result
    except ValueError as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message": str(e)}
    except Exception as e:
        logger.error(f"Error parsing metadata: {str(e)}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message": f"Terjadi kesalahan saat memproses file: {str(e)}"}

@modul.get('/modul/cfg/{id_modul}', dependencies=[Depends(JWTBearer())])
async def get_modul_cfg(
    id_modul: str, 
    response: Response, 
    cfg_service: CFGService = Depends(get_cfg_service)
):
    try:
        nodes, edges = cfg_service.get_cfg_for_modul(id_modul)
        if not nodes and not edges:
            response.status_code = status.HTTP_404_NOT_FOUND
            return {"status": "not_found", "message": "Data CFG belum terbentuk."}
        
        return {"status": "success", "data": {"nodes": nodes, "edges": edges}}
    except Exception as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"status": "error", "message": str(e)}

@modul.post("/modul/addTestCase")
async def add_testcase(
    data_test: TestCaseSchema, 
    response: Response, 
    current_user: dict = Depends(get_current_user),
    test_case_service: TestCaseService = Depends(get_test_case_service)
):
    try:
        test_case_service.create(data_test, current_user['userid'])
        return {"message": "Sukses menambahkan data test case baru"}
    except ValueError as e:
        response.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        return {"message": str(e)}

@modul.put("/modul/editTestCase")
async def edit_testcase(
    data_test: TestCaseEditSchema, 
    response: Response, 
    current_user: dict = Depends(get_current_user),
    test_case_service: TestCaseService = Depends(get_test_case_service)
):
    try:
        test_case_service.update(data_test, current_user['userid'])
        return {"message": "Sukses update data test case"}
    except ValueError as e:
        response.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        return {"message": str(e)}

@modul.delete("/modul/deleteTestCase")
async def delete_testcase(
    test_data: TestCaseDeleteSchema, 
    current_user: dict = Depends(get_current_user),
    test_case_service: TestCaseService = Depends(get_test_case_service)
):
    test_case_service.delete(test_data.id_test_case)
    return {"message": "Sukses delete data test case"}

@modul.get("/modul/TestCase/{id_topik_modul}")
async def get_testcase_list(
    id_topik_modul: str, 
    current_user: dict = Depends(get_current_user),
    test_case_service: TestCaseService = Depends(get_test_case_service)
):
    data = test_case_service.get_by_topik(id_topik_modul, current_user['userid'])
    return {"message": "Sukses", "data": data}

@modul.get("/modul/DetailTestCase/{id_test_case}", dependencies=[Depends(JWTBearer())])
async def get_testcase_detail(
    id_test_case: str, 
    response: Response, 
    test_case_service: TestCaseService = Depends(get_test_case_service)
):
    try:
        data = test_case_service.get_detail(id_test_case)
        return {"message": "Sukses", "data": data}
    except ValueError as e:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": str(e)}

@modul.post('/modul/run/{id_topik_modul}')
def run_testing_app(
    id_topik_modul: str, 
    response: Response, 
    current_user: dict = Depends(get_current_user),
    test_execution_service: TestExecutionService = Depends(get_test_execution_service)
):
    try:
        result_data = test_execution_service.run_test(id_topik_modul, current_user['userid'])
        return result_data
    except Exception as e:
        logger.error(f"Error test execution: {str(e)}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message": f"Terjadi kesalahan saat eksekusi: {str(e)}"}

@modul.get('/modul/getResultTest/{id_topik_modul}')
async def get_result_testing(
    id_topik_modul: str, 
    response: Response, 
    current_user: dict = Depends(get_current_user),
    test_execution_service: TestExecutionService = Depends(get_test_execution_service)
):
    try:
        result_data = test_execution_service.get_execution_result(id_topik_modul, current_user['userid'])
        return result_data
    except ValueError as e:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": str(e)}
    except Exception as e:
        logger.error(f"Error getting test results: {str(e)}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message": "Terjadi kesalahan pada server"}

@modul.get("/modul/downloadSourceCode/{id_modul}/{filename}", dependencies=[Depends(JWTBearer())])
async def download_source_code(
    id_modul: str, 
    filename: str, 
    response: Response,
    modul_service: ModulService = Depends(get_modul_service)
):
    try:
        file_path = modul_service.get_download_file_path(id_modul, filename)
        mime = magic.Magic(mime=True)
        return FileResponse(path=file_path, filename=filename, media_type=mime.from_file(file_path))
    except ValueError as e:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": str(e)}

@modul.get("/modul/getSourceCodeText/{id_modul}", dependencies=[Depends(JWTBearer())])
async def get_source_code_text(
    id_modul: str, 
    response: Response, 
    modul_service: ModulService = Depends(get_modul_service)
):
    try:
        code_text = modul_service.get_source_code_text(id_modul)
        return {"data": code_text}
    except ValueError as e:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": str(e)}