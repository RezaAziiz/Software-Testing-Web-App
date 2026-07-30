import logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s:     %(message)s")

import sys
import asyncio
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    import uvicorn.config
    uvicorn.config.Config.setup_event_loop = lambda self: asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from routes.auth import auth
from routes.cfg import cfg
from routes.student import student
from routes.teacher import teacher
from routes.batch import batch
from routes.modul import modul
from routes.topik import topik
from routes.combo import combo
from routes.grade import grade
from routes.progress import progress
from infrastructure.file_storage import FileStorageManager
from config.database import Base, engine

from jobs.schedule import schedule_init, schedule_run_uncomplete, schedule_run_alpha
from jobs.train_model import run_train_model
from decouple import config
from apscheduler.schedulers.background import BackgroundScheduler
import uvicorn
import locale
import os
try:
    locale.setlocale(locale.LC_ALL, 'id_ID.utf8')
except locale.Error:
    try:
        locale.setlocale(locale.LC_ALL, 'id_ID.UTF-8')
    except locale.Error:
        locale.setlocale(locale.LC_ALL, '')

app = FastAPI(docs_url="/doc")

@app.on_event("startup")
def configure_thread_pool():
    import anyio
    limiter = anyio.to_thread.current_default_thread_limiter()
    limiter.total_tokens = 500
def cors_headers(app):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[config('API_FR', default='http://localhost:5173')],
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=True,
        expose_headers=["X-Already-Logged-In"],
    )
    return app


app.include_router(auth)
app.include_router(student)
app.include_router(teacher)

# app.include_router(batch)
app.include_router(modul)
app.include_router(topik)
app.include_router(combo)
app.include_router(grade)
app.include_router(progress)
# app.include_router(cfg)

app = cors_headers(app)

if not os.path.exists("static"):
        os.makedirs("static")

file_manager = FileStorageManager()

@app.get("/static/{file_path:path}")
async def serve_static(file_path: str):
    # Intercept requests for JaCoCo resources (CSS/JS/images)
    # They are static and bundled in the app, no need to fetch from GCS
    if "jacoco-resources" in file_path:
        filename = os.path.basename(file_path)
        bundled_resource_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "jacoco-resources", filename))
        if os.path.exists(bundled_resource_path) and not os.path.isdir(bundled_resource_path):
            return FileResponse(bundled_resource_path)

    try:
        local_path = file_manager.ensure_static_file(file_path)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Not Found")

    if os.path.isdir(local_path):
        raise HTTPException(status_code=404, detail="Not Found")

    return FileResponse(local_path)

@app.get("/")
async def root():
    return {"message": "SAS API version 1.1"}

# Batch Proses run example
# @app.on_event('startup')
# def init_data():
#     schedule_init()

#     scheduler = BackgroundScheduler()
#     # scheduler.add_job(schedule_run, 'cron', hour='*') # every hour
#     # run schedule every 1 night a clock
#     scheduler.add_job(run_train_model, 'cron', hour='01', minute='00')
#     scheduler.add_job(schedule_run_uncomplete, 'cron', hour='01', minute='00')
#     scheduler.add_job(schedule_run_alpha, 'cron', hour='21', minute='00')
#     # scheduler.add_job(schedule_run_alpha, 'cron', hour='14', minute='28')
#     scheduler.start()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get('PORT', config('PORT_APP', default='8080'))))
