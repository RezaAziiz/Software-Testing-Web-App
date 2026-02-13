# schemas/class.py
from datetime import date
from pydantic import BaseModel, Field
from typing import List

class ClassSchema(BaseModel):
    ms_class_grade: str = Field(..., min_length=1, max_length=10)
    ms_class_major: str = None
    ms_class_class: str = Field(..., min_length=1, max_length=10)
    ms_class_teacher: str = Field(..., min_length=1, max_length=100)
    ms_class_description: str
    ms_class_total_hour: str

class Class(ClassSchema):
    ms_class_id: str

# list pegawai API
class Classes(BaseModel):
    limit: int = Field(default=5)
    offset: int = Field(default=0)
    data: List[Class]