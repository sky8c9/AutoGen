from pydantic import BaseModel
from fastapi import UploadFile
from typing import List

class Entity(BaseModel):
    ein: str
    legal_name: str
    dba: str
    address: str
    contact: str

class UsrSelect(BaseModel):
    idx: int
    report: str
    fileA: UploadFile
    fileB: UploadFile

class Report(BaseModel):
    header: List[str]
    entries: List[List[str]]