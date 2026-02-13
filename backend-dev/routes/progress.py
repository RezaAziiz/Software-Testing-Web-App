# routes/progress.py
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

progress = APIRouter()

@progress.get('/progress/search', dependencies=[Depends(JWTBearer())],
          description="Searching progress data siswa")
async def search_progress(limit: int = 10, offset: int = 0, page: int = 1, keyword: str = None, id_topik:str = None):
    if keyword is not None:
        keyword = "%"+keyword+"%"
    else:
        keyword = "%"
    
    offset = (page - 1) * limit
    base_query = """
        SELECT s.ms_student_id,
               s.ms_student_nim,
               s.ms_student_name
        FROM ms_student s
        WHERE ( s.ms_student_nim LIKE :keyword or
                s.ms_student_name LIKE :keyword  )
        ORDER BY ms_student_nim
    """
    query_text = text(base_query)
    
    all_data = conn.execute(query_text, keyword=keyword).fetchall()

    query_text = text(base_query +
                      "limit :l offset :o")
    data = conn.execute(query_text, l=limit, o=offset,
                        keyword=keyword).fetchall()
    max_page = math.ceil(len(all_data)/limit)

    #add data nilai topik
    tempList = []
    for temp in data :
        row_dict = temp._asdict()
        score_query = " SELECT IF(COUNT(view_table.tr_student_id)=COUNT(tm.ms_id_topik_modul),  sum(view_table.tr_nilai), -1) AS score "
        score_query += "  FROM (SELECT * from tr_penyelesaian_modul pm WHERE pm.tr_student_id = '"
        score_query += row_dict["ms_student_id"]
        score_query += "' ) AS view_table "
        score_query += "  RIGHT JOIN ms_topik_modul tm ON view_table.tr_id_topik_modul = tm.ms_id_topik_modul "
        score_query += "      INNER JOIN ms_topik_pengujian tp ON tm.ms_id_topik = tp.ms_id_topik "
        if id_topik is not None and id_topik != "":
            score_query += "    WHERE tp.ms_id_topik = '"
            score_query += id_topik
            score_query += "'   "
        score_query += "     GROUP BY tp.ms_id_topik "
        score_query += " ORDER BY tp.ms_nama_topik ASC "
        score_data = conn.execute(score_query).fetchall()
        row_dict["score"] = score_data
        tempList.append(row_dict)
    response = {"limit": limit, "offset": offset, "data": tempList,
                "page": page, "total_data": len(all_data), "max_page": max_page}
    return response

async def search_list_modul(id_topik:str):
    
    base_query = """
        SELECT tm.ms_id_topik_modul, mp.ms_nama_modul
        FROM ms_topik_modul tm 
        INNER JOIN ms_modul_program mp ON tm.ms_id_modul = mp.ms_id_modul
        WHERE tm.ms_id_topik = :idTopik
        ORDER BY mp.ms_nama_modul asc
    """
    
    query_text = text(base_query)
    
    all_data = conn.execute(query_text, idTopik=id_topik).fetchall()
 
    response = {"data": all_data}
    return response


async def search_detail_progress(limit: int = 10, offset: int = 0, page: int = 1, keyword: str = None, id_topik:str = None):
    if keyword is not None:
        keyword = "%"+keyword+"%"
    else:
        keyword = "%"
    
    offset = (page - 1) * limit
    base_query = """
        SELECT s.ms_student_id,
               s.ms_student_nim,
               s.ms_student_name
        FROM ms_student s
        WHERE ( s.ms_student_nim LIKE :keyword or
                s.ms_student_name LIKE :keyword  )
        ORDER BY ms_student_nim
    """
    query_text = text(base_query)
    
    all_data = conn.execute(query_text, keyword=keyword).fetchall()

    query_text = text(base_query +
                      "limit :l offset :o")
    data = conn.execute(query_text, l=limit, o=offset,
                        keyword=keyword).fetchall()
    max_page = math.ceil(len(all_data)/limit)

    #add data nilai topik
    tempList = []
    for temp in data :
        row_dict = temp._asdict()
        score_query = " SELECT IFNULL(pm.tr_nilai, '-') as score "
        score_query += " FROM ms_topik_modul tm "
        score_query += " INNER JOIN ms_modul_program mp ON tm.ms_id_modul = mp.ms_id_modul "
        score_query += " LEFT JOIN (SELECT * from tr_penyelesaian_modul pm WHERE pm.tr_student_id = '"
        score_query += row_dict["ms_student_id"]
        score_query += "') AS pm ON pm.tr_id_topik_modul = tm.ms_id_topik_modul"
        score_query += " WHERE tm.ms_id_topik = '"
        score_query += id_topik
        score_query += "' "
        score_query += " ORDER BY mp.ms_nama_modul asc "
        score_data = conn.execute(score_query, ).fetchall()
        row_dict["score"] = score_data
        tempList.append(row_dict)
    response = {"limit": limit, "offset": offset, "data": tempList,
                "page": page, "total_data": len(all_data), "max_page": max_page}
    return response


