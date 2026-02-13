# routes/class.py
from schemas.classes import ClassSchema, Classes
from models.classes import Class
from fastapi import APIRouter, Response, status, UploadFile, Depends, Request
from config.database import conn
from datetime import date
from middleware.auth_bearer import JWTBearer
from utilities.utils import get_hashed_password, getDataFromJwt
from utilities.excelutil import create_excel_data
from utilities.pdfutil import create_pdf_data
from utilities.imageutil import resize, getResolution
from fastapi.responses import FileResponse
import os
import math
from sqlalchemy.sql import text
import base64
import magic
import shutil
import uuid

classes = APIRouter()

@classes.get('/class/all', dependencies=[Depends(JWTBearer())], response_model=Classes,
          description="Menampilkan semua data")
async def find_all_class(limit: int = 10, offset: int = 0):
    query = Class.select().offset(offset).limit(limit)
    data = conn.execute(query).fetchall()
    response = {"limit": limit, "offset": offset, "data": data}
    return response

@classes.get('/class/search', dependencies=[Depends(JWTBearer())],
          description="Searching data kelas")
async def search_kelas(limit: int = 10, offset: int = 0, page: int = 1, classInfo: str = None, teacherInfo: str = None):
    if classInfo is not None:
        classInfo = "%"+classInfo+"%"
    else:
        classInfo = "%"
    
    if teacherInfo is not None:
        teacherInfo = "%"+teacherInfo+"%"
    else:
        teacherInfo = "%"

    offset = (page - 1) * limit
    base_query = "CREATE OR REPLACE VIEW get_ms_class AS "
    base_query += "SELECT "
    base_query += "T.ms_teacher_name, "
    base_query += "C.* "
    base_query += "FROM ms_class C "
    base_query += "JOIN ms_teacher T "
    base_query += "ON C.ms_class_teacher = T.ms_teacher_id "
    query_text = text(base_query)

    create_view = conn.execute(query_text)

    base_query = "SELECT "
    base_query += "* "
    base_query += "FROM get_ms_class "
    base_query += "WHERE "
    base_query += "ms_class_grade LIKE :classInfo AND "
    base_query += "ms_class_teacher LIKE :teacherInfo "
    query_text = text(base_query)

    all_data = conn.execute(query_text, classInfo=classInfo, teacherInfo=teacherInfo).fetchall()

    query_text = text(base_query +
                      "limit :l offset :o")
    data = conn.execute(query_text, classInfo=classInfo, teacherInfo=teacherInfo, l=limit, o=offset).fetchall()
    max_page = math.ceil(len(all_data)/limit)
    
    response = {"limit": limit, "offset": offset, "data": data,
                "page": page, "total_data": len(all_data), "max_page": max_page}
    return response

@classes.get('/class/{id}', dependencies=[Depends(JWTBearer())],
          description="Menampilkan detail data kelas")
async def find_class(id: str, response: Response):
    query = Class.select().where(Class.c.ms_class_id == id)

    data = conn.execute(query).fetchone()
    if data is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "data tidak ditemukan", "status": response.status_code}

    response = {"message": f"sukses mengambil data dengan id {id}", "data": data}
    return response

@classes.post('/class', dependencies=[Depends(JWTBearer())],
           description="Menambah data class")
async def insert_class(request: Request, pgw: ClassSchema, response: Response):
    currentUser = getDataFromJwt(request)

    # cek duplicate
    cek_duplicate_data = Class.select().filter(Class.c.ms_class_grade == pgw.ms_class_grade) \
        .filter(Class.c.ms_class_major == pgw.ms_class_major) \
        .filter(Class.c.ms_class_class == pgw.ms_class_class)
    cek_duplicate_data = conn.execute(cek_duplicate_data).fetchone()
    if cek_duplicate_data is not None:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"status": response.status_code, "message": "duplicate data, kelas is already exist"}

    query = Class.insert().values(
        ms_class_id             = str(uuid.uuid4()),
        ms_class_grade          = pgw.ms_class_grade,
        ms_class_major          = pgw.ms_class_major,
        ms_class_class          = pgw.ms_class_class,
        ms_class_teacher        = pgw.ms_class_teacher,
        ms_class_description    = pgw.ms_class_description,
        ms_class_total_hour     = pgw.ms_class_total_hour,        
        updated                 = date.today(),
        created                 = date.today(),
        updatedby               = currentUser['userid'],
        createdby               = currentUser['userid']
    )
    # print(query)
    conn.execute(query)
    data = Class.select().order_by(Class.c.ms_class_id.desc())
    response = {"message": f"Data Successfully Saved",
                "data": conn.execute(data).fetchone()}
    return response

@classes.put('/class/{id}', dependencies=[Depends(JWTBearer())],
          description="Mengubah data kelas")
async def update_class(request: Request, id: str, pgw: ClassSchema, response: Response):
    currentUser = getDataFromJwt(request)

    # cek userGroup
    if currentUser["group"] != "Admin":
        response.status_code = status.HTTP_403_FORBIDDEN
        return {"status": response.status_code}

    prev_data = Class.select().filter(Class.c.ms_class_id == id)
    prev_data = conn.execute(prev_data).fetchone()
    query = Class.update().values(
        ms_class_grade          = pgw.ms_class_grade,
        ms_class_major          = pgw.ms_class_major,
        ms_class_class          = pgw.ms_class_class,
        ms_class_teacher        = pgw.ms_class_teacher,
        ms_class_description    = pgw.ms_class_description,
        ms_class_total_hour     = pgw.ms_class_total_hour,
        updated                 = date.today(),
        updatedby               = currentUser['userid'],
    ).where(Class.c.ms_class_id == id)
    
    conn.execute(query)
    data = Class.select().where(Class.c.ms_class_id == id)
    response = {"message": f"sukses mengubah data dengan id {id}",
                "data": conn.execute(data).fetchone()}
    return response

@classes.delete('/class/{id}', dependencies=[Depends(JWTBearer())],
             description="Menghapus data kelas")
async def delete_kelas(id: str, response: Response):

    query = Class.select().where(Class.c.ms_class_id == id)
    data = conn.execute(query).fetchone()
    if data is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "data tidak ditemukan", "status": response.status_code}

    query = Class.delete().where(Class.c.ms_class_id == id)
    conn.execute(query)
    response = {"message": f"sukses menghapus data dengan id {id}"}
    return response