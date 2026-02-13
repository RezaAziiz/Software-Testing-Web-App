# routes/teacher.py
from schemas.teacher import TeacherSchema, Teachers, TeacherProfile
from models.teacher import Teacher
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
import sqlalchemy as sa
import base64
import magic
import shutil
import uuid
import json
from sqlalchemy import func, select, bindparam
from utilities.emailutil import send_email


teacher = APIRouter()


@teacher.get('/teacher/all', dependencies=[Depends(JWTBearer())], response_model=Teachers,
          description="Menampilkan semua data")
async def find_all_teacher(limit: int = 10, offset: int = 0):
    query = Teacher.select().offset(offset).limit(limit)
    data = conn.execute(query).fetchall()
    response = {"limit": limit, "offset": offset, "data": data}
    return response


@teacher.get('/teacher/search', dependencies=[Depends(JWTBearer())],
          description="Searching data guru")
async def search_teacher(limit: int = 10, offset: int = 0, page: int = 1, nameInfo: str = None, genderInfo: str = None, subjectNameInfo: str = None):
    if nameInfo is not None:
        nameInfo = "%"+nameInfo+"%"
    else:
        nameInfo = "%"
    
    if genderInfo is not None:
        genderInfo = "%"+genderInfo+"%"
    else:
        genderInfo = "%"

    if subjectNameInfo is not None:
        subjectNameInfo = "%"+subjectNameInfo+"%"
    else:
        subjectNameInfo = "%"

    offset = (page - 1) * limit
    base_query = "select view_table.* from (select v.*, "
    base_query += "(select u.ms_teacher_name from ms_teacher u where u.ms_teacher_id = v.updatedby) AS updatedby_name, "
    base_query += "(select u.ms_teacher_name from ms_teacher u where u.ms_teacher_id = v.createdby) AS createdby_name, "
    base_query += "(select s.ms_system_value from ms_system s WHERE s.ms_system_category = 'status' and s.ms_system_sub_category = 'flag' and s.ms_system_cd = v.isactive) AS status_name, "
    base_query += "(select GROUP_CONCAT(st.ms_teacher_subject_name SEPARATOR ', ') from ms_subject_teacher_relation st WHERE st.ms_teacher_id = v.ms_teacher_id) AS subject_info "
    base_query += "from ms_teacher v ) view_table where "
    base_query += "view_table.ms_teacher_name like :nameInfo "
    base_query += "or view_table.ms_teacher_gender like :genderInfo "
    base_query += "or view_table.subject_info like :subjectNameInfo "
    query_text = text(base_query)
    
    all_data = conn.execute(query_text, nameInfo=nameInfo, genderInfo=genderInfo, subjectNameInfo=subjectNameInfo).fetchall()

    query_text = text(base_query +
                      "limit :l offset :o")
    data = conn.execute(query_text, l=limit, o=offset,
                        nameInfo=nameInfo, genderInfo=genderInfo, subjectNameInfo=subjectNameInfo).fetchall()
  
    max_page = math.ceil(len(all_data)/limit)
    
    response = {"limit": limit, "offset": offset, "data": data,
                "page": page, "total_data": len(all_data), "max_page": max_page}
    return response


@teacher.get('/teacher/{id}', dependencies=[Depends(JWTBearer())],
          description="Menampilkan detail data")
