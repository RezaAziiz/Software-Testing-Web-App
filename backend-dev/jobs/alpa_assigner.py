from datetime import datetime, date
from models.student import Student
from models.teacher import Teacher
from config.database import conn
from sqlalchemy import select
from sqlalchemy.sql import text
import uuid

def alpa_assigner():
    print("running alpa assigner job")
   

def alpa_assigner_teacher():
    print("running alpa assigner teacher job")
  