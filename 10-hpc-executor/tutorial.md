# HPC Executor
The HPC Executor is slightly more challenging to deploy. The steps are as follows:

1. Build the HPC Executor binary.
2. Create an **env** file with all the necessary credentials.
3. Transfer (scp) the binary to a login node of a Slurm cluster.
4. Transfer (scp) the **env** file to the login node and ensure it is securely accessible only by you.
5. Log in (ssh) to the login node.
6. Start a Tmux session and launch the HPC Executor.
7. Detach from the Tmux session and exit.

## Building
First, install Golang, then clone the repo below.

```bash
git@github.com:colonyos/executors.git
cd hpc
make
```

The **make** command will create a binary in **./hpc/bin** called **hpc_executor**.

## Confiruation
Create a **env** file with the following content. Replace all TODOs with valid values.

```bash
export LANG=en_US.UTF-8
export LANGUAGE=en_US.UTF-8
export LC_ALL=en_US.UTF-8
export LC_CTYPE=UTF-8
export TZ=Europe/Stockholm
export COLONIES_TLS="true"
export COLONIES_SERVER_HOST="server.colonyos.io"
export COLONIES_SERVER_PORT="443"
export COLONIES_COLONY_NAME="hpc"
export COLONIES_COLONY_PRVKEY=""
export COLONIES_PRVKEY="TODO"
export COLONIES_EXECUTOR_NAME="hpc"
export AWS_S3_ENDPOINT="TODO, e.g s3.colonyos.io:443"
export AWS_S3_ACCESSKEY="TODO"
export AWS_S3_SECRETKEY="TODO"
export AWS_S3_REGION_KEY=""
export AWS_S3_BUCKET="hpc"
export AWS_S3_TLS="true"
export AWS_S3_SKIPVERIFY="false"
export EXECUTOR_ADD_DEBUG_LOGS="false"
export EXECUTOR_TYPE="container-executor"
export EXECUTOR_SW_NAME="colonyos/hpcexecutor:v1.0.3"
export EXECUTOR_SW_TYPE="slurm"
export EXECUTOR_SW_VERSION="22.05.07"
export EXECUTOR_HW_CPU="128000m"
export EXECUTOR_HW_MODEL="AMD EPYC CPU 7763"
export EXECUTOR_HW_NODES="1536"
export EXECUTOR_HW_MEM="256Gi"
export EXECUTOR_HW_STORAGE="20Gi"
export EXECUTOR_HW_GPU_COUNT="0"
export EXECUTOR_HW_GPU_MEM="0"
export EXECUTOR_HW_GPU_NODES_COUNT="0"
export EXECUTOR_HW_GPU_NAME="n/a"
export EXECUTOR_LOCATION_LONG=""
export EXECUTOR_LOCATION_LAT=""
export EXECUTOR_LOCATION_DESC="TODO"
export EXECUTOR_HOME_DIR="TODO"
export EXECUTOR_FS_DIR="/TODO/colonyos/cfs"
export EXECUTOR_LOG_DIR="/TODO/colonyos/logs/standard"
export EXECUTOR_IMAGE_DIR="/TODO/colonyos/images"
export SLURM_ACCOUNT="TODO"
export SLURM_PARTITION="standard"
export SLURM_MODULE=""
export GRES="true"
export SINGULARITY_CACHEDIR=/TODO/colonyos/singularity/cache
export SINGULARITY_TMPDIR=/TODO/colonyos/singularity/tmp
export SINGULARITY_LOCALCACHEDIR=/TODO/colonyos/singularity/localcache
```

## Starting the HPC Executor 
```bash
scp env loginode:~ 
scp hpc_executor loginode:~ 
ssh loginnode
chmod og-rwx env
tmux
source env
./hpc_executor start -v
ctrl-b+d to detach
exit
```

## Testing
Use for example Pollinator to run a test job.

```bash
mkdir test; cd test
pollinator new -n hpc
pollinator run --follow
```
