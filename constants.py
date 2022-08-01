class Table:
    TABLE_LOC = ['50, 690, 690, 50']
    INFO_COL = 0
    PAYROLL_ITEM_COL = 1
    HOUR_COL = 2
    AMOUNT_COL = 3 

class KeyWord:
    EMPLOYEE_SEPARATOR = 'Total'
    OFFICER_SALARY = 'salary'
    HOURLY = 'hourly'

class MedLeaveReport:
    COL_LABELS = ['SSN', 'LastName', 'FirstName', 'MiddleInitial', 'Hours', 'Wages', 'WACaresExempt(Y/N)']
    EXCL_LIST = ['tip']
    MED_LEAVE_RATE = 0.006

class EamsReport:
    COL_LABELS = ['SSN', 'LastName', 'FirstName', 'MiddleName', 'Suffix', 'Hours', 'Wages', 'SOC']
    EXCL_LIST = ['sick']

class LnIReport:
    WORKED_LIST = ['overtime', 'wage']

class Summary:
    COL_LABELS = ['Company', 'Med Leave Wages', 'Med Leave Premium', 'LnI Wages', 'LnI Hours']

class IO:
    Input = 'INPUT'
    EAMS = 'EAMS'
    Med_Leave = 'MED_LEAVE'
    Folders = [Input, EAMS, Med_Leave]