async def find_teacher(id: str, response: Response):
    query = Teacher.select().where(Teacher.c.ms_teacher_id == id)
    querySubject = select(TeacherSubject.c.ms_teacher_subject_name).where(TeacherSubject.c.ms_teacher_id == id)
    # queryTeacherSubject = TeacherSubject.select().where(TeacherSubject.c.ms_teacher_id == id)
    """
    Kenapa pakai huruf c pada Pegawai.c ?
    karena memakai ImmutableColumnCollection
    untuk melihat apa isinya silahkan uncomment print dibawah ini 
    dan lihat di terminal/cmd
    """

    # dataTeacher = conn.execute(queryTeacher).fetchone()
    # dataTeacherSubject = conn.execute(queryTeacherSubject).fetchone()
    # if dataTeacher is None:
    #     response.status_code = status.HTTP_404_NOT_FOUND
    #     return {"message": "data tidak ditemukan", "status": response.status_code}

    # response = {"message": f"sukses mengambil data dengan id {id}", "dataTeacher": dataTeacher, "dataTeacherSubject": dataTeacherSubject}
    # return response

    data = conn.execute(query).fetchone()
    dataSubject = conn.execute(querySubject).fetchall()

    # print(dataSubject)
    # dataTeacherSubject = conn.execute(queryTeacherSubject).fetchone()
    if data is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "data tidak ditemukan", "status": response.status_code}

    # dataTeacherSubject = conn.execute(queryTeacherSubject).fetchone()
    if dataSubject is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "data tidak ditemukan", "status": response.status_code}

    array_load = []
    index = 1
    
    for row in dataSubject:
        json_data = {"id": index, "value": row[0]}
        array_load.append(json_data)
        index = index + 1

    decoded_data = json.dumps(array_load)

    # print(decoded_data)

    response = {"message": f"sukses mengambil data dengan id {id}", "data": data, "subject_data": decoded_data}
    return response

@teacher.get('/teacher/profile/{id}', dependencies=[Depends(JWTBearer())],
          description="Menampilkan detail data")
async def find_teacher_profile(id: str, response: Response):
    query = Teacher.select().where(Teacher.c.ms_teacher_id == id)
    querySubject = select(TeacherSubject.c.ms_teacher_subject_name).where(TeacherSubject.c.ms_teacher_id == id)
    """
    Kenapa pakai huruf c pada Pegawai.c ?
    karena memakai ImmutableColumnCollection
    untuk melihat apa isinya silahkan uncomment print dibawah ini 
    dan lihat di terminal/cmd
    """

    data = conn.execute(query).fetchone()
    dataSubject = conn.execute(querySubject).fetchall()

    if data is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "data tidak ditemukan", "status": response.status_code}

    if dataSubject is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "data tidak ditemukan", "status": response.status_code}

    array_load = []
    index = 1

    for row in dataSubject:
        json_data = {"id": index, "value": row[0]}
        array_load.append(json_data)
        index = index + 1

    decoded_data = json.dumps(array_load)

    response = {"message": f"sukses mengambil data dengan id {id}", "data": data, "subject_data": decoded_data}
    return response


@teacher.put('/teacher/profile/{id}', dependencies=[Depends(JWTBearer())],
          description="mengubah data guru")
