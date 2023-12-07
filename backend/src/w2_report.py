import os, shutil
import numpy as np
import pandas as pd
from constants import EarningSummary, W2Template, EFW2Template
from collections import defaultdict
from report import Report

class W2Report(Report):
    def __init__(self, entity, info_file, earning_file):
        super().__init__(entity, info_file, earning_file)

        # w2 & efw2 params
        self.w2_employee_record = dict()
        self.efw2_employee_record = dict()
        self.w2_employer_record = None
        self.efw2_employer_record = None

        # 940 FUTA params
        self.total_payment = 0
        self.excess_payment = 0

    def run(self):
        super().run()

        # 940 FUTA summary
        futa_line3 = f'FUTA Line 3: ${round(self.total_payment, 2)}\n'
        futa_line5 = f'FUTA Line 5: ${round(self.excess_payment, 2)}\n'
        summary_txt = '\n'.join([futa_line3, futa_line5])

        # create w2 report - convert dict values to list
        w2_record = [entry.tolist() for entry in self.w2_employee_record.values()] 
        w2_col_titles = self.getRecordTitle(W2Template.TEMPLATE_FILE, W2Template.EMPLOYEE_SHEET)

        efw2_record = [entry.tolist() for entry in self.efw2_employee_record.values()]
        efw2_col_titles = self.getRecordTitle(EFW2Template.TEMPLATE_FILE, EFW2Template.EMPLOYEE_SHEET)

        return self.createSummary(summary_txt, [w2_col_titles, efw2_col_titles], [w2_record, efw2_record])

    def getRecordLength(self, template, sheet):
        return len(pd.read_excel(template, sheet_name=sheet).columns)
    
    def getRecordTitle(self, template, sheet):
        df = pd.read_excel(template, sheet)
        return list(df.head())
    
    def genTemplate(self):
        self.processEmployeeRecord()
        self.processEmployerRecord()
        
        ein, legal_name, dba, address, contact = self.entity
        w2_oname = f'w2_{legal_name}({dba})_filled'
        efw2_oname = f'efw2_{legal_name}({dba})_filled'

        self.createTemplate(w2_oname, W2Template, self.w2_employee_record, self.w2_employer_record)
        self.createTemplate(efw2_oname, EFW2Template, self.efw2_employee_record, self.efw2_employer_record)

    def createTemplate(self, oname, template_cls, employees_record, employer_record):
        if not os.path.exists(template_cls.OUTPUT_FOLDER):
            os.makedirs(template_cls.OUTPUT_FOLDER)

        # clone template & write employee and employer data to template
        ofile = f'{template_cls.OUTPUT_FOLDER}/{oname}_template.xlsx'
        shutil.copy(template_cls.TEMPLATE_FILE, ofile)

        employee_df = pd.DataFrame(employees_record.values())
        self.appendToFile(ofile, employee_df, template_cls.EMPLOYEE_SHEET, template_cls.SHEET_START_INDEX)

        employer_df = pd.DataFrame([employer_record])
        self.appendToFile(ofile, employer_df, template_cls.EMPLOYER_SHEET, template_cls.SHEET_START_INDEX)

    def processEmployerRecord(self):
        # decompose entity info
        ein, legal_name, dba, address, contact = self.entity
        address_first, address_second = address.split(', ', 1)

        # w2 employer record 
        w2_info = '\n'.join([legal_name, address_first, address_second])
        w2_employer_record_len = self.getRecordLength(W2Template.TEMPLATE_FILE, W2Template.EMPLOYER_SHEET)
        self.w2_employer_record= np.empty(w2_employer_record_len, dtype=object)
        w2_employer_payload = [ein, w2_info]
        np.put(self.w2_employer_record, W2Template.EMPLOYER_INFO_INDICES, w2_employer_payload)

        # efw2 employer record        
        efw2_ein = ''.join(ein.split('-'))
        location, city, state, zip = address.split(', ')
        contact_name, _, contact_phone = contact.split(', ')
        contact_phone = ''.join(contact_phone.split('-'))
        efw2_employer_record_len = self.getRecordLength(EFW2Template.TEMPLATE_FILE, EFW2Template.EMPLOYER_SHEET)
        self.efw2_employer_record = np.empty(efw2_employer_record_len, dtype=object)
        efw2_employer_payload = ['RE', EFW2Template.TAX_YEAR, efw2_ein, 0, legal_name, location, city, state, zip, 'N', 'R', contact_name, contact_phone]
        np.put(self.efw2_employer_record, EFW2Template.EMPLOYER_INFO_INDICES, efw2_employer_payload)
    
    def getEmployeeInfo(self):
        # create & store employee info dictionary for w2_template & efw2_template
        records = pd.read_csv(self.info_file, dtype=str).fillna('').to_numpy()
        for record in records: 
            ssn, first_name, middle_initial, last_name, dob, title, pfml_exempt, addr1, addr2, city, state, zip = record
            full_name = ' '.join([first_name, middle_initial, last_name])
            ssn_efw2 = ''.join(ssn.split('-'))
            w2_info_payload = [ssn, f'{full_name}\n{addr1} {addr2}\n{city}, {state}, {zip}']
            efw2_info_payload = ['RW', ssn_efw2, first_name, middle_initial, last_name, addr1, city, state, zip]
            
            info = dict()
            info[W2Template.ID] = w2_info_payload
            info[EFW2Template.ID] = efw2_info_payload
            self.employee_info[ssn] = info

    def getEmployeeEarning(self):
        # read input file dataframe and trim off total summary column and row
        df = pd.read_csv(self.earning_file)
        col_names = list(df.columns[:-1])  
        records = df.to_numpy()[:-1, :-1]

        # process employee earning record
        for record in records:
            ssn = record[0].split(' ')[-1]
            summary = defaultdict(float)
            for i in range(1, len(record)):
                col_name = col_names[i].lower()
                val = abs(record[i])

                # earning cell
                if record[i] > 0:
                    if EarningSummary.TIPS_EARNING in col_name:
                        summary[EarningSummary.TIPS_EARNING] += val 
                        continue
                    else:
                        summary[EarningSummary.OTHER_EARNING] += val
                        continue

                # tax cell
                for keyword in EarningSummary.FED_TAX_KEYWORDS:
                    if keyword in col_name:
                        summary[keyword] += val

            self.employee_earning[ssn] = summary

    def computeYearlyEarning(self, ssn):
        # modify earning calculations as needed
        other_earning = self.employee_earning[ssn][EarningSummary.OTHER_EARNING]
        tips = self.employee_earning[ssn][EarningSummary.TIPS_EARNING]
        total_earning = other_earning + tips
        ss_wage = total_earning - tips
        med_wage = total_earning

        # 940 FUTA computation
        self.total_payment += total_earning
        self.excess_payment += max(0, total_earning - EarningSummary.FUTA_THRESHOLD)

        # return earnings payload
        earning_payload = [total_earning, ss_wage, med_wage, tips]
        fed_payload = [self.employee_earning[ssn][EarningSummary.FED_TAX_KEYWORDS[i]] for i in range(len(EarningSummary.FED_TAX_KEYWORDS))]
        earning_payload = list(map(lambda x : '{:.2f}'.format(x), earning_payload))
        fed_payload = list(map(lambda x : '{:.2f}'.format(x), fed_payload))
        return earning_payload, fed_payload
    
    def processEmployeeRecord(self):
        w2_employee_record_len = self.getRecordLength(W2Template.TEMPLATE_FILE, W2Template.EMPLOYEE_SHEET)
        efw2_employee_record_len = self.getRecordLength(EFW2Template.TEMPLATE_FILE, EFW2Template.EMPLOYEE_SHEET)
       
        # process employee
        for ssn in self.employee_earning:
            self.w2_employee_record[ssn] = np.empty(w2_employee_record_len, dtype=object)
            self.efw2_employee_record[ssn] = np.empty(efw2_employee_record_len, dtype=object)

            # set employee info
            np.put(self.w2_employee_record[ssn], W2Template.EMPLOYEE_INFO_INDICES, self.employee_info[ssn][W2Template.ID])
            np.put(self.efw2_employee_record[ssn], EFW2Template.EMPLOYEE_INFO_INDICES, self.employee_info[ssn][EFW2Template.ID])

            # set employee earning
            earning_payload, fed_payload = self.computeYearlyEarning(ssn)
            np.put(self.w2_employee_record[ssn], W2Template.EARNING_SUMMARY_INDICES, earning_payload)
            np.put(self.w2_employee_record[ssn], W2Template.FED_TAX_INDICES, fed_payload)
            np.put(self.efw2_employee_record[ssn], EFW2Template.EARNING_SUMMARY_INDICES, earning_payload)
            np.put(self.efw2_employee_record[ssn], EFW2Template.FED_TAX_INDICES, fed_payload)

if __name__ == "__main__":
    # quick test goes here
    entity = ['11-1111111', 'ABC LLC', 'ABC', '123 AVE NE, NEW YORK, NY, 23456', 'Dr Zzz, Owner, 211-111-1111']
    test = W2Report(entity, '../sample/w2_info_file.CSV', '../sample/w2_earning_file.CSV')
    test.run()