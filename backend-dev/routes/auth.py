# routes/auth.py
from schemas.auth import LoginSchema, ChangePasswordSchema, ForgotPasswordSchema, UpdatePasswordSchema, ResetPasswordSchema, VerifyTokenSchema, VerifyTokenJWTSchema
from models.teacher import Teacher
from models.student import Student
from fastapi import APIRouter, Response, status, Request, Depends
from config.database import conn
from utilities.utils import verify_password, encode_jwt, decode_jwt, getDataFromJwt, get_hashed_password, generateToken
from utilities.emailutil import send_email
from middleware.auth_bearer import JWTBearer
from datetime import datetime, timedelta

auth = APIRouter()


@auth.post('/login',
           description="Login api")
async def login(pgw: LoginSchema, response: Response):

    cek_teacher = Teacher.select().filter(Teacher.c.ms_teacher_kode_dosen == pgw.nis_or_nip)
    cek_teacher = conn.execute(cek_teacher).fetchone()
 
    cek_student = Student.select().filter(Student.c.ms_student_nim == pgw.nis_or_nip)
    cek_student = conn.execute(cek_student).fetchone()

    if cek_teacher is None and cek_student is None:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"status": response.status_code, "message": "Incorrect NIP/NIM, please try again!"}

    loginAsStudent = cek_teacher is None
    
    if loginAsStudent:
        verifyPass = verify_password(
            pgw.password, cek_student.ms_student_password)
    else:
        verifyPass = verify_password(
            pgw.password, cek_teacher.ms_teacher_password)
        
    if verifyPass is False:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"status": response.status_code, "message": "Incorrect password, please try again!"}

    if loginAsStudent:
        if cek_student.isactive != 'Y':
            response.status_code = status.HTTP_403_FORBIDDEN
            return {"status": response.status_code, "message": "Account is disabled!"}
    else :
        if cek_teacher.isactive != 'Y':
            response.status_code = status.HTTP_403_FORBIDDEN
            return {"status": response.status_code, "message": "Account is disabled!"}
    
    # generate jwt token
    if loginAsStudent:
        to_encode = {
            "userid": cek_student.ms_student_id,
            "name": cek_student.ms_student_name,
            "nim": cek_student.ms_student_nim,
            "login_type": "student"
        }
    else :
        to_encode = {
            "userid": cek_teacher.ms_teacher_id,
            "name": cek_teacher.ms_teacher_name,
            "kode_dosen": cek_teacher.ms_teacher_kode_dosen,
            "login_type": "teacher"
        }
    token = encode_jwt(to_encode)

    if loginAsStudent:
        query = Student.update().values(
            ms_student_current_token = token
        ).where(Student.c.ms_student_id == cek_student.ms_student_id)
    else:
        query = Teacher.update().values(
            ms_teacher_current_token = token
        ).where(Teacher.c.ms_teacher_id == cek_teacher.ms_teacher_id)
    
    if loginAsStudent:
        data = {
            "userid": cek_student.ms_student_id,
            "name": cek_student.ms_student_name,
            "nim": cek_student.ms_student_nim,
            "kelas" : cek_student.ms_student_kelas,
            "token": token,
            "login_type": "student"
        }
    else:
        data = {
            "userid": cek_teacher.ms_teacher_id,
            "name": cek_teacher.ms_teacher_name,
            "kode_dosen": cek_teacher.ms_teacher_kode_dosen,
            "token": token,
            "login_type": "teacher"
        }
    response = {"message": f"Login successful", "data": data}
    return response


# @auth.put('/changePassword', dependencies=[Depends(JWTBearer())],
#           description="mengubah password teacher")
# async def update_user(request: Request, pgw: ChangePasswordSchema, response: Response):
#     currentTeacher = getDataFromJwt(request)

#     cek_teacher = Teacher.select().filter(Teacher.c.ms_teacher_id == currentTeacher["userid"])
#     cek_teacher = conn.execute(cek_teacher).fetchone()
#     if cek_teacher is None:
#         response.status_code = status.HTTP_400_BAD_REQUEST
#         return {"status": response.status_code, "message": "Teacher tidak terdaftar atau password salah"}

#     verifyPass = verify_password(
#         pgw.ms_teacher_old_password, cek_teacher.ms_teacher_password)
#     if verifyPass is False:
#         response.status_code = status.HTTP_400_BAD_REQUEST
#         return {"status": response.status_code, "message": "Teacher tidak terdaftar atau password salah"}