async def update_teacher_profile(request: Request, id: str, pgw: TeacherProfile, response: Response):
    currentUser = getDataFromJwt(request)

    # cek userGroup

    # print(currentUser["userid"])

    if currentUser["userid"] != id:
        response.status_code = status.HTTP_403_FORBIDDEN
        return {"status": response.status_code}

    # cek email
    cek_duplicate_data = Teacher.select().filter(Teacher.c.ms_teacher_email ==
                                     pgw.ms_teacher_email, Teacher.c.ms_teacher_id != id)
    cek_duplicate_data = conn.execute(cek_duplicate_data).fetchone()
    if cek_duplicate_data is not None:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"status": response.status_code, "message": "email sudah digunakan"}
    
    # cek nip
    cek_duplicate_data = Teacher.select().filter(Teacher.c.ms_teacher_nip ==
                                     pgw.ms_teacher_nip, Teacher.c.ms_teacher_id != id)
    cek_duplicate_data = conn.execute(cek_duplicate_data).fetchone()
    if cek_duplicate_data is not None:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"status": response.status_code, "message": "NIP sudah digunakan"}

    # cek no. HP
    cek_duplicate_data = Teacher.select().filter(Teacher.c.ms_teacher_phone ==
                                     pgw.ms_teacher_phone, Teacher.c.ms_teacher_id != id)
    cek_duplicate_data = conn.execute(cek_duplicate_data).fetchone()
    if cek_duplicate_data is not None:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"status": response.status_code, "message": "No. HP sudah digunakan"}

    cek_subject_name = TeacherSubject.select().where(TeacherSubject.c.ms_teacher_id == id)
    cek_subject_name = conn.execute(cek_subject_name).fetchall()
    if cek_subject_name is not None:
        cek_subject_name = TeacherSubject.delete().where(TeacherSubject.c.ms_teacher_id == id)
        conn.execute(cek_subject_name)

    prev_data = Teacher.select().filter(Teacher.c.ms_teacher_id == id)
    prev_data = conn.execute(prev_data).fetchone()
    query = Teacher.update().values(
        ms_teacher_nip=pgw.ms_teacher_nip,
        ms_teacher_name=pgw.ms_teacher_name,
        ms_teacher_gender=pgw.ms_teacher_gender,
        ms_teacher_birthplace=pgw.ms_teacher_birthplace,
        ms_teacher_birthdate=pgw.ms_teacher_birthdate,
        ms_teacher_address=pgw.ms_teacher_address,
        ms_teacher_phone=pgw.ms_teacher_phone,
        ms_teacher_email=pgw.ms_teacher_email,
        ms_teacher_education=pgw.ms_teacher_education,
        ms_teacher_group=pgw.ms_teacher_group,
        ms_teacher_password=pgw.ms_teacher_password,
        ms_teacher_profile_picture=pgw.ms_teacher_profile_picture,
        isactive=pgw.isactive,
        updated=date.today(),
        updatedby=currentUser['userid'],
    ).where(Teacher.c.ms_teacher_id == id)
    
    conn.execute(query)

    if pgw.ms_teacher_subject_name is not None:
        parsed_subject_datas = json.loads(pgw.ms_teacher_subject_name)
        for subject in parsed_subject_datas:
            query = TeacherSubject.insert().values(
                ms_teacher_id=id,
                ms_teacher_subject_name=subject['value']
            )
            conn.execute(query)

    data = Teacher.select().where(Teacher.c.ms_teacher_id == id)
    response = {"message": f"sukses mengubah data dengan id {id}",
                "data": conn.execute(data).fetchone()}
    return response


@teacher.get('/teacher/email/{email}', dependencies=[Depends(JWTBearer())],
          description="Menampilkan detail data")
async def find_teacher(email: str, response: Response):
        query = Teacher.select().where(Teacher.c.ms_teacher_email == email)
        """
        Kenapa pakai huruf c pada Pegawai.c ?
        karena memakai ImmutableColumnCollection
        untuk melihat apa isinya silahkan uncomment print dibawah ini 
        dan lihat di terminal/cmd
        """

        data = conn.execute(query).fetchone()
        if data is None:
            response.status_code = status.HTTP_404_NOT_FOUND
            return {"message": "data tidak ditemukan", "status": response.status_code}

        response = {"message": f"sukses mengambil data dengan email {email}", "data": data}
        return response


@teacher.get('/teacher/nip/{nip}', dependencies=[Depends(JWTBearer())],
          description="Menampilkan detail data")
async def find_teacher(nip: str, response: Response):
    query = Teacher.select().where(Teacher.c.ms_teacher_nip == nip)
    """
    Kenapa pakai huruf c pada Pegawai.c ?
    karena memakai ImmutableColumnCollection
    untuk melihat apa isinya silahkan uncomment print dibawah ini 
    dan lihat di terminal/cmd
    """

    data = conn.execute(query).fetchone()
    if data is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "data tidak ditemukan", "status": response.status_code}

    response = {"message": f"sukses mengambil data dengan nis {nip}", "data": data}
    return response


@teacher.get('/teacher/emailid/{email}/{id}', dependencies=[Depends(JWTBearer())],
          description="Menampilkan detail data")
