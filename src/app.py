import sys
import numpy as np
import pandas as pd
from PyQt5 import QtWidgets
from ui import Ui_MainWindow
from w2_report import W2Report
from  quarterly_report import QuarterlyReport
from constants import EntityDataSource, EFW2Template

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, obj=None, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.ein_list = self.legal_name_list = self.dba_list = self.address_list = self.contact_list = []
        self.aPath = self.bPath = ''

        # load & setup ui components
        self.setupUi(self)
        self.loadEntity2Ui()
        self.setSignal()

    def loadEntity2Ui(self):
        # set default values to ui components
        self.getEntityInfo()
        self.showEntity(0)
        self.W2_Report_RButton.setChecked(True)
        self.Entity_List.addItems(self.ein_list + ' | ' + self.legal_name_list + ' | ' + self.dba_list)

    def setSignal(self):
        # linked event actions
        self.Entity_List.activated.connect(self.showEntity)
        self.Quarterly_Report_RButton.clicked.connect(self.selectQuarterlyReport)
        self.W2_Report_RButton.clicked.connect(self.selectW2Report)
        self.Info_Browse_Button.clicked.connect(self.browseInfo)
        self.Earning_Browse_Button.clicked.connect(self.browseEarning)
        self.Run_Button.clicked.connect(self.run)

    # reuse 941 template data as testing data - TEST ONLY !!!
    def _getEntityInfoTesting(self):
        # read entity data source file
        df = pd.read_excel('../template/941_data_template.xlsx').to_numpy()

        # preprocess data if needed - delete this part if data already in the right format
        _, entity_payload, _ = np.hsplit(df, EntityDataSource.SPLIT_INDICES)
        entity_payload = entity_payload[entity_payload[:, EntityDataSource.SORT_DEFAULT_COL].argsort()]

        # unpack entity payload
        self.ein_list, self.legal_name_list, self.dba_list, self.address_list, self.contact_list = entity_payload.T

    def getEntityInfo(self):
        # read & unpack entity payload
        entity_payload = pd.read_excel(EntityDataSource.ENTITY_SOURCE_FILE).to_numpy()
        entity_payload = entity_payload[entity_payload[:, EntityDataSource.SORT_DEFAULT_COL].argsort()]
        self.ein_list, self.legal_name_list, self.dba_list, self.address_list, self.contact_list = entity_payload.T

    def showEntity(self, idx):
        # define what to display
        ein_str = f'EIN: {self.ein_list[idx]}\n'
        legal_name_str = f'Entity: {self.legal_name_list[idx]}\n' 
        dba_name_str = f'DBA: {self.dba_list[idx]}\n'
        address_str = f'Address: {self.address_list[idx]}\n'
        contact_str = f'Contact: {self.contact_list[idx]}\n'

        # display entity info
        txt = '\n'.join([ein_str, legal_name_str, dba_name_str, address_str, contact_str])
        self.Summary_Text.setText(txt)

    def _selectFile(self):
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Single File', '', '*.csv')
        return fileName
    
    def selectW2Report(self):
        print('select w2 report')

    def selectQuarterlyReport(self):
        print('select quarterly report')

    def browseInfo(self):
        self.aPath = self._selectFile()
        self.Info_Path.setText(self.aPath)

    def browseEarning(self):
        self.bPath = self._selectFile()
        self.Earning_Path.setText(self.bPath)

    def inform(self, message, icon):
        # send message to dialog box
        msg = QtWidgets.QMessageBox()
        msg.setIcon(icon)
        msg.setText(message)
        msg.exec()

    def run(self):
        try:
            # get selected entity and change data format to match template
            idx = self.Entity_List.currentIndex()
            entity = [self.ein_list[idx], self.legal_name_list[idx], self.dba_list[idx], self.address_list[idx], self.contact_list[idx]]

            # build template
            if self.W2_Report_RButton.isChecked() == True:
                W2Report(entity, self.aPath, self.bPath).run()
                self.inform('Finished !!!', QtWidgets.QMessageBox.Information)
            elif self.Quarterly_Report_RButton.isChecked() == True:
                summary = QuarterlyReport(entity, self.aPath, self.bPath).run()
                self.inform(summary, QtWidgets.QMessageBox.Information)

        except Exception as e:
            if self.aPath == '' or self.bPath == '': # empty file
                self.inform('Missing file !!!', QtWidgets.QMessageBox.Critical)
            else: # file error
                self.inform('Check input file & report type !!!', QtWidgets.QMessageBox.Critical)
                print(e)
            return

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    window = MainWindow()
    window.show()

    app.exec()