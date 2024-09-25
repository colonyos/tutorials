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

    # Wait for the process to be executed, timeout after 10 seconds
    process = colonies.wait(process, 10, prvkey)

    # Check if the process has completed successfully
    if process.output is None:
        raise HTTPException(status_code=500, detail="Process execution failed or timed out")
    
    return {"fahrenheit": process.output}

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
