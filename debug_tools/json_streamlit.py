import json
import os
import pandas as pd
import streamlit as st

from collections import defaultdict
from collections import defaultdict
from datetime import datetime, timedelta
from dateutil import parser

input_file = 'random/split_file_254.jsonl' #'devicelog_preprocessing/devicelog_processed.json'

### ---------------------------------------------- ###
### ---- DECLEARING VAR, DICT, LISTS and FUNC ---- ###
### ---------------------------------------------- ###

## Constants
# Create a Streamlit sidebar with sliders for constants
st.sidebar.title("Evaluate data from this date")
days_ago = st.sidebar.slider("Days back in time", min_value=0, max_value=365, value=80)
max_timestamp_date = (datetime.now() - timedelta(days=days_ago)).date()

st.sidebar.title("Filtering options")
st.sidebar.markdown("The sliders represent how many times an event has happend during a day. Flagged units have values in between min and max. Units that are over max value will be marked as sick. All other units are ignored.")
# Define the slider parameters as a dictionary
slider_params = {
    "Voltage level threshold": (0.0, 10.0, 4.7),
    "Number of low Voltage": (0, 100, (2, 15)),
    "RSSI level threshold": (-100, 0, -85),
    "Number of low RSSI": (0, 100, (3, 15)),
    "Number of CommReset": (0, 500, (30, 50)),
    "Number of Boot": (0, 500, (30, 50)),
    "Number of Fatal Error": (0, 100, (3, 5)),
    "Number of XeThruStartup": (0, 500, (30, 50)),
    "Number of Uptime": (0, 500, (0, 0)),
    "Max days as flagged in a row": (0, 365, 3),
}

# Initialize a dictionary to store the values
slider_values = {}

# Create sliders and extract values
for param_name, (min_val, max_val, default_val) in slider_params.items():
    slider_values[param_name] = st.sidebar.slider(
        param_name,
        min_value=min_val,
        max_value=max_val,
        value=default_val
    )

# Extract values for specific parameters
voltage_level = slider_values["Voltage level threshold"]
rssi_level = slider_values["RSSI level threshold"]
(min_number_of_lowVoltage, max_number_of_lowVoltage) = slider_values["Number of low Voltage"]
(min_number_of_lowRssi, max_number_of_lowRssi) = slider_values["Number of low RSSI"]
(min_number_of_commReset, max_number_of_commReset) = slider_values["Number of CommReset"]
(min_number_of_boot, max_number_of_boot) = slider_values["Number of Boot"]
(min_number_of_fatalError, max_number_of_fatalError) = slider_values["Number of Fatal Error"]
(min_number_of_XeThruStartup, max_number_of_XeThruStartup) = slider_values["Number of XeThruStartup"]
(min_number_of_uptime, max_number_of_uptime) = slider_values["Number of Uptime"]
threshold_consecutive_flagged = slider_values["Max days as flagged in a row"]

# Empty lists, will contain sick and flagged units, and their data
unique_sick_units = set()
unique_flagged_units = set()
sick_units = []
flagged_units = []
data = []

# Initialize a dictionary to store dates for each unit ID
dates_by_unit = defaultdict(list)
# Create a dictionary to keep track of unit categorization
unit_categorization = {}
# Initialize a dictionary to store daily event frequencies for each unit ID
daily_type_frequencies = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
daily_resetreason_frequencies = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
daily_lowvoltage_frequencies = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
daily_lowrssi_frequencies = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
# Initialize a low rssi/voltage list to calculate average
low_voltage_values = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
low_rssi_values = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
# Initialize a dictionary to store consecutive flagged days for each unit ID
consecutive_flagged_days = defaultdict(int)

### -------------------------------------- ###
### ---- MANGING DATA FROM INPUT FILE ---- ###
### -------------------------------------- ###

# Reading data
with open(input_file, 'r') as file:
    for line in file:
        json_obj = json.loads(line)
        unit_id = json_obj['UnitID']
        timestamp_str = json_obj['Timestamp']
        timestamp = parser.parse(timestamp_str)
        timestamp_date = timestamp.date()

        # Check if timestamp_date for unitID is less than "days_ago"
        if timestamp_date < max_timestamp_date:
            continue
        
        dates_by_unit.setdefault(unit_id, []).append(timestamp_date.strftime('%Y-%m-%d'))   

        type_value = json_obj.get('Type', json_obj.get('ContentType', ''))
        daily_type_frequencies[unit_id][timestamp_date][type_value] += 1

        reset_reason = json_obj.get('Payload', {}).get('ResetReason', '') or json_obj.get('Content', {}).get('ResetReason', 'No Reset Reason')
        daily_resetreason_frequencies[unit_id][timestamp_date][reset_reason] += 1
        
        voltage = json_obj.get('Payload', {}).get('Voltage', '') or json_obj.get('Content', {}).get('ResetReason', '')
        if voltage and voltage < voltage_level:
            daily_lowvoltage_frequencies[unit_id][timestamp_date]['Low voltage'] += 1
            low_voltage_values[unit_id][timestamp_date]['Sum voltage'] += voltage

        rssi = json_obj.get('Payload', {}).get('NetworkInfo', {}).get('Rssi', '') or json_obj.get('Payload', {}).get('NetworkInfo', {}).get('Rssi', '')
        if rssi and rssi < rssi_level:
            daily_lowrssi_frequencies[unit_id][timestamp_date]['Low rssi'] += 1
            low_rssi_values[unit_id][timestamp_date]['Sum rssi'] += rssi

