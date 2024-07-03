# Serverless computing
Serverless computing is a cloud computing model that allows developers to build and run applications without the need to manage the underlying infrastructure. A core component of serverless computing is Function as a Service (FaaS). FaaS enables developers to write functions that are executed in response to specific events.

Popular examples of FaaS platforms include AWS Lambda, Azure Functions, and Google Cloud Functions. In this tutorial, we will explore how ColonyOS can be used for serverless computing. The advantage of ColonyOS is that it facilitates creation of hybrid environments (compute continuums), allowing computations to be distributed across different platforms seamlessly. It also enables a loosely connected system, enhancing scalability and fault tolerance.

We will develop a simple FaaS function that converts Celsius to Fahrenheit.

```python
fahrenheit = (celsius * 9/5) + 32
```

## Prequesties
Look at Tutorial 1, 2, and 3, how to setup a development environment.

## Deploying functions
We are going to save the function source code in ColonyFS then fetch the code to execute the function. This can be done in a few different ways:

**Option 1:** Save an entire Python script in ColonyFS and launch the script using the Python3 command, as demonstrated in Tutorial 1.

**Option 2:** Only save the function code in ColonyFS and develop a custom executor to fetch the code and then inject it into the Python runtime environment. The advantage of this option is that code execution will be much faster than Option 1, but it becomes less flexible as we can only execute Python code.

**Option 3:** Serialize the function code (e.g., using Base64) and store the code in the meta-specification itself.

To demonstrate the Python ColonyOS SDK, we are going to implement Option 2. We will use the built-in inspect module in Python to get the source code of the function we want to call.

```python
import inspect

def convert(celsius):
    return (celsius * 9/5) + 32

source_code = inspect.getsource(convert)
print(source_code)
```

```bash
python3 deploy.py
```

```console
def convert(celsius):
    return (celsius * 9/5) + 32
```

The next step is to store the source code in ColonyFS.

```python
import inspect
from pycolonies import colonies_client

def convert(celsius):
    return (celsius * 9/5) + 32

colonies, colonyname, colony_prvkey, executor_name, prvkey = colonies_client()
source_code = inspect.getsource(convert)
colonies.upload_data(colonyname, prvkey, filename="convert", data=source_code.encode('utf-8'), label="/faas")
```

Run the the deploy script again.
```bash
python3 deploy.py
```

We should now have store the source code in ColonyFS.

```bash
colonies fs label ls
```

```console
╭───────┬───────╮
│ LABEL │ FILES │
├───────┼───────┤
│ /faas │ 1     │
╰───────┴───────╯
```

```bash
colonies fs ls -l /faas
```

```console
╭──────────┬───────┬──────────────────────────────────────────────────────────────────┬─────────────────────┬───────────╮
│ FILENAME │ SIZE  │ LATEST ID                                                        │ ADDED               │ REVISIONS │
├──────────┼───────┼──────────────────────────────────────────────────────────────────┼─────────────────────┼───────────┤
│ convert  │ 0 KiB │ a254fab9ca5b52686eeb436ae32570eb0ae5cf7bc092c16a012791b730c7ed2b │ 2024-07-02 08:55:13 │ 1         │
╰──────────┴───────┴──────────────────────────────────────────────────────────────────┴─────────────────────┴───────────╯
```

We can also use the download the code using the Colonies CLI.

```bash
colonies fs sync -l /faas -d ./faas --yes
```

```console
INFO[0000] Calculating sync plans
Downloading /home/johan/dev/github/colo~ ... done! [54B]
```

```bash
cat faas/convert
```

```console
def convert(celsius):
    return (celsius * 9/5) + 32
```

We can of course also use the Colonies CLI to update the source if we want.


## FaaS Executor
The next step is to develop an executor that can execute the code stored in ColonyFS.

First we need to define the function specification:

```json
{
    "conditions": {
        "executortype": "faas-executor"
    },
    "funcname": "execute",
    "kwargs": {
        "function": "convert",
        "arg": "21"
    }
}
```

To execute the function we need to parse the function spec, fetch the source code, and the execute the function. 

