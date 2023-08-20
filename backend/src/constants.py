class EarningSummary:
    # W2 earning report keywords
    FED_TAX_KEYWORDS = ['federal', 'social', 'medicare']
    OTHER_EARNING = 'earning'
    TIPS_EARNING = 'tips'

    # Quaterly earning report keywords
    EMPLOYEE_SEPARATOR = 'Total'
    HOURLY = 'hourly'
    WORKED_LIST = ['overtime', 'wage']
    OTHER_LIST = ['salary']

    # Fixed hour 
    FIXED_HOUR = 480

class EntityDataSource:
    # Entity list
    ENTITY_SOURCE_FILE = '../sample/sample_entity_list.xlsx'

    # Use for 941 template data preprocessing
    SORT_DEFAULT_COL = 2
    SPLIT_INDICES = [2, 7]

class Template:
    TEMPLATE_FILE = ''
    ID = ''
    OUTPUT_FOLDER = ''
    SHEET_START_INDEX = 2
    TAX_YEAR = 2023

class W2Template(Template):
    TEMPLATE_FILE = '../template/w2_data_template.xlsx'
    ID = 'W2'
    OUTPUT_FOLDER = '../w2_template_out'

    # Sheet info
    EMPLOYER_SHEET = 'Employer'
    EMPLOYEE_SHEET = 'Employee'

    # Info section
    EMPLOYER_INFO_INDICES = EMPLOYEE_INFO_INDICES = [0, 1]

    # Earning & tax section
    FED_TAX_INDICES = [4, 6, 8]
    EARNING_SUMMARY_INDICES = [3, 5, 7, 9]

class EFW2Template(Template):
    TEMPLATE_FILE = '../template/EFW2_template.xlsx'
    ID = 'EFW2'
    OUTPUT_FOLDER = '../efw2_template_out'

    # Sheet info
    EMPLOYER_SHEET = 'RE_RECORD'
    EMPLOYEE_SHEET = 'RW_RECORD'

    # Prefill RA_RECORD with submitter info before running the program
    EMPLOYER_INFO_INDICES = [0, 1, 3, 5, 8, 9, 11, 12, 13, 15, 20, 23, 24]
    EMPLOYEE_INFO_INDICES = [0, 1, 2, 3, 4, 6, 8, 9 ,10]

    # Mapping between efw2 and w2 indices - shift w2 indices by 13 
    FED_TAX_INDICES = [idx + 13 for idx in W2Template.FED_TAX_INDICES]
    EARNING_SUMMARY_INDICES = [idx + 13 for idx in W2Template.EARNING_SUMMARY_INDICES]

class PFMLTemplate(Template):
    ID = 'PFML'
    OUTPUT_FOLDER = '../med_template_out'

    EMPLOYER_SHARE = 0.2724
    EMPLOYEE_SIZE_THRESHOLD = 50
    PFML_TAX_RATE = 0.008
    CARES_FUND_TAX_RATE = 0.0058

    COL_TITLE = ['SSN', 'LastName', 'FirstName', 'MiddleInitial', 'Hours', 'Wages', 'WACaresExempt(Y/N)', 'DOB']
    EXCL_LIST = ['tip']

    EMPLOYEE_INFO_INDICES = [0, 1, 2, 3, 6, 7]
    EARNING_SUMMARY_INDICES = [4, 5]

class EAMSTemplate(Template):
    # SSN, LastName, FirstName, MiddleName, Suffix, Hours, Wages
    ID = 'EAMS'
    OUTPUT_FOLDER = '../eams_template_out'
    
    COL_TITLE = ['SSN', 'LastName', 'FirstName', 'MiddleName', 'Suffix', 'Hours', 'Wages', 'SOC']
    EXCL_LIST = ['sick']

    EMPLOYEE_INFO_INDICES = [0, 1, 2, 3, 4, 7]
    EARNING_SUMMARY_INDICES = [5, 6]

    
