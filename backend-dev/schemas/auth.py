# schemas/user.py
from datetime import date
from pydantic import BaseModel, Field
from typing import List


class LoginSchema(BaseModel):
    nis_or_nip: str = Field(..., min_length=3, max_length=20)
    password: str = Field(..., min_length=1, max_length=255)

class ChangePasswordSchema(BaseModel):
    ms_teacher_old_password: str = Field(..., min_length=1, max_length=255)
    ms_teacher_password: str = Field(..., min_length=1, max_length=255)
    ms_teacher_confirm_password: str = Field(..., min_length=1, max_length=255)

class ResetPasswordSchema(BaseModel):
    ms_teacher_id: str = Field()

class UpdatePasswordSchema(BaseModel):
    ms_teacher_email: str = Field(..., min_length=1, max_length=255)
    ms_teacher_token: str = Field(..., min_length=1, max_length=5)
    ms_teacher_password: str = Field(..., min_length=1, max_length=255)
    ms_teacher_confirm_password: str = Field(..., min_length=1, max_length=255)

class VerifyTokenSchema(BaseModel):
    ms_teacher_email: str = Field(..., min_length=1, max_length=255)
    ms_teacher_token: str = Field(..., min_length=1, max_length=5)

class ForgotPasswordSchema(BaseModel):
    ms_teacher_email: str = Field(..., min_length=1, max_length=255)


class Auth(LoginSchema):
    ms_teacher_id: int

class VerifyTokenJWTSchema(BaseModel):
    ms_teacher_id: int
    ms_teacher_current_token: str = Field(..., min_length=0, max_length=255)
