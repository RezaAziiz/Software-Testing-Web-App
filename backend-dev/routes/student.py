# routes/student.py
from schemas.student import StudentSchema, Students
from models.student import Student
from models.classes import Class
from fastapi import APIRouter, Response, status, UploadFile, Depends, Request, BackgroundTasks
from config.database import conn
from datetime import date
from middleware.auth_bearer import JWTBearer
from utilities.utils import get_hashed_password, getDataFromJwt
from utilities.excelutil import create_excel_data
from utilities.pdfutil import create_pdf_data
from utilities.imageutil import resize, getResolution
from fastapi.responses import FileResponse
from utilities.frutil import check_face, add_data_training
import os
import math
from sqlalchemy import func, select, bindparam, text
import base64
import magic
import shutil
import uuid
import pandas as pd

from utilities.emailutil import send_email

student = APIRouter()


@student.get('/student/all', dependencies=[Depends(JWTBearer())],
          description="Menampilkan semua data")
async def find_all_student(limit: int = 10, offset: int = 0):
    query = Student.select().offset(offset).limit(limit)
    print(query)
    data = conn.execute(query).fetchall()
    print(data)
    response = {"limit": limit, "offset": offset, "data": data}
    return response


@student.get('/student/search', dependencies=[Depends(JWTBearer())],
          description="Searching data siswa")
async def search_student(limit: int = 10, offset: int = 0, page: int = 1, keyword: str = '%'):
    if keyword is not None:
        keyword = "%"+keyword+"%"
    
    offset = (page - 1) * limit
    base_query = """
        SELECT s.* 
        FROM ms_student s
        WHERE ( s.ms_student_nim LIKE :keyword or
                s.ms_student_name LIKE :keyword or
                s.ms_student_kelas LIKE :keyword or
                s.ms_student_prodi LIKE :keyword )
        ORDER BY ms_student_nim
    """
    query_text = text(base_query)
    
    all_data = conn.execute(query_text, keyword=keyword).fetchall()

    query_text = text(base_query +
                      "limit :l offset :o")
    data = conn.execute(query_text, l=limit, o=offset,
                        keyword=keyword).fetchall()
    max_page = math.ceil(len(all_data)/limit)

    response = {"limit": limit, "offset": offset, "data": data,
                "page": page, "total_data": len(all_data), "max_page": max_page}
    return response

@student.post('/student/upload', dependencies=[Depends(JWTBearer())],
          description="upload data siswa")
async def upload_student(request: Request, file: UploadFile, response: Response):
   
    currentUser = getDataFromJwt(request)

    
    # cek user type
    if currentUser["login_type"] != "teacher":
        response.status_code = status.HTTP_403_FORBIDDEN
        return {"status": response.status_code}

    # read excel file to json
    df = pd.read_excel(file.file, dtype={
        "NIM": str,
    })
    # replace NaN column to False
    df = df.fillna(False)    
    data = df.to_dict(orient="records")

    if len(data) == 0:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            "status": response.status_code,
            "message": "Please check your data. No data found."
        }

    # validate null data per row
    for index, d in enumerate(data):

        if d['NIM'] == False :
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {
                "status": response.status_code,
                "message": f"data in row {index+2} not complete, please complete data before upload to system"
            }

        if d['Nama'] == False :
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {
                "status": response.status_code,
                "message": f"data in row {index+2} not complete, please complete data before upload to system"
            }

        if d['Kelas'] == False :
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {
                "status": response.status_code,
                "message": f"data in row {index+2} not complete, please complete data before upload to system"
            }
        
        if d['Prodi'] == False :
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {
                "status": response.status_code,
                "message": f"data in row {index+2} not complete, please complete data before upload to system"
            }
    
        duplicate = df[df.duplicated()]
        if not duplicate.empty :
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {
                "status": response.status_code,
                "message": f"terdapat NIM yang duplicate"
            }
       # insert / update data siswa
    for index, d in enumerate(data):
        query = Student.select().where(Student.c.ms_student_nim == d['NIM'])
        dataCheck = conn.execute(query).fetchone()
        if dataCheck is not None:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {
                "status": response.status_code,
                "message": f"terdapat {d['NIM']} sudah terdaftar"
            }
        
    # insert / update data siswa
    for index, d in enumerate(data):
        query = Student.select().where(Student.c.ms_student_nim == d['NIM'])
        data = conn.execute(query).fetchone()
        if data is None:

            # insert data student
            query = Student.insert().values(
                ms_student_id=str(uuid.uuid4()),
                ms_student_nim=d['NIM'],
                ms_student_name=d['Nama'],
                ms_student_kelas=d['Kelas'],
                ms_student_prodi=d['Prodi'],
                ms_student_password=get_hashed_password('admin123!!'),
                isactive='Y',
                updated=date.today(),
                created=date.today(),
                updatedby=currentUser['userid'],
                createdby=currentUser['userid']
            )

            try :
                conn.execute(query)
                conn.execute(text("COMMIT;"))
            except Exception as e:
                response.status_code = status.HTTP_400_BAD_REQUEST
                return {
                    "status": response.status_code,
                    "message": str(e)
                }

        else:

            # update data student
            query = Student.update().where(Student.c.ms_student_nim == d['NIM']).values(
                ms_student_name=d['Nama'],
                ms_student_kelas=d['Kelas'],
                ms_student_prodi=d['Prodi'],
                updated=date.today(),
                createdby=currentUser['userid']
            )
            try :
                conn.execute(query)
                conn.execute(text("COMMIT;"))
            except Exception as e:
                response.status_code = status.HTTP_400_BAD_REQUEST
                return {
                    "status": response.status_code,
                    "message": str(e)
                }
    
    response.status_code = status.HTTP_200_OK
    return {"status": response.status_code, "message": "upload success"}


