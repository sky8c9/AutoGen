import os
import numpy as np
import pandas as pd
from constants import EarningSummary, PFMLTemplate, EAMSTemplate
from report import Report

class QuarterlyReport(Report):
    def __init__(self, entity, info_file, earning_file):
        super().__init__(entity, info_file, earning_file)

        # summary data storage
        self.total_med_wage = 0
        self.total_care_wage = 0
        self.total_lni_wage = 0
        self.total_lni_hour = 0

        # earning summary records
        self.eams_employee_record = dict()
        self.pfml_employee_record = dict()

    def run(self):
        super().run()

        # summary report
        pfml_tax = f'Med Pay: ${round(self.total_med_wage * PFMLTemplate.PFML_TAX_RATE, 2)}\n' if (len(self.pfml_employee_record) >= PFMLTemplate.EMPLOYEE_SIZE_THRESHOLD) else f'Med Pay: ${round(self.total_med_wage * PFMLTemplate.PFML_TAX_RATE * (1 - PFMLTemplate.EMPLOYER_SHARE), 2)}\n'
        cares_fund_tax = f'Cares Fund: ${round(self.total_care_wage * PFMLTemplate.CARES_FUND_TAX_RATE, 2)}\n'
        lni_wage = f'Total LnI Wage: ${round(self.total_lni_wage)}\n'
        lni_hour = f'Total LnI Hour: {round(self.total_lni_hour)}\n'
        summary_txt = '\n'.join([pfml_tax, cares_fund_tax, lni_wage, lni_hour])

        # create report - convert dict values to list
        eams_record = [entry.tolist() for entry in self.eams_employee_record.values()] 
        pfml_record = [entry.tolist() for entry in self.pfml_employee_record.values()]
        return self.createSummary(summary_txt, [EAMSTemplate.COL_TITLE, PFMLTemplate.COL_TITLE], [eams_record, pfml_record])
    
    def contains(self, s, items):
        for item in items:
            if item in s:
                return True
        return False
    
    def genTemplate(self):
        ein, legal_name, dba, address, contact = self.entity
        eams_oname = f'eams_{legal_name}({dba})_filled'
        pfml_oname = f'pfml_{legal_name}({dba})_filled'

        self.processEmployeeRecord()
        self.createTemplate(eams_oname, EAMSTemplate, self.eams_employee_record)
        self.createTemplate(pfml_oname, PFMLTemplate, self.pfml_employee_record)

    def createTemplate(self, oname, template_cls, employee_record):
        if not os.path.exists(template_cls.OUTPUT_FOLDER):
            os.makedirs(template_cls.OUTPUT_FOLDER)

        # write employee data to an empty template file
        ofile = f'{template_cls.OUTPUT_FOLDER}/{oname}_template.CSV'
        employee_df = pd.DataFrame(employee_record.values(), columns=template_cls.COL_TITLE)
        self.toCSV(ofile, employee_df)

    def getEmployeeInfo(self):
        # create & store employee info dictionary for eams template & pfml template
        records = pd.read_csv(self.info_file).fillna('').astype(str).to_numpy()
        for record in records: 
            ssn, first_name, middle_initial, last_name, dob, title, pfml_exempt, addr1, addr2, city, state, zip = record
            middle_initial = middle_initial[0] if len(middle_initial) > 0 else ''

            eams_info_payload = [ssn, last_name, first_name, middle_initial, '', title]
            pfml_info_payload = [ssn, last_name, first_name, middle_initial, pfml_exempt, dob]

            info = dict()
            info[EAMSTemplate.ID] = eams_info_payload
            info[PFMLTemplate.ID] = pfml_info_payload
            self.employee_info[ssn] = info

    def getEmployeeEarning(self):
        record = pd.read_csv(self.earning_file).fillna('').astype(str).to_numpy()
        info, payroll_item, hour, wage = np.hsplit(record, np.size(record, 1))

        info = np.hstack(info)
        payroll_item = list(map(lambda x : x.lower(), np.hstack(payroll_item)))
        hour = list(map(lambda x : 0 if x == '' else float(x), np.hstack(hour)))
        wage = list(map(lambda x : 0 if x == '' else float(x), np.hstack(wage)))

        i = 0
        while(i < len(record) - 1):
            med_leave_excl_wage = 0
            eams_excl_wage = 0
            eams_excl_hour = 0
            lni_worked_hours = 0
            total_hours = 0
            flag = True

            # Process payroll items
            ssn = info[i].split(' ')[-1]
            while(not (EarningSummary.EMPLOYEE_SEPARATOR in info[i])):                
                # Other non tracking earning type
                if self.contains(payroll_item[i], EarningSummary.OTHER_LIST):
                    flag = False

                # PFML excluding list running sum
                if self.contains(payroll_item[i], PFMLTemplate.EXCL_LIST):
                    med_leave_excl_wage += wage[i]

                # EAMS excluding list running sum
                if self.contains(payroll_item[i], EAMSTemplate.EXCL_LIST):
                    eams_excl_hour += hour[i]
                    eams_excl_wage += wage[i]

                # LnI hour and wage
                if self.contains(payroll_item[i], EarningSummary.WORKED_LIST):
                    lni_worked_hours += hour[i]

                # Add to total hour
                total_hours += hour[i]

                i+=1
            
            # PFML & Cares fund report
            med_wages = wage[i] - med_leave_excl_wage
            self.total_med_wage += med_wages
            exempt_status = self.employee_info[ssn][PFMLTemplate.ID][4]
            if exempt_status.lower() != 'y':
                self.total_care_wage += med_wages           
            pfml_earning_payload = [round(total_hours) if flag else EarningSummary.FIXED_HOUR, '{:.2f}'.format(med_wages)]

            # EAMS report
            eams_wages = wage[i] - eams_excl_wage
            eams_hours = total_hours - eams_excl_hour
            eams_earning_payload = [round(eams_hours), '{:.2f}'.format(eams_wages)] if flag else None
            
            # LnI report
            self.total_lni_wage += wage[i] if flag else 0
            self.total_lni_hour += lni_worked_hours if flag else 0

            # Add to earning Summary
            earning = dict()
            earning[PFMLTemplate.ID] = pfml_earning_payload
            earning[EAMSTemplate.ID] = eams_earning_payload
            self.employee_earning[ssn] = earning         
          
            i+=1

    def processEmployeeRecord(self):
        eams_employee_record_len = len(EAMSTemplate.COL_TITLE)
        pfml_employee_record_len = len(PFMLTemplate.COL_TITLE)

        # process employee
        for ssn in self.employee_earning:
            # set employee info & earning
            if self.employee_earning[ssn][EAMSTemplate.ID]:
                self.eams_employee_record[ssn] = np.empty(eams_employee_record_len, dtype=object)
                np.put(self.eams_employee_record[ssn], EAMSTemplate.EMPLOYEE_INFO_INDICES, self.employee_info[ssn][EAMSTemplate.ID])
                np.put(self.eams_employee_record[ssn], EAMSTemplate.EARNING_SUMMARY_INDICES, self.employee_earning[ssn][EAMSTemplate.ID])
            if self.employee_earning[ssn][PFMLTemplate.ID]:
                self.pfml_employee_record[ssn] = np.empty(pfml_employee_record_len, dtype=object)
                np.put(self.pfml_employee_record[ssn], PFMLTemplate.EMPLOYEE_INFO_INDICES, self.employee_info[ssn][PFMLTemplate.ID])
                np.put(self.pfml_employee_record[ssn], PFMLTemplate.EARNING_SUMMARY_INDICES, self.employee_earning[ssn][PFMLTemplate.ID])

if __name__ == "__main__":
    # quick test goes here
    entity = ['11-1111111', 'ABC LLC', 'ABC', '123 AVE NE, NEW YORK, NY, 23456', 'Dr Zzz, Owner, 211-111-1111']
    test = QuarterlyReport(entity, '../sample/quarter_info_file.CSV', '../sample/quarter_earning_file.CSV')
    test.run()