import shutil
from fastapi import APIRouter, Response, status, UploadFile, Depends, Request
from fastapi.responses import FileResponse
from middleware.auth_bearer import JWTBearer
from utilities.utils import getDataFromJwt, dataTypeValidation
from models.modul import Modul
from models.edge import Edge
from models.node import Node
from models.system import System
from models.tr_edge import TrEdge
from models.tr_node import TrNode
from models.param_modul import ParamModul
from models.topik_modul import TopikModul
from schemas.modul import TestCaseSchema, TestCaseEditSchema, TestCaseDeleteSchema, ModulSchema, ModulEditSchema, IdModulSchema
from models.test_case import TestCase
from models.penyelesaian_modul import PenyelesaianModul
import subprocess
from distutils.dir_util import copy_tree, remove_tree
import os   
from config.database import conn
import magic
import uuid
import json
from xml.dom import minidom
from sqlalchemy.sql import text
import math
from decouple import config
    
from datetime import date, datetime

modul = APIRouter()

@modul.get('/modul/detailByIdTopikModul/{id_topik_modul}', dependencies=[Depends(JWTBearer())],
          description="Menampilkan detail data modul")
async def modul_detail(id_topik_modul: str, response: Response):
    #get data modul
    getModulQuery = TopikModul.select().where(TopikModul.c.ms_id_topik_modul == id_topik_modul)
    dataTopikModul = conn.execute(getModulQuery).fetchone()
    if dataTopikModul is None :
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "data tidak ditemukan", "status": response.status_code}
    id_modul = dataTopikModul["ms_id_modul"] 
    dataModul = await modul_detail(id_modul, response)
    dataModul['id_topik_modul'] = id_topik_modul
    dataModul['id_topik'] = dataTopikModul["ms_id_topik"] 
    return dataModul


@modul.get('/modul/detail/{id_modul}', dependencies=[Depends(JWTBearer())],
          description="Menampilkan detail data modul")
async def modul_detail(id_modul: str, response: Response):
    query = " SELECT m.*, "
    query += "       (SELECT s.ms_system_value FROM ms_system as s WHERE s.ms_system_category = :category AND s.ms_system_sub_category = :subCategory AND s.ms_system_cd = m.ms_jenis_modul ) as nama_jenis_modul "
    query += "  FROM ms_modul_program as m  "
    query += " WHERE m.ms_id_modul = :idModul "
    query_modul = text(query)
    data_modul = conn.execute(query_modul, category='modul', subCategory = 'jenis_modul', idModul=id_modul).fetchone()
    
    query_param = ParamModul.select().where(ParamModul.c.ms_id_modul == id_modul).order_by(ParamModul.c.no_urut.asc())
    data_param_modul = conn.execute(query_param).fetchall()

    query_node = Node.select().where(Node.c.ms_id_modul == id_modul).order_by(Node.c.ms_no)
    data_nodes = conn.execute(query_node).fetchall()

    query_base = " SELECT node_start.ms_id_node as id_node_start,"
    query_base += "       node_start.ms_line_number as line_number_start, "
    query_base += "       node_finish.ms_id_node as id_node_finish, "
    query_base += "       node_finish.ms_line_number as line_number_finish, "
    query_base += "       edge.ms_label "
    query_base += "  FROM ms_cfg_edge as edge  "
    query_base += "       INNER JOIN ms_cfg_node as node_start ON edge.ms_id_start_node = node_start.ms_id_node "
    query_base += "		 INNER JOIN ms_cfg_node as node_finish ON edge.ms_id_finish_node = node_finish.ms_id_node "
    query_base += " WHERE edge.ms_id_modul = :idModul ORDER BY node_start.ms_line_number "
    query_edge = text(query_base)
    data_edges = conn.execute(query_edge, idModul=id_modul).fetchall()

    data = {"data_modul": data_modul, 
            "data_parameter_modul": data_param_modul,
            "data_cfg": {"nodes": data_nodes,
                         "edges": data_edges}}
    if data is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "data tidak ditemukan", "status": response.status_code}

    response = {"message": f"sukses mengambil data dengan id {id_modul}", "data": data}
    return response

@modul.get('/modul/search', dependencies=[Depends(JWTBearer())],
          description="Searching data modul dengan pagination")
async def search_modul(limit: int = 10, offset: int = 0, page: int = 1, keyword: str = None):
    if keyword is not None:
        keyword = "%"+keyword+"%"
    else:
        keyword = "%"
    
    if page < 1 :
        page = 1
   
    offset = (page - 1) * limit
    base_query = " select m.*, "
    base_query += " (select s.ms_system_value from ms_system s where s.ms_system_category='modul' and s.ms_system_sub_category = 'jenis_modul' and s.ms_system_cd = m.ms_jenis_modul) as jenis_modul, "
    base_query += " (select s.ms_system_value from ms_system s where s.ms_system_category='modul' and s.ms_system_sub_category = 'tingkat_kesulitan' and s.ms_system_cd = m.ms_tingkat_kesulitan) as tingkat_kesulitan "
    base_query += " from ms_modul_program m "
    base_query += " where m.ms_nama_modul like :keyword "
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