# Filtering data
def filter_flagged(unit_id, type_freq, reset_reason_freq, low_voltage_freq, low_rssi_freq):
    if (
    min_number_of_commReset < type_freq['CommReset'] < max_number_of_commReset or
    min_number_of_boot < type_freq['Boot'] < max_number_of_boot or

    (min_number_of_XeThruStartup < type_freq['XeThruStartup'] < max_number_of_XeThruStartup and
    json_obj.get('Payload', {}).get('Success', False) is False and
    json_obj.get('Payload', {}).get('State', '') == 'starting') or

    min_number_of_fatalError < reset_reason_freq['Fatal'] < max_number_of_fatalError or

    (any(value > min_number_of_lowVoltage and value < max_number_of_lowVoltage for value in low_voltage_freq.values())) or
    (any(value > min_number_of_lowRssi and value < max_number_of_lowRssi for value in low_rssi_freq.values()))):
        consecutive_flagged_days[unit_id] += 1  # Increment the consecutive flagged days counter
        return True 
    else:
        consecutive_flagged_days[unit_id] = 0  # Reset the consecutive flagged days counter
        return False

def filter_sick(unit_id, type_freq, reset_reason_freq, low_voltage_freq, low_rssi_freq):
    if (
    # If a type, reset reason, rssi or voltage is "wrong"
    (type_freq['CommReset'] > max_number_of_commReset or
    type_freq['Boot'] > max_number_of_boot or

    (type_freq['XeThruStartup'] > max_number_of_XeThruStartup and
    json_obj.get('Payload', {}).get('Success', False) is False and
    json_obj.get('Payload', {}).get('State', '') == 'starting') or

    reset_reason_freq['Fatal'] > max_number_of_fatalError or

    (any(value > max_number_of_lowVoltage for value in low_voltage_freq.values())) or
    (any(value > max_number_of_lowRssi for value in low_rssi_freq.values())))   
    
    # If unit has been flagged for more than threshold_consecutive_flagged
    or (filter_flagged(unit_id, type_freq, reset_reason_freq, low_voltage_freq, low_rssi_freq) and consecutive_flagged_days[unit_id] >= threshold_consecutive_flagged)):
        #print(f'{consecutive_flagged_days}, {threshold_consecutive_flagged}')
        consecutive_flagged_days[unit_id] = 0  # Reset the consecutive flagged days counter
        return True
    else:
        consecutive_flagged_days[unit_id] = 0  # Reset the consecutive flagged days counter
        return False

# Formatig data
def format_data(event_freq, reset_freq, voltage_freq, rssi_freq):
    type_freq_str = '\n'.join([f"{event_type}: {count}" for event_type, count in event_freq.items()])
    reset_reason_freq_str = '\n'.join([f"{reason}: {count}" for reason, count in reset_freq.items()])
    low_voltage_freq_str = '\n'.join([f"{reason}: {count}" for reason, count in voltage_freq.items()])
    low_rssi_freq_str = '\n'.join([f"{reason}: {count}" for reason, count in rssi_freq.items()])

    if 'Low voltage' in voltage_freq:
        sum_voltage = low_voltage_values[unit_id][date]['Sum voltage']
        num_low_voltage = daily_lowvoltage_frequencies[unit_id][date]['Low voltage']
        if num_low_voltage > 0:
            average_voltage = sum_voltage / num_low_voltage
            low_voltage_values[unit_id][date]['Average voltage'] = average_voltage
            average_voltage_str = f"Average voltage: {average_voltage:.2f}"
            low_voltage_freq_str += f"\n{average_voltage_str}"

    if 'Low rssi' in rssi_freq:
        sum_rssi = low_rssi_values[unit_id][date]['Sum rssi']
        num_low_rssi = daily_lowrssi_frequencies[unit_id][date]['Low rssi']
        if num_low_rssi > 0:
            average_rssi = sum_rssi / num_low_rssi
            low_rssi_values[unit_id][date]['Average rssi'] = average_rssi
            average_rssi_str = f"Average rssi: {average_rssi:.2f}"
            low_rssi_freq_str += f"\n{average_rssi_str}"


    return type_freq_str, reset_reason_freq_str, low_voltage_freq_str, low_rssi_freq_str

# Appending data to data_list
def append_data(data_list, unit_id, date, type_freq_str, resetreason_freq_str, lowvoltage_freq_str, lowrssi_freq_str):
    data_list.append({
        'UnitID': unit_id,
        'Date': date.strftime('%Y-%m-%d'),
        'Number of type': type_freq_str,
        'Number of reset reason': resetreason_freq_str,
        'Number of low voltage': lowvoltage_freq_str,
        'Number of low rssi': lowrssi_freq_str
    })

