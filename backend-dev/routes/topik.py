import shutil
from fastapi import APIRouter, Response, status, UploadFile, Depends, Request
from fastapi.responses import FileResponse
from middleware.auth_bearer import JWTBearer
from utilities.utils import getDataFromJwt
from models.topik import Topik
from models.topik_modul import TopikModul
from models.modul import Modul
from models.edge import Edge
from models.node import Node
from models.system import System
from models.tr_edge import TrEdge
from models.tr_node import TrNode
from models.param_modul import ParamModul
from schemas.topik import TopikSchema, EditTopikSchema, IdTopikSchema, MappingTopikModulSchema, DeleteTopikModulSchema
from models.test_case import TestCase
from models.penyelesaian_modul import PenyelesaianModul
import subprocess
from distutils.dir_util import copy_tree, remove_tree
import os   
from config.database import conn, SessionLocal
import magic
import uuid
import json
from xml.dom import minidom
from sqlalchemy.sql import text
import math
from decouple import config
    
from datetime import date, datetime

topik = APIRouter()

@topik.get('/topik/search', dependencies=[Depends(JWTBearer())],
          description="Searching data topik dengan pagination")
async def search_topik(limit: int = 10, offset: int = 0, page: int = 1, keyword: str = None, orderBy: str = "ms_nama_topik", order:str= "asc" ):
    if keyword is not None:
        keyword = "%"+keyword+"%"
    else:
        keyword = "%"
    
    if page < 1 :
        page = 1
   
    offset = (page - 1) * limit
    base_query = """
    SELECT tp.ms_id_topik, 
         tp.ms_nama_topik,
		 tp.ms_deskripsi_topik,
		 tp.`status`,
		 (SELECT COUNT(*) FROM ms_topik_modul tm WHERE tm.ms_id_topik = tp.ms_id_topik) AS jml_modul,
		 (SELECT COUNT(distinct tr_student_id)
		  FROM tr_penyelesaian_modul pm 
		 WHERE pm.tr_id_topik_modul IN 
		       (SELECT tm.ms_id_topik_modul 
				    FROM ms_topik_modul tm 
					WHERE tm.ms_id_topik = tp.ms_id_topik)) AS jml_student
    FROM ms_topik_pengujian tp
    WHERE tp.ms_nama_topik LIKE :keyword or tp.ms_deskripsi_topik LIKE :keyword
    """
    if orderBy is not None and order is not None:
        base_query += " order by " + orderBy + " " + order + " "

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

@topik.get('/topik/challenge', dependencies=[Depends(JWTBearer())],
          description="get data topik dengan pagination")
