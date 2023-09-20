import json
import pandas as pd
from openpyxl import Workbook
from collections import defaultdict

input_file = 'random/devicelog_snip.json'

# Initialize dictionaries for frequency counts
commReset_frequency = {}
boot_frequency = {}
fatal_error_frequency = {}

with open(input_file, 'r') as f:
    for line in f:
        json_obj = json.loads(line)

        unit_id = json_obj['UnitID']
        type_value= json_obj['Type'].get('Type', '')
        reset_reason = json_obj['Payload'].get('ResetReason', '')
        
        if (type_value == 'commReset') not in unit_id:
            commReset_frequency[unit_id] = commReset_frequency.get(unit_id, 0) 
        else:
            commReset_frequency[unit_id] += type_value == 'CommReset'
        
        if (type_value == 'Boot') not in unit_id:
            boot_frequency[unit_id] = boot_frequency.get(unit_id, 0) 
        else:
            boot_frequency[unit_id] += type_value == 'Boot'
        
        if (type_value == 'Fatal') not in unit_id:
            fatal_error_frequency[unit_id] = fatal_error_frequency.get(unit_id, 0) 
        else:
            fatal_error_frequency[unit_id] += reset_reason == 'Fatal Error'


df = pd.DataFrame({
    'UnitID': list(commReset_frequency.keys()),
    'Frequency of CommReset': list(commReset_frequency.values()),
    'Frequency of Boot': list(boot_frequency.values()),
    'Frequency of Fatal Error': list(fatal_error_frequency.values())
})

workbook = Workbook()

sheet = workbook.active

for index, row in df.iterrows():
    sheet.append(row.tolist())

workbook.save('test_output.xlsx')