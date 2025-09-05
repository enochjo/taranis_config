import os
import json
import pandas as pd
from generate_json_v2 import generate_entry_cartesian, generate_entry_polar

# Toggle to switch between Cartesian and Polar
generate_mode = "polar"  # Set to "cartesian" or "polar"

# Text file containing all PPI file timestamps
output_times_file = '/global/homes/e/enochjo/github/taranis_config/new_timeseries.txt'

# Directory containing the processed Taranis files
data_dir = "/pscratch/sd/e/enochjo/taranis/taranis_corcsapr2cfrppiqcM1.c1/"
# data_dir = "/pscratch/sd/e/enochjo/taranis/taranis_corcsapr2cfrppiqcM1_gridded.c1/"

# Directory to save the generated JSON file for missing files
output_json_missing = f'/pscratch/sd/e/enochjo/taranis/joblist/missing_files_{generate_mode}.json'

# Read the timestamps from the file
with open(output_times_file, "r") as f:
    timestamps = [line.strip() for line in f]

# Determine expected filenames and entry generation function based on the mode
if generate_mode == "cartesian":
    expected_files = [
        f"taranis_corcsapr2cfrppiqcM1.c1.{pd.to_datetime(time).strftime('%Y%m%d.%H%M%S')}_gridded.nc"
        for time in timestamps
    ]
    generate_entry = generate_entry_cartesian
elif generate_mode == "polar":
    expected_files = [
        f"taranis_corcsapr2cfrppiqcM1.c1.{pd.to_datetime(time).strftime('%Y%m%d.%H%M%S')}.nc"
        for time in timestamps
    ]
    generate_entry = generate_entry_polar
else:
    raise ValueError("Invalid mode. Please set generate_mode to 'cartesian' or 'polar'.")

# Get the list of files in the data directory
existing_files = set(os.listdir(data_dir))
# import pdb; pdb.set_trace()
# Find missing files
missing_files = [file for file in expected_files if file not in existing_files]

# Generate JSON entries for missing files
json_entries_missing = {}
for file in missing_files:
    # Extract the date_time from the filename
    date_time = file.split(".")[2] + "." + file.split(".")[3].split("_")[0] # Polar 
    # date_time = file.split(".")[2] + "." + file.split(".")[3] # Cartesian
    # import pdb; pdb.set_trace()
    json_entries_missing[file] = generate_entry(date_time)

# Save the missing files JSON
with open(output_json_missing, "w") as f:
    json.dump(json_entries_missing, f, indent=4)

# import pdb; pdb.set_trace()

print(f"Missing {generate_mode.capitalize()} JSON file with {len(json_entries_missing)} entries saved to {output_json_missing}")