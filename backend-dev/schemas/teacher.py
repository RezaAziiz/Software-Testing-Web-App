# schemas/teacher.py
from datetime import date
from pydantic import BaseModel, Field
from typing import List, Optional

class TeacherSchema(BaseModel):
    ms_teacher_nip: str = Field(..., min_length=1, max_length=20)
    ms_teacher_name: str = Field(..., min_length=1, max_length=255)
    ms_teacher_birthplace: str = Field(..., min_length=3, max_length=255)
    ms_teacher_address: str = Field(..., min_length=3, max_length=255)
    ms_teacher_phone: str = Field(..., min_length=10, max_length=14)
    ms_teacher_email: str = Field(..., min_length=1, max_length=255)
    ms_teacher_education: str = Field(..., min_length=1, max_length=255)
    ms_teacher_password: str = Field(..., min_length=8, max_length=255)
    # ms_teacher_class_id: Optional[str] = Field(..., min_length=1, max_length=255)

    ms_teacher_profile_picture: str = None
    ms_teacher_current_token: str = None

    ms_teacher_gender: str
    isactive: str
    ms_teacher_group: str

    ms_teacher_birthdate: date

    #load subject name for teacher's subjects 
    ms_teacher_subject_name: str


class Teacher(TeacherSchema):
    ms_teacher_id: int

# list teacher API
class Teachers(BaseModel):
    limit: int = Field(default=5)
    offset: int = Field(default=0)
    data: List[Teacher]

class TeacherProfile(BaseModel):
    ms_teacher_nip: str = Field(..., min_length=1, max_length=20)
    ms_teacher_name: str = Field(..., min_length=1, max_length=255)
    ms_teacher_birthplace: str = Field(..., min_length=3, max_length=255)
    ms_teacher_address: str = Field(..., min_length=3, max_length=255)
    ms_teacher_phone: str = Field(..., min_length=10, max_length=14)
    ms_teacher_email: str = Field(..., min_length=1, max_length=255)
    ms_teacher_education: str = Field(..., min_length=1, max_length=255)
    ms_teacher_password: str = Field(..., min_length=8, max_length=255)

    ms_teacher_profile_picture: str = None
    ms_teacher_current_token: str = None

    ms_teacher_gender: str
    isactive: str
    ms_teacher_group: str

    ms_teacher_birthdate: date

    #load subject name for teacher's subjects 
    ms_teacher_subject_name: str