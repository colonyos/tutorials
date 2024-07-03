# Using Python
This tutorial demonstrates how to use the Python SDK to submit function specifications and develop custom executors.

## Setup Dev environment
First, make sure all backend servers are started.

```bash
wget https://raw.githubusercontent.com/colonyos/colonies/main/docker-compose.env; 
source docker-compose.env; 
wget https://raw.githubusercontent.com/colonyos/colonies/main/docker-compose.yml;
docker-compose up
``` 

## Install PyColonies
PyColonies requires Python version 3.10 or higher.

The following Python versions have been tested:
* 3.13-rc
* 3.12.4
* 3.10.14

```bash
pip3 install pycolonies
``` 

## Submit a job to a Docker Executor
Let's submit a function spec to the Docker Executor. This will launch a Docker container running the command `echo hello world`. 

The `colonies_client` function is a helper function to set up the SDK. It reads credentials and settings from environmental variables, so remember to source the `docker-compose.env` file before running the code. This ensures that all necessary configuration details, such as colony name, private key, and executor details, are correctly initialized.

```python
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
```

```bash
source docker-compose.env
python3 echo.py
```

```console
Process fcded45d038842cece166d7f76e1d733cd3735ef6c0b436324bee47080d84835 submitted
Output:
Pulling from library/ubuntu
Digest: sha256:0b897358ff6624825fb50d20ffb605ab0eaea77ced0adb8c6a4b756513dec6fc
Status: Image is up to date for ubuntu:20.04
hello world
```

## Developing an Executor
To develop an executor, the following conceptual steps must be followed:

1. Generate a new private key.
2. Register the executor with the Colonies server using the colony's private key.
3. Call the assign function to receive process assignments.
4. Interpret the assigned process and perform some kind of computation.
5. Complete the process and set output values.
6. Repeat Step 3 to receive the next process assignment.

```python
from pycolonies import Crypto
from pycolonies import colonies_client
import signal
import os

class PythonExecutor:
    def __init__(self):
        colonies, colonyname, colony_prvkey, _, _ = colonies_client()
        self.colonies = colonies
        self.colonyname = colonyname
        self.colony_prvkey = colony_prvkey
        self.executorname = "helloworld-executor"
        self.executortype = "helloworld-executor"

        crypto = Crypto()
        self.executor_prvkey = crypto.prvkey()
        self.executorid = crypto.id(self.executor_prvkey)

        self.register()

    def register(self):
        executor = {
            "executorname": self.executorname,
            "executorid": self.executorid,
            "colonyname": self.colonyname,
            "executortype": self.executortype
        }

        try:
            executor = self.colonies.add_executor(executor, self.colony_prvkey)
            self.colonies.approve_executor(self.colonyname, self.executorname, self.colony_prvkey)

            self.colonies.add_function(self.colonyname,
                                       self.executorname,
                                       "helloworld",
                                       self.executor_prvkey)
        except Exception as err:
            print(err)
            os._exit(0)

        print("Executor", self.executorname, "registered")

    def start(self):
        while (True):
            try:
                process = self.colonies.assign(self.colonyname, 10, self.executor_prvkey)
                print("Process", process.processid, "is assigned to executor")
                self.colonies.add_log(process.processid, "Hello from executor\n", self.executor_prvkey)
                if process.spec.funcname == "helloworld":
                    self.colonies.close(process.processid, ["helloworld"], self.executor_prvkey)
            except Exception as err:
                print(err)
                pass

    def unregister(self):
        self.colonies.remove_executor(self.colonyname, self.executorname, self.colony_prvkey)
        print("Executor", self.executorname, "unregistered")
        os._exit(0)

def sigint_handler(signum, frame):
    executor.unregister()

if __name__ == '__main__':
    signal.signal(signal.SIGINT, sigint_handler)
    executor = PythonExecutor()
    executor.start()
```

To start the executor type:

```bash
python3 helloworld_executor.py
```

```console
Executor helloworld-executor registered
```

We should now have two executors. Start a new terminal and type.

```bash
source docker-compose.env
colonies executor ls
```

```console
╭─────────────────────┬─────────────────────┬──────────┬─────────────────────╮
│ NAME                │ TYPE                │ LOCATION │ LAST HEARD FROM     │
├─────────────────────┼─────────────────────┼──────────┼─────────────────────┤
│ helloworld-executor │ helloworld-executor │          │ 2024-06-30 20:46:24 │
│ dev-docker          │ container-executor  │ n/a      │ 2024-06-30 20:44:46 │
╰─────────────────────┴─────────────────────┴──────────┴─────────────────────╯
```