async def find_teacher(email: str, id: str, response: Response):
        query = Teacher.select().filter(Teacher.c.ms_teacher_email == email, Teacher.c.ms_teacher_id != id)
        """
        Kenapa pakai huruf c pada Pegawai.c ?
        karena memakai ImmutableColumnCollection
        untuk melihat apa isinya silahkan uncomment print dibawah ini 
        dan lihat di terminal/cmd
        """

        data = conn.execute(query).fetchone()
        if data is None:
            response.status_code = status.HTTP_404_NOT_FOUND
            return {"message": "data tidak ditemukan", "status": response.status_code}

        response = {"message": f"sukses mengambil data dengan email {email}", "data": data}
        return response


@teacher.get('/teacher/nipid/{nip}/{id}', dependencies=[Depends(JWTBearer())],
          description="Menampilkan detail data")
async def find_teacher(nip: str, id: str, response: Response):
    query = Teacher.select().filter(Teacher.c.ms_teacher_nip == nip, Teacher.c.ms_teacher_id != id)
    """
    Kenapa pakai huruf c pada Pegawai.c ?
    karena memakai ImmutableColumnCollection
    untuk melihat apa isinya silahkan uncomment print dibawah ini 
    dan lihat di terminal/cmd
    """

    data = conn.execute(query).fetchone()
    if data is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "data tidak ditemukan", "status": response.status_code}

    response = {"message": f"sukses mengambil data dengan nis {nip}", "data": data}
    return response


@teacher.post('/teacher/', dependencies=[Depends(JWTBearer())],
           description="Menambah data guru")
async def insert_teacher(request: Request, pgw: TeacherSchema, response: Response):
    currentUser = getDataFromJwt(request)

    # cek userGroup
    if currentUser["group"] != "Admin":
        response.status_code = status.HTTP_403_FORBIDDEN
        return {"status": response.status_code}

    # cek email
    cek_duplicate_data = Teacher.select().filter(Teacher.c.ms_teacher_email == pgw.ms_teacher_email)
    cek_duplicate_data = conn.execute(cek_duplicate_data).fetchone()
    if cek_duplicate_data is not None:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"status": response.status_code, "message": "email sudah digunakan"}
    
    # cek nip
    cek_duplicate_data = Teacher.select().filter(Teacher.c.ms_teacher_nip == pgw.ms_teacher_nip)
    cek_duplicate_data = conn.execute(cek_duplicate_data).fetchone()
    if cek_duplicate_data is not None:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"status": response.status_code, "message": "NIP sudah digunakan"}

    # cek no HP
    cek_duplicate_data = Teacher.select().filter(Teacher.c.ms_teacher_phone == pgw.ms_teacher_phone)
    cek_duplicate_data = conn.execute(cek_duplicate_data).fetchone()
    if cek_duplicate_data is not None:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"status": response.status_code, "message": "No. HP sudah digunakan"}
    
    # mencari nilai id
    queryCountTeacher = """
        select
            max(ms_teacher.ms_teacher_id) + 1 as "numberOfTeacher"
        from ms_teacher
    """

    countDataTeacher = conn.execute(text(queryCountTeacher)).fetchone()
    # print(countDataTeacher.numberOfTeacher)
    
    cek_duplicate_data = TeacherSubject.select().filter(TeacherSubject.c.ms_teacher_id == countDataTeacher.numberOfTeacher)
    cek_duplicate_data = conn.execute(cek_duplicate_data).fetchone()
    if cek_duplicate_data is not None:
        TeacherSubject.delete().where(TeacherSubject.c.ms_teacher_id == countDataTeacher.numberOfTeacher)

    if pgw.isactive is None:
        pgw.isactive = "Y"

    query = Teacher.insert().values(
        ms_teacher_id=str(uuid.uuid4()),
        ms_teacher_nip=pgw.ms_teacher_nip,
        ms_teacher_name=pgw.ms_teacher_name,
        ms_teacher_gender=pgw.ms_teacher_gender,
        ms_teacher_birthplace=pgw.ms_teacher_birthplace,
        ms_teacher_birthdate=pgw.ms_teacher_birthdate,
        ms_teacher_address=pgw.ms_teacher_address,
        ms_teacher_phone=pgw.ms_teacher_phone,
        ms_teacher_email=pgw.ms_teacher_email,
        ms_teacher_education=pgw.ms_teacher_education,
        ms_teacher_group=pgw.ms_teacher_group,
        ms_teacher_password=get_hashed_password('admin123!!'),
        ms_teacher_profile_picture=pgw.ms_teacher_profile_picture,        
        # ms_teacher_class_id=pgw.ms_teacher_class_id,
        isactive=pgw.isactive,
        updated=date.today(),
        created=date.today(),
        updatedby=currentUser['userid'],
        createdby=currentUser['userid']
    )

    conn.execute(query)

    findIdTeacher = select([Teacher.c.ms_teacher_id]).select_from(Teacher).where(Teacher.c.ms_teacher_nip == pgw.ms_teacher_nip)

    findIdTeacher = conn.execute(findIdTeacher).fetchone()
    
    send_email("Password Password",
    f"""
    <html>
        <body>
            <img src="cid:image-logo" style="display: inline-block;">
            <h1 style="font-family: nunito; color: rgb(255, 178, 82); font-weight: 900; display: inline-block;">
                Student Attendance System
            </h1>
            <br>
            <span style="display: block;">
                Hi, {pgw.ms_teacher_name}
            </span>
            <span style="display: block;">
                Below is your account information:
            </span>
            <br>
            <span style="display: block; color: #68B984">
                Email Account: {pgw.ms_teacher_email}
            </span>
            <br>
            <span style="display: block; color: #68B984">
                Account Password: admin123!!
            </span>
            <br>
            <span style="display: block;">
                Thanks and best regards
            </span>
        </body>
    </html>
    """, pgw.ms_teacher_email)

    data = Teacher.select().order_by(Teacher.c.ms_teacher_id.desc())
    response = {"message": f"sukses menambahkan data baru",
                "data": conn.execute(data).fetchone()}
    return response