@student.get('/student/{id}', dependencies=[Depends(JWTBearer())],
          description="Menampilkan detail data")
async def find_student(id: str, response: Response):
    query = Student.select().where(Student.c.ms_student_id == id)
    data = conn.execute(query).fetchone()
    if data is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "data tidak ditemukan", "status": response.status_code}

    response = {"message": f"sukses mengambil data dengan id {id}", "data": data}
    return response


@student.post('/student/', dependencies=[Depends(JWTBearer())],
           description="Menambah data siswa")
async def insert_student(request: Request, pgw: StudentSchema, response: Response):
    currentUser = getDataFromJwt(request)

    # cek user type
    if currentUser["login_type"] != "teacher":
        response.status_code = status.HTTP_403_FORBIDDEN
        return {"status": response.status_code}

    # cek nim
    cek_duplicate_data = Student.select().filter(Student.c.ms_student_nim == pgw.ms_student_nim)
    cek_duplicate_data = conn.execute(cek_duplicate_data).fetchone()
    if cek_duplicate_data is not None:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"status": response.status_code, "message": "NIM sudah digunakan"}

    query = Student.insert().values(
        ms_student_id=str(uuid.uuid4()),
        ms_student_nim=pgw.ms_student_nim,
        ms_student_name=pgw.ms_student_name,
        ms_student_kelas=pgw.ms_student_kelas,
        ms_student_prodi=pgw.ms_student_prodi,
        ms_student_password=get_hashed_password('admin123!!'),
        isactive='Y',
        updated=date.today(),
        created=date.today(),
        updatedby=currentUser['userid'],
        createdby=currentUser['userid']
    )    
    conn.execute(query)
    conn.execute(text("COMMIT;"))

    response = {"message": f"sukses menambahkan data baru"}
    return response


@student.put('/student/{id}', dependencies=[Depends(JWTBearer())],
          description="mengubah data siswa")
async def update_student(request: Request, id: str, pgw: StudentSchema, response: Response):
    currentUser = getDataFromJwt(request)

     # cek user type
    if currentUser["login_type"] != "teacher":
        response.status_code = status.HTTP_403_FORBIDDEN
        return {"status": response.status_code}

    # cek nim
    cek_duplicate_data = Student.select().filter(Student.c.ms_student_nim ==
                                     pgw.ms_student_nim, Student.c.ms_student_id != id)
    cek_duplicate_data = conn.execute(cek_duplicate_data).fetchone()
    if cek_duplicate_data is not None:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"status": response.status_code, "message": "NIM sudah digunakan"}

    prev_data = Student.select().filter(Student.c.ms_student_id == id)
    prev_data = conn.execute(prev_data).fetchone()
    query = Student.update().values(
        ms_student_nim=pgw.ms_student_nim,
        ms_student_name=pgw.ms_student_name,
        ms_student_kelas=pgw.ms_student_kelas,
        ms_student_prodi=pgw.ms_student_prodi,
        updated=date.today(),
        updatedby=currentUser['userid'],
    ).where(Student.c.ms_student_id == id)
    
    conn.execute(query)
    conn.execute(text("COMMIT;"))
    response = {"message": f"sukses mengubah data dengan id {id}"}
    return response


@student.delete('/student/{id}', dependencies=[Depends(JWTBearer())],
             description="menghapus data siswa")
async def delete_student(id: str, response: Response):

    query = Student.select().where(Student.c.ms_student_id == id)
    data = conn.execute(query).fetchone()
    if data is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "data tidak ditemukan"}

    query = Student.delete().where(Student.c.ms_student_id == id)
    conn.execute(query)
    conn.execute(text("COMMIT;"))
    response = {"message": f"sukses menghapus data dengan nim {data['ms_student_nim']}"}
    return response