# @modul.get('/modul/cfgModul/{id_modul}', dependencies=[Depends(JWTBearer())],
#           description="Menampilkan cfg data modul")
async def cfg_modul(request: Request, id_modul:str):
    currentUser = getDataFromJwt(request)
    
    query = Modul.select().where(Modul.c.ms_id_modul == id_modul)
    data_modul = conn.execute(query).fetchone()
    if data_modul is None :
        return {"message": "id tidak ada"}
    else :
        # parse an xml file by name
        file = minidom.parse("modules/"+id_modul+"/jacoco_report_test/jacocoTestReport.xml")
        sourceCode=open("modules/"+id_modul+"/"+data_modul.ms_source_code)
        lines=sourceCode.readlines()
        #use getElementsByTagName() to get tag
        tag_classes = file.getElementsByTagName('class')

        # all item attributes
        
        methods = []
        for tag_class in tag_classes :
            tag_methods = tag_class.childNodes
            if  tag_class.attributes['sourcefilename'].value == data_modul.ms_source_code :
                counter = 0
                for tag_method in tag_methods:
                    if (tag_method.tagName == "method"):
                        if ((counter + 1) < tag_methods.length) and (tag_methods[counter + 1].tagName == "method"):
                            data_method = {"source_file_name" : tag_class.attributes['sourcefilename'].value,
                                        "nama_method" : tag_method.attributes['name'].value,
                                        "start_line" : int(tag_method.attributes['line'].value),
                                        "end_line" : int(tag_methods[counter + 1].attributes['line'].value)}
                        else :
                            data_method = {
                                        "source_file_name" : tag_class.attributes['sourcefilename'].value,
                                        "nama_method" : tag_method.attributes['name'].value,
                                        "start_line" : int(tag_method.attributes['line'].value),
                                        "end_line" : -1}
                        counter += 1
                        methods.append(data_method)

        #set nodes
        models = file.getElementsByTagName('sourcefile')
        for elem in models:
            if  elem.attributes['name'].value == data_modul.ms_source_code :
                for method in methods:
                    nodes=[]
                    for line in elem.childNodes:
                        if line.tagName == "line":
                            ln = int(line.attributes['nr'].value)
                            if (ln >= method['start_line']) and (ln < method['end_line'] or method['end_line'] == -1) :
                                node = {"id_node": str(uuid.uuid4()), 
                                        "source_file_name" : elem.attributes['name'].value,
                                        "line_number": ln, 
                                        "code": lines[ln-1].strip()}
                                nodes.append(node)
                    method['nodes'] = nodes

        for method in methods :
            nodes = method['nodes']
            tempStatement =[]
            counter = 0
            for node in nodes :
                counter += 1
                node['startIf'] = None
                node['startLoop'] = None
                lineNumber = node['line_number']
                code = node['code']
                print(lineNumber)
                print(code)
                print(tempStatement)
                #start statement
                if str.__contains__(code, 'if (') :
                    tempStatement.append({"statement":"if", "lineNumber":lineNumber})
                elif (str.__contains__(code, 'for') or 
                    str.__contains__(code, 'while')) :
                    tempStatement.append({"statement":"loop", "lineNumber":lineNumber})
                
                #end statement
                if str.__contains__(lines[lineNumber-2].strip(), 'else') and len(tempStatement) > 0:
                    temp = tempStatement.pop()
                    tempStatement.append(temp)
                elif str.__contains__(lines[lineNumber].strip(), '}') and len(tempStatement) > 0 :
                    temp = tempStatement.pop()
                    if temp['statement'] == 'if':
                        node['startIf'] = temp['lineNumber']
                    else:
                        node['startLoop'] = temp['lineNumber']
            

        #set edges
        for method in methods:
            nodes = method['nodes']
            prevLineNumber = 0
            loopStart = 0
            edges = []
            counter = 0
            for node in nodes:
                currentLn = node['line_number']
                if prevLineNumber == 0 :
                    prevLineNumber = currentLn
                else :
                    if node['startIf'] is not None :
                        if loopStart != 0:
                            edge = {"start":loopStart, "end":currentLn}
                            edges.append(edge)
                            loopStart = 0
                        edge = {"start":node['startIf'], "end":currentLn}
                        edges.append(edge)
                        if counter + 1 < len(nodes):
                            edge = {"start":node['startIf'], "end":nodes[counter+1]['line_number']}
                            edges.append(edge)
                    elif node['startLoop'] is not None :
                        edge = {"start":prevLineNumber, "end":currentLn}
                        edges.append(edge)
                        edge = {"start":currentLn, "end":node['startLoop']}
                        edges.append(edge)
                        loopStart = node['startLoop']
                    else :
                        if loopStart != 0:
                            edge = {"start":loopStart, "end":currentLn}
                            edges.append(edge)
                            loopStart = 0
                        edge = {"start":prevLineNumber, "end":currentLn}
                        edges.append(edge)
                    prevLineNumber = currentLn
                counter += 1
            method['edges'] = edges
        #insert cfg to database
        for method in methods:
            nodes = method['nodes']
            edges = method['edges']
            newEdges = []
            for edge in edges:
                startNode = findIdNodes(nodes, edge['start'])
                endNode = findIdNodes(nodes, edge['end'])
                newEdge = {"id_start_node":startNode['id_node'],
                        "id_finish_node":endNode['id_node'],
                        "start_ln":startNode['line_number'],
                        "finish_ln":endNode['line_number']}
                newEdges.append(newEdge)
            method['edges'] = newEdges
        #delete prev data
        query = Node.delete().where(Node.c.ms_id_modul == id_modul)
        conn.execute(query)
        query = Edge.delete().where(Edge.c.ms_id_modul == id_modul)
        conn.execute(query)
        nodes = methods[1]['nodes']
        edges = methods[1]['edges']
        counter = 1
        for node in nodes:
            query = Node.insert().values(
                ms_id_modul=id_modul,
                ms_id_node=node['id_node'],
                ms_no=counter,
                ms_line_number=node['line_number'],
                ms_source_code=node['code'],
                updated=datetime.today(),
                created=datetime.today(),
                updatedby=currentUser['userid'],
                createdby=currentUser['userid']
            )
            conn.execute(query)
            counter += 1
        for edge in edges:
            query = Edge.insert().values(
                ms_id_edge=str(uuid.uuid4()),
                ms_id_modul=id_modul,
                ms_id_start_node=edge['id_start_node'],
                ms_id_finish_node=edge['id_finish_node'],
                ms_label="",
                updated=datetime.today(),
                created=datetime.today(),
                updatedby=currentUser['userid'],
                createdby=currentUser['userid']
            )
            conn.execute(query)
            counter += 1
        conn.execute(text("COMMIT;"))
        return {"data_method":methods}

def findIdNodes(dataNodes:list, lineNumber: int):
    result = None
    for node in dataNodes:
        if node['line_number'] == lineNumber :
            result = node
    return result

