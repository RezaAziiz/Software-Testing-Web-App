# schemas/student.py
from datetime import date
from pydantic import BaseModel, Field
from typing import List, Optional


class StudentSchema(BaseModel):
    ms_student_nim: str = Field(..., min_length=1, max_length=20)
    ms_student_name: str = Field(..., min_length=1, max_length=255)
    ms_student_kelas: str = Field(..., min_length=1, max_length=255)
    ms_student_prodi: str = Field(..., min_length=8, max_length=255)
    
class Student(StudentSchema):
    ms_student_id: str

# list student API
class Students(BaseModel):
    limit: int = Field(default=5)
    offset: int = Field(default=0)
    data: List[Student]
