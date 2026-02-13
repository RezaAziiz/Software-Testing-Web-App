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
from utilities.excelutil import create_excel_file

grade = APIRouter()

@grade.get('/grade/search', dependencies=[Depends(JWTBearer())],
          description="Searching grade data siswa")
async def search_student(limit: int = 10, offset: int = 0, page: int = 1, keyword: str = '%', id_topik:str = '%'):
    if keyword is not None:
        keyword = "%"+keyword+"%"
    if id_topik is not None:
        id_topik = "%"+id_topik+"%"
    
    offset = (page - 1) * limit
    print(id_topik)
    if id_topik != "%"+"%" :
        base_query = """
            SELECT viewTable.ms_student_nim,
                viewTable.ms_student_name,
                IFNULL(viewTable.JmlModulSelesai,0) as JmlModulSelesai,
                IFNULL(viewTable.jmlPoint,0) as JmlPoint,
                IFNULL(viewTable.lastModulName,'-') as lastModulName
                FROM (
                SELECT s.ms_student_nim, 
                    s.ms_student_name,
                    IFNULL(tm.ms_id_topik,"") AS id_topik,
                        SUM(case when pm.tr_status_penyelesaian = 'Y' then 1 else 0 end) as JmlModulSelesai,
                        SUM(pm.tr_nilai) AS jmlPoint,
                        (SELECT m.ms_nama_modul 
                            FROM tr_penyelesaian_modul pm1
                            INNER JOIN ms_topik_modul tm1 ON pm1.tr_id_topik_modul = tm1.ms_id_topik_modul
                            INNER JOIN ms_modul_program m ON m.ms_id_modul = tm1.ms_id_modul
                            WHERE pm1.tr_tgl_eksekusi = max(pm.tr_tgl_eksekusi)
                            AND pm1.tr_student_id = s.ms_student_id) AS lastModulName 
                from ms_student s 
                LEFT JOIN tr_penyelesaian_modul pm ON pm.tr_student_id = s.ms_student_id
                LEFT JOIN ms_topik_modul tm ON tm.ms_id_topik_modul = pm.tr_id_topik_modul 
                GROUP BY s.ms_student_id,
                        s.ms_student_nim,
                        s.ms_student_name,
                        tm.ms_id_topik) AS viewTable
                WHERE (viewTable.lastModulName LIKE :keyword OR
                    viewTable.ms_student_nim LIKE :keyword OR
                    viewTable.ms_student_name LIKE :keyword)
                        AND viewTable.id_topik LIKE :idTopik
                ORDER BY viewTable.ms_student_nim
        """
    else :
        base_query = """
            SELECT  viewTable.ms_student_nim,
                    viewTable.ms_student_name,
                    IFNULL(viewTable.JmlModulSelesai,0) as JmlModulSelesai,
                    IFNULL(viewTable.jmlPoint,0) as JmlPoint,
                    viewTable.lastModulName
                FROM (
                SELECT 
                    s.ms_student_id,
                    s.ms_student_nim, 
                    s.ms_student_name,
                    SUM(case when pm.tr_status_penyelesaian = 'Y' then 1 else 0 end) as JmlModulSelesai,
                    SUM(pm.tr_nilai) AS jmlPoint,
                    IFNULL((SELECT m.ms_nama_modul
                                FROM tr_test_case_modul tcm 
                                        INNER JOIN ms_topik_modul tm ON tcm.tr_id_topik_modul = tm.ms_id_topik_modul
                                        INNER JOIN ms_modul_program m ON m.ms_id_modul = tm.ms_id_modul
                                WHERE tcm.tr_student_id = s.ms_student_id
                                ORDER BY tcm.updated DESC LIMIT 1), '-') AS lastModulName
                from ms_student s 
                LEFT JOIN tr_penyelesaian_modul pm ON pm.tr_student_id = s.ms_student_id
                GROUP BY s.ms_student_id,
                        s.ms_student_nim,
                        s.ms_student_name) AS viewTable
                WHERE (viewTable.lastModulName LIKE :keyword OR
                    viewTable.ms_student_nim LIKE :keyword OR
                    viewTable.ms_student_name LIKE :keyword)
                ORDER BY viewTable.ms_student_nim
        """
    query_text = text(base_query)
    
    all_data = conn.execute(query_text, keyword=keyword, idTopik=id_topik).fetchall()

    query_text = text(base_query +
                      "limit :l offset :o")
    data = conn.execute(query_text, l=limit, o=offset,
                        keyword=keyword, idTopik=id_topik).fetchall()
    max_page = math.ceil(len(all_data)/limit)

    response = {"limit": limit, "offset": offset, "data": data,
                "page": page, "total_data": len(all_data), "max_page": max_page}
    return response


@grade.get('/grade/download', dependencies=[Depends(JWTBearer())],
          description="Download data siswa")
async def download_student(limit: int = 10, offset: int = 0, page: int = 1, keyword: str = '%', id_topik:str = '%'):

    # total data siswa
    query = func.count(Student.c.ms_student_id)
    total = conn.execute(query).fetchone()[0]
    limit = int(total)

    data = await search_student(limit, offset, page, keyword, id_topik)
    data = data["data"] 
    
    if len(data) == 0:
        response.status_code = status.HTTP_204_NO_CONTENT
        return {"status": response.status_code, "message": "No data found"}

    # create excel file
    file_name = "Data Grade"
    workbook = create_excel_file(file_name)
    worksheet = workbook.add_worksheet()

    # start column and row
    col = 0
    row = 0

    # set header
    text_format = workbook.add_format({'num_format': '@'})
    worksheet.write_string(row, col, 'NIM', text_format)
    worksheet.set_column(row, col, 16.82)
    worksheet.write(row, col+1, 'Nama')
    worksheet.set_column(row, col+1, 23.73)
    worksheet.write(row, col+2, 'Jumlah Modul Selesai')
    worksheet.set_column(row, col+2, 34.18)
    worksheet.write(row, col+3, 'Jumlah Point')
    worksheet.set_column(row, col+3, 17)
    worksheet.write(row, col+4, 'Modul Terakhir')
    worksheet.set_column(row, col+4, 20.55)
    
    row+=1
    # set data
    for index in range(len(data)):
        # field NIM
        if data[index]['ms_student_nim'] is not None:
            ms_student_sin = data[index]['ms_student_nim']
            worksheet.write_string(row, col, ms_student_sin)
        # field Nama
        if data[index]['ms_student_name'] is not None:
            ms_student_name = data[index]['ms_student_name']
            worksheet.write(row, col+1, ms_student_name)
        # field Jumlah Modul Selesai
        if data[index]['JmlModulSelesai'] is not None:
            jmlModulSelesai = data[index]['JmlModulSelesai']
            worksheet.write(row, col+2, jmlModulSelesai)
        # field Jumlah Point
        if data[index]['JmlPoint'] is not None:
            jmlPoint = data[index]['JmlPoint']
            worksheet.write(row, col+3, jmlPoint)
        # field Modul Terakhir
        if data[index]['lastModulName'] is not None:
            lastModulName = data[index]['lastModulName']
            worksheet.write(row, col+4, lastModulName)
        row+=1

    # close excel file
    workbook.close()

    if os.path.exists(f"excel_report/{file_name}.xlsx"):
        headers = {
            'Content-Disposition': f'attachment; filename="{file_name}.xlsx"'}
        return FileResponse(f"excel_report/{file_name}.xlsx", headers=headers)
    else:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        response = {"message": "generate file excel failed"}
        return response