@modul.post("/modul/uploadSourceCode/{id_modul}", dependencies=[Depends(JWTBearer())])
async def upload(request:Request, response:Response, id_modul:str, source_code: UploadFile):
    try:
        # print(id_modul)
        if os.path.exists("modules/"+id_modul):
            remove_tree("modules/"+id_modul)
        if not os.path.exists('modules'):
            os.makedirs('modules')
        if not os.path.exists('modules/'+id_modul):
            os.makedirs('modules/'+id_modul)
        new_filename = source_code.filename
        target_file = 'modules/'+id_modul+'/'+new_filename
        with open(target_file, 'wb') as f:
            shutil.copyfileobj(source_code.file, f)
        
        #update file source code data
        query = Modul.update().values(
            ms_source_code=new_filename,
        ).where(Modul.c.ms_id_modul == id_modul)
        conn.execute(query)

        #generate cfg
        gradle_command = config('GRADLE_COMMAND')
        #preparation folder
        if not os.path.exists("engine-testing"):
            os.makedirs("engine-testing")
        if not os.path.exists("engine-testing/"+id_modul):
            os.makedirs("engine-testing/"+id_modul)
        copy_tree("jacoco-engine", "engine-testing/"+id_modul)
       
        #setup folder src java
        if not os.path.exists("engine-testing/"+id_modul+"/src"):
            os.makedirs("engine-testing/"+id_modul+"/src")
        if not os.path.exists("engine-testing/"+id_modul+"/src/main"):
            os.makedirs("engine-testing/"+id_modul+"/src/main")
        if not os.path.exists("engine-testing/"+id_modul+"/src/main/java"):
            os.makedirs("engine-testing/"+id_modul+"/src/main/java")

        shutil.copyfile(target_file, "engine-testing/"+id_modul+"/src/main/java/"+new_filename)
        # output = subprocess.check_output("cd engine-testing/"+id_modul+" & gradlew test", shell=True)
        output = subprocess.check_output("cd engine-testing/"+id_modul+" && "+gradle_command+" test", shell=True)
        print(output)
        output_string = output.decode("utf-8")
        if "BUILD SUCCESSFUL" in output_string:
            if not os.path.exists("modules/"+id_modul):
                os.makedirs("modules/"+id_modul)
            if not os.path.exists("modules/"+id_modul+"/report_test"):
                os.makedirs("modules/"+id_modul+"/report_test")
            if not os.path.exists("modules/"+id_modul+"/jacoco_report_test"):
                os.makedirs("modules/"+id_modul+"/jacoco_report_test")
                
            copy_tree("engine-testing/"+id_modul+"/build/reports/tests/test", "modules/"+id_modul+"/report_test")
            copy_tree("engine-testing/"+id_modul+"/build/test-results/test", "modules/"+id_modul+"/test-results")
            copy_tree("engine-testing/"+id_modul+"/build/reports/jacoco/test", "modules/"+id_modul+"/jacoco_report_test")

            #generate cfg
            result = await cfg_modul(request, id_modul)
            response = {"message": f"Successfully uploaded {source_code.filename}", "location file": f"{new_filename}"}
        else:
            response ={"message": "Source code have error, please upload correct source code"}
            os.remove('modules/'+id_modul+'/'+new_filename)
        
        conn.execute(text("COMMIT;"))
    except Exception as e:
        print(e)
        response.status_code = 500
        response = {"message": "Error On Upload Data"}
    finally:
        remove_tree("engine-testing/"+id_modul)
        source_code.file.close()
    
    return response

@modul.post("/modul/addModul", dependencies=[Depends(JWTBearer())])
async def addModul(request: Request, data_modul: ModulSchema, response: Response):
    currentUser = getDataFromJwt(request)
    # duplicate validation
    query = Modul.select().where(Modul.c.ms_nama_modul==data_modul.nama_modul)
    dataModul = conn.execute(query).fetchone()
    if dataModul is not None :
        response.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        return {"message": "data dengan nama modul \"" + data_modul.nama_modul + "\" sudah pernah dibuat sebelumnya "}

    #validation tingkat kesulitan
    resultValidation = dataTypeValidation("int", data_modul.tingkat_kesulitan, "tingkat kesulitan")
    if not resultValidation['status'] :
        response.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        return {"message": resultValidation['message']}

    id_modul = str(uuid.uuid4())
    query = Modul.insert().values(
        ms_id_modul=id_modul,
        ms_jenis_modul=data_modul.jenis_modul,
        ms_nama_modul=data_modul.nama_modul,
        ms_deskripsi_modul=data_modul.deskripsi_modul,
        ms_class_name=data_modul.class_name,
        ms_function_name=data_modul.function_name,
        ms_return_type=data_modul.return_type,
        ms_jml_parameter=data_modul.jumlah_param,
        ms_tingkat_kesulitan=data_modul.tingkat_kesulitan,
        updated=datetime.today(),
        created=datetime.today(),
        updatedby=currentUser['userid'],
        createdby=currentUser['userid']
    )
    conn.execute(query)
    counter = 1
    for x in data_modul.parameters:
        query_param = ParamModul.insert().values(
            ms_id_parameter=str(uuid.uuid4()),
            ms_id_modul=id_modul,
            ms_nama_parameter=x.param_name,
            ms_tipe_data=x.param_type,
            ms_rules=x.param_rules,
            no_urut=counter,
            updated=datetime.today(),
            created=datetime.today(),
            updatedby=currentUser['userid'],
            createdby=currentUser['userid']
        )
        counter += 1
        conn.execute(query_param)
    conn.execute(text("COMMIT;"))
    response = {"message": f"sukses menambahkan data test case baru", "id_modul":id_modul}
    return response

@modul.put("/modul/editModul", dependencies=[Depends(JWTBearer())])
async def editModul(request: Request, data_modul: ModulEditSchema, response: Response):
    currentUser = getDataFromJwt(request)
    query = Modul.update().values(
        ms_jenis_modul=data_modul.jenis_modul,
        ms_nama_modul=data_modul.nama_modul,
        ms_deskripsi_modul=data_modul.deskripsi_modul,
        ms_class_name=data_modul.class_name,
        ms_function_name=data_modul.function_name,
        ms_return_type=data_modul.return_type,
        ms_jml_parameter=data_modul.jumlah_param,
        ms_tingkat_kesulitan=data_modul.tingkat_kesulitan,
        updated=datetime.today(),
        created=datetime.today(),
        updatedby=currentUser['userid'],
        createdby=currentUser['userid']
    ).where(Modul.c.ms_id_modul == data_modul.id_modul)
    conn.execute(query)

    #delete prev param
    query = ParamModul.delete().where(ParamModul.c.ms_id_modul == data_modul.id_modul)
    conn.execute(query)

    #insert new param
    counter = 1
    for x in data_modul.parameters:
        query_param = ParamModul.insert().values(
            ms_id_parameter=str(uuid.uuid4()),
            ms_id_modul=data_modul.id_modul,
            ms_nama_parameter=x.param_name,
            ms_tipe_data=x.param_type,
            ms_rules=x.param_rules,
            no_urut=counter,
            updated=datetime.today(),
            created=datetime.today(),
            updatedby=currentUser['userid'],
            createdby=currentUser['userid']
        )
        counter += 1
        conn.execute(query_param)
    conn.execute(text("COMMIT;"))
    response = {"message": f"sukses mengupdate data test case baru", "id_modul":data_modul.id_modul}
    return response


