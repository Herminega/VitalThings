#!/bin/bash
input_file='debug_tools/devicelog_preprocessing/devicelog_processed.json'
unit_ids_file='return_units.txt'
output_directory='results/return_results'

while IFS= read -r unit || [[ -n "$unit" ]]; do
    jq_filter='select(.UnitID == $unit and (.Type == "CommReset" or .Payload.ResetReason == "Fatal" or .Payload.Voltage < 4.7))'
    jq_keys='[.UnitID, .Timestamp, .Type, .Payload.ResetReason, (.Payload.FatalInfo | tostring), .Payload.Count, .Payload.Voltage]'
    header='UnitID, Timestamp, Type, Reset Reason, Fatal message, Count, Voltage'

    output_file="$output_directory/results_$unit.csv"

    (echo "$header" && jq -r --arg unit "$unit" "$jq_filter | $jq_keys | @csv" "$input_file") > "$output_file"
done < "$unit_ids_file"