async def getDataChallange(request: Request, keyword: str = None, status: str = "learning" ):
    currentUser = getDataFromJwt(request)
    keyword = "%"
    if keyword is not None:
        keyword = "%"+keyword+"%"
    
    base_query = " select t.ms_nama_topik, " 
    base_query += "       t.ms_id_topik, "
    base_query += "       IFNULL(t.ms_deskripsi_topik,'') as ms_deskripsi_topik, "
    base_query += "       (select count(1) from ms_topik_modul tm where tm.ms_id_topik = t.ms_id_topik ) as jml_modul, "
    base_query += "       IFNULL((SELECT sum(m.ms_tingkat_kesulitan * 100) "
    base_query += "       	    from ms_topik_modul tm "
    base_query += "       		 INNER JOIN ms_modul_program m ON tm.ms_id_modul = m.ms_id_modul "
    base_query += "       		where tm.ms_id_topik = t.ms_id_topik ),0) as jml_point,  "
    base_query += "     (SELECT count(pm.tr_id_topik_modul) "
    base_query += "         FROM ms_topik_modul tm "
    base_query += "			INNER join  tr_penyelesaian_modul pm ON tm.ms_id_topik_modul = pm.tr_id_topik_modul "
    base_query += "			WHERE pm.tr_student_id = :id_user and tm.ms_id_topik = t.ms_id_topik and pm.tr_status_penyelesaian = 'Y' ) AS jml_completed_modul, "
    base_query += "		IFNULL((SELECT sum(pm.tr_nilai) "                        
    base_query += "         FROM ms_topik_modul tm "
    base_query += "			INNER join  tr_penyelesaian_modul pm ON tm.ms_id_topik_modul = pm.tr_id_topik_modul  "           
    base_query += "			WHERE pm.tr_student_id = :id_user and tm.ms_id_topik = t.ms_id_topik ),0) AS jml_ongoing_point "
    base_query += " from ms_topik_pengujian t "
    base_query += " where t.status = 'P' "
    base_query += " and (t.ms_nama_topik like :keyword "
    base_query += " or t.ms_deskripsi_topik like :keyword ) "
    if status == "learning":
        base_query += " and t.ms_id_topik not in ( SELECT DISTINCT (SELECT tm.ms_id_topik FROM ms_topik_modul tm WHERE tm.ms_id_topik_modul = tc.tr_id_topik_modul) "
        base_query += "                           FROM tr_test_case_modul tc "
        base_query += "                           LEFT JOIN tr_penyelesaian_modul pm ON tc.tr_id_topik_modul = pm.tr_id_topik_modul "
        base_query += " 	                                   AND tc.tr_student_id = pm.tr_student_id "
        base_query += "                            WHERE tc.tr_student_id =  :id_user  ) "
    elif status == "ongoing":
        base_query += " and t.ms_id_topik  in ( SELECT DISTINCT (SELECT tm.ms_id_topik FROM ms_topik_modul tm WHERE tm.ms_id_topik_modul = tc.tr_id_topik_modul) "
        base_query += "                           FROM tr_test_case_modul tc "
        base_query += "                      LEFT JOIN tr_penyelesaian_modul pm ON tc.tr_id_topik_modul = pm.tr_id_topik_modul "
        base_query += " 	                                   AND tc.tr_student_id = pm.tr_student_id "
        base_query += "                          WHERE tc.tr_student_id =  :id_user  )   "
        base_query += " AND  (select count(1) from ms_topik_modul tm where tm.ms_id_topik = t.ms_id_topik ) > (SELECT count(pm.tr_id_topik_modul) "
        base_query += "                                                                                          FROM ms_topik_modul tm  "
        base_query += "                                                                                         INNER join  tr_penyelesaian_modul pm ON tm.ms_id_topik_modul = pm.tr_id_topik_modul "
        base_query += "	                                                                                        WHERE pm.tr_student_id = :id_user and tm.ms_id_topik = t.ms_id_topik and pm.tr_status_penyelesaian = 'Y' ) "   
    elif status == "completed": 
        base_query += " AND  (select count(1) from ms_topik_modul tm where tm.ms_id_topik = t.ms_id_topik ) = (SELECT count(pm.tr_id_topik_modul) "
        base_query += "                                                                                          FROM ms_topik_modul tm  "
        base_query += "                                                                                         INNER join  tr_penyelesaian_modul pm ON tm.ms_id_topik_modul = pm.tr_id_topik_modul "
        base_query += "	                                                                                        WHERE pm.tr_student_id = :id_user and tm.ms_id_topik = t.ms_id_topik and pm.tr_status_penyelesaian = 'Y' ) "   
        base_query += "	AND  (select count(1) from ms_topik_modul tm where tm.ms_id_topik = t.ms_id_topik ) > 0	"
    query_text = text(base_query)
    all_data = conn.execute(query_text, keyword=keyword, id_user=currentUser["userid"]).fetchall()
   
    response = { "data": all_data,
                 "total_data": len(all_data)}
    return response

@topik.get('/topik/listChallenge', dependencies=[Depends(JWTBearer())],
          description="Menampilkan list data challange")
