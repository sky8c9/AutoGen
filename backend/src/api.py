import os, tempfile
import numpy as np
import pandas as pd

from fastapi import APIRouter, UploadFile, File, Form
from typing import Annotated
from w2_report import W2Report
from  quarterly_report import QuarterlyReport
from constants import EntityDataSource, PFMLTemplate, EAMSTemplate, W2Template
from models import Entity, UsrSelect
from enum import Enum

class FakeDb:
    def __init__(self):
        self.ein_list = self.legal_name_list = self.dba_list = self.address_list = self.contact_list = []

    def getEntity(self, idx):
        # get up to date data entry and return entry at index idx
        self.getEntityList()
        return [self.ein_list[idx], self.legal_name_list[idx], self.dba_list[idx], self.address_list[idx], self.contact_list[idx]]

    def getEntityList(self):
        # read entity data source file
        df = pd.read_excel("../entity_list.xlsx").to_numpy()

        # preprocess data if needed - delete this part if data already in the right format
        _, entity_payload, _ = np.hsplit(df, EntityDataSource.SPLIT_INDICES)
        entity_payload = entity_payload[entity_payload[:, EntityDataSource.SORT_DEFAULT_COL].argsort()]

        # unpack entity payload
        self.ein_list, self.legal_name_list, self.dba_list, self.address_list, self.contact_list = entity_payload.T

        # set and return entity list
        l = []
        for i in range(len(self.ein_list)):
            e = Entity(
                ein = self.ein_list[i], 
                legal_name = self.legal_name_list[i], 
                dba = self.dba_list[i], 
                address = self.address_list[i], 
                contact = self.contact_list[i]
            )

            l.append(e)
            
        return l

class ReportType(Enum):
    w2 = "W2Report"
    quarterly = "QuarterlyReport"
    
db = FakeDb()
web = APIRouter()

# APIs def
@web.get("/report")
async def loadReport():
    return [report.value for report in ReportType]

@web.get("/entity")
async def loadEntity():
    entity_list = db.getEntityList()
    return entity_list

@web.post("/generator")
async def createTemplate(
    idx: Annotated[int, Form(...)], 
    report: Annotated[str, Form(...)], 
    fileA: Annotated[UploadFile, File(...)], 
    fileB: Annotated[UploadFile, File(...)]
):

    # call generator with uploaded files
    with tempfile.NamedTemporaryFile(delete=False) as td1, tempfile.NamedTemporaryFile(delete=False) as td2:
        contentsA = await fileA.read()
        contentsB = await fileB.read()

        # write content of uploaded files to temp directory
        with open(td1.name, "wb") as writer:
            writer.write(contentsA)
        
        with open(td2.name, "wb") as writer:
            writer.write(contentsB)

        # run template generator
        entity = db.getEntity(idx)
        reportCls = globals()[report]
        res = reportCls(entity, td1, td2).run()

        # remove temp directory
        td1.close()
        os.unlink(td1.name)

        td2.close()
        os.unlink(td2.name)

        # return response
        return res.dict()