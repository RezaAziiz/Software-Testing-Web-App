import shutil
from fastapi import APIRouter, Response, status, UploadFile, Depends, Request
from fastapi.responses import FileResponse
from middleware.auth_bearer import JWTBearer
from utilities.utils import getDataFromJwt
import subprocess
from distutils.dir_util import copy_tree
from utilities.graphUtil import Graph
import os   
cfg = APIRouter()

@cfg.get("/cfg", 
          description="Generate cfg data")
async def generateDataCfg():
    
    data = []
    count = 1
    with open("jacoco-engine/src/main/java/com/tutorial/jacoco/User.java","r") as file:
        for line in file:
            data.append({"Line Number ":count, "Source Code": line.replace("\n","")})
            count += 1

    # Create a graph given in the above diagram
    g = Graph(4)
    g.addEdge(0, 1)
    g.addEdge(0, 2)
    g.addEdge(0, 3)
    g.addEdge(2, 0)
    g.addEdge(2, 1)
    g.addEdge(1, 3)
    
    s = 2 ; d = 3
    print ("Following are all different paths from % d to % d :" %(s, d))
    g.printAllPaths(s, d)
    # This code is contributed by Neelam Yadav
    
    return {"data":g}