# schemas/student.py
from datetime import date
from pydantic import BaseModel, Field
from typing import List, Optional

class TestCaseObject(BaseModel):
    param_name: str = Field(..., min_length=1, max_length=255)
    param_type: str = Field(..., min_length=1, max_length=255)
    param_value:  str = Field(..., min_length=1)

class ParameterObject(BaseModel):
    param_name: str = Field(..., min_length=1)
    param_type: str = Field(..., min_length=1)
    param_rules:  str = Field(..., min_length=1)

class TestCaseSchema(BaseModel):
    id_topik_modul: str = Field(..., min_length=1, max_length=255)
    no: str = Field(..., min_length=1, max_length=2)
    object_pengujian: str = Field(..., min_length=1, max_length=255)
    data_test_input: List[TestCaseObject]
    expected_result: str = Field(..., min_length=1, max_length=255)

class TestCaseEditSchema(BaseModel):
    id_test_case: str = Field(..., min_length=1, max_length=255)
    id_topik_modul: str = Field(..., min_length=1, max_length=255)
    no: str = Field(..., min_length=1, max_length=2)
    object_pengujian: str = Field(..., min_length=1, max_length=255)
    data_test_input: List[TestCaseObject]
    expected_result: str = Field(..., min_length=1, max_length=255)

class TestCaseDeleteSchema(BaseModel):
    id_test_case: str = Field(..., min_length=1, max_length=255)

class ModulSchema(BaseModel):
    nama_modul: str = Field(..., min_length=1, max_length=255)
    deskripsi_modul: str = Field(..., min_length=1)
    jenis_modul: str = Field(..., min_length=1, max_length=1)
    jumlah_param: int
    class_name: str = Field(..., min_length=1, max_length=255)
    function_name: str = Field(..., min_length=1, max_length=255)
    return_type: str = Field(..., min_length=0, max_length=255)
    parameters: List[ParameterObject]
    tingkat_kesulitan: str = Field(..., min_length=1, max_length=1)

class ModulEditSchema(BaseModel):
    id_modul: str = Field(..., min_length=1, max_length=255)
    nama_modul: str = Field(..., min_length=1, max_length=255)
    deskripsi_modul: str = Field(..., min_length=1)
    jenis_modul: str = Field(..., min_length=1, max_length=1)
    jumlah_param: int
    class_name: str = Field(..., min_length=1, max_length=255)
    function_name: str = Field(..., min_length=1, max_length=255)
    return_type: str = Field(..., min_length=0, max_length=255)
    parameters: List[ParameterObject]
    tingkat_kesulitan: str = Field(..., min_length=1, max_length=1)

class IdModulSchema(BaseModel):
    id_modul: str = Field(..., min_length=1, max_length=255)
    