# routes/role.py
from fastapi import APIRouter, Response, status, Depends
from config.database import conn
from middleware.auth_bearer import JWTBearer
from sqlalchemy.sql import text
from models.system import System

combo = APIRouter()


@combo.get('/combo/tingkat_kesulitan', dependencies=[Depends(JWTBearer())],
           description="Menampilkan data combo tingkat kesulitan")
async def get_combo_status():
    query = """
        select 
            ms_system_value as "label",
            ms_system_cd as "value" 
        from ms_system
        where 
            ms_system_category = 'modul'
            and ms_system_sub_category = 'tingkat_kesulitan'
    """

    data = conn.execute(query).fetchall()
    response = {"message": f"sukses mengambil data", "data": data}
    return response

@combo.get('/combo/validasi_parameter', dependencies=[Depends(JWTBearer())],
           description="Menampilkan data combo validasi_parameter")
async def get_combo_status(data_type:str = ""):
    if data_type == "" :
        query = """
            select 
                ms_system_description as "label",
                ms_system_value as "value" 
            from ms_system
            where 
                ms_system_category = 'modul'
                and ms_system_sub_category = 'param_validation'
        """      
    else :
        query_param = System.select().where(System.c.ms_system_category=='rule_data_type', 
                                            System.c.ms_system_sub_category=='validation_list',
                                            System.c.ms_system_cd == data_type)
        dataparam = conn.execute(query_param).fetchone()
        param = dataparam['ms_system_value']
        query = f"""
            select 
                ms_system_description as "label",
                ms_system_value as "value" 
            from ms_system
            where 
                ms_system_category = 'modul'
                and ms_system_sub_category = 'param_validation'
                and ms_system_cd in {param}
        """

    data = conn.execute(query).fetchall()
    response = {"message": f"sukses mengambil data", "data": data}
    return response

@combo.get('/combo/data_type', dependencies=[Depends(JWTBearer())],
           description="Menampilkan data combo data type")
async def get_combo_status():
    query = """
        select 
            ms_system_value as "label",
            ms_system_cd as "value" 
        from ms_system
        where 
            ms_system_category = 'modul'
            and ms_system_sub_category = 'data_type'
    """

    data = conn.execute(query).fetchall()
    response = {"message": f"sukses mengambil data", "data": data}
    return response

@combo.get('/combo/module_type', dependencies=[Depends(JWTBearer())],
           description="Menampilkan data combo data type")
async def get_combo_status():
    query = """
        select 
            ms_system_value as "label",
            ms_system_cd as "value" 
        from ms_system
        where 
            ms_system_category = 'modul'
            and ms_system_sub_category = 'jenis_modul'
    """

    data = conn.execute(query).fetchall()
    response = {"message": f"sukses mengambil data", "data": data}
    return response

@combo.get('/combo/condition', dependencies=[Depends(JWTBearer())],
           description="Menampilkan data combo condition")
async def get_combo_status(data_type:str = ""):
    if data_type == "" :
        query = """
             select 
                ms_system_value as "label",
                ms_system_cd as "value" 
            from ms_system
            where 
                ms_system_category = 'rule_option'
                and ms_system_sub_category = 'condition'
        """      
    else :
        query_param = System.select().where(System.c.ms_system_category=='rule_data_type', 
                                            System.c.ms_system_sub_category=='condition_list',
                                            System.c.ms_system_cd == data_type)
        dataparam = conn.execute(query_param).fetchone()
        param = dataparam['ms_system_value']
        query = f"""
            select 
                ms_system_value as "label",
                ms_system_cd as "value" 
            from ms_system
            where 
                ms_system_category = 'rule_option'
                and ms_system_sub_category = 'condition'
                and ms_system_cd in {param}
        """

    data = conn.execute(query).fetchall()
    response = {"message": f"sukses mengambil data", "data": data}
    return response

@combo.get('/combo/topik', dependencies=[Depends(JWTBearer())],
           description="Menampilkan data combo topik")
async def get_combo_status():
    query = f"""
        SELECT tp.ms_id_topik as "value",
               tp.ms_nama_topik as "label"
        FROM ms_topik_pengujian tp
    """
    data = conn.execute(query).fetchall()
    response = {"message": f"sukses mengambil data", "data": data}
    return response