async def list_topik(request: Request, idTopik:str, status:str = 'All'):
    currentUser = getDataFromJwt(request)
    
    base_query = " select t.ms_nama_topik, " 
    base_query += "       IFNULL((SELECT sum(m.ms_tingkat_kesulitan * 100) "
    base_query += "       	    from ms_topik_modul tm "
    base_query += "       		 INNER JOIN ms_modul_program m ON tm.ms_id_modul = m.ms_id_modul "
    base_query += "       		where tm.ms_id_topik = t.ms_id_topik ),0) as jml_point,  "
    base_query += "     (select count(1) from ms_topik_modul tm where tm.ms_id_topik = t.ms_id_topik ) as jml_modul, "
    base_query += "     (SELECT count(pm.tr_id_topik_modul) "
    base_query += "         FROM ms_topik_modul tm "
    base_query += "			INNER join tr_penyelesaian_modul pm ON tm.ms_id_topik_modul = pm.tr_id_topik_modul "
    base_query += "			WHERE pm.tr_student_id = :id_user and tm.ms_id_topik = t.ms_id_topik and pm.tr_status_penyelesaian = 'Y' ) AS jml_completed_modul, "
    base_query += "		IFNULL((SELECT sum(pm.tr_nilai) "                        
    base_query += "         FROM ms_topik_modul tm "
    base_query += "			INNER join  tr_penyelesaian_modul pm ON tm.ms_id_topik_modul = pm.tr_id_topik_modul  "           
    base_query += "			WHERE pm.tr_student_id = :id_user and tm.ms_id_topik = t.ms_id_topik ),0) AS jml_ongoing_point "
    base_query += " from ms_topik_pengujian t "
    base_query += " where t.status = 'P' "
    base_query += " and t.ms_id_topik = :idTopik "
    
    query_text = text(base_query)
    data = conn.execute(query_text, idTopik=idTopik, id_user=currentUser["userid"]).fetchone()

    base_query = " select distinct tm.ms_id_topik_modul, " 
    base_query += "       tm.ms_no, " 
    base_query += "       m.ms_nama_modul, " 
    base_query += "       m.ms_tingkat_kesulitan, " 
    base_query += "       (select s.ms_system_value from ms_system s where s.ms_system_category='modul' and s.ms_system_sub_category = 'tingkat_kesulitan' and s.ms_system_cd = m.ms_tingkat_kesulitan) as tingkat_kesulitan, " 
    base_query += "       IFNULL(pm.tr_nilai,0) as ongoing_point, " 
    base_query += "       IFNULL(pm.tr_status_penyelesaian,'B') as status, " 
    base_query += "       IFNULL(tcm.tr_id_topik_modul,'Kosong') as status_test_case " 
    base_query += " from ms_topik_modul tm inner join ms_modul_program m on tm.ms_id_modul = m.ms_id_modul "
    base_query += " left join tr_penyelesaian_modul pm on pm.tr_id_topik_modul = tm.ms_id_topik_modul and pm.tr_student_id = :id_user "
    base_query += " left join tr_test_case_modul tcm on tcm.tr_id_topik_modul = tm.ms_id_topik_modul and tcm.tr_student_id = :id_user "
    base_query += " where  (pm.tr_student_id = :id_user or pm.tr_student_id is null)   "
    base_query += " and tm.ms_id_topik = :idTopik "
    if status == "All":
        base_query += " order by tm.ms_no asc "
        query_text = text(base_query)
        data_challenge = conn.execute(query_text, idTopik=idTopik, id_user=currentUser["userid"]).fetchall()
    elif status == "N":
        base_query += " and (pm.tr_status_penyelesaian = :status or pm.tr_status_penyelesaian is null) "
        base_query += " order by tm.ms_no asc "
        query_text = text(base_query)
        data_challenge = conn.execute(query_text, idTopik=idTopik, id_user=currentUser["userid"], status=status).fetchall()
    else:
        base_query += " and pm.tr_status_penyelesaian = :status "
        base_query += " order by tm.ms_no asc "
        query_text = text(base_query)
        data_challenge = conn.execute(query_text, idTopik=idTopik, id_user=currentUser["userid"], status=status).fetchall()
        
   
    response = { "data_challenge": data_challenge,
                 "data_topik": data}
    return response

@topik.get('/topik/nextChallenge', dependencies=[Depends(JWTBearer())],
          description="Menampilkan data next challenge")