#     if pgw.ms_teacher_password != pgw.ms_teacher_confirm_password:
#         response.status_code = status.HTTP_400_BAD_REQUEST
#         return {"status": response.status_code, "message": "Password dan confirm password tidak sama"}

#     new_password = get_hashed_password(pgw.ms_teacher_password)
#     prev_data = Teacher.select().filter(
#         Teacher.c.ms_teacher_id == currentTeacher["userid"])
#     prev_data = conn.execute(prev_data).fetchone()
#     query = Teacher.update().values(
#         ms_teacher_kode_dosen=prev_data.ms_teacher_kode_dosen,
#         ms_teacher_name=prev_data.ms_teacher_name,
#         ms_teacher_password=new_password,
#         ms_teacher_email=prev_data.ms_teacher_email,
#         updated=datetime.today(),
#         created=prev_data.created,
#         updatedby=currentTeacher['userid'],
#         createdby=prev_data.createdby
#     ).where(Teacher.c.ms_teacher_id == currentTeacher['userid'])
#     conn.execute(query)
#     data = Teacher.select().where(Teacher.c.ms_teacher_id == currentTeacher['userid'])
#     response = {"message": f"Sukses mengubah password dengan id {currentTeacher['userid']}", "data": conn.execute(
#         data).fetchone()}
#     return response


# @auth.put('/forgotPassword',
#           description="mengubah password via forgot password")
# async def update_user(request: Request, pgw: UpdatePasswordSchema, response: Response):
#     cek_teacher = Teacher.select().filter(Teacher.c.ms_teacher_email == pgw.ms_teacher_email,
#                                     Teacher.c.ms_teacher_token == pgw.ms_teacher_token)
#     cek_teacher = conn.execute(cek_teacher).fetchone()
#     if cek_teacher is None:
#         response.status_code = status.HTTP_400_BAD_REQUEST
#         return {"status": response.status_code, "message": "OTP code is not valid"}

#     if pgw.ms_teacher_password != pgw.ms_teacher_confirm_password:
#         response.status_code = status.HTTP_400_BAD_REQUEST
#         return {"status": response.status_code, "message": "Confirm New Password must be matched with New Password"}

#     new_password = get_hashed_password(pgw.ms_teacher_password)
#     query = Teacher.update().values(
#         ms_teacher_password=new_password,
#         ms_teacher_token=None,
#         updated=datetime.today(),
#     ).where(Teacher.c.ms_teacher_id == cek_teacher.ms_teacher_id)
#     conn.execute(query)
#     data = Teacher.select().where(Teacher.c.ms_teacher_id == cek_teacher.ms_teacher_id)
#     response = {"message": f"Sukses mengubah password dengan id {cek_teacher.ms_teacher_id}",
#                 "data": conn.execute(data).fetchone()}
#     return response


# @auth.post('/forgotPassword', description="forgot password teacher")
# async def forgot_password_user(request: Request, pgw: ForgotPasswordSchema, response: Response):

#     cek_teacher = Teacher.select().filter(Teacher.c.ms_teacher_email == pgw.ms_teacher_email)
#     cek_teacher = conn.execute(cek_teacher).fetchone()

#     if cek_teacher.isactive != 'Y':
#         response.status_code = status.HTTP_403_FORBIDDEN
#         return {"status": response.status_code, "message": "Account is disabled!"}

#     if cek_teacher is None:
#         response.status_code = status.HTTP_400_BAD_REQUEST
#         return {"status": response.status_code, "message": "Token has been sent to your email"}
    
#     token = generateToken()
#     # send_email("Forgot Password",
#     #            f"Berikut token untuk mengganti password : {token}", pgw.ms_teacher_email)

#     expire_token = datetime.now() + timedelta(minutes = 2)
#     send_email("Reset Password",
#         f"""
#         <html>
#             <body>
#                 <img src="cid:image-logo" style="display: inline-block;">
#                 <h1 style="font-family: nunito; color: rgb(255, 178, 82); font-weight: 900; display: inline-block;">
#                     Student Attendance System
#                 </h1>
#                 <br>
#                 <span style="display: block;">
#                     Hi, {cek_teacher.ms_teacher_name}
#                 </span>
#                 <span style="display: block;">
#                     Below is the requested OTP code to reset your password
#                 </span>
#                 <p style="font-family: nunito; font-size: 22px; font-weight: 800; letter-spacing: 6px; display: block;">
#                     {token}
#                 </p>
#                 <span style="display: block;">
#                     This OTP code will expire on <b>{expire_token.strftime("%d %B %Y %H:%M")}</b>
#                 </span>
#                 <span style="display: block;">
#                     Thanks and best regards
#                 </span>
#             </body>
#         </html>
#         """, pgw.ms_teacher_email)
    
