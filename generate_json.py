import os
import json
import re

# Specify a date filter (YYYYMMDD) or set to None to include all
target_date = "201901"  # Change this to filter for a specific date, e.g., "20190123"

# Directory containing the NetCDF files
# data_dir = "/pscratch/sd/e/enochjo/taranis/corcsapr2cfrppiqcM1.b1/"
data_dir = "/pscratch/sd/e/enochjo/taranis/taranis_corcsapr2cfrppiqcM1.c1/"
output_json = "/pscratch/sd/e/enochjo/taranis/joblist/cartesian_"+target_date+".json"
# taranis_corcsapr2cfrppiqcM1.c1.20190302.234502.nc
def generate_entry_polar(filename):
    # Extract YYYYMMDD.HHMMSS from the filename
    match = re.match(r"corcsapr2cfrppiqcM1\.b1\.(\d{8})\.(\d{6})\.nc", filename)
    date_time = f"{match.group(1)}.{match.group(2)}"  # e.g., "20190123.123456"
    return {
        "input_data_dir": "$TARANIS_DATA_HOME/",
        "input_data_selection": '*'+date_time+'*',
        "output_data_dir": "$TARANIS_OUTPUT_DIR/",
        "image_output_dir": "$TARANIS_OUTPUT_DIR/images/",
        "sonde_directory": "$TARANIS_OUTPUT_DIR/corinterpolatedsondeM1.c1/",
        "processing_config": "$TARANIS_CONFIG_HOME/corcsapr2_mask_kdp_attencorr.json",
        "quicklook_config": "$TARANIS_CONFIG_HOME/corcsapr2_quicklooks.json",
        "cal_file_zh": "$TARANIS_DATA_HOME/cacti_csapr2_zh_conf_b1.csv",
        "cal_file_zdr": "$TARANIS_DATA_HOME/cacti_csapr2_zdr_conf_b1.csv",
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

def generate_entry_cartesian(filename):
    # Extract YYYYMMDD.HHMMSS from the filename
    match = re.match(r"taranis_corcsapr2cfrppiqcM1\.c1\.(\d{8})\.(\d{6})\.nc", filename)
    date_time = f"{match.group(1)}.{match.group(2)}"  # e.g., "20190123.123456"
    return {
        "input_data_dir": "$TARANIS_DATA_HOME/",
        "input_data_selection": '*'+date_time+'*',
        "output_data_dir": "$TARANIS_OUTPUT_DIR/",
        "image_output_dir": "$TARANIS_OUTPUT_DIR/images/",
        "sonde_directory": "$TARANIS_OUTPUT_DIR/corinterpolatedsondeM1.c1/",
        "processing_config": "$TARANIS_CONFIG_HOME/corcsapr2_mask_kdp_attencorr.json",
        "quicklook_config": "$TARANIS_CONFIG_HOME/corcsapr2_quicklooks.json",
        "cal_file_zh": "$TARANIS_CONFIG_HOME/cacti_csapr2_zh_conf_b1.csv",
        "cal_file_zdr": "$TARANIS_CONFIG_HOME/cacti_csapr2_zdr_conf_b1.csv",
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

def find_radar_files(directory, target_date=None):
    """Find radar files in the directory, filtering by a specific date."""
    radar_files = []
    pattern = re.compile(r"corcsapr2cfrppiqcM1\.b1\.(\d{8})\.\d{6}\.nc")
    
    for filename in sorted(os.listdir(directory)):
        if target_date is None or target_date in filename:
            radar_files.append(filename)
    
    return radar_files

json_entries = {}
for filename in find_radar_files(data_dir, target_date):
    # json_entries[f"{filename}"] = generate_entry_polar(filename)
    json_entries[f"{filename}"] = generate_entry_cartesian(filename)

# Save to JSON file
with open(output_json, "w") as f:
    json.dump(json_entries, f, indent=4)

print(f"JSON file with {len(json_entries)} entries saved to {output_json}")
