from pycolonies import FuncSpec, Conditions, Gpu
from pycolonies import colonies_client

colonies, colonyname, colony_prvkey, executor_name, prvkey = colonies_client()

func_spec = FuncSpec(
    funcname="execute",
    kwargs={
        "cmd": "echo hello world",
        "docker-image": "ubuntu:20.04"
    },
    conditions = Conditions(
        colonyname=colonyname,
        executortype="container-executor",
        executornames=["dev"],
        processes_per_node=1,
        nodes=1,
        walltime=60,
        cpu="1000m",
        mem="1Gi",
        gpu=Gpu(count=0)
    ),
    maxexectime=55,
    maxretries=3
)

process = colonies.submit_func_spec(func_spec, prvkey)
print("Process", process.processid, "submitted")

# wait for the process to be executed, timeout after 10 seconds
process = colonies.wait(process, 10, prvkey)

print("Output:")
log = colonies.get_process_log(colonyname, process.processid, 100, -1, prvkey)
for l in log:
    print(l["message"], end="")
