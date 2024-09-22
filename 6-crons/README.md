# Cron scheduling
Cron scheduling can be used automate execution of workflows at specified intervals. It is also possible to randomly spawn workflows within a specified interval. 

## Cron expressions
Cron expressions has the following format:
```
┌───────────── second (0 - 59)
│ ┌───────────── minute (0 - 59) 
│ │ ┌───────────── hour (0 - 23)
│ │ │ ┌───────────── day of the month (1 - 31)
│ │ │ │ ┌───────────── month (1 - 12) 
│ │ │ │ │ ┌───────────── day of the week
│ │ │ │ │ │ 
│ │ │ │ │ │ 
* * * * * *
```

### Examples

Spawn a workflow every second starting at 00 seconds: 
```
0/1 * * * * *
```

Spawn a workflow every other second starting at 00 seconds: 
```
0/2 * * * * *
```

Spawn a workflow every minute starting at 30 seconds: 
```
30 * * * * *
```

Spawn a workflow every Monday at 15:03:59: 
```
59 3 15 * * MON
```

Spawn a workflow every Christmas Eve at 15:00: 
```
0 0 15 24 12 * 
```

# Using the Colonies CLI to manage crons  
Cron workflows can either be added using the Colonies API/SDK or by using the CLI.

Let's first define a workflow that runs a container using the following configuration. This workflow executes a containerized task with specific resource requirements and constraints. It runs the Unix command echo hello world inside an Ubuntu container (ubuntu:20.04).

```json
[{
    "conditions": {
        "executortype": "container-executor",
        "executornames": [
            "dev-docker"
        ],
        "nodes": 1,
        "processespernode": 1,
        "mem": "10Gi",
        "cpu": "1000m",
        "gpu": {
            "count": 0
        },
        "walltime": 60
    },
        "nodename": "echo",
    "funcname": "execute",
    "kwargs": {
        "cmd": "echo hello world",
        "docker-image": "ubuntu:20.04"
    },
    "maxexectime": 55,
    "maxretries": 3
}]

```

Now, let's add a cron to schedule this workflow every 5 seconds.

```console
colonies cron add --name echo_cron --cron "0/5 * * * * *" --spec ./echo_wf.json
```

Output:
```console
INFO[0000] Will not wait for previous processgraph to finish
INFO[0000] Cron added CronID=83e4010ff9c8d9c762c83fc4d8d3ea24c29478f6342a72b40440ead2685be658

```

Note that a new workflow will be submitted every 5 seconds, even if the previous workflow has not finished. This means that workflows may queue up if the execution time exceeds 5 seconds. To prevent this, you can modify the behavior using the --waitprevious flag. When enabled, a new workflow will only be submitted 5 seconds after the previous one has completed, ensuring sequential execution without overlap.

```console
colonies cron add --name echo_cron --cron "0/5 * * * * *" --spec ./echo_wf.json  --waitprevious
```

Let's check if any process has run:

```console
╭──────────┬──────┬─────────────────────────┬─────────────────────┬───────────────┬────────────────────┬───────────┬───────╮
│ FUNCNAME │ ARGS │ KWARGS                  │ SUBMSSION TIME      │ EXECUTOR NAME │ EXECUTOR TYPE      │ INITIATOR │ LABEL │
├──────────┼──────┼─────────────────────────┼─────────────────────┼───────────────┼────────────────────┼───────────┼───────┤
│ execute  │      │ docker-image:ubuntu:... │ 2024-09-22 14:25:45 │ dev-docker    │ container-executor │ myuser    │       │
│ execute  │      │ cmd:echo hello world... │ 2024-09-22 14:25:40 │ dev-docker    │ container-executor │ myuser    │       │
│ execute  │      │ cmd:echo hello world... │ 2024-09-22 14:25:35 │ dev-docker    │ container-executor │ myuser    │       │
│ execute  │      │ cmd:echo hello world... │ 2024-09-22 14:25:30 │ dev-docker    │ container-executor │ myuser    │       │
│ execute  │      │ cmd:echo hello world... │ 2024-09-22 14:25:25 │ dev-docker    │ container-executor │ myuser    │       │
│ execute  │      │ cmd:echo hello world... │ 2024-09-22 14:25:20 │ dev-docker    │ container-executor │ myuser    │       │
╰──────────┴──────┴─────────────────────────┴─────────────────────┴───────────────┴────────────────────┴───────────┴───────╯
```

