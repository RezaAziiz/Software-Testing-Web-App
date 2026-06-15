import os
import uuid
import math
from datetime import datetime
from fastapi import UploadFile
from utilities.utils import dataTypeValidation
from schemas.modul import ModulSchema, ModulEditSchema
from repositories.modul_repository import ModulRepository
from services.cfg_service import CFGService
from infrastructure.file_storage import FileStorageManager
from infrastructure.gradle_executor import GradleExecutor

class ModulService:
    def __init__(
        self, 
        modul_repo: ModulRepository, 
        cfg_service: CFGService = None,
        file_manager: FileStorageManager = None,
        gradle_executor: GradleExecutor = None
    ):
        self.modul_repo = modul_repo
        self.cfg_service = cfg_service
        self.file_manager = file_manager
        self.gradle_executor = gradle_executor

    def get_detail(self, id_modul: str) -> dict:
        data_modul = self.modul_repo.find_detail_with_lookup(id_modul)
        if not data_modul:
            raise ValueError(f"Data modul dengan id {id_modul} tidak ditemukan")

        data_param_modul = self.modul_repo.get_parameters(id_modul)
        return {
            "data_modul": data_modul,
            "data_parameter_modul": data_param_modul
        }

    def search(self, keyword: str, limit: int, offset: int, page: int) -> dict:
        search_keyword = f"%{keyword}%" if keyword else "%"
        page = max(1, page)
        offset = (page - 1) * limit

        data, total_data = self.modul_repo.search(search_keyword, limit, offset)
        max_page = math.ceil(total_data / limit) if total_data > 0 else 1

        return {
            "limit": limit,
            "offset": offset,
            "data": data,
            "page": page,
            "total_data": total_data,
            "max_page": max_page
        }

    def create(self, data: ModulSchema, user_id: str) -> str:
        # Duplicate Validation
        existing_modul = self.modul_repo.find_by_name(data.nama_modul)
        if existing_modul:
            raise ValueError(f'Data dengan nama modul "{data.nama_modul}" sudah pernah dibuat sebelumnya')

        # Validation tingkat kesulitan
        val_result = dataTypeValidation("int", data.tingkat_kesulitan, "tingkat kesulitan")
        if not val_result['status']:
            raise ValueError(val_result['message'])

        now = datetime.now()
        id_modul = str(uuid.uuid4())

        # Format Modul Data
        modul_data = {
            "ms_id_modul": id_modul,
            "ms_jenis_modul": data.jenis_modul,
            "ms_nama_modul": data.nama_modul,
            "ms_deskripsi_modul": data.deskripsi_modul,
            "ms_class_name": data.class_name,
            "ms_function_name": data.function_name,
            "ms_return_type": data.return_type,
            "ms_jml_parameter": data.jumlah_param,
            "ms_tingkat_kesulitan": data.tingkat_kesulitan,
            "updated": now,
            "created": now,
            "updatedby": user_id,
            "createdby": user_id
        }
        self.modul_repo.insert(modul_data)

        # Format Parameter Data
        params_data = []
        for index, param in enumerate(data.parameters, start=1):
            params_data.append({
                "ms_id_parameter": str(uuid.uuid4()),
                "ms_id_modul": id_modul,
                "ms_nama_parameter": param.param_name,
                "ms_tipe_data": param.param_type,
                "ms_rules": param.param_rules,
                "no_urut": index,
                "updated": now,
                "created": now,
                "updatedby": user_id,
                "createdby": user_id
            })
        self.modul_repo.insert_parameters(params_data)

        return id_modul

    def update(self, data: ModulEditSchema, user_id: str) -> str:
        now = datetime.now()
        id_modul = data.id_modul

        # Format Updated Modul Data
        modul_data = {
            "ms_jenis_modul": data.jenis_modul,
            "ms_nama_modul": data.nama_modul,
            "ms_deskripsi_modul": data.deskripsi_modul,
            "ms_class_name": data.class_name,
            "ms_function_name": data.function_name,
            "ms_return_type": data.return_type,
            "ms_jml_parameter": data.jumlah_param,
            "ms_tingkat_kesulitan": data.tingkat_kesulitan,
            "updated": now,
            "updatedby": user_id,
        }
        self.modul_repo.update(id_modul, modul_data)

        # Replace Parameters (Delete then Insert)
        self.modul_repo.delete_parameters(id_modul)
        
        params_data = []
        for index, param in enumerate(data.parameters, start=1):
            params_data.append({
                "ms_id_parameter": str(uuid.uuid4()),
                "ms_id_modul": id_modul,
                "ms_nama_parameter": param.param_name,
                "ms_tipe_data": param.param_type,
                "ms_rules": param.param_rules,
                "no_urut": index,
                "updated": now,
                "created": now,
                "updatedby": user_id,
                "createdby": user_id
            })
        self.modul_repo.insert_parameters(params_data)

        return id_modul

    def delete(self, id_modul: str) -> None:
        # Validation check
        is_used = self.modul_repo.check_used_in_topik(id_modul)
        if is_used:
            raise ValueError("Data modul tidak dapat dihapus karena sedang digunakan")
            
        # Delete operation
        self.modul_repo.delete(id_modul)


    def upload_and_process(self, id_modul: str, source_code: UploadFile, user_id: str) -> dict:
        """
        Memproses upload file java, menjalankan compile test via gradle, 
        dan mengenerate CFG jika sukses.
        """
        # Simpan file menggunakan FileStorageManager
        target_file = self.file_manager.save_uploaded_source_code(id_modul, source_code)
        self.modul_repo.update(id_modul, {"ms_source_code": source_code.filename})

        # Cek Compile via Gradle
        workspace = f"engine-testing/{id_modul}"
        self.file_manager.setup_test_workspace(workspace, target_file, source_code.filename)
        is_compile_success = self.gradle_executor.run_tests(workspace)
        
        self.file_manager.copy_reports_to_module(workspace, id_modul)
        self.file_manager.cleanup_workspace(workspace)

        if is_compile_success:
            # Baca file dan generate CFG (File I/O aman di dalam layer Service/Infrastructure)
            with open(target_file, 'r', encoding='utf-8') as f:
                java_code = f.read()
            
            self.cfg_service.delete_cfg_for_modul(id_modul)
            cfg_result = self.cfg_service.generate_cfg_from_java_code(java_code)
            self.cfg_service.save_cfg_to_database(id_modul, cfg_result, java_code, user_id)
            
            return {
                "message": f"Successfully uploaded {source_code.filename}", 
                "location file": source_code.filename, 
                "cfg": {
                    "status": "success", 
                    "nodes_count": cfg_result.total_nodes, 
                    "edges_count": cfg_result.total_edges
                }
            }
        else:
            if os.path.exists(target_file):
                os.remove(target_file)
            raise ValueError("Source code memiliki error (Compile Gagal), silakan perbaiki dan upload ulang.")

    def get_source_code_text(self, id_modul: str) -> str:
        """Mengambil isi file source code menjadi teks"""
        data_modul = self.modul_repo.find_by_id(id_modul)
        
        if not data_modul or not data_modul['ms_source_code']:
            raise ValueError("Data source code tidak ada")
            
        try:
            return self.file_manager.read_source_code_text(id_modul, data_modul['ms_source_code'])
        except FileNotFoundError:
            raise ValueError("File fisik tidak ditemukan pada direktori.")

    def get_detail_by_topik(self, id_topik_modul: str) -> dict:
        """Mengambil detail modul berdasarkan topik dan merakit (assembly) data CFG"""
        # Ambil data dari repository
        data_topik_modul = self.modul_repo.find_detail_by_topik_modul(id_topik_modul)
        if not data_topik_modul:
            raise ValueError("Data tidak ditemukan")
        
        id_modul = data_topik_modul['ms_id_modul']
        detail = self.get_detail(id_modul) # Reuse fungsi get_detail yang sudah ada
        
        nodes, edges = self.cfg_service.get_cfg_for_modul(id_modul)
        
        detail['data_cfg'] = {"nodes": nodes, "edges": edges}
        detail['data_modul'] = dict(detail['data_modul'])
        detail['data_modul']['id_topik_modul'] = id_topik_modul
        detail['data_modul']['id_topik'] = data_topik_modul._mapping.get('ms_id_topik', '') 
        
        return detail

    def get_download_file_path(self, id_modul: str, filename: str) -> str:
        """Memvalidasi dan mengembalikan path absolut untuk file download"""
        file_path = os.path.join("modules", id_modul, filename)
        if not os.path.exists(file_path):
            raise ValueError("File tidak ada")
        return file_path