@modul.post("/modul/addTestCase", dependencies=[Depends(JWTBearer())])
async def addTestcase(request: Request, data_test: TestCaseSchema, response: Response):
    currentUser = getDataFromJwt(request)
    #get data modul in topik modul
     #get data modul
    getModulQuery = TopikModul.select().where(TopikModul.c.ms_id_topik_modul == data_test.id_topik_modul)
    dataTopikModul = conn.execute(getModulQuery).fetchone()
    if dataTopikModul is None :
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "data tidak ditemukan", "status": response.status_code}
    id_modul = dataTopikModul["ms_id_modul"] 

    queryModul = Modul.select().where(Modul.c.ms_id_modul==id_modul)
    dataModul = conn.execute(queryModul).fetchone()
    
    # duplicate validation
    query = TestCase.select().where(TestCase.c.tr_id_topik_modul==data_test.id_topik_modul, 
                                    TestCase.c.tr_object_pengujian == data_test.object_pengujian, 
                                    TestCase.c.tr_student_id == currentUser['userid'])
    dataTestCase = conn.execute(query).fetchone()
    if dataTestCase is not None :
        response.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        return {"message": "data dengan object pengujian \"" + data_test.object_pengujian + "\" sudah ada "}

    dataInput = []
    for x in data_test.data_test_input:
        
        #validate parameter
        resultValidation = dataTypeValidation(x.param_type, x.param_value, x.param_name)
        print(resultValidation)
        if not resultValidation['status'] :
            response.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
            return {"message": resultValidation['message']}
        
        dataInput.append({
            "param_name":x.param_name,
            "param_type":x.param_type,
            "param_value":x.param_value,
        })
    
    #validate expected result
    resultValidation = dataTypeValidation(dataModul['ms_return_type'], data_test.expected_result, "Ekspektasi")
    if not resultValidation['status'] :
        response.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        return {"message": resultValidation['message']}
    
    query = TestCase.insert().values(
        tr_id_test_case=str(uuid.uuid4()),
        tr_id_topik_modul=data_test.id_topik_modul,
        tr_student_id=currentUser['userid'],
        tr_no=data_test.no,
        tr_object_pengujian=data_test.object_pengujian,
        tr_data_test_input=json.dumps(dataInput),
        tr_expected_result=data_test.expected_result,
        updated=datetime.today(),
        created=datetime.today(),
        updatedby=currentUser['userid'],
        createdby=currentUser['userid']
    )
    
    conn.execute(query)
    conn.execute(text("COMMIT;"))
    response = {"message": f"sukses menambahkan data test case baru"}
    return response

@modul.put("/modul/editTestCase", dependencies=[Depends(JWTBearer())])
async def editTestcase(request: Request, data_test: TestCaseEditSchema, response: Response):
    currentUser = getDataFromJwt(request)
    #get data modul in topik modul
    getModulQuery = TopikModul.select().where(TopikModul.c.ms_id_topik_modul == data_test.id_topik_modul)
    dataTopikModul = conn.execute(getModulQuery).fetchone()
    if dataTopikModul is None :
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "data tidak ditemukan", "status": response.status_code}
    id_modul = dataTopikModul["ms_id_modul"] 

    queryModul = Modul.select().where(Modul.c.ms_id_modul==id_modul)
    dataModul = conn.execute(queryModul).fetchone()

    # duplicate validation
    query = TestCase.select().where(TestCase.c.tr_id_topik_modul==data_test.id_topik_modul, TestCase.c.tr_object_pengujian == data_test.object_pengujian, 
                                    TestCase.c.tr_id_test_case != data_test.id_test_case)
    dataTestCase = conn.execute(query).fetchone()
    if dataTestCase is not None :
        response.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        return {"message": "data dengan object pengujian \"" + data_test.object_pengujian + "\" sudah ada "}

    dataInput = []
    for x in data_test.data_test_input:

        #validate parameter
        resultValidation = dataTypeValidation(x.param_type, x.param_value, x.param_name)
        if not resultValidation['status'] :
            response.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
            return {"message": resultValidation['message']}
        
        dataInput.append({
            "param_name":x.param_name,
            "param_type":x.param_type,
            "param_value":x.param_value,
        })
    #validate expected result
    resultValidation = dataTypeValidation(dataModul['ms_return_type'], data_test.expected_result, "expected result")
    if not resultValidation['status'] :
        response.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        return {"message": resultValidation['message']}

    query = TestCase.update().values(
        tr_no=data_test.no,
        tr_object_pengujian=data_test.object_pengujian,
        tr_data_test_input=json.dumps(dataInput),
        tr_expected_result=data_test.expected_result,
        updated=datetime.today(),
        updatedby=currentUser['userid'],
    ).where(TestCase.c.tr_id_test_case == data_test.id_test_case)
    
    conn.execute(query)
    conn.execute(text("COMMIT;"))
    response = {"message": f"sukses update data test case"}
    return response

@modul.delete("/modul/delete", dependencies=[Depends(JWTBearer())])
async def delete_Modul(request: Request, param: IdModulSchema, response: Response):
    #validasi testcase data, jika sudah ada maka tidak bisa didelete
    base_query = " SELECT *  "
    base_query += " FROM ms_topik_modul tm  "
    base_query += " WHERE tm.ms_id_modul = :idModul "
    query_text = text(base_query)
    check = conn.execute(query_text, idModul=param.id_modul).fetchall()
    if len(check) > 0:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message": f"data modul tidak dapat dihapus karena sedang digunakan"}
   
    query = Modul.delete().where(Modul.c.ms_id_modul == param.id_modul)
    conn.execute(query)
    conn.execute(text("COMMIT;"))

    response = {"message": f"sukses delete data modul"}
    return response


@modul.delete("/modul/deleteTestCase", dependencies=[Depends(JWTBearer())])
async def deleteTestcase(request: Request, test_data: TestCaseDeleteSchema, response: Response):
    query = TestCase.delete().where(TestCase.c.tr_id_test_case == test_data.id_test_case)
    conn.execute(query)
    conn.execute(text("COMMIT;"))

    response = {"message": f"sukses delete data test case"}
    return response