Type the following command to list all registered crons:

```console
colonies cron ls
```

```console
╭──────────────────────────────────────────────────────────────────┬───────────┬───────────╮
│ CRONID                                                           │ NAME      │ INITIATOR │
├──────────────────────────────────────────────────────────────────┼───────────┼───────────┤
│ 83e4010ff9c8d9c762c83fc4d8d3ea24c29478f6342a72b40440ead2685be658 │ echo_cron │ myuser    │
╰──────────────────────────────────────────────────────────────────┴───────────┴───────────╯
```

Type the following command to get info about a specific cron:

```console
colonies cron get --cronid 83e4010ff9c8d9c762c83fc4d8d3ea24c29478f6342a72b40440ead2685be658
```

╭────────────────────────────────────────────────────────────────────────────────────────────╮
│ Cron                                                                                       │
├─────────────────────────┬──────────────────────────────────────────────────────────────────┤
│ CronId                  │ 83e4010ff9c8d9c762c83fc4d8d3ea24c29478f6342a72b40440ead2685be658 │
│ Name                    │ echo_cron                                                        │
│ Colony                  │ dev                                                              │
│ InitiatorID             │ 3fc05cf3df4b494e95d6a3d297a34f19938f7daa7422ab0d4f794454133341ac │
│ Initiator               │ myuser                                                           │
│ Cron Expression         │ 0/5 * * * * *                                                    │
│ Interval                │ -1                                                               │
│ Random                  │ false                                                            │
│ NextRun                 │ 2024-09-22 14:29:00                                              │
│ LastRun                 │ 2024-09-22 14:29:00                                              │
│ PrevProcessGraphID      │ 879457499ef7d413d2691bd588dbd9cb6cc4fc9fd61e8a9e05b0873b9f466709 │
│ WaitForPrevProcessGraph │ true                                                             │
│ CheckerPeriod           │ 1000                                                             │
╰─────────────────────────┴──────────────────────────────────────────────────────────────────╯
╭───────────────────────────────────────────────────────────────╮
│ Function Specification                                        │
├─────────────┬─────────────────────────────────────────────────┤
│ Func        │ execute                                         │
│ Args        │ None                                            │
│ KwArgs      │ cmd:echo hello world docker-image:ubuntu:20.04  │
│ MaxWaitTime │ 0                                               │
│ MaxExecTime │ 55                                              │
│ MaxRetries  │ 3                                               │
│ Label       │                                                 │
╰─────────────┴─────────────────────────────────────────────────╯

To remove a cron:
```console
colonies cron remove  --cronid 83e4010ff9c8d9c762c83fc4d8d3ea24c29478f6342a72b40440ead2685be658
```

```console
INFO[0000] Removing cron CronId=83e4010ff9c8d9c762c83fc4d8d3ea24c29478f6342a72b40440ead2685be658
```

# Using Python to manage crons
Below is an example code using the Python SDK to manage crons.

```python
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
print("Adding new cron with id: ", cron["cronid"])

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
```

```console
python3 cron_example.py
```

```console
Adding new cron with id:  6d5e1538251274267fcb0e7fe3eda3ce573f2ab3b31b2e981da8dbae7d4d852a
6d5e1538251274267fcb0e7fe3eda3ce573f2ab3b31b2e981da8dbae7d4d852a
6d5e1538251274267fcb0e7fe3eda3ce573f2ab3b31b2e981da8dbae7d4d852a
```
