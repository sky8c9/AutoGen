import os, shutil
import concurrent.futures
import camelot
import numpy as np
import pandas as pd
from constants import IO, Table, KeyWord, MedLeaveReport, EamsReport, LnIReport, Summary
from re import search

class Report():
    def __init__(self, fileName):
        self.fileName = fileName
        self.company_name = fileName.split('/')[1]
        self.total_med_wages = 0
        self.total_lni_wages = 0
        self.total_lni_hours = 0
        self.medReportDf = pd.DataFrame(columns=MedLeaveReport.COL_LABELS)
        self.eamsReportDf = pd.DataFrame(columns=EamsReport.COL_LABELS)

    def gen(self):
        self.addEmployee(self.fileName)
        self.medLeaveReportGen()
        self.eamsReportGen()

    def addEmployee(self, fname):
        # Extract dataframes from multiple pages
        tables = camelot.read_pdf(fname, flavor='stream', pages='all', table_areas=Table.TABLE_LOC)
        
        # Loop through each table
        for table in tables:
            df = table.df

            # print(df)
            
            # Convert payroll items to lower case, hour and amount column to numeric data format
            df[Table.PAYROLL_ITEM_COL] = df[Table.PAYROLL_ITEM_COL].str.lower()
            df[Table.HOUR_COL] = pd.to_numeric(df[Table.HOUR_COL].str.replace(',','')).fillna(0)
            df[Table.AMOUNT_COL] = pd.to_numeric(df[Table.AMOUNT_COL].str.replace(',','')).fillna(0)

            # Process all row - except the final summary row
            i = 0
            while(i < len(df) - 1):
                med_leave_excl_wage = 0
                eams_excl_wage = 0
                eams_excl_hour = 0
                lni_worked_hours = 0
                addToReport = True
                total_hours = 0

                # Process employee info
                fName, mName, lName = self.getName(df.iloc[i][Table.INFO_COL])
                ssn = df.iloc[i+1][Table.INFO_COL]
            
                # Process payroll items
                while(not (KeyWord.EMPLOYEE_SEPARATOR in df.iloc[i][Table.INFO_COL])):                    
                    # Skip corporate officer salary
                    if KeyWord.OFFICER_SALARY in df.iloc[i][Table.PAYROLL_ITEM_COL]:
                        addToReport = False

                    # Medical Leave excluding list running sum
                    if self.contains(df.iloc[i][Table.PAYROLL_ITEM_COL], MedLeaveReport.EXCL_LIST):
                        med_leave_excl_wage +=df.iloc[i][Table.AMOUNT_COL]

                    # EAMS excluding list running sum
                    if self.contains(df.iloc[i][Table.PAYROLL_ITEM_COL], EamsReport.EXCL_LIST):
                        eams_excl_hour += df.iloc[i][Table.HOUR_COL]
                        eams_excl_wage += df.iloc[i][Table.AMOUNT_COL]

                    # Update hours based on selection criteria
                    hr = df.iloc[i][Table.HOUR_COL] 
                    total_hours += hr
                    if self.contains(df.iloc[i][Table.PAYROLL_ITEM_COL], LnIReport.WORKED_LIST):
                        lni_worked_hours += hr
                    
                    i+=1    

                if addToReport:
                    # Update wages and hours of current employee
                    eams_wages = df.iloc[i][Table.AMOUNT_COL] - eams_excl_wage
                    med_wages = df.iloc[i][Table.AMOUNT_COL] - med_leave_excl_wage
                    eams_hours = total_hours - eams_excl_hour

                    # Update total
                    self.total_med_wages += med_wages
                    self.total_lni_wages += lni_worked_hours
                    self.total_lni_hours += lni_worked_hours

                    # Append fields to dataframe
                    EamsNameConvention = lName.replace(' ', '-') + ', ' + fName.replace(' ', '-') + ' ' + mName
                    self.eamsReportDf.loc[len(self.eamsReportDf)] = [ssn, EamsNameConvention, lName, fName, mName, '', eams_hours, eams_wages, '']
                    self.medReportDf.loc[len(self.medReportDf)] = [ssn, lName, fName, mName, total_hours, med_wages, 'N']

                i+=1

    def contains(self, s, items):
        for item in items:
            if item in s:
                return True
        return False

    def getName(self, name):
        # Split input name and find location of middle initial
        l = name.split(' ')
        last_name = l[-1]
        mIndex =  [i for i, s in enumerate(l) if len(s) == 1] 

        if len(mIndex) > 0: # case when there is middle initial
            first_name = l[:mIndex[0]]
            middle_initial = l[mIndex[0]]
        else: # otherwise
            first_name = l[:-1]
            middle_initial = ''
    
        return ' '.join(first_name), middle_initial, last_name

    def medLeaveReportGen(self):
        # Format med leave report and output csv
        self.medReportDf['Wages'] = self.medReportDf['Wages'].round(2)
        self.medReportDf['Hours'] = self.medReportDf['Hours'].apply(np.round).astype(int)
        self.medReportDf.to_csv(f'{IO.Med_Leave}/{self.company_name} - MedLeave.csv', float_format='%.2f', index=False)

    def eamsReportGen(self):
        # Format eams report and output csv
        self.eamsReportDf['Wages'] = self.eamsReportDf['Wages'].round(2)
        self.eamsReportDf['Hours'] = self.eamsReportDf['Hours'].apply(np.round).astype(int)
        self.eamsReportDf[['SSN', 'EamsNameConvention', 'Hours', 'Wages']].to_csv(f'{IO.EAMS}/{self.company_name} - EAMS.csv', float_format='%.2f', header=None, index=False)

def createReportFolder(folders):
    for folder in folders:
        if not os.path.exists(folder):
            os.makedirs(folder)
        elif folder != IO.Input:
            # Wipe out old report files
            for files in os.listdir(folder):
                path = os.path.join(folder, files)
                try:
                    shutil.rmtree(path)
                except OSError:
                    os.remove(path)

def createSummary(entries):
    summary = pd.DataFrame(columns=Summary.COL_LABELS)
    for entry in entries:
        summary.loc[len(summary)] = entry
    summary.to_csv('Summary.csv', float_format='%.2f', header=None, index=False)

def main():
    createReportFolder(IO.Folders)    

    # Assign worker and compute
    tasks = []
    for file in os.listdir(IO.Input):
        tasks.append(Report(f'{IO.Input}/{file}'))

    with concurrent.futures.ThreadPoolExecutor() as executor:
        for idx, task in enumerate(tasks):
            executor.submit(task.gen)

    # Summary Report
    entries = [[task.company_name, task.total_med_wages, task.total_lni_wages, task.total_lni_wages * MedLeaveReport.MED_LEAVE_RATE, task.total_lni_hours] for task in tasks]
    createSummary(entries)

if __name__ == "__main__":
	main()