```python
# parse function spec
function = process.spec.kwargs["function"]
arg = process.spec.kwargs["arg"]

# fetch source code
source_code = self.colonies.download_data(self.colonyname, self.executor_prvkey, label="/faas", filename=function)
source_code_str = source_code.decode('utf-8')

# call the function
namespace = {}
exec(source_code_str, globals(), namespace)
f = namespace[function]
r = f(float(arg))

self.colonies.close(process.processid, [r], self.executor_prvkey)
```

Full example:

```python
from pycolonies import Crypto
from pycolonies import colonies_client
import signal
import os
import uuid

class FaaSExecutor:
    def __init__(self):
        colonies, colonyname, colony_prvkey, _, _ = colonies_client()
        self.colonies = colonies
        self.colonyname = colonyname
        self.colony_prvkey = colony_prvkey
        self.executorname = "faas-executor" + uuid.uuid4().hex[:6]
        self.executortype = "faas-executor"

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
                                       "execute",
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
                self.colonies.add_log(process.processid, "Executing function \n", self.executor_prvkey)

                if process.spec.funcname == "execute":
                    # parse function spec
                    function = process.spec.kwargs["function"]
                    arg = process.spec.kwargs["arg"]

                    # fetch source code
                    source_code = self.colonies.download_data(self.colonyname, self.executor_prvkey, label="/faas", filename=function)
                    source_code_str = source_code.decode('utf-8')

                    # call the function
                    namespace = {}
                    exec(source_code_str, globals(), namespace)
                    f = namespace[function]
                    r = f(float(arg))

                    self.colonies.close(process.processid, [r], self.executor_prvkey)

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
    executor = FaaSExecutor()
    executor.start()
```

## Run the example

```bash
python3 faas_executor.py
```

```console
Executor faas-executor8e961b registered
```

Start a another terminal and submit a function spec.

```bash
colonies function submit --spec convert.json --out --wait
```

```console
INFO[0000] Process submitted                             ProcessId=25e470faae748f6f5755d0e5734de893b12eb2a8778b8f7c41d915961e61e3cf
INFO[0000] Process finished successfully                 ProcessId=25e470faae748f6f5755d0e5734de893b12eb2a8778b8f7c41d915961e61e3cf
69.8
```

Seems to be working, we got 69.8 back. Try starting another FaaS Executor. Observe how the requests are load balanced between the executors. To automatically scale, we could use Kubernetes to deploy several FaaS Executors. This will be demonstrated in a future tutorial.

## HTTP frontent
In this final step we are going to use Fast API to develop a HTTP API. First, install FastAPI.

```bash
pip3 install fastapi uvicorn
```

The Fronend code:

```python
from fastapi import FastAPI, HTTPException
from pycolonies import FuncSpec, Conditions, colonies_client

app = FastAPI()

colonies, colonyname, colony_prvkey, executor_name, prvkey = colonies_client()

@app.get("/convert")
def convert(celsius: float):
    # Define the function specification
    func_spec = FuncSpec(
        funcname="execute",
        kwargs={
            "function": "convert",
            "arg": str(float(celsius))
        },
        conditions=Conditions(
            colonyname=colonyname,
            executortype="faas-executor",
        )
    )

    # Submit the function specification to the colonies
    process = colonies.submit_func_spec(func_spec, prvkey)
    print("Process", process.processid, "submitted")

    # wait for the process to be executed, timeout after 10 seconds
    process = colonies.wait(process, 10, prvkey)

    # check if the process has completed successfully
    if process.output is None:
        raise HTTPException(status_code=500, detail="Process execution failed or timed out")

    return {"fahrenheit": process.output}

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

```

### Submit a HTTP request.
```bash
curl -X GET "http://127.0.0.1:8000/convert?celsius=21.0"
```

```console
{"fahrenheit":[69.8]}
```

## Resilience and Fault Tolerance
Notice that it is possible to make an HTTP request even if no FaaS Executor is started. However, the submit function in the FastAPI code will timeout after 10 seconds. If a FaaS Executor is started before 10 seconds, the request will still be completed successfully. By setting **maxexectime** and **maxretries**, we can force an assigned process to be reassigned, returning to the queue at the Colonies server and being assigned to another executor. This mechanism is highly advantageous for DevOps and other operational scenarios.