@teacher.put('/teacher/{id}', dependencies=[Depends(JWTBearer())],
          description="mengubah data guru")
async def update_teacher(request: Request, id: str, pgw: TeacherSchema, response: Response):
    currentUser = getDataFromJwt(request)

    # cek userGroup
    if currentUser["group"] != "Admin":
        response.status_code = status.HTTP_403_FORBIDDEN
        return {"status": response.status_code}

    # cek email
    cek_duplicate_data = Teacher.select().filter(Teacher.c.ms_teacher_email ==
                                     pgw.ms_teacher_email, Teacher.c.ms_teacher_id != id)
    cek_duplicate_data = conn.execute(cek_duplicate_data).fetchone()
    if cek_duplicate_data is not None:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"status": response.status_code, "message": "email sudah digunakan"}
    
    # cek nip
    cek_duplicate_data = Teacher.select().filter(Teacher.c.ms_teacher_nip ==
                                     pgw.ms_teacher_nip, Teacher.c.ms_teacher_id != id)
    cek_duplicate_data = conn.execute(cek_duplicate_data).fetchone()
    if cek_duplicate_data is not None:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"status": response.status_code, "message": "NIP sudah digunakan"}

    # cek no. HP
    cek_duplicate_data = Teacher.select().filter(Teacher.c.ms_teacher_phone ==
                                     pgw.ms_teacher_phone, Teacher.c.ms_teacher_id != id)
    cek_duplicate_data = conn.execute(cek_duplicate_data).fetchone()
    if cek_duplicate_data is not None:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"status": response.status_code, "message": "No. HP sudah digunakan"}

   
    prev_data = Teacher.select().filter(Teacher.c.ms_teacher_id == id)
    prev_data = conn.execute(prev_data).fetchone()
    query = Teacher.update().values(
        ms_teacher_nip=pgw.ms_teacher_nip,
        ms_teacher_name=pgw.ms_teacher_name,
        ms_teacher_gender=pgw.ms_teacher_gender,
        ms_teacher_birthplace=pgw.ms_teacher_birthplace,
        ms_teacher_birthdate=pgw.ms_teacher_birthdate,
        ms_teacher_address=pgw.ms_teacher_address,
        ms_teacher_phone=pgw.ms_teacher_phone,
        ms_teacher_email=pgw.ms_teacher_email,
        ms_teacher_education=pgw.ms_teacher_education,
        ms_teacher_group=pgw.ms_teacher_group,
        ms_teacher_password=pgw.ms_teacher_password,
        ms_teacher_profile_picture=pgw.ms_teacher_profile_picture,                
        # ms_teacher_class_id=pgw.ms_teacher_class_id,
        isactive=pgw.isactive,
        updated=date.today(),
        updatedby=currentUser['userid'],
    ).where(Teacher.c.ms_teacher_id == id)
    
    conn.execute(query)
    

    data = Teacher.select().where(Teacher.c.ms_teacher_id == id)
    response = {"message": f"sukses mengubah data dengan id {id}",
                "data": conn.execute(data).fetchone()}
    return response


