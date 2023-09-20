import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font
from openpyxl.utils.dataframe import dataframe_to_rows

input_file='from json to csv/results/return_results/results_1.csv'

df = pd.read_csv(input_file)

grouped = df.groupby('UnitID')

workbook = Workbook()

sheet = workbook.active

headers = ['UnitID', 'Frequency of CommSet', 'Frequency of Boot', 'Frequency of Fatal Error']
sheet.append(headers)

for unit, data in grouped:
    frequency_commReset = data[data[' Type'] == 'CommReset'].shape[0]
    frequency_boot = data[data[' Type'] == 'Boot'].shape[0]
    frequency_fatal_error = data[data[' Reset Reason'] == 'Fatal'].shape[0]
    row = [unit, frequency_commReset, frequency_boot,frequency_fatal_error]
    sheet.append(row)

workbook.save('from csv to excel/test_output.xlsx')