#     query = Teacher.update().values(
#         ms_teacher_token=token,
#         updated=datetime.today(),
#     ).where(Teacher.c.ms_teacher_id == cek_teacher.ms_teacher_id)
#     conn.execute(query)

#     response = {"message": "Token sudah dikirimkan ke email"}
#     return response

# @auth.post('/verifyToken', description="forgot password teacher")
# async def verify_token(request: Request, body: VerifyTokenSchema, response: Response):

#     cek_teacher = Teacher.select().filter(Teacher.c.ms_teacher_email == body.ms_teacher_email, 
#                                     Teacher.c.ms_teacher_token == body.ms_teacher_token)

#     cek_teacher = conn.execute(cek_teacher).fetchone()

#     if cek_teacher.isactive != 'Y':
#         response.status_code = status.HTTP_403_FORBIDDEN
#         return {"status": response.status_code, "message": "Account is disabled!"}

#     if cek_teacher is None:
#         response.status_code = status.HTTP_400_BAD_REQUEST
#         return {"status": response.status_code, "message": "OTP code is not valid"}

#     timedif = datetime.today() - cek_teacher.updated
#     if timedif.seconds > 120:
#         response.status_code = status.HTTP_400_BAD_REQUEST
#         return {"status": response.status_code, "message": "OTP code has expired, please request a new OTP code"}

#     response = {"message": "Token valid"}
#     return response

# @auth.put('/resetPassword', dependencies=[Depends(JWTBearer())],
#           description="me-reset password teacher")
# async def reset_user(request: Request, pgw: ResetPasswordSchema, response: Response):
#     currentTeacher = getDataFromJwt(request)

#     teacher = Teacher.select().filter(Teacher.c.ms_teacher_id == currentTeacher["userid"])
#     teacher = conn.execute(teacher).fetchone()
#     if teacher is None:
#         response.status_code = status.HTTP_400_BAD_REQUEST
#         return {"status": response.status_code, "message": "Teacher tidak terdaftar atau password salah"}

#     reset_password_teacher = Teacher.select().filter(Teacher.c.ms_teacher_id == pgw.ms_teacher_id)
#     reset_password_teacher = conn.execute(reset_password_teacher).fetchone()
#     if reset_password_teacher is None:
#         response.status_code = status.HTTP_400_BAD_REQUEST
#         return {"status": response.status_code, "message": "Reset password gagal"}

#     new_password = 'admin123'
#     encrypted_new_password = get_hashed_password(new_password)
#     query = Teacher.update().values(
#         ms_teacher_password=encrypted_new_password,
#         updated=datetime.today(),
#         updatedby=currentTeacher['userid'],
#     ).where(Teacher.c.ms_teacher_id == pgw.ms_teacher_id)

#     send_email("Reset Password",
#                f"Berikut password baru : {new_password}", reset_password_teacher.ms_teacher_email)

#     conn.execute(query)
#     data = Teacher.select().where(Teacher.c.ms_teacher_id == pgw.ms_teacher_id)
#     response = {"message": f"Sukses me-reset password dengan id {pgw.ms_teacher_id}", "data": conn.execute(
#         data).fetchone()}
#     return response


# @auth.get('/verifyTokenJWT', description="verify teacher's token")
# async def verify_token(request: Request, pgw: VerifyTokenJWTSchema, response: Response):

#     # print(body.ms_teacher_current_token)
#     # print(body.ms_teacher_id)

#     # return {pgw}

#     cek_teacher = Teacher.select().filter(Teacher.c.ms_teacher_id == pgw.ms_teacher_id, 
#                                     Teacher.c.ms_teacher_current_token == pgw.ms_teacher_current_token)

#     cek_teacher = conn.execute(cek_teacher).fetchone()

#     print('hello', flush=True)

#     if cek_teacher.isactive != 'Y':
#         response.status_code = status.HTTP_403_FORBIDDEN
#         return {"status": response.status_code, "message": "Account is disabled!"}

#     if cek_teacher is None:
#         response.status_code = status.HTTP_400_BAD_REQUEST
#         return {"status": response.status_code, "message": "JWT Token is not valid"}
    
#     query = Teacher.select().filter(Teacher.c.ms_teacher_id == pgw.ms_teacher_id, Teacher.c.ms_teacher_current_token == pgw.ms_teacher_current_token)

#     data = conn.execute(query).fetchone()

#     response = {"message": "Token valid", "data": data}
#     return response