async def list_topik(request: Request, idTopikModul:str):
    currentUser = getDataFromJwt(request)
    
    base_query = """
    SELECT tm.*
    FROM ms_topik_modul tm 
    WHERE tm.ms_id_topik = (SELECT temp1.ms_id_topik 
                            FROM ms_topik_modul temp1
                                    WHERE temp1.ms_id_topik_modul = :id_topik_modul)
    AND tm.ms_no = (SELECT (temp1.ms_no + 1) 
                            FROM ms_topik_modul temp1
                                    WHERE temp1.ms_id_topik_modul = :id_topik_modul) 
    """ 
    
    query_text = text(base_query)
    data = conn.execute(query_text, id_topik_modul=idTopikModul).fetchone()
    
    base_query_current = """
    SELECT tm.*
    FROM ms_topik_modul tm 
    WHERE tm.ms_id_topik_modul = :id_topik_modul
    """ 
    
    query_text_current = text(base_query_current)
    dataCurrent = conn.execute(query_text_current, id_topik_modul=idTopikModul).fetchone()
    
    response = { "data": data,
                 "data_current": dataCurrent}
    return response

@topik.get('/topik/checkChallenge', dependencies=[Depends(JWTBearer())],
          description="Mengecek data challenge bisa di jalankan atau tidak")
async def list_topik(request: Request, idTopikModul:str):
    currentUser = getDataFromJwt(request)
    
    base_query = """
    SELECT tm.*
    FROM ms_topik_modul tm 
    WHERE tm.ms_id_topik = (SELECT temp1.ms_id_topik 
                            FROM ms_topik_modul temp1
                                    WHERE temp1.ms_id_topik_modul = :id_topik_modul)
    AND tm.ms_no = (SELECT (temp1.ms_no - 1) 
                            FROM ms_topik_modul temp1
                                    WHERE temp1.ms_id_topik_modul = :id_topik_modul) 
    """ 
    
    query_text = text(base_query)
    data = conn.execute(query_text, id_topik_modul=idTopikModul).fetchone()
    if data is None:
        allowed = True
    else:
        check_Query = """
                        SELECT *
                            FROM tr_penyelesaian_modul
                            WHERE tr_id_topik_modul = :id_prev_topik_modul
                                AND tr_student_id = :idStudent
                                AND tr_status_penyelesaian = 'Y' 
                        """ 
        check_Query = text(check_Query)
        data = conn.execute(check_Query, id_prev_topik_modul=data["ms_id_topik_modul"], idStudent=currentUser['userid']).fetchone()
        if data is None:
            allowed = False
        else:
            allowed = True
    response = { "data_allowed": allowed }
    return response


@topik.get('/topik/getListTopik', dependencies=[Depends(JWTBearer())],
          description="Menampilkan list data topik")
async def list_topik(response: Response):
    query = Topik.select()
    data_topik = conn.execute(query).fetchall()
    if len(data_topik) == 0:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "tidak ada data topik", "data": data_topik}
    return {"message": "sukses mengambil data ", "data": data_topik}

@topik.get('/topik/getDetailData', dependencies=[Depends(JWTBearer())],
          description="Menampilkan detail data topik")
async def list_topik(response: Response, id_topik: str):
    query = Topik.select().where(Topik.c.ms_id_topik == id_topik)
    data_topik = conn.execute(query).fetchone()
    if data_topik is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": f"tidak ada data topik dengan id {id_topik}"}
    else :
        queryModul = """
                    SELECT tm.ms_id_topik_modul,
                        tm.ms_id_topik,
                        mp.ms_id_modul,
                        mp.ms_nama_modul,
                        mp.ms_deskripsi_modul,
                        mp.ms_tingkat_kesulitan,
                        (select s.ms_system_value from ms_system s where s.ms_system_category='modul' and s.ms_system_sub_category = 'tingkat_kesulitan' and s.ms_system_cd = mp.ms_tingkat_kesulitan) as tingkat_kesulitan 
                    FROM ms_topik_modul tm
                        INNER JOIN ms_modul_program mp ON tm.ms_id_modul = mp.ms_id_modul
                    WHERE tm.ms_id_topik = :idTopik
                    ORDER BY tm.ms_no asc
                    """
        dataModul = conn.execute(text(queryModul), idTopik=id_topik).fetchall()
    return {"message": "sukses mengambil data ", "data": data_topik, "dataModul":dataModul}

