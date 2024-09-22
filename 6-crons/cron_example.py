from pycolonies import colonies_client
from pycolonies import Workflow, FuncSpec, Conditions, Gpu
import time

colonies, colonyname, colony_prvkey, executor_name, prvkey = colonies_client()

wf = Workflow(colonyname=colonyname)
f = FuncSpec(
    funcname="execute",
    kwargs={
        "cmd": "echo hello world",
        "docker-image": "ubuntu:20.04"
    },
    conditions = Conditions(
        colonyname=colonyname,
        executortype="container-executor",
        executornames=["dev-docker"],
        processespernode=1,
        nodes=1,
        walltime=60,
        cpu="1000m",
        mem="1Gi",
        gpu=Gpu(count=0)
    ),
    maxexectime=55,
    maxretries=3
)

f.nodename = "echo"
wf.functionspecs.append(f)

# Add a cron
wait_for_prev_wf = True
cron = colonies.add_cron("echo_cron", "0/1 * * * * *", wait_for_prev_wf, wf, colonyname, prvkey)

# List all crons, max 10 crons are listed
crons = colonies.get_crons(colonyname, 10, prvkey)

for cron in crons:
    print(cron["cronid"])

# Get a cron by id
cron = colonies.get_cron(cron["cronid"], prvkey)
print(cron["cronid"])

# Sleep for 2 seconds to allow the cron to run
time.sleep(2)

# Delete a cron by id
colonies.del_cron(cron["cronid"], prvkey)