@modul.get("/modul/TestCase/{id_topik_modul}", dependencies=[Depends(JWTBearer())])
async def getTestcase(request: Request, id_topik_modul: str, response: Response):
    currentUser = getDataFromJwt(request)
    id_user = currentUser['userid']
    query = TestCase.select().where(TestCase.c.tr_id_topik_modul == id_topik_modul, TestCase.c.tr_student_id == id_user).order_by(TestCase.c.tr_no.asc())
    data_test_case = conn.execute(query).fetchall()
    
    if data_test_case is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "data tidak ditemukan", "status": response.status_code}

    response = {"message": f"sukses mengambil data test case dengan id {id_topik_modul}", "data": data_test_case}
    return response

@modul.get("/modul/DetailTestCase/{id_test_case}", dependencies=[Depends(JWTBearer())])
async def getDetailTestcase(request: Request, id_test_case: str, response: Response):
    currentUser = getDataFromJwt(request)
    id_user = currentUser['userid']
    query = TestCase.select().where(TestCase.c.tr_id_test_case == id_test_case)
    data_test_case = conn.execute(query).fetchone()
    
    if data_test_case is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "data tidak ditemukan", "status": response.status_code}

    response = {"message": f"sukses mengambil data test case dengan id {id_test_case}", "data": data_test_case}
    return response

@modul.get("/modul/downloadSourceCode/{id_modul}/{filename}", dependencies=[Depends(JWTBearer())])
async def download(id_modul:str, filename: str):
    if os.path.exists('modules'):
        file_path = 'modules/'+id_modul+'/'+filename
        if os.path.exists(file_path):
            mime = magic.Magic(mime=True)
            return FileResponse(path=file_path, filename=file_path, media_type=mime.from_file(file_path))
        else:
            return {"message": "File tidak ada"}
    else:
        return {"message": "File tidak ada"}
    
@modul.get("/modul/getSourceCodeText/{id_modul}", dependencies=[Depends(JWTBearer())])
async def getSourceCodeText(id_modul:str, response:Response):
    query = Modul.select().where(Modul.c.ms_id_modul == id_modul)
    data_modul = conn.execute(query).fetchone()
    print(id_modul)
    # validasi data source code
    if data_modul.ms_source_code is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "data source code tidak ada, silahkan upload terlebih dahulu source code nya "}
    
    if os.path.exists('modules'):
        file_path = 'modules/'+id_modul+'/'+data_modul.ms_source_code
        if os.path.exists(file_path): 
            sourceCode=open("modules/"+id_modul+"/"+data_modul.ms_source_code)
            lines=sourceCode.readlines()
            sourceData =""
            for line in lines:
                sourceData += line
            return {"data":sourceData}
        else:
            return {"message": "File tidak ada"}
    else:
        return {"message": "File tidak ada"}

@modul.post('/modul/generateTestUnitClass/{id_topik_modul}', 
          description="Generate Unit Testing")
async def generateTestUnitClass(id_topik_modul: str, id_user:str, destinationFolder: str):
    #get data modul in topik modul
    getModulQuery = TopikModul.select().where(TopikModul.c.ms_id_topik_modul == id_topik_modul)
    dataTopikModul = conn.execute(getModulQuery).fetchone()
    id_modul = dataTopikModul["ms_id_modul"] 

    query = Modul.select().where(Modul.c.ms_id_modul == id_modul)
    data_modul = conn.execute(query).fetchone()
    className = data_modul['ms_class_name']
    functionName = data_modul['ms_function_name']
    returnType = data_modul['ms_return_type']
    
    query = TestCase.select().where(TestCase.c.tr_id_topik_modul == id_topik_modul, TestCase.c.tr_student_id == id_user).order_by(TestCase.c.tr_no.asc())
    data_test_case = conn.execute(query).fetchall()
    
    filename = className + "Test.java"
    targetFile = destinationFolder+filename
    file = open(targetFile, 'w')
    file.write('import org.junit.Assert;\n')
    file.write('import org.junit.Test;\n')
    file.write('\n\n')
    file.write('public class '+className+'Test {\n ')
    for testCase in data_test_case:
        dataTest = json.loads(testCase['tr_data_test_input'])
        print(dataTest)
        file.write('\t@Test \n ')
        file.write('\tpublic void '+testCase['tr_object_pengujian'].replace(" ", "_")+'() { \n ')
        file.write('\t\t'+className+' objectTest = new '+className+'(); \n')
        file.write('\t\t'+returnType+' actual = objectTest.'+functionName+'(')
        if len(dataTest) == 1:
            if dataTest[0]['param_type'] == 'String' : 
                if dataTest[0]['param_value'] == "{}" :
                    file.write('""')
                elif dataTest[0]['param_value'] == "{null}" :
                    file.write('null')
                else :    
                    file.write('"'+dataTest[0]['param_value']+'"')
            elif dataTest[0]['param_type'] == 'char':
                file.write('\''+dataTest[0]['param_value']+'\'')
            else :
                if dataTest[0]['param_type'] == 'float':
                    file.write(dataTest[0]['param_value']+'f')
                else:
                    file.write(dataTest[0]['param_value'])
        elif len(dataTest) >=2:
            counter = 0
            for param in dataTest:
                if param['param_type'] == 'String' : 
                    if param['param_value'] == "{}" :
                        file.write('""')
                    elif param['param_value'] == "{null}" :
                        file.write('null')
                    else :    
                        file.write('"'+param['param_value']+'"')
                elif param['param_type'] == 'char' :
                    file.write('\''+param['param_value']+'\'')
                else :
                    if param['param_type'] == 'float':
                        file.write(param['param_value']+'f')
                    else:
                        file.write(param['param_value'])
                #handling sparator
                if counter +1 < len(dataTest):
                    file.write(',')
                counter += 1 #counter count data
        file.write('); \n')
        #generate assert equals
        file.write('\t\tAssert.assertEquals(')
        if returnType == 'char' or returnType == 'String' : 
            file.write('"'+testCase['tr_expected_result']+'"')
        else :
            file.write(testCase['tr_expected_result'])
        if returnType == 'float' or returnType == 'double' : # handlling for return value double an float need add delta in assert
            file.write(', actual, 0.0f);\n ')
        else :
            file.write(', actual);\n ')

        file.write('\t}\n\n')   
    file.write('}')
    file.close()
    return {"message":"File generated"}



@modul.post('/modul/run/{id_topik_modul}', dependencies=[Depends(JWTBearer())], 
          description="Running Unit Testing")