@teacher.delete('/teacher/{id}', dependencies=[Depends(JWTBearer())],
             description="menghapus data guru")
async def delete_teacher(id: str, response: Response):

    query = Teacher.select().where(Teacher.c.ms_teacher_id == id)
    data = conn.execute(query).fetchone()
    if data is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "data tidak ditemukan", "status": response.status_code}
    

    query = Teacher.delete().where(Teacher.c.ms_teacher_id == id)
    conn.execute(query)

    response = {"message": f"sukses menghapus data dengan id {id}"}
    return response


@teacher.post("/teacher/uploadImage")
def upload(image1: UploadFile):
    try:
        if not os.path.exists('file_uploaded'):
            os.makedirs('file_uploaded')
        now = date.today()
        split_tup = os.path.splitext(image1.filename)
        date_str = now.strftime("%Y%m%d")
        new_filename = date_str + uuid.uuid4().hex + split_tup[1]
        target_file = 'file_uploaded/'+new_filename
        with open(target_file, 'wb') as f:
            shutil.copyfileobj(image1.file, f)

        width, height = getResolution(target_file)  
        image_buffer, image = resize(
            target_file, (round(width/4), round(height/4)), format='JPEG')
        image.save(target_file)
        
    except Exception:
        return {"message": "There was an error uploading the file"}
    finally:
        image1.file.close()

    return {"message": f"Successfully uploaded {image1.filename}", "file_name": f"{new_filename}"}


@teacher.get("/teacher/downloadImage/{filename}")
def download(filename: str, ):
    if os.path.exists('file_uploaded'):
        file_path = 'file_uploaded/'+filename
        if os.path.exists(file_path):
            mime = magic.Magic(mime=True)
            return FileResponse(path=file_path, filename=file_path, media_type=mime.from_file(file_path))
        else:
            return {"message": "File tidak ada"}
    else:
        return {"message": "File tidak ada"}


@teacher.get("/teacher/getImageBase64/{filename}")
def download(filename: str, response: Response):
    if os.path.exists('file_uploaded'):
        file_path = 'file_uploaded/'+filename
        if os.path.exists(file_path):
            with open(file_path, "rb") as image_file:
                encoded_image_string = base64.b64encode(image_file.read())
                return {"message": "File ditemukan", "data": encoded_image_string}
        else:
            response.status_code = status.HTTP_404_NOT_FOUND
            return {"message": "File tidak ditemukan", "status": response.status_code}
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "File tidak ditemukan", "status": response.status_code}