@topik.post("/topik/addTopik", dependencies=[Depends(JWTBearer())])
async def addTopik(request: Request, data_topik: TopikSchema, response: Response):
    currentUser = getDataFromJwt(request)
    
    id_topik = str(uuid.uuid4())
    query = Topik.insert().values(
        ms_id_topik=id_topik,
        ms_nama_topik=data_topik.nama_topik,
        ms_deskripsi_topik=data_topik.deskripsi_topik,
        updated=datetime.today(),
        created=datetime.today(),
        updatedby=currentUser['userid'],
        createdby=currentUser['userid']
    )
    conn.execute(query)
    conn.execute(text("COMMIT;"))
    response = {"message": f"sukses menambahkan data topik baru", "id_topik":id_topik}
    return response

@topik.put("/topik/publish", dependencies=[Depends(JWTBearer())])
async def publishTopik(request: Request, data_topik: IdTopikSchema, response: Response):
    currentUser = getDataFromJwt(request)
    
    id_topik = data_topik.id_topik
    getPrevData = Topik.select().where(Topik.c.ms_id_topik == id_topik)
    prevTopik = conn.execute(getPrevData).fetchone()
    data_status = 'P'
    if prevTopik['status'] == 'P':
        data_status = 'D' 
    query = Topik.update().values(
        status=data_status,
        updated=datetime.today(),
        updatedby=currentUser['userid'],
    ).where(Topik.c.ms_id_topik == id_topik)
    conn.execute(query)
    conn.execute(text("COMMIT;"))
    response = {"message": f"sukses publish data topik", "id_topik":id_topik}
    return response

@topik.put("/topik/editTopik", dependencies=[Depends(JWTBearer())])
async def editTopik(request: Request, data_topik: EditTopikSchema, response: Response):
    currentUser = getDataFromJwt(request)
    
    id_topik = data_topik.id_topik
    query = Topik.update().values(
        ms_nama_topik=data_topik.nama_topik,
        ms_deskripsi_topik=data_topik.deskripsi_topik,
        updated=datetime.today(),
        updatedby=currentUser['userid'],
    ).where(Topik.c.ms_id_topik == id_topik)
    conn.execute(query)
    conn.execute(text("COMMIT;"))
    response = {"message": f"sukses mengubah data topik", "id_topik":id_topik}
    return response

@topik.delete("/topik/deleteTopik", dependencies=[Depends(JWTBearer())])
async def deleteTopik(request: Request, data_topik: IdTopikSchema, response: Response):
    
    id_topik = data_topik.id_topik
    #validasi testcase data, jika sudah ada maka tidak bisa didelete
    base_query = " SELECT *  "
    base_query += " FROM ms_topik_modul tm  "
    base_query += " INNER JOIN tr_test_case_modul tc ON tm.ms_id_topik_modul = tc.tr_id_topik_modul "
    base_query += " WHERE tm.ms_id_topik = :idTopik "
    query_text = text(base_query)
    check = conn.execute(query_text, idTopik=id_topik).fetchall()
    if len(check) > 0:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message": f"data id topik modul tidak dapat dihapus karena sedang digunakan"}
    
    #delete topik modul
    query = TopikModul.delete().where(TopikModul.c.ms_id_topik == id_topik)
    conn.execute(query)

    query = Topik.delete().where(Topik.c.ms_id_topik == id_topik)
    conn.execute(query)
    conn.execute(text("COMMIT;"))
    response = {"message": f"sukses menghapus data topik", "id_topik":id_topik}
    return response

