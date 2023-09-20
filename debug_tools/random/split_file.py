import os
import json

in_file = '/Users/herminealfsen/Documents/VitalThings/Git/support-tools/Debug_tools/devicelog_preprocessing/devicelogs.json'
output_prefix = 'split_file_'
path = '/Users/herminealfsen/Documents/VitalThings/Git/support-tools/Debug_tools/random'
lines_per_file = 100000

file_count = 1
line_count = 0

with open(in_file,"r") as file:
    output_file = open(os.path.join(path,output_prefix + str(file_count)+'.jsonl'),'w')
    for line in file:
        output_file.write(line)
        line_count += 1
        if line_count == lines_per_file:
            output_file.close()
            file_count += 1
            output_file = open(os.path.join(path,output_prefix + str(file_count)+'.jsonl'),'w')
            line_count = 0

if line_count != 0:
    output_file.close()

