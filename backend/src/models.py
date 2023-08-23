from pydantic import BaseModel
from fastapi import UploadFile
from typing import List, Optional

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

class Summary(BaseModel):
    descr: str
    headers: List[List[Optional[str]]]
    entries: List[List[List[Optional[str]]]]