async def running_testing_app(request: Request, id_topik_modul: str):
    currentUser = getDataFromJwt(request)
    # loginType = currentUser['login_type']
    id_user = currentUser['userid']
 
    getModulQuery = TopikModul.select().where(TopikModul.c.ms_id_topik_modul == id_topik_modul)
    dataTopikModul = conn.execute(getModulQuery).fetchone()
    if dataTopikModul is None :
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "data tidak ditemukan", "status": response.status_code}
    id_modul = dataTopikModul["ms_id_modul"] 

    query = Modul.select().where(Modul.c.ms_id_modul == id_modul)
    data_modul = conn.execute(query).fetchone()
    if data_modul is None:
        return {"message": "data modul not found"}

    file_name = data_modul['ms_source_code']
    target_file = "modules/"+id_modul+"/"+file_name
    
       #preparation folder
    if not os.path.exists("engine-testing"):
        os.makedirs("engine-testing")
    if not os.path.exists("engine-testing/"+id_user):
        os.makedirs("engine-testing/"+id_user)
    if not os.path.exists("engine-testing/"+id_user+"/"+id_topik_modul):
        os.makedirs("engine-testing/"+id_user+"/"+id_topik_modul)
    
    copy_tree("jacoco-engine", "engine-testing/"+id_user+"/"+id_topik_modul)

    #setup folder src java
    if not os.path.exists("engine-testing/"+id_user+"/"+id_topik_modul+"/src"):
        os.makedirs("engine-testing/"+id_user+"/"+id_topik_modul+"/src")
    if not os.path.exists("engine-testing/"+id_user+"/"+id_topik_modul+"/src/main"):
        os.makedirs("engine-testing/"+id_user+"/"+id_topik_modul+"/src/main")
    if not os.path.exists("engine-testing/"+id_user+"/"+id_topik_modul+"/src/main/java"):
        os.makedirs("engine-testing/"+id_user+"/"+id_topik_modul+"/src/main/java")

    shutil.copyfile(target_file, "engine-testing/"+id_user+"/"+id_topik_modul+"/src/main/java/"+file_name)
    await generateTestUnitClass(id_topik_modul, id_user, "engine-testing/"+id_user+"/"+id_topik_modul+"/src/test/java/")
    try:
        gradle_command = config('GRADLE_COMMAND')
        output = subprocess.check_output("cd engine-testing/"+id_user+"/"+id_topik_modul+" && "+gradle_command+" test", shell=True)
        output_string = output.decode("utf-8")
        if "BUILD SUCCESSFUL" in output_string:
            data = "test success"
            status_exsekusi = "Y"
            if os.path.exists("static/"+id_user+"/"+id_topik_modul):
                remove_tree("static/"+id_user+"/"+id_topik_modul)
            if not os.path.exists("static/"+id_user):
                os.makedirs("static/"+id_user)
            if not os.path.exists("static/"+id_user+"/"+id_topik_modul):
                os.makedirs("static/"+id_user+"/"+id_topik_modul)
            if not os.path.exists("static/"+id_user+"/"+id_topik_modul+"/report_test"):
                os.makedirs("static/"+id_user+"/"+id_topik_modul+"/report_test")
            if not os.path.exists("static/"+id_user+"/"+id_topik_modul+"/jacoco_report_test"):
                os.makedirs("static/"+id_user+"/"+id_topik_modul+"/jacoco_report_test")
                
            copy_tree("engine-testing/"+id_user+"/"+id_topik_modul+"/build/reports/tests/test", "static/"+id_user+"/"+id_topik_modul+"/report_test")
            copy_tree("engine-testing/"+id_user+"/"+id_topik_modul+"/build/test-results/test", "static/"+id_user+"/"+id_topik_modul+"/test-results")
            copy_tree("engine-testing/"+id_user+"/"+id_topik_modul+"/build/reports/jacoco/test", "static/"+id_user+"/"+id_topik_modul+"/jacoco_report_test")
    except subprocess.CalledProcessError as e: #Handling if testing is failed
            data = "Test failed"
            status_exsekusi = "N"
            if os.path.exists("static/"+id_user+"/"+id_topik_modul):
                remove_tree("static/"+id_user+"/"+id_topik_modul)
            if not os.path.exists("static/"+id_user):
                os.makedirs("static/"+id_user)
            if not os.path.exists("static/"+id_user+"/"+id_topik_modul):
                os.makedirs("static/"+id_user+"/"+id_topik_modul)
            if not os.path.exists("static/"+id_user+"/"+id_topik_modul+"/report_test"):
                os.makedirs("static/"+id_user+"/"+id_topik_modul+"/report_test")
            copy_tree("engine-testing/"+id_user+"/"+id_topik_modul+"/build/reports/tests/test", "static/"+id_user+"/"+id_topik_modul+"/report_test")
            copy_tree("engine-testing/"+id_user+"/"+id_topik_modul+"/build/test-results/test", "static/"+id_user+"/"+id_topik_modul+"/test-results")
    finally:
       remove_tree("engine-testing/"+id_user+"/"+id_topik_modul)
    testResult = saveDataResultTest("static/"+id_user+"/"+id_topik_modul+"/test-results/TEST-"+data_modul['ms_class_name']+"Test.xml", id_topik_modul, id_user, status_exsekusi)
    coverageScore = saveDataCoverageTest("static/"+id_user+"/"+id_topik_modul+"/jacoco_report_test/jacocoTestReport.xml", id_topik_modul, id_user, data_modul["ms_tingkat_kesulitan"], data_modul["ms_function_name"])
    #get min coverage
    query_min_coverage = System.select().where(System.c.ms_system_category=='common',System.c.ms_system_sub_category=='minimum_value', System.c.ms_system_cd == 'coverage')
    dataMinCoverage = conn.execute(query_min_coverage).fetchone()
    conn.execute(text("COMMIT;"))
    response = {"modul_id":id_modul, 
                "topik_modul_id":id_topik_modul, 
                "result_test": testResult, 
                "coverage_score":coverageScore,
                "minimum_coverage_score":float(dataMinCoverage['ms_system_value']),
                "point":round(coverageScore*int(data_modul["ms_tingkat_kesulitan"]),0)}
    return response