@topik.post("/topik/mappingModul", dependencies=[Depends(JWTBearer())])
async def mappingTopikModul(request: Request, data_topik_modul: MappingTopikModulSchema, response: Response):
    currentUser = getDataFromJwt(request)

    # get prev data
    query = TopikModul.select().where(TopikModul.c.ms_id_topik == data_topik_modul.id_topik).order_by(TopikModul.c.ms_no.desc())
    prevData = conn.execute(query).fetchall()
    
    listModul = data_topik_modul.list_modul
    counter = len(prevData)
    for modul in listModul:
        queryPrev = TopikModul.select().where(TopikModul.c.ms_id_topik == data_topik_modul.id_topik, TopikModul.c.ms_id_modul == modul.id_modul)
        prevData = conn.execute(queryPrev).fetchone()
        if prevData is None :
            id_topik_modul = str(uuid.uuid4())
            counter += 1
            query = TopikModul.insert().values(
                ms_id_topik_modul= id_topik_modul,
                ms_id_topik=data_topik_modul.id_topik,
                ms_id_modul=modul.id_modul,
                ms_no = counter,
                updated=datetime.today(),
                created=datetime.today(),
                updatedby=currentUser['userid'],
                createdby=currentUser['userid']
            )
            conn.execute(query)
    conn.execute(text("COMMIT;"))
    return {"message": f"sukses menambahkan data modul pada topik {data_topik_modul.id_topik}"}

@topik.put("/topik/editMappingModul", dependencies=[Depends(JWTBearer())])
async def editMappingTopikModul(request: Request, data_topik_modul: MappingTopikModulSchema, response: Response):
    currentUser = getDataFromJwt(request)

    queryCheckData = """
        SELECT COUNT(distinct tr_student_id) as usedTopikModul
		  FROM tr_penyelesaian_modul pm 
		 WHERE pm.tr_id_topik_modul IN 
		       (SELECT tm.ms_id_topik_modul 
				    FROM ms_topik_modul tm 
					WHERE tm.ms_id_topik = :idTopik)
    """
    dataUsed = conn.execute(text(queryCheckData), idTopik=data_topik_modul.id_topik).fetchone()
    print (dataUsed.usedTopikModul)
    if dataUsed.usedTopikModul == 0:
        queryDelete = TopikModul.delete().where(TopikModul.c.ms_id_topik == data_topik_modul.id_topik)
        conn.execute(queryDelete)
        listModul = data_topik_modul.list_modul
        counter = 0
        for modul in listModul:
            id_topik_modul = str(uuid.uuid4())
            counter += 1
            query = TopikModul.insert().values(
                ms_id_topik_modul= id_topik_modul,
                ms_id_topik=data_topik_modul.id_topik,
                ms_id_modul=modul.id_modul,
                ms_no = counter,
                updated=datetime.today(),
                created=datetime.today(),
                updatedby=currentUser['userid'],
                createdby=currentUser['userid']
            )
            conn.execute(query)
        conn.execute(text("COMMIT;"))
        return {"message": f"sukses mengubah data modul pada topik {data_topik_modul.id_topik}"}
    else:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message": "data modul tidak bisa di update karena ada modul yg sedang digunakan"}

@topik.delete("/topik/mappingModul", dependencies=[Depends(JWTBearer())])
async def deleteMappingTopikModul(request: Request, param: DeleteTopikModulSchema, response: Response):
    #validasi testcase data, jika sudah ada maka tidak bisa didelete
    queryCheck = TestCase.select().where(TestCase.c.tr_id_topik_modul == param.id_topik_modul)
    check = conn.execute(queryCheck).fetchall()
    if len(check) > 0:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message": f"data id topik modul tidak dapat dihapus karena sedang digunakan"}
    else :
        queryDelete = TopikModul.delete().where(TopikModul.c.ms_id_topik_modul == param.id_topik_modul)
        conn.execute(queryDelete)
        conn.execute(text("COMMIT;"))
        return {"message": f"sukses hapus data modul pada topik {param.id_topik_modul}"}

@topik.get("/topik/listModul", dependencies=[Depends(JWTBearer())])
async def mappingTopikModul(request: Request, id_topik: str, response: Response):
    currentUser = getDataFromJwt(request)

    query = " SELECT tm.ms_no, tm.ms_id_topik_modul, mp.* "
    query += "  FROM ms_topik_modul as tm  "
    query += "  INNER JOIN ms_modul_program as mp on tm.ms_id_modul = mp.ms_id_modul  "
    query += " WHERE tm.ms_id_topik = :idTopik "
    query += " ORDER BY tm.ms_no asc "
    query_modul = text(query)
    data_moduls = conn.execute(query_modul, idTopik=id_topik).fetchall()

    
    return {"message": "sukses mengambil data ", "data": data_moduls}