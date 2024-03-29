import pandas as pd
from abc import abstractclassmethod
from models import Summary

class Report():
    def __init__(self, entity, info_file, earning_file):
        # io 
        self.info_file = info_file
        self.earning_file = earning_file
        self.entity = entity
      
        # data storage
        self.employee_info = dict()
        self.employee_earning = dict()
      
    def run(self):
        # process info
        self.getEmployeeInfo()  
        self.getEmployeeEarning()
        self.genTemplate()

    def createSummary(self, descr, headers, entries):
        # create summary
        return Summary (
            descr = descr,
            headers = headers,
            entries = entries
        )
    
        # add to db
        # Todo

    def appendToFile(self, ofile, data_frame, sheet, start_index):
        with pd.ExcelWriter(ofile, mode='a', if_sheet_exists='overlay') as writer:
            data_frame.to_excel(writer, sheet_name=sheet, header=None, startrow=start_index, index=False)

    def writeToFile(self, ofile, data_frame):
        with pd.ExcelWriter(ofile) as writer:
            data_frame.to_excel(writer, header=None, index=False)

    def toCSV(self, ofile, data_frame):
        data_frame.to_csv(ofile, index=False)

    @abstractclassmethod
    def getEmployeeInfo(self):
        pass

    @abstractclassmethod
    def getEmployeeEarning(self):
        pass

    @abstractclassmethod
    def genTemplate(self):
        pass


    
   
 
  