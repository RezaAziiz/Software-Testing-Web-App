# middleware/auth_bearer.py

from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from utilities.utils import decode_jwt

from models.teacher import Teacher
from models.student import Student
from config.database import conn

class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=403, detail="Invalid authentication scheme.")
            if not self.verify_jwt(credentials.credentials, False):
                raise HTTPException(status_code=403, detail="Invalid token.")
            if not self.verify_jwt(credentials.credentials):
                raise HTTPException(status_code=403, detail="Expired token.")

            # payload = decode_jwt(credentials.credentials)
            
            # isStudent = 'nim' in payload
            # isLoggedIn = False
            # if not isStudent:
            #     print(credentials.credentials)
            #     queryTeacher = Teacher.select() \
            #         .filter(Teacher.c.ms_teacher_id == payload['userid']) \
            #         .filter(Teacher.c.ms_teacher_current_token == credentials.credentials)

            #     queryTeacher = conn.execute(queryTeacher).fetchone()

            #     if queryTeacher:
            #         isLoggedIn = True

            # if isStudent:
            #     queryStudent = Student.select() \
            #         .filter(Student.c.ms_student_id == payload['userid']) \
            #         .filter(Student.c.ms_student_current_token == credentials.credentials)

            #     queryStudent = conn.execute(queryStudent).fetchone()

            #     if queryStudent:
            #         isLoggedIn = True
            
            # if not isLoggedIn:
            #     raise HTTPException(status_code=403, 
            #         detail="Already logged in.",
            #         headers={"X-Already-Logged-In": "?1"},
            #     )

            return credentials.credentials
        else:
            raise HTTPException(status_code=403, detail="Invalid authorization code.")

    def verify_jwt(self, jwtoken: str, expiry_check = True) -> bool:
        isTokenValid: bool = False
        options = {
            'verify_iat': expiry_check,
            'verify_exp': expiry_check,
            'verify_nbf': expiry_check,
        }
        try:
            payload = decode_jwt(jwtoken, options)
        except:
            payload = None
        if payload:
            isTokenValid = True
        return isTokenValid