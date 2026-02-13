from datetime import datetime, date
from models.student import Student
from config.database import conn
from sqlalchemy import select
from jobs.alpa_assigner import alpa_assigner, alpa_assigner_teacher
from jobs.uncomplete_assigner import uncomplete_assigner, uncomplete_teacher_assigner

def schedule_init():
    pass

def schedule_run_uncomplete():
    # dapatkan kalender tanggal sekarang
    pass

def schedule_run_alpha():
    # dapatkan kalender tanggal sekarang
   pass