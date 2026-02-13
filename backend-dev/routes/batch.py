from jobs.uncomplete_assigner import uncomplete_assigner, uncomplete_teacher_assigner
from jobs.alpa_assigner import alpa_assigner, alpa_assigner_teacher
from fastapi import APIRouter, Response, status, UploadFile, Depends, Request, Body, WebSocket

batch = APIRouter(prefix="/batch", tags=["Batch Program"])

@batch.post("/uncomplete/student")
async def uncomplete():
    uncomplete_assigner()

@batch.post("/uncomplete/teacher")
async def uncomplete_teacher():
    uncomplete_teacher_assigner()

@batch.post("/alpha-assigner/student")
async def alpha_assigner():
    alpa_assigner()

@batch.post("/alpha-assigner/teacher")
async def alpha_assigner_teacher():
    alpa_assigner_teacher()