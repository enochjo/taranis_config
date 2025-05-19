#!/bin/bash
#SBATCH -N 1
#SBATCH -C cpu
#SBATCH -q regular
#SBATCH -J taranis_polar
#SBATCH --mail-user=enoch.jo@pnnl.gov
#SBATCH --mail-type=ALL
#SBATCH -A m1657
#SBATCH -t 08:00:00

# OpenMP settings:
export OMP_NUM_THREADS=1
export OMP_PLACES=threads
export OMP_PROC_BIND=spread
export PODMANHPC_MOUNT_PROGRAM=/global/common/shared/das/podman/bin/fuse-overlayfs-wrap


PATH=/global/common/shared/tig/podman-hpc/bin/:$PATH
podman-hpc rmsqi enochjo2009/taranis:v3.0

source /global/homes/e/enochjo/.config/containers/login.sh
podman-hpc login docker.io -u $PODMAN_USERNAME -p $PODMAN_PASSWORD
podman-hpc pull enochjo2009/taranis:v3.0
podman-hpc migrate enochjo2009/taranis:v3.0

# Set paths
PYTHON_SCRIPT="./process_cacti_csapr2_case.py"
CASE_CONFIG_FILE="/data/case_list.json"
CASE_NAME="'test_201901'"
NUM_WORKERS=12

# Run the Python script
podman-hpc run --rm --entrypoint= --mount type=bind,source=/pscratch/sd/e/enochjo/taranis/,target=/data taranis:v2.0.5 \
    /bin/bash -c "cd /taranis/cacti_processing/scripts && source enoch_set_env_from_b1.sh && $PYTHON_SCRIPT $CASE_CONFIG_FILE $CASE_NAME $NUM_WORKERS"

# srun -n 288 -c 10  --cpu_bind=cores podman-hpc run --rm --mpi --mount type=bind,source=/pscratch/sd/e/enochjo/taranis/,target=/data taranis:v1.9 /bin/bash -c "cd /taranis/cacti_processing/scripts && source enoch_set_env_from_b1.sh && ./process_cacti_csapr2_case.py \$TARANIS_CONFIG_HOME/case_list_csapr2_enoch.json "test_run" 1"
# srun -n 96 --cpu_bind=cores podman-hpc run --rm --mpi --entrypoint= --mount type=bind,source=/pscratch/sd/e/enochjo/taranis/,target=/data taranis:v2.0.3 /bin/bash -c "cd /taranis/cacti_processing/scripts && source enoch_set_env_from_b1.sh && ./process_cacti_csapr2_case.py /data/case_list.json "test_run_sbatch" 1"

# srun -n 16 --cpu_bind=cores podman-hpc run --rm --mpi --mount type=bind,source=/global/cfs/projectdirs/m1657/enochjo/cacti/taranis/,target=/data taranis:v1.8 /bin/bash -c "cp /data/temp_fixes/process.py /taranis/taranis/taranis/ && cd /taranis/cacti_processing/scripts && source enoch_set_env_from_b1.sh && ./process_cacti_csapr2_case.py \$TARANIS_CONFIG_HOME/case_list_csapr2_enoch.json "test_run" 1"

# srun -n 24 -c 10  --cpu_bind=cores podman-hpc run --rm --mpi --mount type=bind,source=/global/cfs/projectdirs/m1657/enochjo/cacti/taranis/,target=/data taranis:v1.8 /bin/bash -c "cd /taranis/cacti_processing/scripts && source enoch_set_env_from_b1.sh && ./process_cacti_csapr2_grid_case.py \$TARANIS_CONFIG_HOME/case_list_csapr2_enoch.json "grid_run" 1"

# node tests
# srun -n 2 -c 128 --cpu_bind=cores podman-hpc run --rm --mpi --mount type=bind,source=/pscratch/sd/e/enochjo/taranis/,target=/data taranis:v1.9 /bin/bash -c "cd /taranis/cacti_processing/scripts && source enoch_set_env_from_b1.sh && ./process_cacti_csapr2_grid_case.py \$TARANIS_CONFIG_HOME/case_list_csapr2_enoch.json "grid_run" 1"

# srun -n 24 -c 10 --cpu_bind=cores podman-hpc run --rm --mpi --entrypoint= --mount type=bind,source=/pscratch/sd/e/enochjo/taranis/,target=/data taranis:v2.0.1 /bin/bash -c "cd /taranis/cacti_processing/scripts && source enoch_set_env_from_b1.sh && ./process_cacti_csapr2_case.py /data/case_list.json "test_run_sbatch" 1"
# srun -n 1 -c 256 --cpu_bind=cores podman-hpc run --rm --mpi --entrypoint= --mount type=bind,source=/pscratch/sd/e/enochjo/taranis/,target=/data taranis:v2.0.1 /bin/bash -c "cd /taranis/cacti_processing/scripts && source enoch_set_env_from_b1.sh && ./process_cacti_csapr2_case.py /data/case_list.json "test_run_sbatch" 1"

# cd /taranis/cacti_processing/scripts && source enoch_set_env_from_b1.sh
# python -m memory_profiler process_cacti_csapr2_case.py /data/case_list.json "test_201901" 1
# python -m memory_profiler process_cacti_csapr2_case.py /data/case_list.json "test_run" 1
# ./process_cacti_csapr2_case.py /data/case_list.json "test_arm" 0
# ./process_cacti_csapr2_grid_case.py /data/case_list.json "grid_arm" 0


# python -m memory_profiler process_cacti_csapr2_case.py /data/case_list.json "test_memory" 1
# ./process_cacti_csapr2_case.py /data/case_list.json "test_201901" 12