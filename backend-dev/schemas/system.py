# schemas/system.py
from datetime import date
from pydantic import BaseModel, Field
from typing import List

class SystemSchema(BaseModel):
    ms_system_value: str