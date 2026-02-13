# schemas/student.py
from datetime import date
from pydantic import BaseModel, Field
from typing import List, Optional

class TopikSchema(BaseModel):
    nama_topik: str = Field(..., min_length=1, max_length=255)
    deskripsi_topik: str = Field(..., min_length=1, max_length=255)

class EditTopikSchema(BaseModel):
    id_topik: str = Field(..., min_length=1, max_length=255)
    nama_topik: str = Field(..., min_length=1, max_length=255)
    deskripsi_topik: str = Field(..., min_length=1, max_length=255)

class IdTopikSchema(BaseModel):
    id_topik: str = Field(..., min_length=1, max_length=255)

class DeleteTopikModulSchema(BaseModel):
    id_topik_modul: str = Field(..., min_length=1, max_length=50)

class ParamModulSchema(BaseModel):
    id_modul: str = Field(..., min_length=1, max_length=255)

class MappingTopikModulSchema(BaseModel):
    id_topik: str = Field(..., min_length=1, max_length=255)
    list_modul: List[ParamModulSchema]