# Create dataframe by reading and formatting data in directories 
for unit_id, date_type_freq in daily_type_frequencies.items():
    # Initialize the consecutive_flagged_days for this unit
    consecutive_flagged_days[unit_id] = 0
    # Initialize unit categorization if it doesn't exist
    if unit_id not in unit_categorization:
        unit_categorization[unit_id] = {
            'is_sick': False,
            'is_flagged': False,
        }

    for date, type_freq in date_type_freq.items(): 
        # Number of reset reason, voltage, and rssi for each unitID per date
        reset_reason_freq = daily_resetreason_frequencies[unit_id][date]
        low_voltage_freq = daily_lowvoltage_frequencies[unit_id][date]
        low_rssi_freq = daily_lowrssi_frequencies[unit_id][date]

        # Formatting data
        type_freq_str, resetreason_freq_str, lowvoltage_freq_str, lowrssi_freq_str = format_data(type_freq, reset_reason_freq, low_voltage_freq, low_rssi_freq)

        # Get status for unitID per date
        is_sick = filter_sick(unit_id, type_freq, reset_reason_freq, low_voltage_freq, low_rssi_freq)
        is_flagged = filter_flagged(unit_id, type_freq, reset_reason_freq, low_voltage_freq, low_rssi_freq)
        
        # Update unit categorization
        unit_categorization[unit_id]['is_sick'] = unit_categorization[unit_id]['is_sick'] or is_sick
        unit_categorization[unit_id]['is_flagged'] = unit_categorization[unit_id]['is_flagged'] or is_flagged 

        # Append data only if unit is marked as 'sick' or 'flagged'
        if is_sick or is_flagged:
            append_data(data, unit_id, date, type_freq_str, resetreason_freq_str, lowvoltage_freq_str, lowrssi_freq_str)

# Create lists based on unit categorization
for unit_id, categorization in unit_categorization.items():
    if categorization['is_sick']:
        if unit_id not in unique_sick_units:
            unique_sick_units.add(unit_id)
            sick_units.append({'UnitID': unit_id})
        
    elif categorization['is_flagged']:
        if unit_id not in unique_flagged_units:
            unique_flagged_units.add(unit_id)
            flagged_units.append({'UnitID': unit_id})

# Creating DataFrames from lists
df_flagged_units = pd.DataFrame(flagged_units)
df_sick_units = pd.DataFrame(sick_units)
df_data = pd.DataFrame(data)

### -------------------------------------- ###
### ------- CREATING STREAMLIT PAGE ------ ###
### -------------------------------------- ###

# Main is called in the end of the script
def main():
    st.title("Unit Monitoring Dashboard")
    # Create a two-column layout
    col1, col2 = st.columns(2)

    # Create a search input widget, to search for unitIDs
    search_input = st.text_input("Search for a unit:")
    # Create a search button
    search_button = st.button("Search")

    if search_button:
        # Show units based on search input
        filtered_flagged_units = df_flagged_units[df_flagged_units['UnitID'].str.lower().str.contains(search_input.lower())]
        filtered_sick_units = df_sick_units[df_sick_units['UnitID'].str.lower().str.contains(search_input.lower())]
    else:
        # Show all units on flagged and sick list
        filtered_flagged_units = df_flagged_units
        filtered_sick_units = df_sick_units

    # Create an expander for flagged units
    with col1:
        st.title("Flagged Units")
        with st.expander(f"View Flagged Units ({len(filtered_flagged_units)} units)", expanded=True):
            display_list(filtered_flagged_units)

    # Create an expander for sick units
    with col2:
        st.title("Sick Units")
        with st.expander(f"View Sick Units ({len(filtered_sick_units)} units)", expanded=True):
            display_list(filtered_sick_units)

    apply_custom_css()

# Displaying the units from each list
def display_list(units):
    for _, row in units.iterrows():
        if st.button(row['UnitID']):
            unit_details(row['UnitID'])

# Styling the display of the expanders- adding scroll function
def apply_custom_css():
    css='''
    <style>
        [data-testid="stExpander"] div:has(>.streamlit-expanderContent) {
            overflow: scroll;
            height: 400px;
        }
    </style>
    '''

    st.markdown(css, unsafe_allow_html=True)

# When a unitID is clicked- show more details on this unit
def unit_details(unit_id):
    # Use the 'with' context manager to create the sidebar
    with st.sidebar:
        st.title(f"Details for Unit ID: {unit_id}")

        # Load unit details
        unit_data = df_data[df_data['UnitID'] == unit_id]

        # Display the modified DataFrame using st.table()
        st.dataframe(unit_data, hide_index = True)

        # Add a button to navigate back to the list
        if st.button("Back to List"):
            main()  # Call the main function to return to the list

if __name__ == "__main__":
    main()
