from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
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

from jobs.schedule import schedule_init, schedule_run_uncomplete, schedule_run_alpha
from jobs.train_model import run_train_model
from decouple import config
from apscheduler.schedulers.background import BackgroundScheduler
import uvicorn
import locale
import os
locale.setlocale(locale.LC_ALL, 'id_ID.utf8')

app = FastAPI(docs_url="/doc")

def cors_headers(app):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=True,
        expose_headers=["X-Already-Logged-In"],
    )
    return app


app.include_router(auth)
app.include_router(student)
# app.include_router(teacher)

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

app.mount("/static", StaticFiles(directory="static"), name="static")
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
    uvicorn.run(app, host="0.0.0.0", port=config('PORT_APP'))
