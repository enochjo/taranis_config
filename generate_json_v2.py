import os
import json
import pandas as pd

# This code assumes that you already have a text file containing the dates 
# e.g., 2018-10-17T01:45:03.000000000 of the PPI files.
# Note that the first part of the campaign with "sus" data from 10-15 to 11-11 
# contains only the PPI files that have been corrected.
# The second part of the campaign contains all PPI files from 11-11 onwards.

# Directory containing the NetCDF files
output_times_file = '/global/homes/e/enochjo/github/taranis_config/new_timeseries.txt'

# data_dir = "/pscratch/sd/e/enochjo/taranis/taranis_corcsapr2cfrppiqcM1.c1/"
# data_dir = "/pscratch/sd/e/enochjo/taranis/corcsapr2cfrppiqcM1.b1/"

# output_json_cartesian = "/global/homes/e/enochjo/github/taranis_config/cartesian_new_timeseries.json"
# output_json_polar = "/global/homes/e/enochjo/github/taranis_config/polar_new_timeseries.json"
output_json_cartesian = f'/pscratch/sd/e/enochjo/taranis/joblist/cartesian_new_timeseries.json'
output_json_polar = f'/pscratch/sd/e/enochjo/taranis/joblist/polar_new_timeseries.json'

def generate_entry_cartesian(date_time):
    """Generate a JSON entry for a given date_time."""
    return {
        "input_data_dir": "$TARANIS_DATA_HOME/",
        "input_data_selection": f"*{date_time}*",
        "output_data_dir": "$TARANIS_OUTPUT_DIR/",
        "image_output_dir": "$TARANIS_OUTPUT_DIR/images/",
        "sonde_directory": "$TARANIS_OUTPUT_DIR/corinterpolatedsondeM1.c1/",
        "processing_config": "$TARANIS_CONFIG_HOME/corcsapr2_mask_kdp_attencorr.json",
        "quicklook_config": "$TARANIS_CONFIG_HOME/corcsapr2_quicklooks.json",
        "cal_file_zh": "$TARANIS_OUTPUT_DIR/calibration/cacti_csapr2_zh_conf_enoch.csv",
        "cal_file_zdr": "$TARANIS_OUTPUT_DIR/calibration/cacti_csapr2_zdr_conf_enoch.csv",
        "cal_method": "csv",
        "task_array": False,
        "modes": ["taranis_corcsapr2cfrppiqcM1.c1"],
        "drop_list": [
            "attenuation_corrected_differential_reflectivity",
            "attenuation_corrected_differential_reflectivity_lag_1",
            "attenuation_corrected_reflectivity_h",
            "reflectivity_v",
            "specific_differential_phase",
            "uncorrected_copol_correlation_coeff",
            "uncorrected_differential_phase",
            "uncorrected_differential_reflectivity",
            "uncorrected_differential_reflectivity_lag_1",
            "uncorrected_mean_doppler_velocity_h",
            "uncorrected_mean_doppler_velocity_v",
            "uncorrected_reflectivity_h",
            "uncorrected_reflectivity_v",
            "uncorrected_spectral_width_h",
            "uncorrected_spectral_width_v"
        ]
    }

def generate_entry_polar(date_time):
    """Generate a JSON entry for a given date_time."""
    return {
        "input_data_dir": "$TARANIS_DATA_HOME/",
        "input_data_selection": f'*{date_time}*',
        "output_data_dir": "$TARANIS_OUTPUT_DIR/",
        "image_output_dir": "$TARANIS_OUTPUT_DIR/images/",
        "sonde_directory": "$TARANIS_OUTPUT_DIR/corinterpolatedsondeM1.c1/",
        "processing_config": "$TARANIS_CONFIG_HOME/corcsapr2_mask_kdp_attencorr.json",
        "quicklook_config": "$TARANIS_CONFIG_HOME/corcsapr2_quicklooks.json",
        "cal_file_zh": "$TARANIS_OUTPUT_DIR/calibration/cacti_csapr2_zh_conf_enoch.csv",
        "cal_file_zdr": "$TARANIS_OUTPUT_DIR/calibration/cacti_csapr2_zdr_conf_enoch.csv",
        "cal_method": "csv",
        "task_array": False,
        "modes": ["corcsapr2cfrppiqcM1.b1"],
        "drop_list": [
            "attenuation_corrected_differential_reflectivity",
            "attenuation_corrected_differential_reflectivity_lag_1",
            "attenuation_corrected_reflectivity_h",
            "reflectivity_v",
            "specific_differential_phase",
            "uncorrected_copol_correlation_coeff",
            "uncorrected_differential_phase",
            "uncorrected_differential_reflectivity",
            "uncorrected_differential_reflectivity_lag_1",
            "uncorrected_mean_doppler_velocity_h",
            "uncorrected_mean_doppler_velocity_v",
            "uncorrected_reflectivity_h",
            "uncorrected_reflectivity_v",
            "uncorrected_spectral_width_h",
            "uncorrected_spectral_width_v"
        ]
    }

if __name__ == "__main__":
    # Read the timestamps from the file
    with open(output_times_file, "r") as f:
        timestamps = [line.strip() for line in f]

    # Process the timestamps for Cartesian and Polar JSON files
    json_entries_cartesian = {}
    json_entries_polar = {}
    for time in timestamps:
        # Convert time to the required filename format (YYYYMMDD.HHMMSS)
        date_time = pd.to_datetime(time).strftime("%Y%m%d.%H%M%S")
        filename_cartesian = f"taranis_corcsapr2cfrppiqcM1.c1.{date_time}.nc"
        filename_polar = f"corcsapr2cfrppiqcM1.b1.{date_time}.nc"
        json_entries_cartesian[filename_cartesian] = generate_entry_cartesian(date_time)
        json_entries_polar[filename_polar] = generate_entry_polar(date_time)

    # Save Cartesian JSON file
    with open(output_json_cartesian, "w") as f:
        json.dump(json_entries_cartesian, f, indent=4)

    # Save Polar JSON file
    with open(output_json_polar, "w") as f:
        json.dump(json_entries_polar, f, indent=4)

    print(f"Cartesian JSON file with {len(json_entries_cartesian)} entries saved to {output_json_cartesian}")
    print(f"Polar JSON file with {len(json_entries_polar)} entries saved to {output_json_polar}")