## Submit a function
Let's a function spec to the *helloworld-executor*.

```python
from pycolonies import func_spec
from pycolonies import colonies_client

colonies, colonyname, colony_prvkey, executor_name, prvkey = colonies_client()

func_spec = func_spec(func="helloworld",
                      args=[],
                      colonyname=colonyname,
                      executortype="helloworld-executor")

# submit the function spec to the colonies server
process = colonies.submit_func_spec(func_spec, prvkey)
print("Process", process.processid, "submitted")

# wait for the process to be executed
process = colonies.wait(process, 10, prvkey)
print(process.output[0])
```

In another terminal type:
```bash
source docker-compose.env
python3 submit_helloworld.py
```

```console
Process d294198cbae0c16e51d9361b00b907525f560a3c9a14283e3732f56ac94a2fa5 submitted
helloworld
```

We can also look up the process using the CLI. Note the output field.

```bash
colonies process get -p d294198cbae0c16e51d9361b00b907525f560a3c9a14283e3732f56ac94a2fa5
```

```bash
╭───────────────────────────────────────────────────────────────────────────────────────╮
│ Process                                                                               │
├────────────────────┬──────────────────────────────────────────────────────────────────┤
│ Id                 │ d294198cbae0c16e51d9361b00b907525f560a3c9a14283e3732f56ac94a2fa5 │
│ IsAssigned         │ True                                                             │
│ InitiatorID        │ 3fc05cf3df4b494e95d6a3d297a34f19938f7daa7422ab0d4f794454133341ac │
│ Initiator          │ myuser                                                           │
│ AssignedExecutorID │ 957fccbf1cc8de0974cfe6d3bbe198eeb94c54f7d7cda92a2c8c71891329e225 │
│ AssignedExecutorID │ Successful                                                       │
│ PriorityTime       │ 1702493583582577247                                              │
│ SubmissionTime     │ 2024-06-30 20:53:03                                              │
│ StartTime          │ 2024-06-30 20:53:03                                              │
│ EndTime            │ 2024-06-30 20:53:03                                              │
│ WaitDeadline       │ 2024-06-30 20:54:43                                              │
│ ExecDeadline       │ 2024-06-30 20:53:13                                              │
│ WaitingTime        │ 22.772ms                                                         │
│ ProcessingTime     │ 24.746ms                                                         │
│ Retries            │ 0                                                                │
│ Input              │                                                                  │
│ Output             │ helloworld                                                       │
│ Errors             │                                                                  │
╰────────────────────┴──────────────────────────────────────────────────────────────────╯
╭──────────────────────────╮
│ Function Specification   │
├─────────────┬────────────┤
│ Func        │ helloworld │
│ Args        │ None       │
│ KwArgs      │ None       │
│ MaxWaitTime │ 100        │
│ MaxExecTime │ 10         │
│ MaxRetries  │ 3          │
│ Label       │            │
╰─────────────┴────────────╯
╭────────────────────────────────────────╮
│ Conditions                             │
├──────────────────┬─────────────────────┤
│ Colony           │ dev                 │
│ ExecutorNames    │ None                │
│ ExecutorType     │ helloworld-executor │
│ Dependencies     │                     │
│ Nodes            │ 0                   │
│ CPU              │ 0m                  │
│ Memory           │ 0Mi                 │
│ Processes        │ 0                   │
│ ProcessesPerNode │ 0                   │
│ Storage          │ 0Mi                 │
│ Walltime         │ 0                   │
│ GPUName          │                     │
│ GPUs             │ 0                   │
│ GPUPerNode       │ 0                   │
│ GPUMemory        │ 0Mi                 │
╰──────────────────┴─────────────────────╯

No attributes found
```

## Submit using the CLI
We can of course also submit a function spec to the *helloworld-executor* using the Colonies CLI.

```json
{
    "conditions": {
        "executortype": "helloworld-executor"
    },
    "funcname": "helloworld"
}
```

```bash
colonies function submit --spec helloworld.json --follow
```

```console
INFO[0000] Process submitted                             ProcessId=109f1a1948c4fd1b91ddf9f6822426a9725bf2e93e0261d8541791f41376f31f
INFO[0000] Printing logs from process                    ProcessId=109f1a1948c4fd1b91ddf9f6822426a9725bf2e93e0261d8541791f41376f31f
Hello from executor
INFO[0001] Process finished successfully
```
