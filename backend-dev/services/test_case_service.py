import uuid
import json
from datetime import datetime
from utilities.utils import dataTypeValidation
from schemas.modul import TestCaseSchema, TestCaseEditSchema
from repositories.test_case_repository import TestCaseRepository
from repositories.modul_repository import ModulRepository

class TestCaseService:
    def __init__(self, test_case_repo: TestCaseRepository, modul_repo: ModulRepository):
        self.test_case_repo = test_case_repo
        self.modul_repo = modul_repo

    def get_by_topik(self, id_topik_modul: str, student_id: str) -> list:
        return self.test_case_repo.find_by_topik_and_student(id_topik_modul, student_id)

    def get_detail(self, id_test_case: str) -> dict:
        data = self.test_case_repo.find_by_id(id_test_case)
        if not data:
            raise ValueError("Data test case tidak ditemukan")
        return data

    def create(self, data: TestCaseSchema, student_id: str) -> str:
        """Logika untuk menambah Test Case baru"""
        modul_data = self.modul_repo.find_detail_by_topik_modul(data.id_topik_modul)
        if not modul_data:
            raise ValueError("Data modul tidak ditemukan")

        # Validasi Duplikat Object Pengujian
        duplicate = self.test_case_repo.find_duplicate(data.id_topik_modul, data.object_pengujian, student_id)
        if duplicate:
            raise ValueError(f'Data dengan object pengujian "{data.object_pengujian}" sudah ada')

        # Validasi Tipe Data Input Parameter
        data_input = []
        for param in data.data_test_input:
            val_result = dataTypeValidation(param.param_type, param.param_value, param.param_name)
            if not val_result['status']:
                raise ValueError(val_result['message'])
            
            data_input.append({
                "param_name": param.param_name,
                "param_type": param.param_type,
                "param_value": param.param_value,
            })

        # Validasi Tipe Data Expected Result
        val_expected = dataTypeValidation(modul_data['ms_return_type'], data.expected_result, "Ekspektasi")
        if not val_expected['status']:
            raise ValueError(val_expected['message'])

        # Format dan Simpan ke DB
        now = datetime.now()
        test_case_id = str(uuid.uuid4())
        
        insert_data = {
            "tr_id_test_case": test_case_id,
            "tr_id_topik_modul": data.id_topik_modul,
            "tr_student_id": student_id,
            "tr_no": data.no,
            "tr_object_pengujian": data.object_pengujian,
            "tr_data_test_input": json.dumps(data_input),
            "tr_expected_result": data.expected_result,
            # "tr_test_result": "", 
            "updated": now,
            "created": now,
            "updatedby": student_id,
            "createdby": student_id
        }
        
        self.test_case_repo.insert(insert_data)
        return test_case_id

    def update(self, data: TestCaseEditSchema, student_id: str) -> str:
        """Logika untuk mengubah Test Case"""
        
        # Dapatkan return type modul
        modul_data = self.modul_repo.find_detail_by_topik_modul(data.id_topik_modul)
        if not modul_data:
            raise ValueError("Data modul tidak ditemukan")

        # Validasi Duplikat (Kecuali ID test case ini sendiri)
        duplicate = self.test_case_repo.find_duplicate(
            data.id_topik_modul, data.object_pengujian, student_id, exclude_id=data.id_test_case
        )
        if duplicate:
            raise ValueError(f'Data dengan object pengujian "{data.object_pengujian}" sudah ada')

        # Validasi Tipe Data Input
        data_input = []
        for param in data.data_test_input:
            val_result = dataTypeValidation(param.param_type, param.param_value, param.param_name)
            if not val_result['status']:
                raise ValueError(val_result['message'])
            
            data_input.append({
                "param_name": param.param_name,
                "param_type": param.param_type,
                "param_value": param.param_value,
            })

        # Validasi Tipe Data Expected Result
        val_expected = dataTypeValidation(modul_data['ms_return_type'], data.expected_result, "expected result")
        if not val_expected['status']:
            raise ValueError(val_expected['message'])

        # Format Update DB
        now = datetime.now()
        update_data = {
            "tr_no": data.no,
            "tr_object_pengujian": data.object_pengujian,
            "tr_data_test_input": json.dumps(data_input),
            "tr_expected_result": data.expected_result,
            "updated": now,
            "updatedby": student_id,
        }
        
        self.test_case_repo.update(data.id_test_case, update_data)
        return data.id_test_case

    def delete(self, id_test_case: str) -> None:
        """Hapus data test case"""
        self.test_case_repo.delete(id_test_case)