# @modul.post('/modul/saveDataResultTest/{id_modul}', 
#           description="Save Data result test from xaml")
def saveDataResultTest(pathFileResult: str, id_topik_modul: str, id_user:str, status_exsekusi:str):
    dataResultTest = minidom.parse(pathFileResult)
    tagTestCase = dataResultTest.getElementsByTagName('testcase')
    isFailedCase = False
    for testCase in tagTestCase:
        childNode = testCase.childNodes
        resultTest = 'F' # Set defauit result to failed
        nameCase = testCase.getAttribute("name")
        if len(childNode) == 0: ## testcase success
            resultTest = 'P'
        else:
            isFailedCase = True
        #Update data to db
        query = TestCase.update().values(
            tr_test_result=resultTest,
            updated=datetime.today(),
            updatedby=id_user,
        ).where(TestCase.c.tr_id_topik_modul == id_topik_modul, 
                TestCase.c.tr_student_id == id_user, 
                TestCase.c.tr_object_pengujian == nameCase.replace("_", " "))
        conn.execute(query)
        print(id_topik_modul)
        print(id_user)
        print(nameCase.replace("_", " "))
    querySelesaiModul = PenyelesaianModul.select().where(PenyelesaianModul.c.tr_id_topik_modul == id_topik_modul,
                                                        PenyelesaianModul.c.tr_student_id == id_user)
    data_selesai_modul = conn.execute(querySelesaiModul).fetchone()
    tglEksekusi = datetime.today()
    if data_selesai_modul is None :
        queryInsert = PenyelesaianModul.insert().values(
            tr_id_topik_modul=id_topik_modul,
            tr_student_id=id_user,
            tr_tgl_mulai=tglEksekusi,
            tr_result_report="static/"+id_user+"/"+id_topik_modul+"/report_test/index.html",
            tr_tgl_eksekusi=tglEksekusi,
            tr_status_eksekusi=status_exsekusi,
            updated=datetime.today(),
            created=datetime.today(),
            updatedby=id_user,
            createdby=id_user
        )
        conn.execute(queryInsert)
    else :
        queryUpdate = PenyelesaianModul.update().values(
            tr_tgl_eksekusi=datetime.today(),
            tr_status_eksekusi=status_exsekusi,
            updated=datetime.today(),
            updatedby=id_user,
        ).where(PenyelesaianModul.c.tr_id_topik_modul == id_topik_modul,
                PenyelesaianModul.c.tr_student_id == id_user)
        conn.execute(queryUpdate)
    if status_exsekusi == 'N':
        queryUpdate = PenyelesaianModul.update().values(
            tr_persentase_coverage=0,
            tr_nilai=0,
            tr_status_penyelesaian='N'
        ).where(PenyelesaianModul.c.tr_id_topik_modul == id_topik_modul,
                PenyelesaianModul.c.tr_student_id == id_user)
        conn.execute(queryUpdate)

    return {"status_eksekusi":(not isFailedCase), "tgl_eksekusi": tglEksekusi.strftime('%d %B %Y, %H:%M:%S')}

def saveDataCoverageTest(pathFileResult: str, id_topik_modul: str, id_user:str, tingkatKesulitan:str, method_name: str):
    coveragePercent = 0
    getModulQuery = TopikModul.select().where(TopikModul.c.ms_id_topik_modul == id_topik_modul)
    dataTopikModul = conn.execute(getModulQuery).fetchone()
    id_modul = dataTopikModul["ms_id_modul"] 
    
    if os.path.exists(pathFileResult):
        dataCoverageTest = minidom.parse(pathFileResult)
        tagMethod = dataCoverageTest.getElementsByTagName('method')
        totalNode = 0
        totalCovered = 0
        for method in tagMethod:
            nameCase = method.getAttribute("name")
            if nameCase == method_name : 
                childNodes = method.childNodes
                for child in childNodes :
                    type_name = child.getAttribute("type")
                    if type_name != "METHOD":
                        totalNode += int(child.getAttribute("missed"))
                        totalNode += int(child.getAttribute("covered"))
                        totalCovered += int(child.getAttribute("covered"))
        coveragePercent = round((totalCovered/totalNode) * 100,2)
        nilai = coveragePercent * int(tingkatKesulitan)

        #ge minimum coverage score
        query_min_coverage = System.select().where(System.c.ms_system_category=='common',System.c.ms_system_sub_category=='minimum_value', System.c.ms_system_cd == 'coverage')
        dataMinCoverage = conn.execute(query_min_coverage).fetchone()

        if (coveragePercent > float(dataMinCoverage['ms_system_value'])) :
            queryUpdate = PenyelesaianModul.update().values(
                tr_persentase_coverage=coveragePercent,
                tr_coverage_report="static/"+id_user+"/"+id_topik_modul+"/jacoco_report_test/html/index.html",
                tr_tgl_selesai=datetime.today(),
                tr_nilai = round(nilai,0),
                tr_status_penyelesaian = 'Y',
                updated=datetime.today(),
                updatedby=id_user,
            ).where(PenyelesaianModul.c.tr_id_topik_modul == id_topik_modul,
                    PenyelesaianModul.c.tr_student_id == id_user)
        else :
            queryUpdate = PenyelesaianModul.update().values(
                tr_persentase_coverage=coveragePercent,
                tr_coverage_report="static/"+id_user+"/"+id_topik_modul+"/jacoco_report_test/html/index.html",
                tr_nilai = round(nilai,0),
                updated=datetime.today(),
                updatedby=id_user,
            ).where(PenyelesaianModul.c.tr_id_topik_modul == id_topik_modul,
                    PenyelesaianModul.c.tr_student_id == id_user)
        conn.execute(queryUpdate)
        #add/update data cfg
        #delete data PreviousData
        queryDeleteTrNode = TrNode.delete().where(TrNode.c.tr_id_topik_modul == id_topik_modul, TrNode.c.tr_id_student == id_user)
        conn.execute(queryDeleteTrNode)
    
    
        #get data node cfg based modul
        queryNodeModul = Node.select().where(Node.c.ms_id_modul == id_modul)
        dataNodes = conn.execute(queryNodeModul).fetchall()
        for node in dataNodes:
            queryInsertTrNode = TrNode.insert().values(
                tr_id_node = node['ms_id_node'],
                tr_id_topik_modul = id_topik_modul,
                tr_id_student = id_user,
                tr_status = 'N', 
                updated=datetime.today(),
                created=datetime.today(),
                updatedby=id_user,
                createdby=id_user
            )
            conn.execute(queryInsertTrNode)
        #update data
        dataCoverageTest = minidom.parse(pathFileResult)
        tag_lines = dataCoverageTest.getElementsByTagName('line')
        for line in tag_lines :
            lineNumber = line.getAttribute('nr')
            mi = int(line.getAttribute('mi'))
            ci = int(line.getAttribute('ci'))
            mb = int(line.getAttribute('mb'))
            cb = int(line.getAttribute('cb'))
            queryGetNode = Node.select().where(Node.c.ms_id_modul == id_modul, Node.c.ms_line_number == lineNumber)
            dataNode = conn.execute(queryGetNode).fetchone()
            if dataNode is not None :
                if mb == 0: #executed
                    status_executed = 'Y'
                elif cb > 0 and mb > 0 :
                    status_executed = 'S'
                elif cb > 0:
                    status_executed = 'Y'
                else:
                    status_executed = 'N'
                queryTrNodeUpdate = TrNode.update().values(
                    tr_status = status_executed,
                    updated=datetime.today(),
                    updatedby=id_user,
                ).where(TrNode.c.tr_id_node == dataNode['ms_id_node'], TrNode.c.tr_id_topik_modul == id_topik_modul, TrNode.c.tr_id_student == id_user)
                conn.execute(queryTrNodeUpdate)
        
        #delete prev data Edge
        queryDeleteTrEdge = TrEdge.delete().where(TrEdge.c.tr_id_topik_modul == id_topik_modul, TrEdge.c.tr_id_student == id_user)
        conn.execute(queryDeleteTrEdge)
        
        #get data node cfg based modul
        queryNodeEdge = Edge.select().where(Edge.c.ms_id_modul == id_modul)
        dataEdges = conn.execute(queryNodeEdge).fetchall()
        for edge in dataEdges:
            queryInsertTrEdge = TrEdge.insert().values(
                tr_id_edge = edge['ms_id_edge'],
                tr_id_topik_modul = id_topik_modul,
                tr_id_student = id_user,
                tr_status = 'N', 
                updated=datetime.today(),
                created=datetime.today(),
                updatedby=id_user,
                createdby=id_user
            )
            conn.execute(queryInsertTrEdge)
        # update edge based node
        # TODO


    return coveragePercent