@progress.get('/progress/listTopik', dependencies=[Depends(JWTBearer())],
          description="Searching list data siswa")
async def search_topik(id_topik:str = None):
    
    if id_topik is not None and id_topik != "" :
        base_query = """
            SELECT tp.ms_nama_topik as namaTopik,
                   tp.ms_id_topik as idTopik
            FROM ms_topik_pengujian tp 
            WHERE tp.ms_id_topik = :id_topik
            ORDER BY tp.ms_nama_topik asc
        """
    else :
        base_query = """
            SELECT tp.ms_nama_topik as namaTopik,
                   tp.ms_id_topik as idTopik
            FROM ms_topik_pengujian tp 
            ORDER BY tp.ms_nama_topik asc
        """
    query_text = text(base_query)
    
    all_data = conn.execute(query_text, idTopik=id_topik).fetchall()
 
    response = {"data": all_data}
    return response

def truncate_string(s, max_length):
    return s[:max_length] + "..." if len(s) > max_length else s


@progress.get('/progress/download', dependencies=[Depends(JWTBearer())],
          description="Download data siswa")
async def download_student(limit: int = 10, offset: int = 0, page: int = 1, keyword: str = None, id_topik:str = None):

    # total data siswa
    query = func.count(Student.c.ms_student_id)
    total = conn.execute(query).fetchone()[0]
    limit = int(total)

    data = await search_progress(limit, offset, page, keyword, id_topik)
    data = data["data"] 
    
    dataTopik = await search_topik(id_topik)
    dataTopik = dataTopik["data"] 
    
    if len(data) == 0:
        response.status_code = status.HTTP_204_NO_CONTENT
        return {"status": response.status_code, "message": "No data found"}

    # create excel file
    file_name = "Data Progress"
    workbook = create_excel_file(file_name)
    worksheet = workbook.add_worksheet("Summary")

    # start column and row
    col = 0
    row = 0

    # set header
    text_format = workbook.add_format({'num_format': '@'})
    worksheet.write_string(row, col, 'NIM', text_format)
    worksheet.set_column(row, col, 16.82)
    worksheet.write(row, col+1, 'Nama')
    worksheet.set_column(row, col+1, 23.73)
    for idx, topik in enumerate(dataTopik):
        worksheet.write(row, col+(2+idx), topik["namaTopik"])
        worksheet.set_column(row, col+(2+idx), 35)
    
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
        # field Score
        if data[index]['score'] is not None:
            for idx, score in enumerate(data[index]['score']):
                nilai = score['score']
                if nilai < 0:
                    nilai = "-"
                worksheet.write(row, col+(2+idx), nilai)
        row+=1

    #detai data
    for topik in dataTopik:
        namaTopik = truncate_string(topik["namaTopik"],25)
        worksheetTopik = workbook.add_worksheet(namaTopik)
        #get data
        # print(topik["idTopik"])
        listModul = await search_list_modul(topik["idTopik"])
        # start column and row
        col = 0
        row = 0
        # set header
        text_format = workbook.add_format({'num_format': '@'})
        worksheetTopik.write_string(row, col, 'NIM', text_format)
        worksheetTopik.set_column(row, col, 16.82)
        worksheetTopik.write(row, col+1, 'Nama')
        worksheetTopik.set_column(row, col+1, 23.73)
        for idx, modul in enumerate(listModul["data"]):
            worksheetTopik.write(row, col+(2+idx), modul["ms_nama_modul"])
            worksheetTopik.set_column(row, col+(2+idx), 35)
        row+=1
        data = await search_detail_progress(limit, offset, page, keyword, topik["idTopik"])
        data = data["data"] 
        # set data
        for index in range(len(data)):
            # field NIM
            if data[index]['ms_student_nim'] is not None:
                ms_student_sin = data[index]['ms_student_nim']
                worksheetTopik.write_string(row, col, ms_student_sin)
            # field Nama
            if data[index]['ms_student_name'] is not None:
                ms_student_name = data[index]['ms_student_name']
                worksheetTopik.write(row, col+1, ms_student_name)
            # field Score
            if data[index]['score'] is not None:
                for idx, score in enumerate(data[index]['score']):
                    nilai = score['score']
                    worksheetTopik.write(row, col+(2+idx), nilai)
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
