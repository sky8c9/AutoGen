import os, shutil, sys, holidays
import numpy as np
import pandas as pd
from pytz import timezone
from datetime import date, datetime, timedelta
from constants import EFTPSDeposit

'''
    Field position & its length
        0: Batch Filer ID - 9
        1: Master Inquiry PIN - 4
        2: File Date - 8
        3: Filer Sequence Number - 3
        4: Payment Reference Number - 4
        5: Action Code - 1
        6: Taxpayer TIN - 9
        7: Taxpayer PIN - 4
        8: Taxpayer Type - 1
        9: Tax Type Code - 5
        10: Tax Period - 6
        11: Settment Date - 8
        12: Payment Amount - 15

    Notation
        P = Payment
        B = Business, I = Individual
        941 = Tax Form + 05 Tax Deposit Action / 07 Tax Balance Payment
'''

class Deposit():
    def __init__(self):
        self.today = datetime.now(timezone("EST"))
        self.file_date = self.getDateFormat(self.today)
        self.payment_date = self.getEarliestPaymentDate(self.today)

    def genImport(self):
        # read & process input data file
        data = pd.read_excel(EFTPSDeposit.DEPOSIT_FILE, dtype=str).to_numpy()
        record_len = len(data)
        field_len = len(EFTPSDeposit.WIDTHS)

        # set static fields for 941 deposit import file
        field_indices = np.array(np.arange(0, field_len))
        static_vals = ["999999999", " ", self.file_date, "001", "P", "B", "94105", self.payment_date]

        # fill blocks with static & dynamic fields
        mask = np.ones(field_len, bool)
        mask[EFTPSDeposit.STATIC_INDICES] = False
        dynamic_indices = field_indices[mask]
        blocks = np.empty([record_len, field_len], dtype=object)
        for i in range(record_len):
            entity, tin, pin, quarter, amount = data[i]
            quarter = self.getTaxPeriod(int(quarter))
            payment_ref = self.getNumericFormat(i + 1, 4)
            amount = self.getNumericFormat(amount, 15, True)
            
            vals = np.empty(field_len, dtype=object)
            dynamic_vals = [payment_ref, tin, pin, quarter, amount]
            np.put(vals, EFTPSDeposit.STATIC_INDICES, static_vals)
            np.put(vals, dynamic_indices, dynamic_vals)
            info = zip(EFTPSDeposit.WIDTHS, vals)
            for j, (width, val) in enumerate(info):
                blocks[i][j] = np.chararray(width)
                blocks[i][j][:] = list(val)

        self.write2File(blocks)
           
    def getDateFormat(self, date):
        return date.strftime("%Y%m%d")
    
    def getNumericFormat(self, val, len, isFloat=False):
        if isFloat:
            val = int(round(float(val), 2) * 100)
        return str(val).zfill(len)
    
    def getTaxPeriod(self, quarter):
        return f"{self.today.year}{str(int(quarter) * 3).zfill(2)}" 
      
    def getEarliestPaymentDate(self, date):
        # ajust date based on current time
        hour = self.today.hour
        paid_day = date
        if (hour >= EFTPSDeposit.EST_THRESHOLD):
            paid_day += timedelta(1)

        # find earliest payment date
        us_holidays = holidays.UnitedStates()
        while ((paid_day.weekday() >= 5) or (paid_day in us_holidays)):
            paid_day += timedelta(1)

        return self.getDateFormat(paid_day)

    def write2File(self, blocks):
        if not os.path.exists(EFTPSDeposit.OUTPUT_FOLDER):
            os.makedirs(EFTPSDeposit.OUTPUT_FOLDER)

        lines = ""
        for i in range(len(blocks)):
            sequence = b"".join(np.hstack(blocks[i]))
            sequence = str(sequence, encoding="utf-8")
            lines += f"{sequence}\n"
        print(lines)

        fpath = os.path.join(EFTPSDeposit.OUTPUT_FOLDER, f"{self.file_date}_941DepositImport.txt")
        with open(fpath, "w") as output:
            output.write(lines)

if __name__ == "__main__":
    deposit = Deposit()
    deposit.genImport()