@modul.get('/modul/getResultTest/{id_topik_modul}', dependencies=[Depends(JWTBearer())], 
          description="Get data result testingn")
async def getDataResultTesting(request: Request, id_topik_modul: str, response:Response):
    currentUser = getDataFromJwt(request)
    id_user = currentUser['userid']
    #query result test
    queryResultTest = PenyelesaianModul.select().where(PenyelesaianModul.c.tr_id_topik_modul == id_topik_modul, PenyelesaianModul.c.tr_student_id == id_user)
    dataResultTest = conn.execute(queryResultTest).fetchone()
    
    if dataResultTest is None :
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "data hasil pengujian dengan id \"" + id_topik_modul + "\" tidak ada "}
    
    getModulQuery = TopikModul.select().where(TopikModul.c.ms_id_topik_modul == id_topik_modul)
    dataTopikModul = conn.execute(getModulQuery).fetchone()
    id_modul = dataTopikModul["ms_id_modul"] 
    
    #query modul detail
    queryModul = Modul.select().where(Modul.c.ms_id_modul == id_modul)
    dataModule = conn.execute(queryModul).fetchone()
    #query cfg
    queryCfgNode = " SELECT n.*, tn.tr_status "
    queryCfgNode += "  FROM ms_cfg_node n "
    queryCfgNode += "     INNER JOIN tr_cfg_node tn ON n.ms_id_node = tn.tr_id_node "
    queryCfgNode += " WHERE tn.tr_id_topik_modul = :idTopikModul "
    queryCfgNode += "  AND tn.tr_id_student = :idUser "
    queryCfgNode += "ORDER BY n.ms_no; "
    queryCfgNode = text(queryCfgNode)
    dataCfgNode = conn.execute(queryCfgNode, idTopikModul=id_topik_modul, idUser=id_user).fetchall()
    #query cfg
    queryCfgEdge = " SELECT e.*, te.tr_status "
    queryCfgEdge += "  FROM ms_cfg_edge e "
    queryCfgEdge += "     INNER JOIN tr_cfg_edge te ON e.ms_id_edge = te.tr_id_edge "
    queryCfgEdge += " WHERE te.tr_id_topik_modul = :idTopikModul "
    queryCfgEdge += "  AND te.tr_id_student = :idUser "
    queryCfgEdge = text(queryCfgEdge)
    dataCfgEdge = conn.execute(queryCfgEdge, idTopikModul=id_topik_modul, idUser=id_user).fetchall()
    #query statistic testcase
    queryTestCase = " SELECT COUNT(*) AS total, "
    queryTestCase += "   SUM(case when tsm.tr_test_result = 'P' then 1 else 0 end) as countPass, "
    queryTestCase += "   SUM(case when tsm.tr_test_result = 'F' then 1 else 0 end) as countFailed "
    queryTestCase += " FROM tr_test_case_modul tsm "
    queryTestCase += " WHERE tsm.tr_id_topik_modul = :idTopikModul "
    queryTestCase += "  AND tsm.tr_student_id = :idUser "
    queryTestCase = text(queryTestCase)
    dataTestCase = conn.execute(queryTestCase, idTopikModul=id_topik_modul, idUser=id_user).fetchone()

    #Query minimum coverage
    query_min_coverage = System.select().where(System.c.ms_system_category=='common',System.c.ms_system_sub_category=='minimum_value', System.c.ms_system_cd == 'coverage')
    dataMinCoverage = conn.execute(query_min_coverage).fetchone()

    response ={"modul_id": id_modul,
               "topik_modul_id": id_topik_modul,
               "status_eksekusi": dataResultTest['tr_status_eksekusi'],
               "coverageScore": dataResultTest['tr_persentase_coverage'],
               "minimum_coverage_score":float(dataMinCoverage['ms_system_value']),
               "point": dataResultTest['tr_nilai'],
               "totalTestCase": dataTestCase['total'],
               "totalPassTestCase": dataTestCase['countPass'],
               "totalFailedTestCase": dataTestCase['countFailed'],
              # "percentPassTestCase": int(dataTestCase['countPass']/dataTestCase['total'])*100,
               "executionDate": dataResultTest['tr_tgl_eksekusi'].strftime('%d %B %Y, %H:%M:%S'),
               "linkReportTesting": dataResultTest['tr_result_report'],
               "linkReportCoverage": dataResultTest['tr_coverage_report'],
               "linkSourceCoverage":"static/"+id_user+"/"+id_topik_modul+"/jacoco_report_test/html/default/"+dataModule['ms_class_name']+".java.html",
               "cfg":{
                   "nodes":dataCfgNode,
                   "edges":dataCfgEdge,
               }}
    return response

# @modul.get("/result_testing")
# async def read_index():
#     return FileResponse('../jacoco-engine/build/reports/tests/test/index.html')