#!/bin/bash
#SBATCH -N 1
#SBATCH -C cpu
#SBATCH -q regular
#SBATCH -J cart
#SBATCH --mail-user=enoch.jo@pnnl.gov
#SBATCH --mail-type=ALL
#SBATCH -A m1657
#SBATCH -t 18:00:00

# OpenMP settings:
export OMP_NUM_THREADS=1
export OMP_PLACES=threads
export OMP_PROC_BIND=spread
export PODMANHPC_MOUNT_PROGRAM=/global/common/shared/das/podman/bin/fuse-overlayfs-wrap


PATH=/global/common/shared/tig/podman-hpc/bin/:$PATH
podman-hpc rmsqi enochjo2009/taranis:v3.0.4

source /global/homes/e/enochjo/.config/containers/login.sh
podman-hpc login docker.io -u $PODMAN_USERNAME -p $PODMAN_PASSWORD
podman-hpc pull enochjo2009/taranis:v3.0.4
podman-hpc migrate enochjo2009/taranis:v3.0.4

# Set paths
PYTHON_SCRIPT="./process_cacti_csapr2_case.py" # Not used for now.
# Note that CASE_CONFIG_FILE is also mounted in podman-hpc
# CASE_CONFIG_FILE="/pscratch/sd/e/enochjo/taranis/joblist/polar_new_timeseries.json"
CASE_CONFIG_FILE="/pscratch/sd/e/enochjo/taranis/joblist/cartesian_new_timeseries.json"
# CASE_CONFIG_FILE="/pscratch/sd/e/enochjo/taranis/joblist/missing_files_polar.json"
# CASE_CONFIG_FILE="/pscratch/sd/e/enochjo/taranis/joblist/missing_files_cartesian.json"

# Extract case names from JSON
CASE_NAMES=($(jq -r 'keys[]' "$CASE_CONFIG_FILE"))  # Modify based on JSON structure if needed
NUM_CASES=${#CASE_NAMES[@]}

# Maximum number of concurrent jobs
# For polar step
# MAX_JOBS=12
# For cartesian step
MAX_JOBS=24

# Maximum runtime before restarting (5 minutes = 300 seconds)
MAX_RUNTIME=1200

# Associative arrays to track job PIDs and start times
declare -A JOB_PIDS
declare -A JOB_STARTS

# Function to clean up all running jobs
# /dev/null is like a "black hole" or trash can
# 0 (standard input), 1 (standard output), and 2 (standard error) 
# 2>&1 redirects errors (2) to location of output.
cleanup() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - Terminating all running jobs..."
    for pid in "${JOB_PIDS[@]}"; do
        if ps -p "$pid" > /dev/null 2>&1; then
            kill -9 "$pid" 2>/dev/null
        fi
    done
    wait 2>/dev/null
    echo "$(date '+%Y-%m-%d %H:%M:%S') - Cleanup complete."
    exit 1
}

# Do cleanup() if SIGTERM (termination) and SIGINT (interrupt) is received.
trap cleanup SIGTERM SIGINT

# Function that checks if a previous job for case_name is still running (hung).
# If so, kills it and cleans up.
# Launches a new srun job in the background.
# Tracks its PID and start time for monitoring.
# Why: Ensures no duplicate jobs run for the same case and provides data for hung job detection and cleanup.
run_job() {
    local case_name="$1"
    if [ -n "${JOB_PIDS[$case_name]}" ] && ps -p "${JOB_PIDS[$case_name]}" > /dev/null 2>&1; then
        echo "$(date '+%Y-%m-%d %H:%M:%S') - Cleaning up previous hung job for $case_name (PID: ${JOB_PIDS[$case_name]})"
        kill -9 "${JOB_PIDS[$case_name]}"
        wait "${JOB_PIDS[$case_name]}" 2>/dev/null
    fi
    srun -n 1 -c 10 --cpu_bind=cores podman-hpc run --rm --entrypoint= \
        --mount type=bind,source=/pscratch/sd/e/enochjo/taranis/,target=/data taranis:v3.0.4 \
        /bin/bash -c "cd /taranis/cacti_processing/scripts && source enoch_set_env_from_b1.sh && ./process_cacti_csapr2_grid_case.py /data/joblist/cartesian_new_timeseries.json $case_name 0" &
    local pid=$!
    JOB_PIDS["$case_name"]=$pid
    JOB_STARTS["$case_name"]=$(date +%s)
    echo "$(date '+%Y-%m-%d %H:%M:%S') - Started job for $case_name (PID: $pid)"
}

# Function that loops through all tracked jobs in JOB_PIDS.
# For each job:
# If it’s still running and has exceeded MAX_RUNTIME, restarts it by calling run_job.
# If it’s finished, removes it from JOB_PIDS and JOB_STARTS.
# Why: Ensures jobs don’t hang indefinitely, keeping the pipeline moving by restarting stuck processes while cleaning up completed ones.
check_hung_jobs() {
    local current_time=$(date +%s)
    for case_name in "${!JOB_PIDS[@]}"; do
        local pid=${JOB_PIDS["$case_name"]}
        local start_time=${JOB_STARTS["$case_name"]}
        [ -z "$start_time" ] && continue

        if ps -p "$pid" > /dev/null 2>&1; then
            local runtime=$((current_time - start_time))
            if [ $runtime -ge $MAX_RUNTIME ]; then
                echo "$(date '+%Y-%m-%d %H:%M:%S') - Job for $case_name (PID: $pid) has run for $runtime seconds, restarting..."
                run_job "$case_name"
            fi
        else
            unset JOB_PIDS["$case_name"]
            unset JOB_STARTS["$case_name"]
        fi
    done
}

# Start initial batch of up to 24 jobs
for ((i = 0; i < NUM_CASES && i < MAX_JOBS; i++)); do
    run_job "${CASE_NAMES[i]}"
done

# Track remaining jobs
NEXT_INDEX=$MAX_JOBS

# Monitor and launch new jobs as others complete
while [ $NEXT_INDEX -lt $NUM_CASES ] || [ ${#JOB_PIDS[@]} -gt 0 ]; do
    wait -n || sleep 10
    check_hung_jobs
    RUNNING_JOBS=$(jobs -r | wc -l)
    while [ $RUNNING_JOBS -lt $MAX_JOBS ] && [ $NEXT_INDEX -lt $NUM_CASES ]; do
        run_job "${CASE_NAMES[$NEXT_INDEX]}"
        ((NEXT_INDEX++))
        RUNNING_JOBS=$(jobs -r | wc -l)
    done
done

# Wait for all remaining jobs to complete
echo "$(date '+%Y-%m-%d %H:%M:%S') - Waiting for remaining jobs..."
wait

echo "$(date '+%Y-%m-%d %H:%M:%S') - All jobs completed."